# Soulful Academy — Personality + Chakra Scan (Final Pro PDF)
# - Logo auto-load from assets/soulful_logo.png
# - Client details on cover
# - Clean single radio dots
# - Pro 6-page PDF: Cover • Personality Table • Personality Tips • Chakra Dashboard • Chakra Remedies (2 pages)

import io, os, base64, datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image, PageBreak
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
LOGO_PATH = "assets/soulful_logo.png"
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
.stRadio div[role='radiogroup'] {{ display:flex; justify-content:center; gap:18px; align-items:center; }}
.stRadio [role="radio"] {{ transform: scale(1.25); accent-color: var(--accent); }}
.stRadio label {{ color: var(--purple); font-weight: 500; font-size: 15px; }}

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

g1, g2, g3 = st.columns([0.8, 0.8, 4])
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
    SMALL = ParagraphStyle("SMALL", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#616161"))
    NORMAL = styles["Normal"]
    BOLD = ParagraphStyle("BOLD", parent=NORMAL, fontName="Helvetica-Bold")

    story = []

    # Cover
    left_cell = []
    if logo:
        left_cell.append(Image(io.BytesIO(logo), width=90, height=90))
    header = Table([[left_cell, Paragraph("<b>Soulful Academy — Chakra & Personality Report</b>", H1)]],
                   colWidths=[3.0*cm, 14.0*cm])
    header.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
    story += [header, Spacer(1,6), Paragraph("A diagnostic report you can email to the client.", SMALL), Spacer(1,14)]

    details = [
        ["Client", meta.get("client","—")],
        ["Coach / Healer", meta.get("coach","—")],
        ["Session Date", meta.get("date","—")],
        ["Gender", meta.get("gender","—")],
        ["Intent / Focus", meta.get("intent","—")],
    ]
    dtbl = Table(details, colWidths=[3.5*cm, 13.5*cm])
    dtbl.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#CCCCCC")),
        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EEE7FF")),
        ("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#311B92")),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
    ]))
    story += [dtbl, PageBreak()]

    # Personality
    story += [Paragraph("Personality Profile (Big Five style)", H2), Spacer(1,6)]

    def personality_verdict(ts: Dict[str,float]) -> str:
        o, c, e, a = ts.get("O",0), ts.get("C",0), ts.get("E",0), ts.get("A",0)
        if c>1.0 and o>0.5: return "Organized Visionary"
        if e>1.0 and a>0.5: return "Warm Communicator"
        if o>1.2 and c<-0.5: return "Creative Explorer"
        if c>1.2 and e<-0.5: return "Calm Strategist"
        return "Balanced Builder"

    verdict = personality_verdict(traits)
    story += [Paragraph(f"<b>What kind of personality are you?</b> {verdict}", NORMAL), Spacer(1,8)]

    pdata = [["Trait","Score (-3..+3)","Summary"]]
    for t,v in traits.items():
        pdata.append([t, f"{v:.2f}", summarize_trait(t,v)])
    ptable = Table(pdata, colWidths=[3.0*cm, 3.8*cm, 10.7*cm])
    ptable.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EDE7F6")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#311B92")),
        ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
        ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#BBBBBB")),
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke, colors.HexColor("#FAFAFA")]),
    ]))
    story += [ptable, Spacer(1,8)]

    align_points = [
        "With high-C (organized) people: agree on clear timelines and definitions of done.",
        "With high-O (creative) people: brainstorm first, then lock one experiment to ship.",
        "With high-E (expressive) people: allow talk-time, then summarize action points.",
        "With high-A (kind) people: invite honest feedback and set gentle boundaries.",
    ]
    story += [Paragraph("<b>How to align with other personalities</b>", BOLD)]
    for tip in align_points:
        story.append(Paragraph("• "+tip, NORMAL))
    story.append(PageBreak())

    # Chakra Dashboard
    story += [Paragraph("Chakra Dashboard", H2), Spacer(1,4)]

    def bar_row(name: str, val: float) -> Table:
        pct = max(0, min(100, round(val/7*100)))
        col = colors.HexColor(CHAKRA_COLORS.get(name, "#777"))
        d = Drawing(260, 14)
        d.add(Rect(0, 0, 260, 14, fillColor=colors.HexColor("#EEEEEE"), strokeColor=None))
        d.add(Rect(0, 0, 2.6*pct, 14, fillColor=col, strokeColor=None))
        d.add(String(2.6*pct+6 if pct<90 else 8, 10, f"{pct}%", fontSize=8, fillColor=colors.HexColor("#333333")))
        status = chakra_status(val)
        why = f"Why: {status} — score {val:.1f}."
        what = "What: focus daily 10–12 min awareness on this chakra."
        rem = chakra_remedy(status, name)
        row = [Paragraph(f"<b>{name}</b>", NORMAL), d, Paragraph(why, SMALL), Paragraph(rem, SMALL)]
        t = Table([row], colWidths=[2.8*cm, 7.0*cm, 4.2*cm, 6.0*cm])
        t.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"), ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#DDDDDD"))]))
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

    # Chakra Remedies tables (2 pages)
    items = list(chakras.items())

    def chakra_table(title_txt: str, subset: List[Tuple[str,float]]):
        story.append(Paragraph(title_txt, H2))
        data = [["Chakra","Avg (1–7)","Status","MyAuraBliss Crystals","Why / What / Remedies"]]
        for ch, val in subset:
            stat = chakra_status(val)
            crystals = ", ".join(MYAURABLISS.get(ch, []))
            why = f"Why: {stat} at {val:.1f}."
            what = "What: 10–12 min daily attention; journal changes."
            rem = chakra_remedy(stat, ch)
            data.append([ch, f"{val:.1f}", stat, crystals, f"{why} {what} {rem}"])
        tbl = Table(data, colWidths=[3.0*cm, 2.5*cm, 2.8*cm, 5.0*cm, 7.5*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EAF6")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.HexColor("#1A237E")),
            ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#CFCFCF")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.whitesmoke, colors.HexColor("#FAFAFA")]),
        ]))
        story.append(tbl)

    chakra_table("Chakra Remedies — Part 1", items[:3]); story.append(PageBreak())
    chakra_table("Chakra Remedies — Part 2", items[3:5]); story.append(PageBreak())
    chakra_table("Chakra Remedies — Part 3", items[5:])

    doc.build(story)
    return buf.getvalue()

# ---------- GENERATE ----------
if st.button("📊 Generate Full Report", type="primary"):
    traits = score_personality(responses)
    chakras = score_chakras(chakra_scores)
    meta = {"client": client_name.strip() or "—", "coach": coach_name.strip() or "—",
            "date": session_date.strip() or "—", "gender": gender, "intent": intent.strip() or "—"}
    pdf_bytes = build_pdf(traits, chakras, logo_bytes, meta)
    st.download_button("📄 Download PDF", data=pdf_bytes,
                       file_name=f"SoulfulAcademy_Report_{meta['client'] or 'Client'}.pdf",
                       mime="application/pdf")
