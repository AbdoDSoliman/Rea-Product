import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from rea_product.cli import main, validate, SECTIONS


def complete():
    return {'version': 1, 'name': '<script>alert(1)</script>', 'language': 'ar', 'status': 'complete',
            'sections': {k: 'تحليل اختباري' for k in SECTIONS},
            'evidence': [{'id': 'E1', 'source': 'image.png', 'locator': 'center', 'observation': 'Button visible'}],
            'claims': [{'id': 'C1', 'statement': 'Button visible', 'status': 'observed', 'evidence': ['E1']}],
            'parity_tests': [{'feature': 'Button', 'procedure': 'Press button', 'expected': 'Dialog opens', 'status': 'not_run'}]}


class ProductTests(unittest.TestCase):
    def test_report_contract_rejects_unsupported_claims(self):
        data = complete()
        data['claims'][0]['evidence'] = ['missing']
        with self.assertRaises(ValueError): validate(data)
        data['claims'][0]['evidence'] = []
        with self.assertRaises(ValueError): validate(data)

    def test_inference_requires_verification(self):
        data = complete()
        data['claims'][0]['status'] = 'inferred'
        with self.assertRaises(ValueError): validate(data)
        data['claims'][0]['verification'] = 'Inspect docs and reproduce behavior'
        validate(data)

    def test_passed_test_needs_execution_evidence(self):
        data = complete()
        data['parity_tests'][0]['status'] = 'passed'
        with self.assertRaises(ValueError): validate(data)

    def test_url_intake_and_preserve_existing_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            self.assertEqual(main(['prepare', 'https://example.com/product', '-o', str(out)]), 0)
            original = (out / 'analysis.json').read_bytes()
            self.assertEqual(main(['prepare', 'https://example.com/other', '-o', str(out)]), 2)
            self.assertEqual((out / 'analysis.json').read_bytes(), original)
            self.assertEqual(main(['report', str(out)]), 2)
            self.assertFalse((out / 'report.html').exists())

    def test_image_requires_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'input.png'
            source.write_bytes(b'fixture')
            out = Path(tmp) / 'out'
            self.assertEqual(main(['prepare', str(source), '-o', str(out)]), 2)
            self.assertEqual(main(['prepare', str(source), '--description', 'A product', '-o', str(out)]), 0)
            self.assertEqual(json.loads((out / 'sources.json').read_text())['sources'][0]['kind'], 'image')

    def test_report_rtl_and_escapes_untrusted_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            (out / 'analysis.json').write_text(json.dumps(complete()))
            self.assertEqual(main(['report', tmp]), 0)
            rendered = (out / 'report.html').read_text()
            self.assertIn('dir="rtl"', rendered)
            self.assertNotIn('<script>', rendered)
            self.assertIn('&lt;script&gt;', rendered)
            self.assertTrue((out / 'report.md').exists())

    @unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg unavailable')
    def test_real_video_frames_and_timestamps(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / 'demo.mp4'
            subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=red:s=160x120:d=1',
                            '-c:v', 'mpeg4', str(video)], check=True)
            out = Path(tmp) / 'out'
            self.assertEqual(main(['prepare', str(video), '--frames', '2', '-o', str(out)]), 0)
            source = json.loads((out / 'sources.json').read_text())['sources'][0]
            self.assertEqual(len(source['frames']), 2)
            self.assertLess(source['frames'][0]['seconds'], source['frames'][1]['seconds'])
            for frame in source['frames']:
                self.assertGreater((out / frame['path']).stat().st_size, 100)

if __name__ == '__main__':
    unittest.main()
