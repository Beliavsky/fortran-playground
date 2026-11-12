import http.client
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
import threading
import unittest
from unittest.mock import patch
import zipfile

import ford_docs as docs
from xfortran_serve import LocalServer

SOURCE = '''module example
implicit none
contains
!> Double an input.
subroutine twice(x,y)
real, intent(in) :: x
real, intent(out) :: y
y=2*x
end subroutine
end module
'''


class DocumentationTests(unittest.TestCase):
    def test_validation_and_artifact_confinement(self):
        for payload in ({'url':'file:///etc/passwd'}, {'url':'https://github.com/a/b','command':'x'},
                        {'url':'https://github.com/a/b','subdirectory':'../x'},
                        {'url':'https://github.com/a/b','revision':'--help'}):
            # A leading dash is permitted as a GitHub ref; it is never a CLI option.
            if payload.get('revision') == '--help':
                self.assertEqual(docs.validate_request(payload)['revision'],'--help')
            else:
                with self.assertRaises(ValueError): docs.validate_request(payload)
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);key='a'*64;(root/key).mkdir();(root/key/'index.html').write_text('hi')
            self.assertEqual(docs.artifact(root,key,'index.html').read_text(),'hi')
            for key,name in [('..','index.html'),('a'*64,'../../secret'),('a'*64,'C:\\secret')]:
                with self.assertRaises(ValueError):docs.artifact(root,key,name)

    def test_source_only_snapshot_rejects_file_includes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir()
            (source/'a.f90').write_text(SOURCE)
            (source/'fpm.toml').write_text('[extra.ford]\npreprocessor="evil"')
            (source/'run.py').write_text('raise RuntimeError()')
            (source/'build').mkdir();(source/'build/old.f90').write_text('bad')
            self.assertEqual(docs.snapshot(source,root/'copy'),1)
            self.assertEqual([p.name for p in (root/'copy').iterdir()],['a.f90'])
            for text in ("include '../../secret'", "include &\n '/etc/passwd'", '!! {! /etc/passwd !}'):
                (source/'a.f90').write_text(text)
                with self.assertRaisesRegex(ValueError,'include|INCLUDE'): docs.snapshot(source,root/'copy')
            with patch.object(docs,'MAX_SOURCE',1):
                with self.assertRaisesRegex(ValueError,'limit'):docs.snapshot(source,root/'copy')

    def test_generation_cache_invalidation_zip_and_failure(self):
        with tempfile.TemporaryDirectory() as temporary, patch('ford_docs.importlib.metadata.version',return_value=docs.FORD_VERSION):
            root=Path(temporary);source=root/'source';source.mkdir();(source/'a.f90').write_text(SOURCE)
            calls=[]
            def run(command,**kwargs):
                calls.append(command);work=Path(kwargs['cwd']);config=(work/'project.md').read_text()
                self.assertIn('preprocess: false',config);self.assertFalse((work/'fpm.toml').exists())
                (work/'html').mkdir();(work/'html/index.html').write_text('API')
                return subprocess.CompletedProcess(command,0)
            r=docs.generate(source,root/'cache',runner=run)
            self.assertFalse(r['cached'])
            again=docs.generate(source,root/'cache',runner=run)
            self.assertTrue(again['cached']);self.assertEqual(len(calls),1)
            with zipfile.ZipFile(root/'cache'/r['key']/'documentation.zip') as z:
                self.assertIn('index.html',z.namelist());self.assertIn('metadata.json',z.namelist())
            (source/'a.f90').write_text(SOURCE+'! change\n')
            self.assertNotEqual(docs.generate(source,root/'cache',runner=run)['key'],r['key'])
            (source/'a.f90').write_text(SOURCE+'! failure\n')
            with self.assertRaisesRegex(ValueError,'could not document'):
                docs.generate(source,root/'cache',runner=lambda *a,**k:subprocess.CompletedProcess(a[0],1))
            with self.assertRaisesRegex(ValueError,'120 seconds'):
                docs.generate(source,root/'cache',runner=lambda *a,**k:(_ for _ in ()).throw(subprocess.TimeoutExpired(a[0],120)))

    def test_github_resolves_commit_before_download_without_fpm_manifest(self):
        archive=io.BytesIO()
        with tarfile.open(fileobj=archive,mode='w:gz') as tar:
            data=SOURCE.encode();info=tarfile.TarInfo('package/src/api.f90');info.size=len(data);tar.addfile(info,io.BytesIO(data))
        calls=[]
        def fetch(url,**kwargs):
            calls.append(url)
            return json.dumps({'sha':'b'*40}).encode() if '/commits/' in url else archive.getvalue()
        with tempfile.TemporaryDirectory() as temporary, patch('ford_docs.generate',return_value={'key':'k'}) as generate:
            docs.github_documentation({'url':'https://github.com/owner/repo','revision':'main'},temporary,downloader=fetch)
            self.assertTrue(calls[0].endswith('/commits/main'))
            self.assertTrue(calls[1].endswith('/'+'b'*40))
            self.assertEqual(generate.call_args.kwargs['revision'],'b'*40)

    @unittest.skipUnless(importlib.util.find_spec('ford'),'optional FORD installation required')
    def test_real_ford_argument_declarations_and_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);source=root/'source';source.mkdir();(source/'a.f90').write_text(SOURCE)
            result=docs.generate(source,root/'cache')
            page=(root/'cache'/result['key']/'proc/twice.html').read_text(encoding='utf8')
            self.assertIn('intent(in)',page);self.assertIn('intent(out)',page)
            search=(root/'cache'/result['key']/'search.html').read_text(encoding='utf8')
            self.assertIn('pilot-assets/lunr.min.js',search)
            self.assertIn('search_database.js',search)
            self.assertNotIn('https://unpkg.com',search)
            self.assertTrue((root/'cache'/result['key']/'search/search_database.js').is_file())
            self.assertTrue(docs.generate(source,root/'cache')['cached'])

    def test_local_http_token_generation_and_sandboxed_output(self):
        with tempfile.TemporaryDirectory() as temporary, patch('xfortran_serve.discover',return_value={}):
            server=LocalServer(temporary,port=0)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            def request(method,path,data=None,token=True):
                client=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=10)
                headers={'Origin':server.origin,'Content-Type':'application/json'}
                if token:headers['X-Local-Token']=server.token
                client.request(method,path,json.dumps(data) if data else None,headers)
                response=client.getresponse();body=response.read();result=(response.status,dict(response.getheaders()),body);client.close();return result
            try:
                self.assertEqual(request('POST','/api/documentation',{'url':'x'},token=False)[0],403)
                key='a'*64;folder=Path(temporary)/'.fortran-docs'/key;folder.mkdir(parents=True);(folder/'index.html').write_text('API')
                with patch('ford_docs.github_documentation',return_value={'key':key}):
                    status,_,body=request('POST','/api/documentation',{'url':'https://github.com/a/b'})
                    self.assertEqual(status,200);self.assertTrue(json.loads(body)['ok'])
                status,headers,body=request('GET','/documentation/view/'+key+'/index.html',token=False)
                self.assertEqual(status,200);self.assertIn('sandbox allow-scripts',headers['Content-Security-Policy'])
                self.assertEqual(body,b'API')
                self.assertEqual(request('GET','/documentation/')[0],200)
            finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main()
