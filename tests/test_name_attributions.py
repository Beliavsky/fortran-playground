import copy
import json
from pathlib import Path
import tempfile
import unittest

from catalog_export import validate_attributions
from xpackage_attributions import ROOT, REPORT, load_attributions, report_text


class AttributionTests(unittest.TestCase):
    def test_review_table_is_current_and_keeps_inferences_distinct(self):
        data = load_attributions()
        self.assertEqual(data['owner_names']['lauvergn']['status'], 'inferred')
        credit = data['project_authors']['github:lauvergn/ad_dnsvm'][0]
        self.assertEqual(credit['status'], 'confirmed')
        self.assertEqual(credit['name'], 'David Lauvergnat')
        self.assertEqual((ROOT/REPORT).read_text(encoding='utf-8'), report_text())

    def test_bad_attributions_require_evidence_scope_and_review_status(self):
        data = load_attributions()
        for field, value in [('evidence', []), ('status', 'guessed'), ('scope', ''), ('reviewed_on', 'yesterday')]:
            invalid = copy.deepcopy(data)
            invalid['owner_names']['lauvergn'][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_attributions(invalid)
        invalid = copy.deepcopy(data)
        invalid['owner_names']['lauvergn']['evidence'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            validate_attributions(invalid)

    def test_conflict_is_reported_and_profile_refresh_does_not_edit_manual_file(self):
        from xgithub_owners import refresh
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root/'fpm_catalog/name-attributions.json'
            path.parent.mkdir()
            path.write_text(json.dumps(load_attributions()), encoding='utf-8')
            original = path.read_bytes()
            refresh([{'repository': 'lauvergn/AD_dnSVM'}], root/'fpm_catalog/owners.json',
                    fetch_owner=lambda login: {'login': login, 'display_name': 'Different Public Name',
                        'profile_url': 'https://github.com/'+login, 'account_type': 'User'})
            self.assertEqual(path.read_bytes(), original)
            self.assertIn('Review: names differ', report_text(root))
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(load_attributions(temporary), {'schema': 1, 'owner_names': {}, 'project_authors': {}})
