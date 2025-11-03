from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image, PageBreak, KeepInFrame
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

CHAKRA_COLORS = {
    "Root": "#EA4335", "Sacral": "#F4A261", "Solar Plexus": "#E9C46A",
    "Heart": "#34A853", "Throat": "#4285F4", "Third Eye": "#7E57C2", "Crown": "#B39DDB"
}

def build_pdf(traits: Dict[str,float],
              chakras: Dict[str,float],
              logo: Optional[bytes],
              meta: Dict[str,str]) -> bytes:
    buf = io.BytesIO()

    # Tighter margins so the page looks “full”
    doc = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28
    )

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=22, leading=26,
                        textColor=colors.HexColor("#212121"), alignment=0)
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=16, leading=20,
                        textColor=colors.HexColor("#311B92"))
    NORMAL = styles["Normal"]
    SMALL  = ParagraphStyle("SMALL", parent=NORMAL, fontSize=9, leading=12,
                            textColor=colors.HexColor("#616161"))
    CELL   = ParagraphStyle("CELL", parent=NORMAL, fontSize=10, leading=13)   # table cells
    CELL_SM= ParagraphStyle("CELL_SM", parent=NORMAL, fontSize=9, leading=12) # tighter cell

    story = []

    # ---------- footer ----------
    def footer(canvas, doc_):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        w, h = A4
        canvas.drawRightString(w-28, 18, f"Page {doc_.page}")
        canvas.drawString(28, 18, "Soulful Academy • What You Seek Is Seeking You")

    # ---------- COVER ----------
    left_cell = []
    if logo:
        left_cell.append(Image(io.BytesIO(logo), width=90, height=90))
    header = Table([[left_cell, Paragraph("<b>Soulful Academy — Chakra & Personality Report</b>", H1)]],
                   colWidths=[3.0*cm, 14.0*cm])
    header.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [header, Spacer(1,6), Paragraph("A diagnostic report you can email to the client.", SMALL), Spacer(1,14)]

    details = [
        [Paragraph("<b>Client</b>", CELL_SM),          Paragraph(meta.get("client","—"), CELL_SM)],
        [Paragraph("<b>Coach / Healer</b>", CELL_SM),  Paragraph(meta.get("coach","—"), CELL_SM)],
        [Paragraph("<b>Session Date</b>", CELL_SM),    Paragraph(meta.get("date","—"), CELL_SM)],
        [Paragraph("<b>Gender</b>", CELL_SM),          Paragraph(meta.get("gender","—"), CELL_SM)],
        [Paragraph("<b>Intent / Focus</b>", CELL_SM),  Paragraph(meta.get("intent","—"), CELL_SM)],
    ]
    dtbl = Table(details, colWidths=[4.0*cm, 12.8*cm])
    dtbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#CCCCCC")),
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EEE7FF")),
        ("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#311B92")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("WORDWRAP",(0,0),(-1,-1),"CJK"),
    ]))
    story += [dtbl, PageBreak()]

    # ---------- PERSONALITY ----------
    def personality_verdict(ts: Dict[str,float]) -> str:
        o, c, e, a = ts.get("O",0), ts.get("C",0), ts.get("E",0), ts.get("A",0)
        if c>1.0 and o>0.5: return "Organized Visionary"
        if e>1.0 and a>0.5: return "Warm Communicator"
        if o>1.2 and c<-0.5: return "Creative Explorer"
        if c>1.2 and e<-0.5: return "Calm Strategist"
        return "Balanced Builder"

    story += [Paragraph("Personality Profile (Big Five style)", H2), Spacer(1,6)]
    verdict = personality_verdict(traits)
    story += [Paragraph(f"<b>What kind of personality are you?</b> {verdict}", NORMAL), Spacer(1,8)]

    pdata = [[Paragraph("<b>Trait</b>", CELL), Paragraph("<b>Score (-3..+3)</b>", CELL), Paragraph("<b>Summary</b>", CELL)]]
    for t,v in traits.items():
        pdata.append([Paragraph(t, CELL), Paragraph(f"{v:.2f}", CELL), Paragraph(summarize_trait(t, v), CELL)])
    ptable = Table(pdata, colWidths=[3.0*cm, 3.5*cm, 11.5*cm])
    ptable.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EDE7F6")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#311B92")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#BBBBBB")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("WORDWRAP",(0,0),(-1,-1),"CJK"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke, colors.HexColor("#FAFAFA")]),
    ]))
    story += [ptable, Spacer(1,8)]

    story += [Paragraph("<b>How to align with other personalities</b>", NORMAL)]
    for tip in [
        "With high-C (organized) people: agree on clear timelines and definitions of done.",
        "With high-O (creative) people: brainstorm first, then lock one experiment to ship.",
        "With high-E (expressive) people: allow talk-time, then summarize next actions.",
        "With high-A (kind) people: invite honest feedback and set gentle boundaries.",
    ]:
        story.append(Paragraph("• "+tip, SMALL))
    story.append(PageBreak())

    # ---------- BIG SUMMARY (from your template) ----------
    summary_blocks = [
        Paragraph("<b>Quick Reading</b>", H2),
        Paragraph(
            "Start with the lowest blocked chakra and move upward. Use the crystal suggestions, pair with 108× Ho’oponopono on the main person/event linked to that chakra, and soften any overactive areas with grounding, slow breathing and clear boundaries.",
            NORMAL
        ),
        Spacer(1,6),
        Paragraph("<b>Follow-up & Home Practice (7-Day Plan)</b>", H2),
        Paragraph("1) Day 1-2: Chakra awareness — 7 to 11 minutes Root→Crown meditation. "
                  "2) Day 3-4: Emotional cleaning — journal ‘Who/what am I still holding in this chakra?’ + 108× Ho’oponopono. "
                  "3) Day 5: Crystal activation — wear/place suggested MyAuraBliss crystal for 11 minutes. "
                  "4) Day 6: Relationship repair — speak your truth (Throat/Heart). "
                  "5) Day 7: Integration — repeat meditation and note shifts. Track progress in the Soulful Academy app or workbook.",
                  SMALL),
        Spacer(1,6),
        Paragraph("<b>Affirmations for Client</b>", H2),
        Paragraph("I am safe. I allow myself to receive love, support and money. My power is gentle and firm. "
                  "My heart forgives and moves forward. My voice is heard. My mind is clear. I am divinely guided and supported.",
                  SMALL),
        Spacer(1,6),
        Paragraph("<b>Crystal Support (MyAuraBliss)</b>", H2),
        Paragraph("Choose bracelet/crystal for the chakras that showed Blocked or Overactive. Wear daily for 21 days, cleanse on full moon, and charge with the affirmation above.",
                  SMALL),
    ]
    story += summary_blocks
    story.append(PageBreak())

    # ---------- CHAKRA DASHBOARD (color bars + mini chart) ----------
    story += [Paragraph("Chakra Dashboard", H2), Spacer(1,4)]

    def bar_row(name: str, val: float) -> Table:
        pct = max(0, min(100, round(val/7*100)))
        col = colors.HexColor(CHAKRA_COLORS.get(name, "#777"))
        d = Drawing(260, 14)
        d.add(Rect(0, 0, 260, 14, fillColor=colors.HexColor("#EEEEEE"), strokeColor=None))
        d.add(Rect(0, 0, 2.6*pct, 14, fillColor=col, strokeColor=None))
        d.add(String(2.6*pct+6 if pct<90 else 8, 10, f"{pct}%", fontSize=8, fillColor=colors.HexColor("#333333")))
        status = chakra_status(val)
        why = Paragraph(f"Why: {status} — score {val:.1f}.", SMALL)
        rem = Paragraph(chakra_remedy(status, name), SMALL)
        row = [Paragraph(f"<b>{name}</b>", CELL), d, why, rem]
        t = Table([row], colWidths=[3.0*cm, 7.0*cm, 4.2*cm, 6.0*cm])
        t.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#DDDDDD")),
            ("WORDWRAP",(0,0),(-1,-1),"CJK"),
        ]))
        return t

    for ch, val in chakras.items():
        story.append(bar_row(ch, val))
        story.append(Spacer(1,4))

    story.append(Spacer(1,6))
    story.append(Paragraph("<b>Chakra balance snapshot (1–7)</b>", NORMAL))
    chart = Drawing(420, 160)
    bc = VerticalBarChart()
    bc.x = 40; bc.y = 30; bc.height = 110; bc.width = 340
    bc.data = [tuple(chakras[k] for k in chakras.keys())]
    bc.categoryAxis.categoryNames = list(chakras.keys())
    bc.valueAxis.valueMin = 0; bc.valueAxis.valueMax = 7; bc.valueAxis.valueStep = 1
    bc.barWidth = 18
    bc.bars[0].fillColor = colors.HexColor("#6E3CBC")
    chart.add(bc)
    story.append(chart)
    story.append(PageBreak())

    # ---------- CHAKRA REMEDIES TABLES (3 pages, same layout as page 3) ----------
    items = list(chakras.items())

    def chakra_table(title_txt: str, subset: List[Tuple[str,float]]):
        story.append(Paragraph(title_txt, H2))
        data = [[Paragraph("<b>Chakra</b>", CELL),
                 Paragraph("<b>Avg (1–7)</b>", CELL),
                 Paragraph("<b>Status</b>", CELL),
                 Paragraph("<b>Crystals</b>", CELL),
                 Paragraph("<b>Why / What / Remedies</b>", CELL)]]
        for ch, val in subset:
            stat = chakra_status(val)
            crystals = ", ".join(MYAURABLISS.get(ch, []))
            why = f"Why: {stat} at {val:.1f}. What: 10–12 min daily attention; journal changes."
            rem = chakra_remedy(stat, ch)
            data.append([
                Paragraph(ch, CELL),
                Paragraph(f"{val:.1f}", CELL),
                Paragraph(stat, CELL),
                Paragraph(crystals, CELL_SM),
                Paragraph(why + " " + rem, CELL_SM),
            ])
        tbl = Table(data, colWidths=[3.0*cm, 2.5*cm, 2.9*cm, 5.0*cm, 7.6*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EAF6")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#1A237E")),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#CFCFCF")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("WORDWRAP",(0,0),(-1,-1),"CJK"),   # <-- wraps long text so it never spills
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke, colors.HexColor("#FAFAFA")]),
        ]))
        story.append(tbl)

    chakra_table("Chakra Remedies — Part 1", items[:3]); story.append(PageBreak())
    chakra_table("Chakra Remedies — Part 2", items[3:5]); story.append(PageBreak())
    chakra_table("Chakra Remedies — Part 3", items[5:])

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
