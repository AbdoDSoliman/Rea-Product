import json
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser
from rea_product.cli import main, validate
from rea_product.rendering import local_image
from test_product import complete


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.ids, self.links, self.images, self.text = [], [], [], []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'a': self.links.append(attrs.get('href', ''))
        if tag == 'img': self.images.append(attrs.get('src', ''))
    def handle_data(self, text): self.text.append(text)


class RenderingTests(unittest.TestCase):
    def test_complete_narrative_and_ledger_survive_presentation(self):
        data = complete()
        data['presentation'] = {'title': 'Short title', 'summary': 'Short summary',
                                'sections': {'components': {'cards': [{'title': 'Module', 'text': 'E1'}]}}}
        data['sections']['components'] = 'Unique technical contract\nFailure and recovery details'
        data['claims'][0]['verification'] = 'Original verification details'
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'analysis.json').write_text(json.dumps(data))
            self.assertEqual(main(['report', tmp]), 0)
            doc = Document((out / 'report.html').read_text())
            text = ''.join(doc.text)
            for value in [*data['sections'].values(), 'Original verification details', data['parity_tests'][0]['procedure'], data['parity_tests'][0]['expected']]:
                for line in value.splitlines(): self.assertIn(line, text)
            self.assertEqual(len(doc.ids), len(set(doc.ids)))
            for href in doc.links:
                if href.startswith('#') and len(href) > 1: self.assertIn(href[1:], doc.ids)

    def test_media_boundary_and_unsafe_sources(self):
        data = complete()
        data['evidence'][0].update(source='javascript:alert(1)', image='../outside.png')
        data['presentation'] = {'title': '<img src=x onerror=alert(1)>', 'hero_image': 'https://example.com/track.jpg'}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); out = root / 'report'; out.mkdir()
            (root / 'outside.png').write_bytes(b'not copied')
            self.assertIsNone(local_image(out, '../outside.png'))
            self.assertIsNone(local_image(out, str(root / 'outside.png')))
            (out / 'analysis.json').write_text(json.dumps(data))
            self.assertEqual(main(['report', str(out)]), 0)
            for name in ['report.html', 'report-evidence.html']:
                doc = Document((out / name).read_text())
                self.assertEqual(doc.images, [])
                self.assertFalse(any(x.startswith('javascript:') for x in doc.links))

    def test_explicit_image_and_english_fallback(self):
        data = complete(); data['language'] = 'en'
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'frame name.jpg').write_bytes(b'fixture')
            data['evidence'][0]['image'] = 'frame name.jpg'
            (out / 'analysis.json').write_text(json.dumps(data))
            self.assertEqual(main(['report', tmp]), 0)
            result = (out / 'report.html').read_text()
            self.assertIn('dir="ltr"', result)
            self.assertIn('Not run', result)
            self.assertIn('frame%20name.jpg', Document(result).images)
            self.assertIn('frame%20name.jpg', Document((out / 'report-evidence.html').read_text()).images)

    def test_invalid_presentation_rejected(self):
        for presentation in [[], {'sections': []}, {'sections': {'unknown': {}}}, {'sections': {'overview': {'cards': [{}]}}}]:
            with self.subTest(presentation=presentation):
                data = complete(); data['presentation'] = presentation
                with self.assertRaises(ValueError): validate(data)
