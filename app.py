# Soulful Academy — Personality + Chakra Scan (Final)
# - Auto logo from assets/soulful_logo.png (no upload needed)
# - Gender radio alignment fixed (no wrapping)
# - Centered single-dot radios for all questions
# - Pro 6-page PDF:
#   1) Cover (Logo + Client Details)
#   2) Personality Table (+ verdict)
#   3) Personality Alignment Tips
#   4) Big Summary (Quick Reading, Follow-up, Affirmations, Crystal Support)
#   5) Chakra Dashboard (7 color bars + % + mini bar chart)
#   6–8) Chakra Remedies tables (3 parts) with safe word wrapping
# - Footer with page number + tagline on every page

import io, os, base64, datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st

# ---------- ReportLab ----------
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart

# ---------- THEME ----------
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE  = "#6E3CBC"
LAVENDER       = "#D9B2FF"
SOFT_GOLD_BG   = "#FFE6D9"
CTA_GOLD_1     = "#FFD86F"
CTA_GOLD_2     = "#FFB347"
TEXT_VIOLET    = "#2D033B"

st.set_page_config(page_title="Soulful Academy — Personality + Chakra Scan", page_icon="🔮", layout="centered")

# ---------- LOGO ----------
LOGO_PATH = "assets/soulful_logo.png"  # place your logo here
logo_bytes: Optional[bytes] = None
logo_html = ""
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_bytes = f.read()
        b64 = base64.b64encode(logo_bytes).decode("utf-8")
        logo_html = f"<div class='header-logo' style=\"background-image:url(data:image/png;base64,{b64})\"></div>"

# ---------- CSS ----------
st.markdown(f"""
<style>
body {{
  background: linear-gradient(135deg, {LAVENDER}, {SOFT_GOLD_BG});
  font-family: 'Poppins', system-ui, -apple-system, Segoe UI, Roboto, Arial;
  color: {TEXT_VIOLET};
}}
section.main > div {{ max-width: 980px; }}
:root {{ --accent:{ACCENT_PURPLE}; --purple:{PRIMARY_PURPLE}; --violet:{TEXT_VIOLET}; }}

/* Header */
.header-band {{
  background: linear-gradient(90deg, var(--accent), var(--purple));
  color:#fff; padding:22px 24px; border-radius:16px; margin-bottom:18px;
  box-shadow:0 12px 36px rgba(78,0,130,.35);
  position:relative; overflow:hidden;
}}
.header-band h1 {{ margin:0; font-weight:800; text-transform:uppercase; letter-spacing:.6px; }}
.header-band p {{ margin:6px 0 0 0; opacity:.95; font-size:15px; }}
.header-logo {{
  position:absolute; right:18px; top:14px; width:84px; height:84px;
  border-radius:12px; background-size:cover; background-position:center;
  box-shadow:0 8px 22px rgba(0,0,0,.2);
}}

/* Radios (single native dots) */
.stRadio div[role='radiogroup'] {{
  display:flex; justify-content:center; gap:18px; align-items:center; flex-wrap:wrap;
}}
.stRadio [role="radio"] {{ transform: scale(1.25); accent-color: var(--accent); }}
.stRadio label {{ white-space: nowrap; color: var(--purple); font-weight:500; font-size:15px; line-height:1; }}

/* CTA */
.stButton > button {{
  background:linear-gradient(135deg,{CTA_GOLD_1},{CTA_GOLD_2});
  color:{PRIMARY_PURPLE}; border:none; font-weight:700; border-radius:999px; padding:10px 20px;
  box-shadow:0 10px 24px rgba(255,184,71,.35); text-transform:uppercase; letter-spacing:.4px;
}}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown(f"""
<div class='header-band'>
  {logo_html}
  <h1>🔮 Personality + Chakra Scan</h1>
  <p>Discover your personality type & chakra balance — powered by Soulful Academy.</p>
</div>
""", unsafe_allow_html=True)

# ---------- CLIENT INFO ----------
c1, c2, c3 = st.columns([1.2, 1, 1])
client_name = c1.text_input("Client Name", value="")
coach_name  = c2.text_input("Coach / Healer", value="Rekha Babulkar")
session_date = c3.text_input("Session Date", value=dt.datetime.now().strftime("%d-%m-%Y"))

g1, g2, g3 = st.columns([0.9, 0.9, 3.2])
gender = g1.radio("Gender", ["Female", "Male", "Other"], horizontal=True, index=0)
intent = st.text_input("Client Intent / Focus", value="Relationship healing / Money flow / Health")

st.divider()

# ---------- PERSONALITY ----------
@dataclass
class Item:
    left: str
    right: str
    trait: str
    reverse: bool = False

PERSONALITY_ITEMS: List[Item] = [
    Item("I am often disorganized", "I keep myself organized", "C"),
    Item("I decide with my head", "I decide with my heart", "A", True),
    Item("I prefer trusted methods", "I like to innovate", "O", True),
    Item("I keep thoughts to myself", "I speak up", "E"),
    Item("I avoid attention", "I enjoy attention", "E"),
    Item("I pursue my own goals", "I look for ways to help others", "A", True),
    Item("I let others start conversations", "I start conversations", "E"),
    Item("I like ideas that are easy", "I like ideas that are complex", "O"),
    Item("I can be careless", "I follow through on tasks", "C"),
    Item("I distrust people easily", "I trust people easily", "A"),
]

def dot_radio(key: str, default: int = 4) -> int:
    opts = list(range(1,8))
    idx = opts.index(st.session_state.get(key, default))
    val = st.radio("", opts, index=idx, key=f"_r_{key}", horizontal=True, label_visibility="collapsed")
    st.session_state[key] = val
    return val

st.header("Part 1 · Personality")
st.caption("For each pair: 1 = left statement, 7 = right statement.")
responses: List[Tuple[Item,int]] = []
for i, item in enumerate(PERSONALITY_ITEMS, start=1):
    lc, rc = st.columns(2)
    with lc: st.write(item.left)
    with rc: st.write(f"<div style='text-align:right'>{item.right}</div>", unsafe_allow_html=True)
    responses.append((item, dot_radio(f"q{i}", 4)))
    st.markdown("---")

# ---------- CHAKRA ----------
CHAKRA_QUESTIONS: Dict[str, List[str]] = {
    "Root": ["I feel safe and grounded in daily life.","I keep consistent routines (sleep, food, movement).","I manage money and basic needs calmly."],
    "Sacral": ["I allow myself pleasure and creativity.","My relationships feel warm and emotionally alive.","I express feelings without guilt or shame."],
    "Solar Plexus": ["I take decisive action toward goals.","I keep healthy boundaries and say no when needed.","I trust my capability to handle challenges."],
    "Heart": ["I forgive myself and others with ease.","I feel connected to people and life.","I practice gratitude and compassion daily."],
    "Throat": ["I speak my truth calmly and clearly.","I listen well and communicate honestly.","I express my needs without fear."],
    "Third Eye": ["I reflect and learn from patterns in my life.","I visualize outcomes before I act.","I trust my intuition when logic is equal."],
    "Crown": ["I feel guided by a higher purpose.","I spend time in silence or meditation.","I experience moments of awe or connection."],
}

MYAURABLISS = {
    "Root": ["Red Jasper","Hematite","Black Tourmaline"],
    "Sacral": ["Carnelian","Orange Calcite","Moonstone"],
    "Solar Plexus": ["Citrine","Tiger's Eye","Yellow Aventurine"],
    "Heart": ["Rose Quartz","Green Aventurine","Malachite"],
    "Throat": ["Sodalite","Blue Apatite","Aquamarine"],
    "Third Eye": ["Amethyst","Lapis Lazuli","Lepidolite"],
    "Crown": ["Clear Quartz","Amethyst","Selenite"],
}

st.header("Part 2 · Chakra Scan")
st.caption("Rate each (1 = Strongly Disagree, 7 = Strongly Agree). Higher is healthier.")
chakra_scores: Dict[str, List[int]] = {k: [] for k in CHAKRA_QUESTIONS}
for ch, qs in CHAKRA_QUESTIONS.items():
    st.subheader(ch)
    for j, q in enumerate(qs, start=1):
        st.write(q)
        chakra_scores[ch].append(dot_radio(f"{ch}_{j}", 4))
    st.markdown("---")

# ---------- SCORING ----------
@st.cache_data
def score_personality(items: List[Tuple[Item,int]]) -> Dict[str,float]:
    vals={t:[] for t in "OCEAN"}
    for it,val in items:
        v=(val-4)  # -3..+3 centered
        if it.reverse: v=-v
        vals[it.trait].append(v)
    return {t: float(np.mean(v)) if v else 0 for t,v in vals.items()}

def summarize_trait(name:str,score:float)->str:
    bands=[(-3,-1.6,"Low"),(-1.6,-0.5,"Below Avg"),(-0.5,0.5,"Balanced"),(0.5,1.6,"High"),(1.6,3.1,"Very High")]
    label=next(lbl for lo,hi,lbl in bands if lo<=score<hi)
    return f"{label}"

@st.cache_data
def score_chakras(scores: Dict[str, List[int]]) -> Dict[str, float]:
    return {k: float(np.mean(v)) if v else 0.0 for k, v in scores.items()}

def chakra_status(v: float) -> str:
    return "Balanced" if 3.8 <= v <= 5.8 else ("Overactive" if v > 5.8 else "Blocked")

def chakra_remedy(status: str, chakra: str) -> str:
    base={"Root":"Grounding walk, red foods.","Sacral":"Creative play, water ritual.",
          "Solar Plexus":"Power poses, small wins.","Heart":"Gratitude meditation.",
          "Throat":"Sing or journal truth.","Third Eye":"Visualization & journaling.","Crown":"Silence & service."}
    crystals=", ".join(MYAURABLISS.get(chakra, []))
    return f"{status}: {base.get(chakra,'')} • Crystals: {crystals}"

# Chakra colors for PDF bars
CHAKRA_COLORS = {
    "Root": "#EA4335", "Sacral": "#F4A261", "Solar Plexus": "#E9C46A",
    "Heart": "#34A853", "Throat": "#4285F4", "Third Eye": "#7E57C2", "Crown": "#B39DDB"
}

# ---------- PRO PDF ----------
def build_pdf(traits: Dict[str,float],
              chakras: Dict[str,float],
              logo: Optional[bytes],
              meta: Dict[str,str]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=28, rightMargin=28, topMargin=28, bottomMargin=28)

    styles = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=22, leading=26, textColor=colors.HexColor("#212121"), alignment=0)
    H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=16, leading=20, textColor=colors.HexColor("#311B92"))
    NORMAL = styles["Normal"]
    SMALL  = ParagraphStyle("SMALL", parent=NORMAL, fontSize=9, leading=12, textColor=colors.HexColor("#616161"))
    CELL   = ParagraphStyle("CELL", parent=NORMAL, fontSize=10, leading=13)   # table cells
    CELL_SM= ParagraphStyle("CELL_SM", parent=NORMAL, fontSize=9, leading=12) # tighter cell

    story = []

    # Footer
    def footer(canvas, doc_):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#666666"))
        w, h = A4
        canvas.drawRightString(w-28, 18, f"Page {doc_.page}")
        canvas.drawString(28, 18, "Soulful Academy • What You Seek Is Seeking You")

    # -------- COVER --------
    left_cell = [Image(io.BytesIO(logo), width=90, height=90)] if logo else []
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

    # -------- PERSONALITY --------
    def personality_verdict(ts: Dict[str,float]) -> str:
        o, c, e, a = ts.get("O",0), ts.get("C",0), ts.get("E",0), ts.get("A",0)
        if c>1.0 and o>0.5: return "Organized Visionary"
        if e>1.0 and a>0.5: return "Warm Communicator"
        if o>1.2 and c<-0.5: return "Creative Explorer"
        if c>1.2 and e<-0.5: return "Calm Strategist"
        return "Balanced Builder"

    story += [Paragraph("Personality Profile (Big Five style)", H2), Spacer(1,6)]
    story += [Paragraph(f"<b>What kind of personality are you?</b> {personality_verdict(traits)}", NORMAL), Spacer(1,8)]

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

    # -------- BIG SUMMARY --------
    story += [
        Paragraph("<b>Quick Reading</b>", H2),
        Paragraph(
            "Start with the lowest blocked chakra and move upward. Use the crystal suggestions, pair with 108× Ho’oponopono on the main person/event linked to that chakra, and soften any overactive areas with grounding, slow breathing and clear boundaries.",
            NORMAL
        ),
        Spacer(1,6),
        Paragraph("<b>Follow-up & Home Practice (7-Day Plan)</b>", H2),
        Paragraph(
            "1) Day 1–2: Chakra awareness — 7–11 minutes Root→Crown meditation. "
            "2) Day 3–4: Emotional cleaning — journal ‘Who/what am I still holding in this chakra?’ + 108× Ho’oponopono. "
            "3) Day 5: Crystal activation — wear/place suggested MyAuraBliss crystal for 11 minutes. "
            "4) Day 6: Relationship repair — speak your truth (Throat/Heart). "
            "5) Day 7: Integration — repeat meditation and note shifts.",
            SMALL
        ),
        Spacer(1,6),
        Paragraph("<b>Affirmations for Client</b>", H2),
        Paragraph(
            "I am safe. I allow myself to receive love, support and money. My power is gentle and firm. "
            "My heart forgives and moves forward. My voice is heard. My mind is clear. I am divinely guided and supported.",
            SMALL
        ),
        Spacer(1,6),
        Paragraph("<b>Crystal Support (MyAuraBliss)</b>", H2),
        Paragraph(
            "Choose bracelet/crystal for the chakras that showed Blocked or Overactive. Wear daily for 21 days, cleanse on full moon, and charge with the affirmation above.",
            SMALL
        ),
        PageBreak()
    ]

    # -------- CHAKRA DASHBOARD --------
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

    # -------- CHAKRA REMEDIES TABLES (3 pages) --------
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
                Paragraph(why + ' ' + rem, CELL_SM),
            ])
        tbl = Table(data, colWidths=[3.0*cm, 2.5*cm, 2.9*cm, 5.0*cm, 7.6*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EAF6")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#1A237E")),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#CFCFCF")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("WORDWRAP",(0,0),(-1,-1),"CJK"),   # wraps long text so nothing spills
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke, colors.HexColor("#FAFAFA")]),
        ]))
        story.append(tbl)

    chakra_table("Chakra Remedies — Part 1", items[:3]); story.append(PageBreak())
    chakra_table("Chakra Remedies — Part 2", items[3:5]); story.append(PageBreak())
    chakra_table("Chakra Remedies — Part 3", items[5:])

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()

# ---------- GENERATE ----------
if st.button("📊 Generate Full Report", type="primary"):
    traits = score_personality(responses)
    chakras = score_chakras(chakra_scores)
    meta = {"client": client_name.strip() or "—", "coach": coach_name.strip() or "—",
            "date": session_date.strip() or "—", "gender": gender, "intent": intent.strip() or "—"}
    pdf_bytes = build_pdf(traits, chakras, logo_bytes, meta)
    st.download_button("📄 Download PDF",
                       data=pdf_bytes,
                       file_name=f"SoulfulAcademy_Report_{(meta['client'] or 'Client').replace(' ','_')}.pdf",
                       mime="application/pdf")
