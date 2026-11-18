#!/usr/bin/env python3
"""Export the two Portuguese study guides without changing their content."""
from __future__ import annotations
import argparse, hashlib, html, json, os, re
from functools import partial
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfdoc import PDFString
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph,
    Spacer, PageBreak, CondPageBreak, LongTable, TableStyle, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'presentation/a2_inf/output'
DEFAULT_FONT_DIR = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/Resources/fonts/truetype'
BLUE = colors.HexColor('#005C9C')
INK = colors.HexColor('#1B2B36')
MUTED = colors.HexColor('#52616B')
PALE = colors.HexColor('#EEF5F9')
WIDTH, HEIGHT = A4
MARGIN = 47
BODY_WIDTH = WIDTH - 2*MARGIN


def register_fonts():
    root = Path(os.environ.get('STUDY_FONT_DIR', DEFAULT_FONT_DIR))
    for alias, file in [('StudyBody','DejaVuSerif.ttf'),('StudyBody-Bold','DejaVuSerif-Bold.ttf'),
                        ('StudyBody-Italic','DejaVuSerif-Italic.ttf'),('StudyBody-BoldItalic','DejaVuSerif-BoldItalic.ttf'),
                        ('StudySans','DejaVuSans.ttf'),('StudySans-Bold','DejaVuSans-Bold.ttf'),
                        ('StudyMono','DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(alias, str(root/file)))
    pdfmetrics.registerFontFamily('StudyBody', normal='StudyBody', bold='StudyBody-Bold', italic='StudyBody-Italic', boldItalic='StudyBody-BoldItalic')
    pdfmetrics.registerFontFamily('StudySans', normal='StudySans', bold='StudySans-Bold', italic='StudySans', boldItalic='StudySans-Bold')


def rich(s):
    # All Markdown text is retained; markup becomes selectable PDF typography.
    s = s.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<font name="StudyMono" size="8.5">\1</font>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<i>\1</i>', s)
    def link(m):
        label, url = m.group(1), m.group(2)
        if url.startswith(('http://','https://')):
            return '<link href="'+html.escape(html.unescape(url),quote=True)+'" color="#005C9C">'+label+'</link>'
        return label
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, s)


def style_set():
    b = ParagraphStyle('Body',fontName='StudyBody',fontSize=10.8,leading=15.2,textColor=INK,
                       spaceAfter=8,allowWidows=0,allowOrphans=0,splitLongWords=1)
    return {
        'body': b,
        'title': ParagraphStyle('Title',parent=b,fontName='StudySans-Bold',fontSize=25,leading=31,textColor=BLUE,spaceAfter=20),
        'h2': ParagraphStyle('H2',parent=b,fontName='StudySans-Bold',fontSize=16,leading=21,textColor=BLUE,spaceBefore=17,spaceAfter=10,keepWithNext=1),
        'h3': ParagraphStyle('H3',parent=b,fontName='StudySans-Bold',fontSize=12,leading=16,textColor=BLUE,spaceBefore=12,spaceAfter=7,keepWithNext=1),
        'q': ParagraphStyle('Question',parent=b,fontName='StudyBody-Bold',spaceBefore=9,keepWithNext=1),
        'quote': ParagraphStyle('Speech',parent=b,fontSize=10.5,leading=15.4,leftIndent=12,rightIndent=12,spaceBefore=4,spaceAfter=12,backColor=PALE,borderPadding=10),
        'bullet': ParagraphStyle('Bullet',parent=b,leftIndent=15,firstLineIndent=-11,spaceAfter=6),
        'small': ParagraphStyle('Source',parent=b,fontName='StudySans',fontSize=8.4,leading=11.5,textColor=MUTED,spaceBefore=5,spaceAfter=10),
        'cell': ParagraphStyle('Cell',parent=b,fontSize=9.1,leading=12.4,spaceAfter=0,allowWidows=1,allowOrphans=1),
        'cell_head': ParagraphStyle('CellHeader',parent=b,fontName='StudySans-Bold',fontSize=9.2,leading=12.2,textColor=colors.white,spaceAfter=0),
        'toc': ParagraphStyle('TocItem',parent=b,fontName='StudySans',fontSize=10.2,leading=15.1,spaceBefore=4,spaceAfter=3),
    }


class GuideDoc(BaseDocTemplate):
    def __init__(self,path,short_title,title):
        super().__init__(str(path),pagesize=A4,leftMargin=MARGIN,rightMargin=MARGIN,topMargin=53,bottomMargin=49,
                         title=title,author='Grupo 3 - INF/UFG',subject='Material de estudo e defesa da A2')
        self.short_title=short_title
        self.addPageTemplates(PageTemplate(id='study',frames=[Frame(MARGIN,49,BODY_WIDTH,HEIGHT-102,id='content',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.chrome))
    def chrome(self,c,doc):
        c._doc.Catalog.Lang=PDFString('pt-BR')
        c.saveState();c.setFillColor(MUTED);c.setFont('StudySans',8)
        c.drawString(MARGIN,HEIGHT-31,'MINERAÇÃO DE DADOS · A2 · MATERIAL DE ESTUDO')
        c.setStrokeColor(colors.HexColor('#D8E4EC'));c.line(MARGIN,HEIGHT-39,WIDTH-MARGIN,HEIGHT-39)
        c.drawString(MARGIN,28,self.short_title);c.drawRightString(WIDTH-MARGIN,28,str(doc.page));c.restoreState()
    def afterFlowable(self,item):
        if isinstance(item,Paragraph) and hasattr(item,'section_anchor'):
            self.canv.bookmarkPage(item.section_anchor)
            self.canv.addOutlineEntry(item.getPlainText(),item.section_anchor,0,False)
            self.notify('TOCEntry',(0,item.getPlainText(),self.page,item.section_anchor))


def make_table(lines,styles):
    values=[]
    for line in lines:
        row=[v.strip() for v in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r':?-+:?',x) for x in row):continue
        values.append(row)
    count=len(values[0])
    if count==3: widths=[BODY_WIDTH*.16,BODY_WIDTH*.42,BODY_WIDTH*.42]
    elif count==4 and values[0][0]=='Métrica':widths=[BODY_WIDTH*.19,BODY_WIDTH*.34,BODY_WIDTH*.14,BODY_WIDTH*.33]
    elif count==4:widths=[BODY_WIDTH*.22,BODY_WIDTH*.28,BODY_WIDTH*.28,BODY_WIDTH*.22]
    else:widths=[BODY_WIDTH/count]*count
    cells=[[Paragraph(rich(x),styles['cell_head'] if i==0 else styles['cell']) for x in row] for i,row in enumerate(values)]
    t=LongTable(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),BLUE),('VALIGN',(0,0),(-1,-1),'TOP'),
       ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F5F8FA')]),
       ('LINEBELOW',(0,0),(-1,0),.5,BLUE),('LINEBELOW',(0,1),(-1,-1),.35,colors.HexColor('#DCE5EB')),
       ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
       ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    return [Spacer(1,4),t,Spacer(1,12)]


def create_guide(source,dest,personal=False):
    styles=style_set();lines=source.read_text().splitlines();title=lines[0].lstrip('# ')
    intro=[];i=1
    while i<len(lines) and not lines[i].startswith('## '):
        if lines[i].strip():intro.append(lines[i])
        i+=1
    toc=TableOfContents();toc.levelStyles=[styles['toc']];toc.dotsMinLevel=0
    story=[Paragraph(rich(title),styles['title']),Paragraph(rich(' '.join(intro)),styles['body']),Spacer(1,7)]
    description=('Leia a explicação de cada slide, pratique a fala e teste as respostas sem consultar. As explicações de estudo não precisam ser todas ditas na apresentação.' if personal else 'Para dominar o trabalho inteiro: siga a sequência do KDD, consulte as decisões por variável e pratique as 44 perguntas. Para a sua fala, use também o guia específico dos slides 1 a 6.')
    story += [Paragraph(description,styles['body']),Spacer(1,10),Paragraph('Sumário navegável',styles['h3']),toc,PageBreak()]
    section=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('## '):
            title2=line[3:]
            if personal and (title2.startswith('Slide ') or title2.startswith('Ensaiar')):story.append(PageBreak())
            else:story.append(CondPageBreak(100))
            h=Paragraph(rich(title2),styles['h2']);h.section_anchor=f'sec{section}';section+=1;story.append(h);i+=1;continue
        if line.startswith('### '):
            story.append(Paragraph(rich(line[4:]),styles['h3']));i+=1;continue
        if line.startswith('|'):
            table=[]
            while i<len(lines) and lines[i].strip().startswith('|'):table.append(lines[i]);i+=1
            story.extend(make_table(table,styles));continue
        if line.startswith('>'):
            q=[]
            while i<len(lines) and lines[i].strip().startswith('>'):q.append(lines[i].strip()[1:].lstrip());i+=1
            story.append(Paragraph(rich(' '.join(q)),styles['quote']));continue
        if line.startswith('- ') or re.match(r'^\d+\. ',line):
            value='• '+line[2:] if line.startswith('- ') else line
            story.append(Paragraph(rich(value),styles['bullet']));i+=1;continue
        p=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||>|- |\d+\. )',lines[i].strip()):p.append(lines[i].strip());i+=1
        value=' '.join(p)
        which='small' if value.startswith('**Fontes para conferir:') else 'q' if re.match(r'^\*\*\d+\. ',value) or (value.startswith('**') and value.endswith('**')) else 'body'
        story.append(Paragraph(rich(value),styles[which]))
    doc=GuideDoc(dest,'Pedro · slides 1 a 6' if personal else 'Guia completo · estudo e defesa',title)
    doc.multiBuild(story, canvasmaker=partial(Canvas, initialFontName='StudySans'))
    pdf=PdfReader(dest)
    assert pdf.outline,'Missing PDF navigation'
    manifest={'source':str(source.relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
              'pdf':str(dest.relative_to(ROOT)),'pdf_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'pages':len(pdf.pages),'sections':section}
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--only',choices=['full','pedro']);args=parser.parse_args()
    register_fonts();items=[]
    if args.only!='pedro':items.append(create_guide(OUT/'Guia_Defesa_A2.md',OUT/'Guia_Defesa_A2.pdf'))
    if args.only!='full':items.append(create_guide(OUT/'Guia_Apresentacao_Pedro.md',OUT/'Guia_Apresentacao_Pedro.pdf',True))
    work=ROOT/'work/a2_estudo_pdf';work.mkdir(parents=True,exist_ok=True)
    (work/'manifesto.json').write_text(json.dumps(items,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(items,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
