"""Prepare evidence for a multimodal agent, then validate and render its analysis.

No model claims are fabricated by this CLI. It works without API credentials.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

IMAGES = {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff'}
VIDEOS = {'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v'}
SECTIONS = ('overview', 'experience', 'components', 'architecture', 'data_and_interfaces',
            'core_mechanism', 'implementation', 'resources_and_costs', 'risks_and_unknowns')
LABELS = {
 'overview': 'المنتج والقيمة / Product and value',
 'experience': 'التجربة والوظائف / Experience and behavior',
 'components': 'تفكيك المكونات / Component breakdown',
 'architecture': 'المعمارية المقترحة / Proposed architecture',
 'data_and_interfaces': 'البيانات والواجهات / Data and interfaces',
 'core_mechanism': 'آلية العمل الأساسية / Core mechanism',
 'implementation': 'خطة التنفيذ / Implementation plan',
 'resources_and_costs': 'الموارد والتكاليف / Resources and costs',
 'risks_and_unknowns': 'المجهول وخطة التحقق / Unknowns and verification',
}


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def prepare(args):
    if not 1 <= args.frames <= 60:
        raise ValueError('--frames must be between 1 and 60')
    sources = []
    for raw in args.source:
        parsed = urlparse(raw)
        if parsed.scheme in ('https', 'http') and parsed.netloc:
            sources.append({'id': f'S{len(sources)+1}', 'kind': 'url', 'location': raw,
                            'inspection': 'pending; open with browser or web tools'})
            continue
        path = Path(raw).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f'Source not found: {raw}')
        suffix = path.suffix.lower()
        if suffix not in IMAGES | VIDEOS:
            raise ValueError(f'Unsupported media: {suffix}')
        kind = 'image' if suffix in IMAGES else 'video'
        if kind == 'image' and not args.description.strip():
            raise ValueError('Image input requires --description explaining the product or behavior')
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest() if hasattr(hashlib, 'file_digest') else None
        sources.append({'id': f'S{len(sources)+1}', 'kind': kind, 'location': str(path),
                        'sha256': digest, 'inspection': 'pending'})
    out = Path(args.out).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError('Output directory is not empty; use a new directory to preserve prior work')
    out.mkdir(parents=True, exist_ok=True)
    for source in sources:
        if source['kind'] != 'video':
            continue
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            source['sampling_error'] = 'ffmpeg/ffprobe unavailable; inspect video with available media tools'
            continue
        try:
            meta = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                   '-of', 'json', source['location']], check=True, capture_output=True, text=True)
            duration = float(json.loads(meta.stdout)['format']['duration'])
            if duration <= 0:
                raise ValueError('Invalid video duration')
            source['duration_seconds'] = duration
            source['frames'] = []
            folder = out / 'evidence' / source['id']
            folder.mkdir(parents=True)
            for index in range(args.frames):
                timestamp = duration * (index + .5) / args.frames
                frame = folder / f'{index+1:03d}.jpg'
                subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(timestamp), '-i', source['location'],
                                '-frames:v', '1', '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease',
                                '-y', str(frame)], check=True, capture_output=True)
                if frame.is_file():
                    source['frames'].append({'path': str(frame.relative_to(out)), 'seconds': round(timestamp, 3)})
            source['sampling_note'] = 'Uniform samples only. Short interactions may be missing; inspect targeted intervals.'
        except (subprocess.SubprocessError, ValueError, KeyError) as exc:
            source['sampling_error'] = f'{type(exc).__name__}: inspect the original video directly'
    manifest = {'version': 1, 'name': args.name, 'language': args.lang,
                'description': args.description, 'sources': sources}
    dump(out / 'sources.json', manifest)
    template = {'version': 1, 'name': args.name, 'language': args.lang, 'status': 'draft',
                'evidence': [], 'claims': [], 'sections': {key: '' for key in SECTIONS}, 'parity_tests': []}
    dump(out / 'analysis.json', template)
    (out / 'PRODUCT.md').write_text(
        f'# {args.name}\n\nStatus: awaiting agent analysis; no conclusions yet.\n\n'
        'Read skills/rea-product/SKILL.md in the Rea-Product repository.\n'
        'Inspect sources.json and the source media/URLs. Fill analysis.json using the report contract.\n'
        'Every observed or inferred claim needs inspected evidence. Proposed implementation is not the original stack.\n'
        'Uniform video frames do not cover all transitions; inspect relevant intervals before conclusions.\n'
        'Then run: python -m rea_product report <this-directory>\n', encoding='utf-8')
    print(out / 'PRODUCT.md')
    return 0


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(data):
    if data.get('version') != 1 or data.get('status') != 'complete':
        raise ValueError('Analysis must have version 1 and status complete')
    if not nonempty(data.get('name')) or not nonempty(data.get('language')):
        raise ValueError('name and language are required')
    for key in SECTIONS:
        if not nonempty(data.get('sections', {}).get(key)):
            raise ValueError(f'Missing section: {key}')
    evidence = data.get('evidence', [])
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('At least one inspected evidence entry is required')
    ids = set()
    for item in evidence:
        if not all(nonempty(item.get(k)) for k in ('id', 'source', 'locator', 'observation')):
            raise ValueError('Evidence requires id, source, locator and observation')
        if item['id'] in ids:
            raise ValueError('Duplicate evidence id')
        ids.add(item['id'])
    claims = data.get('claims', [])
    if not isinstance(claims, list) or not claims:
        raise ValueError('At least one evidence-based claim is required')
    claim_ids = set()
    for item in claims:
        if not all(nonempty(item.get(k)) for k in ('id', 'statement')) or item['id'] in claim_ids:
            raise ValueError('Claims require unique id and statement')
        claim_ids.add(item['id'])
        state = item.get('status')
        if state not in ('observed', 'inferred', 'proposed', 'unknown'):
            raise ValueError('Invalid claim status')
        refs = item.get('evidence', [])
        if not isinstance(refs, list) or any(ref not in ids for ref in refs):
            raise ValueError('Invalid evidence reference')
        if state in ('observed', 'inferred') and not refs:
            raise ValueError('Observed/inferred claims require evidence')
        if state in ('inferred', 'unknown') and not nonempty(item.get('verification')):
            raise ValueError('Inferred/unknown claims require a verification step')
    tests = data.get('parity_tests', [])
    if not isinstance(tests, list) or not tests:
        raise ValueError('Behavioral parity tests are required')
    for test in tests:
        if not all(nonempty(test.get(k)) for k in ('feature', 'procedure', 'expected')):
            raise ValueError('Parity tests require feature, procedure and expected')
        if test.get('status') not in ('not_run', 'passed', 'failed', 'blocked'):
            raise ValueError('Invalid parity test status')
        if test['status'] in ('passed', 'failed') and not nonempty(test.get('result_evidence')):
            raise ValueError('Executed tests require result_evidence')


def report(args):
    out = Path(args.directory).expanduser().resolve()
    data = json.loads((out / 'analysis.json').read_text(encoding='utf-8'))
    validate(data)
    parts = [f"# {data['name']}", 'Rea-Product · Evidence-led reconstruction plan']
    for key in SECTIONS:
        parts.extend([f'## {LABELS[key]}', data['sections'][key]])
    parts.append('## Evidence / الأدلة')
    for item in data['evidence']:
        parts.append(f"- [{item['id']}] {item['source']} — {item['locator']}\n  {item['observation']}")
    parts.append('## Claims / الاستنتاجات')
    for item in data['claims']:
        parts.append(f"- [{item['id']}] ({item['status']}) {item['statement']}\n  Evidence: {', '.join(item.get('evidence', []))}\n  Verification: {item.get('verification', '—')}")
    parts.append('## Parity checks / اختبارات المطابقة')
    for item in data['parity_tests']:
        parts.append(f"- {item['feature']} [{item['status']}]\n  {item['procedure']}\n  Expected: {item['expected']}\n  Result: {item.get('result_evidence', 'Not executed')}")
    markdown = '\n\n'.join(parts) + '\n'
    (out / 'report.md').write_text(markdown, encoding='utf-8')
    direction = 'rtl' if data['language'].lower().startswith('ar') else 'ltr'
    body = []
    for part in parts:
        if part.startswith('# '):
            body.append('<h1>' + html.escape(part[2:]) + '</h1>')
        elif part.startswith('## '):
            body.append('<h2>' + html.escape(part[3:]) + '</h2>')
        else:
            body.append('<div class="text">' + html.escape(part) + '</div>')
    document = ('<!doctype html><html lang="' + html.escape(data['language'], quote=True) + '" dir="' + direction + '">'
                '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                '<title>' + html.escape(data['name']) + '</title><style>'
                'body{max-width:1000px;margin:40px auto;padding:24px;background:#faf9f5;color:#202a30;'
                'font:17px/1.8 system-ui,sans-serif}h1{font-size:2.5rem}h2{border-bottom:1px solid #bbb;'
                'padding-top:28px;color:#12685b}.text{white-space:pre-wrap;overflow-wrap:anywhere;margin:16px 0}'
                '@media print{body{margin:0;max-width:none}h2{break-after:avoid}}</style>' + ''.join(body) + '</html>')
    (out / 'report.html').write_text(document, encoding='utf-8')
    (out / 'PRODUCT.md').write_text(f"# {data['name']}\n\n" + data['sections']['overview'] + '\n\n'
                                  '## Files\n- report.html — human report\n- report.md — readable full report\n'
                                  '- analysis.json — claims, evidence, build plan and parity tests\n'
                                  '- sources.json — original inputs and sampled frames\n', encoding='utf-8')
    print(out / 'report.html')
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog='rea-product', description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prep = sub.add_parser('prepare', help='Prepare video, image + description, or product URL evidence')
    prep.add_argument('source', nargs='+')
    prep.add_argument('--description', default='')
    prep.add_argument('--name', default='Product analysis')
    prep.add_argument('--lang', default='ar')
    prep.add_argument('--frames', type=int, default=12)
    prep.add_argument('-o', '--out', required=True)
    prep.set_defaults(handler=prepare)
    render = sub.add_parser('report', help='Validate and render the completed agent analysis')
    render.add_argument('directory')
    render.set_defaults(handler=report)
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        print(f'rea-product: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
