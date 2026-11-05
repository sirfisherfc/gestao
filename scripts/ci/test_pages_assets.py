"""Exercise the generated artifact: changed assets get new URLs and remain fetchable."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts/implantacao'))
from versionar_assets_pages import versionar


class PagesAssetsTest(unittest.TestCase):
    def test_browser_gets_matching_files_and_new_url_after_an_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);assets=root/'assets';assets.mkdir()
            original='<link href="assets/main.css"><script src="assets/app.js"></script><script src="https://cdn.example.test/sdk.js"></script>'
            (root/'vouchers.html').write_text(original,encoding='utf8')
            (assets/'main.css').write_text('body{color:navy}',encoding='utf8')
            (assets/'app.js').write_text('var version=1;',encoding='utf8')
            mapping=versionar(root)
            html=(root/'vouchers.html').read_text(encoding='utf8')
            self.assertIn('https://cdn.example.test/sdk.js',html)
            for source,url in mapping.items():
                self.assertIn(url,html);self.assertEqual((root/source).read_bytes(),(root/url).read_bytes())
            self.assertNotIn('?v=',html)
            previous=mapping['assets/app.js']
            (assets/'app.js').write_text('var version=2;',encoding='utf8')
            (root/'vouchers.html').write_text(original,encoding='utf8')
            current=versionar(root)
            self.assertNotEqual(previous,current['assets/app.js'])
            self.assertEqual(mapping['assets/main.css'],current['assets/main.css'])
            self.assertTrue((root/'assets/app.js').exists(),'other pages keep their original references')

    def test_does_not_resolve_assets_outside_the_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'assets').mkdir()
            (root/'secret.js').write_text('private',encoding='utf8')
            (root/'vouchers.html').write_text('<script src="assets/../secret.js"></script>',encoding='utf8')
            with self.assertRaises(ValueError):versionar(root)


if __name__=='__main__':unittest.main()
