"""Assemble the AISR lab report from the course template and content.py.

    python report/build.py            # writes report/AISR_LabReport.docx (+ PDF, page-number pass)

The template's front matter (title page, declaration, section breaks, headers and
footers, page border, styles) is kept. Index / List of Figures / List of Tables and
every experiment chapter are rebuilt from content.py, reusing the template's own
paragraph and table formatting. Page numbers for the Index and the lists are taken
from a LibreOffice render and written back in a second pass.
"""
import copy
import re
import shutil
import struct
import subprocess
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

from lxml import etree
from PIL import ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import content as C  # noqa: E402

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
W = '{%s}' % W_NS
NS = {
    'w': W_NS,
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
}
NSDECL = ' '.join(f'xmlns:{k}="{v}"' for k, v in NS.items())
TEXT_W = 8788                       # usable width in twips (template tables)
TNR = ImageFont.truetype('/System/Library/Fonts/Supplemental/Times New Roman.ttf', 110)


def X(xml):
    """Parse a fragment written with w:/r:/wp:/a:/pic: prefixes."""
    return etree.fromstring(f'<root {NSDECL}>{xml}</root>')[0]


def t(s):
    return f'<w:t xml:space="preserve">{escape(s)}</w:t>'


RPR = '<w:rPr><w:lang w:val="en-US"/></w:rPr>'


def runs(text, bold=False, italic=False, size=None, font=None, hl=False):
    """Text with **bold** and _sub_ markup is not used; [[...]] marks a yellow placeholder."""
    out = []
    for part in re.split(r'(\[\[.*?\]\])', text):
        if not part:
            continue
        ph = part.startswith('[[')
        if ph:
            part = part[2:-2]
        rpr = ''
        if font:
            rpr += f'<w:rFonts w:ascii="{font}" w:hAnsi="{font}" w:cs="{font}"/>'
        if bold:
            rpr += '<w:b w:val="1"/><w:bCs w:val="1"/>'
        if italic:
            rpr += '<w:i w:val="1"/>'
        if size:
            rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        if ph or hl:
            rpr += '<w:highlight w:val="yellow"/>'
        rpr += '<w:lang w:val="en-US"/>'
        out.append(f'<w:r><w:rPr>{rpr}</w:rPr>{t(part)}</w:r>')
    return ''.join(out)


def para(text, style='Body', jc='both', extra_ppr='', **kw):
    return X(f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{extra_ppr}<w:jc w:val="{jc}"/></w:pPr>'
             f'{runs(text, **kw)}</w:p>')


def heading(text):
    return X(f'<w:p><w:pPr><w:pStyle w:val="Heading"/></w:pPr>{runs(text)}</w:p>')


def heading2(text):
    return X(f'<w:p><w:pPr><w:pStyle w:val="Heading 2"/></w:pPr>{runs(text)}</w:p>')


def numbered(i, text, bullet=False):
    lab = '•' if bullet else f'{i}.'
    return X('<w:p><w:pPr><w:pStyle w:val="Body"/><w:tabs><w:tab w:val="left" w:pos="454"/></w:tabs>'
             '<w:spacing w:after="40"/><w:ind w:left="454" w:hanging="340"/><w:jc w:val="both"/></w:pPr>'
             f'<w:r>{RPR}{t(lab)}<w:tab/></w:r>{runs(text)}</w:p>')


def page_break():
    return X('<w:p><w:pPr><w:pStyle w:val="Body"/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>')


def spacer():
    return X('<w:p><w:pPr><w:pStyle w:val="Body"/><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:p>')


def caption(kind, label, text):
    style = 'Table Caption' if kind == 'table' else 'Figure Caption'
    keep = '<w:keepNext w:val="1"/>' if kind == 'table' else ''
    return X(f'<w:p><w:pPr><w:pStyle w:val="{style}"/>{keep}</w:pPr>'
             f'<w:r><w:rPr><w:b w:val="1"/><w:bCs w:val="1"/><w:lang w:val="en-US"/></w:rPr>{t(label + ":")}</w:r>'
             f'{runs(" " + text)}</w:p>')


BORDER = '<w:{s} w:val="single" w:color="000000" w:sz="4" w:space="0"/>'
CELL_BORDERS = '<w:tcBorders>' + ''.join(BORDER.format(s=s) for s in ('top', 'left', 'bottom', 'right')) + '</w:tcBorders>'
TBL_PR = ('<w:tblPr><w:tblW w:w="{w}" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/>'
          '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="80" w:type="dxa"/>'
          '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>')


def data_table(headers, rows, widths=None, size=20, first_col_left=True):
    n = len(headers)
    widths = widths or [1] * n
    tot = sum(widths)
    cols = [int(TEXT_W * w / tot) for w in widths]
    cols[-1] += TEXT_W - sum(cols)
    def cell(txt, w, head=False, left=False):
        shd = '<w:shd w:val="clear" w:color="auto" w:fill="D9D9D9"/>' if head else ''
        jc = 'left' if left else 'center'
        paras = ''.join(
            f'<w:p><w:pPr><w:pStyle w:val="Body"/><w:keepNext w:val="1"/><w:spacing w:after="0" w:line="240" w:lineRule="auto"/>'
            f'<w:jc w:val="{jc}"/></w:pPr>{runs(line, bold=head, size=size)}</w:p>' for line in str(txt).split('\n'))
        return (f'<w:tc><w:tcPr><w:tcW w:w="{w}" w:type="dxa"/>{CELL_BORDERS}{shd}<w:vAlign w:val="center"/></w:tcPr>'
                f'{paras}</w:tc>')
    xml = '<w:tbl>' + TBL_PR.format(w=TEXT_W) + '<w:tblGrid>' + ''.join(f'<w:gridCol w:w="{c}"/>' for c in cols) + '</w:tblGrid>'
    xml += '<w:tr><w:trPr><w:tblHeader/><w:cantSplit/></w:trPr>' + ''.join(cell(h, c, head=True) for h, c in zip(headers, cols)) + '</w:tr>'
    for r in rows:
        xml += '<w:tr><w:trPr><w:cantSplit/></w:trPr>' + ''.join(
            cell(v, c, left=(j == 0 and first_col_left)) for j, (v, c) in enumerate(zip(r, cols))) + '</w:tr>'
    return X(xml + '</w:tbl>')


def code_block(code):
    lines = code.rstrip('\n').split('\n')
    body = []
    for k, line in enumerate(lines):
        if k:
            body.append('<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
                        '<w:sz w:val="17"/><w:szCs w:val="17"/></w:rPr><w:br/></w:r>')
        body.append('<w:r><w:rPr><w:rFonts w:ascii="Courier New" w:hAnsi="Courier New" w:cs="Courier New"/>'
                    f'<w:sz w:val="17"/><w:szCs w:val="17"/><w:lang w:val="en-US"/></w:rPr>{t(line)}</w:r>')
    xml = ('<w:tbl>' + TBL_PR.format(w=TEXT_W) + f'<w:tblGrid><w:gridCol w:w="{TEXT_W}"/></w:tblGrid><w:tr><w:tc>'
           f'<w:tcPr><w:tcW w:w="{TEXT_W}" w:type="dxa"/>{CELL_BORDERS}<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/></w:tcPr>'
           '<w:p><w:pPr><w:pStyle w:val="Body"/><w:spacing w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>'
           + ''.join(body) + '</w:p></w:tc></w:tr></w:tbl>')
    return X(xml)


ANS_PT = 11
ANS_WIDTH_PT = (TEXT_W - 160) / 20 * 0.96      # usable line width in points, small safety margin


def wrap(text, size_pt=ANS_PT):
    scale = size_pt / 110
    out = []
    for parag in text.split('\n'):
        line = ''
        for word in parag.split(' '):
            cand = (line + ' ' + word).strip()
            if TNR.getlength(cand) * scale <= ANS_WIDTH_PT:
                line = cand
            else:
                out.append(line); line = word
        out.append(line)
    return out


def ruled_answer(answer, min_rows=6):
    lines = wrap(answer)
    lines += [''] * max(0, min_rows - len(lines))
    rows = []
    for k, line in enumerate(lines):
        top = '<w:top w:val="nil"/>' if k == 0 else '<w:top w:val="single" w:color="808080" w:sz="4" w:space="0"/>'
        rows.append('<w:tr><w:trPr><w:trHeight w:val="322" w:hRule="exact"/><w:cantSplit/></w:trPr><w:tc><w:tcPr>'
                    f'<w:tcW w:w="{TEXT_W}" w:type="dxa"/><w:tcBorders>{top}<w:left w:val="nil"/>'
                    '<w:bottom w:val="single" w:color="808080" w:sz="4" w:space="0"/><w:right w:val="nil"/></w:tcBorders>'
                    '<w:vAlign w:val="bottom"/></w:tcPr><w:p><w:pPr><w:pStyle w:val="Body"/>'
                    '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/><w:jc w:val="left"/></w:pPr>'
                    f'{runs(line, size=ANS_PT * 2, font="Times New Roman")}</w:p></w:tc></w:tr>')
    tblpr = (f'<w:tblPr><w:tblW w:w="{TEXT_W}" w:type="dxa"/><w:jc w:val="center"/><w:tblLayout w:type="fixed"/>'
             '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="80" w:type="dxa"/><w:bottom w:w="20" w:type="dxa"/>'
             '<w:right w:w="80" w:type="dxa"/></w:tblCellMar></w:tblPr>')
    return X('<w:tbl>' + tblpr + f'<w:tblGrid><w:gridCol w:w="{TEXT_W}"/></w:tblGrid>' + ''.join(rows) + '</w:tbl>')


class Images:
    def __init__(self, rels_path, media_dir):
        self.rels_path, self.media = rels_path, media_dir
        self.rels = etree.parse(str(rels_path))
        self.n = 100
        for old in list(self.media.glob('image*.png')):      # sample-report figures are not mine
            old.unlink()
        root = self.rels.getroot()
        for rel in list(root):
            if rel.get('Type').endswith('/image'):
                root.remove(rel)

    def add(self, src, width_cm):
        self.n += 1
        src = Path(src)
        name = f'fig{self.n}{src.suffix.lower()}'
        shutil.copy(src, self.media / name)
        rid = f'rIdImg{self.n}'
        etree.SubElement(self.rels.getroot(), '{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',
                         Id=rid, Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
                         Target=f'media/{name}')
        with open(src, 'rb') as f:
            head = f.read(24)
        if src.suffix.lower() == '.png':
            w, h = struct.unpack('>II', head[16:24])
        else:
            from PIL import Image
            w, h = Image.open(src).size
        cx = int(width_cm * 360000)
        cy = int(cx * h / w)
        max_cy = int(17.5 * 360000)
        if cy > max_cy:
            cx, cy = int(cx * max_cy / cy), max_cy
        return X(
            '<w:p><w:pPr><w:pStyle w:val="Body"/><w:keepNext w:val="1"/><w:spacing w:before="120" w:after="60"/>'
            '<w:jc w:val="center"/></w:pPr><w:r><w:drawing>'
            f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{self.n}" name="Figure {self.n}"/><wp:cNvGraphicFramePr>'
            '<a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr>'
            '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic>'
            f'<pic:nvPicPr><pic:cNvPr id="{self.n}" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic>'
            '</wp:inline></w:drawing></w:r></w:p>')

    def save(self):
        self.rels.write(str(self.rels_path), xml_declaration=True, encoding='UTF-8', standalone=True)


def index_line(text, page, bold=False, indent=0):
    ind = f'<w:ind w:left="{indent}"/>' if indent else ''
    return X(f'<w:p><w:pPr><w:pStyle w:val="Body"/><w:tabs><w:tab w:val="right" w:pos="8762" w:leader="dot"/></w:tabs>'
             f'<w:spacing w:after="0" w:line="276" w:lineRule="auto"/>{ind}<w:jc w:val="left"/></w:pPr>'
             f'{runs(text, bold=bold)}<w:r>{RPR}<w:tab/>{t(str(page))}</w:r></w:p>')


def set_cell(tbl, row, col, text):
    tc = tbl.findall(W + 'tr')[row].findall(W + 'tc')[col]
    ps = tc.findall(W + 'p')
    for p in ps[1:]:
        tc.remove(p)
    p = ps[0]
    ppr = p.find(W + 'pPr')
    rpr = p.find(f'.//{W}rPr')
    for r in p.findall(W + 'r'):
        p.remove(r)
    for r in X(f'<w:p>{runs(text)}</w:p>').findall(W + 'r'):
        if rpr is not None:
            old = copy.deepcopy(rpr)
            new_rpr = r.find(W + 'rPr')
            if new_rpr.find(W + 'highlight') is not None:
                old.append(X('<w:highlight w:val="yellow"/>'))
            r.replace(new_rpr, old)
        p.append(r)


def set_para(p, text, **kw):
    for r in p.findall(W + 'r'):
        p.remove(r)
    for r in X(f'<w:p>{runs(text, **kw)}</w:p>').findall(W + 'r'):
        p.append(r)


def build(pages=None):
    work = HERE / 'build'
    if work.exists():
        shutil.rmtree(work)
    with zipfile.ZipFile(HERE / 'template.docx') as z:
        z.extractall(work)
    doc_path = work / 'word' / 'document.xml'
    tree = etree.parse(str(doc_path))
    body = tree.getroot().find(W + 'body')
    old = list(body)
    tpl_questions = {}
    exp_no = 0
    for el in old:
        txt = ''.join(el.itertext())
        m = re.match(r'Experiment (\d):', txt)
        if el.tag == W + 'p' and m and el.find(f'{W}pPr/{W}pStyle').get(W + 'val') == 'Heading':
            exp_no = int(m.group(1))
        q = re.match(r'(Q\d)\. (.*)', txt)
        if q and exp_no:
            tpl_questions.setdefault(exp_no, []).append(txt)
    front = old[:23]          # title page, section break, declaration, page break
    sect_roman = old[89]       # ends the roman-numbered front matter
    pn = sect_roman.find(f'.//{W}pgNumType')
    pn.set(W + 'fmt', 'lowerRoman'); pn.set(W + 'start', '1')
    final_pn = old[-1].find(f'{W}pgNumType')
    final_pn.set(W + 'fmt', 'decimal'); final_pn.set(W + 'start', '1')
    final_sect = old[-1]
    for el in old:
        body.remove(el)

    P = C.PERSON
    # ---- title page
    tbl = front[8]
    for row, key in enumerate(['name', 'sap', 'roll', 'batch', 'partner', 'github'], start=1):
        set_cell(tbl, row, 1, P[key])
    set_para(front[14], f'Date of submission: {P["submission_date"]}')
    dec = front[18]
    set_cell(dec, 1, 0, P['name']); set_cell(dec, 1, 1, P['sap']); set_cell(dec, 1, 2, P['batch_letter'])
    set_para(front[21], f'Date: {P["submission_date"]}          Place: Dehradun')
    sig = HERE / 'signature.png'
    for el in front:
        body.append(el)

    plain = lambda x: x.replace('[[', '').replace(']]', '')
    for hf in ('header2.xml', 'header3.xml'):
        hp = work / 'word' / hf
        hp.write_text(hp.read_text().replace('Student Name (SAP ID 5001XXXXX)',
                                             escape(f"{plain(P['name'])} (SAP ID {plain(P['sap'])})")))
    imgs = Images(work / 'word' / '_rels' / 'document.xml.rels', work / 'word' / 'media')
    if sig.exists():                                   # signature into the Declaration table
        tc = dec.findall(W + 'tr')[1].findall(W + 'tc')[3]
        for p_ in tc.findall(W + 'p'):
            tc.remove(p_)
        sp = imgs.add(sig, 3.2)
        sp.find(f'{W}pPr/{W}spacing').set(W + 'before', '40')
        tc.append(sp)
    pages = pages or {}
    pg = lambda key: pages.get(key, '0')

    # ---- Index, List of Figures, List of Tables
    figs, tabs = [], []
    for e in C.EXPERIMENTS:
        for item in e['observations'] + e['results']:
            if item[0] == 'table':
                tabs.append(item[1])
            if item[0] == 'fig':
                figs.append(item[2])
        for item in e.get('extra_tables', []):
            tabs.append(item[1])
    body.append(heading('Index'))
    for key, label in (('Declaration', 'Declaration'), ('List of Figures', 'List of Figures'), ('List of Tables', 'List of Tables')):
        body.append(index_line(label, pg(key), bold=True))
    for e in C.EXPERIMENTS:
        body.append(index_line(f"Experiment {e['n']}: {e['title']}", pg(f"Experiment {e['n']}:"), bold=True))
        for k, sub in enumerate(C.SUBHEADINGS, start=1):
            body.append(index_line(f"{e['n']}.{k} {sub}", pg(f"{e['n']}.{k} {sub}"), indent=340))
    for label in ('References', 'Appendix A: Repository and Run Details',
                  'Appendix B: Use of Reference Material and AI Assistants'):
        body.append(index_line(label, pg(label), bold=True))
    body.append(page_break())
    body.append(heading('List of Figures'))
    for label, cap in figs:
        body.append(index_line(f'{label}: {cap}', pg(label + ':')))
    body.append(page_break())
    body.append(heading('List of Tables'))
    for label, cap in tabs:
        body.append(index_line(f'{label}: {cap}', pg(label + ':')))
    body.append(sect_roman)

    # ---- chapters
    for k, e in enumerate(C.EXPERIMENTS):
        if k:
            body.append(page_break())
        n = e['n']
        body.append(heading(f"Experiment {n}: {e['title']}"))
        body.append(para(e['header_line'], jc='left'))
        body.append(para(f"Instructions source: {e['source']}", jc='left'))
        S = lambda i: heading2(f'{n}.{i} {C.SUBHEADINGS[i - 1]}')
        body.append(S(1)); body.append(para(e['aim']))
        body.append(S(2))
        for i, o in enumerate(e['objectives'], 1):
            body.append(numbered(i, o))
        body.append(S(3)); body.append(para(e['software']))
        body.append(S(4))
        for x in e['theory']:
            body.append(para(x))
        body.append(S(5))
        for i, s in enumerate(e['procedure'], 1):
            body.append(numbered(i, s))
        body.append(S(6))
        body.append(para(e['code_intro']))
        body.append(code_block(e['code']))
        body.append(S(7))
        for item in e['observations']:
            emit(body, item, imgs)
        body.append(S(8))
        for item in e['results']:
            emit(body, item, imgs)
        body.append(S(9))
        for item in e['discussion']:
            emit(body, item if isinstance(item, tuple) else ('para', item), imgs)
        body.append(S(10))
        qs = tpl_questions[n]
        assert len(qs) == len(e['answers']), (n, len(qs), len(e['answers']))
        for q, a in zip(qs, e['answers']):
            body.append(para(q, jc='left', extra_ppr='<w:keepNext w:val="1"/><w:spacing w:before="160" w:after="40"/>'))
            body.append(ruled_answer(a))
        body.append(S(11)); body.append(para(e['conclusion']))

    # ---- references and appendices
    body.append(page_break())
    body.append(heading('References'))
    for i, ref in enumerate(C.REFERENCES, 1):
        body.append(X('<w:p><w:pPr><w:pStyle w:val="Body"/><w:tabs><w:tab w:val="left" w:pos="567"/></w:tabs>'
                      '<w:spacing w:after="80" w:line="276" w:lineRule="auto"/><w:ind w:left="567" w:hanging="567"/>'
                      f'<w:jc w:val="left"/></w:pPr><w:r>{RPR}{t(f"[{i}]")}<w:tab/></w:r>{runs(ref)}</w:p>'))
    body.append(page_break())
    body.append(heading('Appendix A: Repository and Run Details'))
    body.append(data_table(['Item', 'Details'], C.APPENDIX_A, widths=[1, 2.4], size=21))
    body.append(spacer())
    body.append(para('Repository layout:', jc='left'))
    body.append(code_block(C.REPO_LAYOUT))
    body.append(page_break())
    body.append(heading('Appendix B: Use of Reference Material and AI Assistants'))
    body.append(para(C.APPENDIX_B_INTRO))
    body.append(data_table(['Experiment', 'Source or AI tool', 'What it was used for'], C.APPENDIX_B,
                           widths=[0.8, 1.6, 3], size=20))
    body.append(final_sect)

    imgs.save()
    tree.write(str(doc_path), xml_declaration=True, encoding='UTF-8', standalone=True)
    out = HERE / 'AISR_LabReport.docx'
    if out.exists():
        out.unlink()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(work.rglob('*')):
            if f.is_file():
                z.write(f, f.relative_to(work).as_posix())
    return out


def emit(body, item, imgs):
    kind = item[0]
    if kind == 'para':
        body.append(para(item[1]))
    elif kind == 'bullets':
        for x in item[1]:
            body.append(numbered(0, x, bullet=True))
    elif kind == 'numbered':
        for i, x in enumerate(item[1], 1):
            body.append(numbered(i, x))
    elif kind == 'table':
        (label, cap), headers, rows = item[1], item[2], item[3]
        widths = item[4] if len(item) > 4 else None
        body.append(caption('table', label, cap))
        body.append(data_table(headers, rows, widths))
        body.append(spacer())
    elif kind == 'fig':
        path, (label, cap) = item[1], item[2]
        width = item[3] if len(item) > 3 else 15.0
        body.append(imgs.add(path, width))
        body.append(caption('fig', label, cap))
    elif kind == 'code':
        body.append(code_block(item[1]))
    else:
        raise ValueError(kind)


def render_pdf(docx):
    outdir = docx.parent
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', str(outdir), str(docx)],
                   check=True, capture_output=True, timeout=600)
    return docx.with_suffix('.pdf')


def find_pages(pdf):
    """Map heading/caption keys to printed page numbers (roman front matter, arabic chapters)."""
    txt = subprocess.run(['pdftotext', '-layout', str(pdf), '-'], capture_output=True, text=True).stdout
    pages = txt.split('\f')
    first_ch = next(i for i, p in enumerate(pages) if re.search(r'^\s*Experiment 1: ', p, re.M)
                    and 'Index' not in p and '1.1 Aim' in p)
    decl = next(i for i, p in enumerate(pages) if re.search(r'^\s*Declaration\s*$', p, re.M))
    def label(i):
        if i >= first_ch:
            return str(i - first_ch + 1)
        r = i - decl + 1
        return ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x'][r - 1]
    keys = {}
    def first(pattern, start=0):
        for i in range(start, len(pages)):
            if re.search(pattern, pages[i], re.M):
                return i
        return None
    keys['Declaration'] = label(decl)
    for k in ('List of Figures', 'List of Tables'):
        i = first(rf'^\s*{k}\s*$')
        keys[k] = label(i)
    for e in C.EXPERIMENTS:
        n = e['n']
        i = first(rf'^\s*Experiment {n}: ', first_ch)
        keys[f'Experiment {n}:'] = label(i)
        for k, sub in enumerate(C.SUBHEADINGS, 1):
            j = first(rf'^\s*{n}\.{k} {re.escape(sub)}\s*$', i)
            keys[f'{n}.{k} {sub}'] = label(j) if j is not None else '?'
        for item in e['observations'] + e['results']:
            if item[0] in ('table', 'fig'):
                lab = (item[1] if item[0] == 'table' else item[2])[0]
                j = first(rf'^\s*{re.escape(lab)}:', i)
                keys[lab + ':'] = label(j) if j is not None else '?'
    for k in ('References', 'Appendix A: Repository and Run Details',
              'Appendix B: Use of Reference Material and AI Assistants'):
        j = first(rf'^\s*{re.escape(k)}\s*$', first_ch)
        keys[k] = label(j) if j is not None else '?'
    return keys, len(pages) - 1


if __name__ == '__main__':
    out = build()
    pdf = render_pdf(out)
    pages, n = find_pages(pdf)
    out = build(pages)
    pdf = render_pdf(out)
    pages2, n2 = find_pages(pdf)
    if pages2 != pages:
        out = build(pages2); pdf = render_pdf(out); pages2, n2 = find_pages(pdf)
    missing = [k for k, v in pages2.items() if v == '?']
    print(f'{out.name}: {n2} pages; unresolved index keys: {missing}')
