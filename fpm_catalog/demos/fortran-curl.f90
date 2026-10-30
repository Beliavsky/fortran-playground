! Offline URL API example, following fortran-curl's examples/url/url.f90 (ISC).
! Parsing and constructing a URL does not make a network request.
program main
   use iso_c_binding, only: c_ptr, c_associated, c_null_ptr
   use curl
   implicit none
   type(c_ptr) :: handle
   character(len=:), allocatable :: host, path, port, query, complete
   integer :: rc
   handle=curl_url()
   if (.not.c_associated(handle)) error stop 'URL allocation failed'
   rc=curl_url_set(handle,CURLUPART_URL,'https://example.org:8443/data/input.csv?sample=1')
   if (rc/=CURLUE_OK) error stop 'URL parsing failed'
   rc=curl_url_get(handle,CURLUPART_HOST,host)
   if (rc/=CURLUE_OK) error stop 'Host extraction failed'
   rc=curl_url_get(handle,CURLUPART_PATH,path)
   if (rc/=CURLUE_OK) error stop 'Path extraction failed'
   rc=curl_url_get(handle,CURLUPART_PORT,port)
   if (rc/=CURLUE_OK) error stop 'Port extraction failed'
   rc=curl_url_get(handle,CURLUPART_QUERY,query)
   if (rc/=CURLUE_OK) error stop 'Query extraction failed'
   if (host/='example.org' .or. path/='/data/input.csv' .or. port/='8443' .or. query/='sample=1') &
      error stop 'Parsed components differ from expected values'
   print '(a)', 'Host: '//host, 'Path: '//path, 'Port: '//port, 'Query: '//query
   rc=curl_url_set(handle,CURLUPART_PATH,'/results/output.csv')
   if (rc/=CURLUE_OK) error stop 'Path update failed'
   rc=curl_url_get(handle,CURLUPART_URL,complete)
   if (rc/=CURLUE_OK) error stop 'URL reconstruction failed'
   if (complete/='https://example.org:8443/results/output.csv?sample=1') error stop 'Reconstructed URL check'
   print '(a)', 'Updated URL: '//complete
   call curl_url_cleanup(handle)
   ! This release uses C cleanup semantics: the caller clears the freed handle.
   handle=c_null_ptr
   print '(a)', 'PASS fortran-curl'
end program main
