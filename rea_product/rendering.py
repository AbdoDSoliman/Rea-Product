"""Portable, evidence-led reports. Presentation metadata never replaces analysis."""
from __future__ import annotations
import html
import re
from pathlib import Path
from urllib.parse import quote, urlparse

ASSETS = Path(__file__).with_name('assets')


def escape(value):
    return html.escape(str(value), quote=True)


def local_image(root, value):
    """Only existing raster assets inside the output directory are embedded."""
    if not isinstance(value, str) or not value or urlparse(value).scheme:
        return None
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        return None
    if path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.gif'}:
        return None
    return quote(path.relative_to(root.resolve()).as_posix())


def source_link(source):
    parsed = urlparse(source)
    if parsed.scheme in {'https', 'http'} and parsed.netloc:
        return f'<a class="raw-link" href="{escape(source)}" target="_blank" rel="noopener noreferrer">{escape(source)} ↗</a>'
    return f'<span class="raw-link">{escape(source)}</span>'


def render_documents(data, root, labels):
    ar = data['language'].lower().startswith('ar')
    def tr(a, b): return a if ar else b
    refs = {e['id']: f'evidence-{i}' for i, e in enumerate(data['evidence'])}
    def rich(text):
        # Match IDs before escaping so source text can never inject markup.
        pattern = '(' + '|'.join(re.escape(k) for k in sorted(refs, key=len, reverse=True)) + ')'
        parts = re.split(r'(?<!\w)' + pattern + r'(?!\w)', str(text))
        return ''.join(f'<a class="ref" href="#{refs[p]}">{escape(p)}</a>' if p in refs else escape(p) for p in parts)
    def paragraphs(text):
        return ''.join(f'<p>{rich(line)}</p>' for line in str(text).splitlines() if line.strip())
    def details(title, text):
        return f'<details class="reading"><summary>{escape(title)}<span class="plus">＋</span></summary><div class="reading-body">{paragraphs(text)}</div></details>'
    def picture(value, caption=''):
        url = local_image(root, value)
        if not url: return ''
        return f'<figure class="rich-image"><a href="{url}"><img src="{url}" loading="lazy" alt="{escape(caption)}"></a><figcaption>{escape(caption)}</figcaption></figure>'
    def section_title(key):
        pair = labels[key].split(' / ')
        return pair[0] if ar else pair[-1]
    p = data.get('presentation', {})
    title = p.get('title') or data['name']
    summary = p.get('summary') or data['sections']['overview'].splitlines()[0]
    hero = local_image(root, p.get('hero_image'))
    nav_items = [(k, section_title(k)) for k in labels] + [('tests', tr('اختبارات المطابقة', 'Parity tests')), ('evidence', tr('الأدلة', 'Evidence'))]
    nav = ''.join(f'<a href="#{key}"><span>{i:02}</span>{escape(label)}</a>' for i, (key, label) in enumerate(nav_items, 1))
    stats = [(len(data['evidence']), tr('دليل موثق', 'Evidence records')), (len(data['claims']), tr('استنتاج مصنّف', 'Classified claims')), (len(data['parity_tests']), tr('اختبار مطابقة', 'Parity tests'))]
    body = '<div class="progress" id="progress"></div>'
    body += f'<header class="masthead"><a class="brand" href="#">REA–PRODUCT</a><span class="mast-meta">{tr("تحليل المنتج وخطة إعادة البناء", "Product teardown & reconstruction")}</span><a class="gallery-link" href="report-evidence.html">{tr("معرض الأدلة", "Evidence gallery")} ↗</a></header><main>'
    body += f'<section class="hero {"" if hero else "no-image"}">'
    if hero:
        body += f'<div class="hero-image"><img src="{hero}" alt="{escape(p.get("hero_caption", title))}"></div>'
    body += f'<div class="hero-copy"><div class="eyebrow">EVIDENCE → UNDERSTANDING → RECONSTRUCTION</div><h1>{escape(title)}</h1><p class="lead">{rich(summary)}</p><a class="cta" href="#overview">{tr("اقرأ التحليل", "Explore the analysis")} ↓</a></div></section>'
    body += '<div class="facts" style="grid-template-columns:repeat(3,1fr)">' + ''.join(f'<div><strong>{n}</strong><span>{text}</span></div>' for n, text in stats) + '</div>'
    body += f'<div class="layout"><aside><nav aria-label="{tr("أقسام التقرير", "Report sections")}">{nav}</nav><div class="aside-note">{tr("اكتمال التحليل لا يعني تحقق المطابقة.", "A complete analysis does not establish parity.")}</div></aside><div class="content">'
    for index, key in enumerate(labels, 1):
        text = data['sections'][key]
        lines = [line for line in text.splitlines() if line.strip()]
        body += f'<section id="{key}"><header class="section-head"><span class="index">{index:02}</span><div><div class="eyebrow">REA–PRODUCT / {escape(key.upper().replace("_", " "))}</div><h2>{escape(section_title(key))}</h2></div></header>'
        # Optional editorial annotations are authored by the analyst, not invented by the renderer.
        annotation = p.get('sections', {}).get(key, {})
        body += f'<p class="section-summary">{rich(annotation.get("summary") or lines[0])}</p>'
        body += picture(annotation.get('image'), annotation.get('caption', ''))
        cards = annotation.get('cards', [])
        if cards:
            body += '<div class="journey-grid">'
            for card in cards:
                body += '<article class="step">' + picture(card.get('image'), card.get('caption', ''))
                body += f'<div class="step-copy"><h3>{escape(card["title"])}</h3><p>{rich(card["text"])}</p></div></article>'
            body += '</div>'
        # Keep the complete source narrative, including contracts and caveats, accessible.
        body += details(tr('التفاصيل الكاملة', 'Full analysis'), text) + '</section>'
    states = {'not_run': tr('لم يُنفذ', 'Not run'), 'passed': tr('ناجح', 'Passed'), 'failed': tr('فشل', 'Failed'), 'blocked': tr('متعطل', 'Blocked')}
    body += f'<section id="tests"><header class="section-head"><span class="index">10</span><div><h2>{tr("المطابقة تُختبر، لا تُفترض.", "Parity must be tested.")}</h2><p>{tr("الحالات أدناه من سجل الاختبارات؛ لا يحول التصميم خطة اختبار إلى نتيجة ناجحة.", "Statuses come from the test ledger; a test plan is not a successful result.")}</p></div></header>'
    body += f'<div class="test-tools"><label for="test-search">{tr("ابحث في الاختبارات", "Search tests")}</label><div class="search-wrap"><input id="test-search" type="search"><span id="test-count" aria-live="polite">{len(data["parity_tests"])}</span></div><button id="expand-tests" type="button" data-open="{tr("فتح الاختبارات", "Expand tests")}" data-close="{tr("طي الاختبارات", "Collapse tests")}">{tr("فتح الاختبارات", "Expand tests")}</button></div><div class="tests-list">'
    for i, test in enumerate(data['parity_tests']):
        body += f'<details class="test"><summary><bdi>{i+1:02}</bdi><span>{escape(test["feature"])}</span><small>{states[test["status"]]}</small><i class="plus">＋</i></summary><div class="test-body">'
        for label, value in [(tr('الإجراء', 'Procedure'), test['procedure']), (tr('القبول', 'Expected'), test['expected']), (tr('دليل التنفيذ', 'Result evidence'), test.get('result_evidence') or tr('لا يوجد', 'None'))]:
            body += f'<div><h4>{label}</h4>{paragraphs(value)}</div>'
        body += '</div></details>'
    body += f'</div><p id="empty-tests" hidden>{tr("لا توجد نتائج.", "No matching tests.")}</p></section>'
    evidence = ''
    for item in data['evidence']:
        evidence += f'<article class="source" id="{refs[item["id"]]}">' + picture(item.get('image'), item['locator'])
        evidence += f'<div><span class="source-id">{escape(item["id"])}</span><p>{escape(item["locator"])}</p><p>{escape(item["observation"])}</p>{source_link(item["source"])}</div></article>'
    body += f'<section id="evidence"><header class="section-head"><span class="index">11</span><div><h2>{tr("الأدلة والمراجع", "Evidence & sources")}</h2></div></header><div class="source-grid">{evidence}</div></section>'
    classifications = {'observed': tr('مشاهد / موثق', 'Observed'), 'inferred': tr('مستنتج', 'Inferred'), 'proposed': tr('مقترح', 'Proposed'), 'unknown': tr('غير محسوم', 'Unknown')}
    body += f'<section><header class="section-head"><div><h2>{tr("سجل الاستنتاجات", "Claims ledger")}</h2></div></header><div class="claims-grid">'
    for claim in data['claims']:
        body += f'<article class="claim-card"><span class="claim-tag {claim["status"]}">{classifications[claim["status"]]}</span><bdi>{escape(claim["id"])}</bdi><p>{escape(claim["statement"])}</p>{rich(" · ".join(claim.get("evidence", [])))}<p>{escape(claim.get("verification", ""))}</p></article>'
    body += f'</div></section><footer><div class="footer-brand">REA–PRODUCT</div><p>{tr("الأدلة أولًا. التنفيذ المقترح ليس كشفًا للنظام الأصلي.", "Evidence first. A proposed build is not a disclosure of original internals.")}</p><div><a href="report.md">Markdown</a><a href="analysis.json">JSON</a><a href="report-evidence.html">{tr("معرض الأدلة", "Evidence gallery")}</a><button id="print-report">{tr("طباعة", "Print")}</button></div></footer></div></div></main>'
    css = (ASSETS / 'report.css').read_text(encoding='utf-8')
    js = (ASSETS / 'report.js').read_text(encoding='utf-8')
    def document(content, scripts=''):
        return f'<!doctype html><html lang="{escape(data["language"])}" dir="{"rtl" if ar else "ltr"}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(title)}</title><style>{css}</style></head><body>{content}{scripts}</body></html>'
    gallery = f'<main class="evidence-only"><a href="report.html">← {tr("التقرير", "Report")}</a><h1>{tr("معرض الأدلة والتوقيتات", "Evidence gallery")}</h1><div class="source-grid">{evidence}</div></main>'
    return document(body, '<script type="text/javascript">' + js + '</script>'), document(gallery)
