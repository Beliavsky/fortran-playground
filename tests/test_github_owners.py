"""Public profile snapshots preserve names on errors and do not infer authorship."""
from io import BytesIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from xgithub_owners import ProfileParser, github_owner, load_owners, refresh


class OwnerTests(unittest.TestCase):
    def test_api_reads_only_public_name_and_account_identity(self):
        data = {'login': 'Example', 'name': '  Public   Name ', 'type': 'User',
                'html_url': 'https://github.com/Example', 'email': 'not-copied@example.test'}
        with patch('xgithub_owners.urlopen', return_value=BytesIO(json.dumps(data).encode())) as request:
            record = github_owner('example')
        self.assertEqual(record['display_name'], 'Public Name')
        self.assertNotIn('email', record)
        self.assertEqual(request.call_args.args[0].full_url, 'https://api.github.com/users/example')

    def test_partial_refresh_preserves_previous_names_and_success_can_clear_them(self):
        packages = [{'repository': 'Example/one'}, {'repository': 'example/two'}]
        calls = []
        def fetch(login):
            calls.append(login)
            return {'login': 'Example', 'display_name': 'Public Name', 'account_type': 'User',
                    'profile_url': 'https://github.com/Example'}
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'fpm_catalog/owners.json'
            data, errors = refresh(packages, path, fetch_owner=fetch)
            self.assertEqual(calls, ['example'])
            self.assertEqual(errors, {})
            self.assertEqual(load_owners(temporary), data['owners'])
            def fail(login):
                raise OSError('offline')
            saved, errors = refresh(packages, path, fetch_owner=fail)
            self.assertEqual(saved, data)
            self.assertIn('example', errors)
            no_name = {**fetch('example'), 'display_name': None}
            saved, errors = refresh(packages, path, fetch_owner=lambda login: no_name)
            self.assertIsNone(saved['owners']['example']['display_name'])
            self.assertFalse(errors)
            with self.assertRaises(ValueError):
                refresh(packages, path, only=['not-a-selected-owner'], fetch_owner=fetch)

    def test_profile_parser_reads_heading_instead_of_readme_names(self):
        for html, name, kind in [
            ('<h1 class="vcard-names"><span itemprop="name" class="p-name vcard-fullname">Federico Perini</span></h1><article>Another Name</article>', 'Federico Perini', 'User'),
            ('<span class="p-name" itemprop="name"> </span><h1 class="h2 lh-condensed">README Name</h1>', None, 'User'),
            ('<h1 class="h2 lh-condensed"><span>Example Organization</span></h1>', 'Example Organization', 'Organization')]:
            parser = ProfileParser()
            parser.feed(html)
            self.assertEqual((parser.name, parser.account_type), (name, kind))

    def test_account_redirect_and_invalid_responses_cannot_replace_saved_names(self):
        packages = [{'repository': 'example/one'}]
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)/'owners.json'
            data, errors = refresh(packages, path, fetch_owner=lambda login: {
                'login': 'different-account', 'display_name': 'Someone Else',
                'account_type': 'User', 'profile_url': 'https://github.com/different-account'})
            self.assertEqual(data['owners'], {})
            self.assertIn('example', errors)
