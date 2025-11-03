# app.py — Soulful Academy: Personality + Chakra Scan
# - Auto logo from /assets/soulful_logo.png
# - Client info form
# - Clean native radio dots
# - Professional 6-page PDF (cover + personality + chakras)

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
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image, PageBreak
)

# ------------------- Theme -------------------
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE  = "#6E3CBC"
LAVENDER       = "#D9B2FF"
SOFT_GOLD_BG   = "#FFE6D9"
CTA_GOLD_1     = "#FFD86F"
CTA_GOLD_2     = "#FFB347"
TEXT_VIOLET    = "#2D033B"

st.set_page_config(page_title="Soulful Academy — Personality + Chakra Scan", page_icon="🔮", layout="centered")

# ------------------- Logo -------------------
LOGO_PATH = "assets/soulful_logo.png"  # place your logo file here
logo_bytes: Optional[bytes] = None
logo_html = ""
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_bytes = f.read()
        b64 = base64.b64encode(logo_bytes).decode("utf-8")
        logo_html = f"<div class='header-logo' style=\"background-image:url(data:image/png;base64,{b64})\"></div>"

# ------------------- CSS -------------------
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

/* Radio styling (single native dots) */
.stRadio div[role='radiogroup'] {{
  display:flex; justify-content:center; gap:18px; align-items:center;
}}
.stRadio [role="radio"] {{ transform: scale(1.25); accent-color: var(--accent); }}
.stRadio label {{ color: var(--purple); font-weight: 500; font-size: 15px; }}

/* CTA */
.stButton > button {{
  background:linear-gradient(135deg,{CTA_GOLD_1},{CTA_GOLD_2});
  color:{PRIMARY_PURPLE}; border:none; font-weight:700;
  border-radius:999px; padding:10px 20px;
  box-shadow:0 10px 24px rgba(255,184,71,.35);
  text-transform:uppercase; letter-spacing:.4px;
}}
</style>
""", unsafe_allow_html=True)

# ------------------- Header -------------------
st.markdown(f"""
<div class='header-band'>
  {logo_html}
  <h1>🔮 Personality + Chakra Scan</h1>
  <p>Discover your personality type & chakra balance — powered by Soulful Academy.</p>
</div>
""", unsafe_allow_html=True)

# ------------------- Client Info -------------------
c1, c2, c3 = st.columns([1.2, 1, 1])
client_name = c1.text_input("Client Name", value="")
coach_name  = c2.text_input("Coach / Healer", value="Rekha Babulkar")
session_date = c3.text_input("Session Date", value=dt.datetime.now().strftime("%d-%m-%Y"))

gcol1, gcol2, gcol3 = st.columns([0.8, 0.8, 4])
gender = gcol1.radio("Gender", ["Female", "Male", "Other"], horizontal=True, index=0)
intent = st.text_input("Client Intent / Focus", value="Relationship healing / Money flow / Health")

st.divider()

# ------------------- Personality Items -------------------
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

# ------------------- Chakra Questions -------------------
CHAKRA_QUESTIONS: Dict[str, List[str]] = {
    "Root": [
        "I feel safe and grounded in daily life.",
        "I keep consistent routines (sleep, food, movement).",
        "I manage money and basic needs calmly.",
    ],
    "Sacral": [
        "I allow myself pleasure and creativity.",
        "My relationships feel warm and emotionally alive.",
        "I express feelings without guilt or shame.",
    ],
    "Solar Plexus": [
        "I take decisive action toward goals.",
        "I keep healthy boundaries and say no when needed.",
        "I trust my capability to handle challenges.",
    ],
    "Heart": [
        "I forgive myself and others with ease.",
        "I feel connected to people and life.",
        "I practice gratitude and compassion daily.",
    ],
    "Throat": [
        "I speak my truth calmly and clearly.",
        "I listen well and communicate honestly.",
        "I express my needs without fear.",
    ],
    "Third Eye": [
        "I reflect and learn from patterns in my life.",
        "I visualize outcomes before I act.",
        "I trust my intuition when logic is equal.",
    ],
    "Crown": [
        "I feel guided by a higher purpose.",
        "I spend time in silence or meditation.",
        "I experience moments of awe or connection.",
    ],
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

# ------------------- Scoring -------------------
@st.cache_data
def score_personality(items: List[Tuple[Item,int]]) -> Dict[str,float]:
    vals={t:[] for t in "OCEAN"}
    for it,val in items:
        v=(val-4)  # -3..+3
        if it.reverse: v=-v
        vals[it.trait].append(v)
    return {t: float(np.mean(v)) if v else 0 for t,v in vals.items()}

def summarize_trait(name:str,score:float)->str:
    bands=[(-3,-1.6,"Low"),(-1.6,-0.5,"Below Avg"),(-0.5,0.5,"Balanced"),(0.5,1.6,"High"),(1.6,3.1,"Very High")]
    label=next(lbl for lo,hi,lbl in bands if lo<=score<hi)
    return f"**{label}**"

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

# ------------------- PDF Builder (PRO style) -------------------
def build_pdf(traits: Dict[str,float],
              chakras: Dict[str,float],
              logo: Optional[bytes],
              meta: Dict[str,str]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)

    s = getSampleStyleSheet()
    # Custom styles
    H1 = ParagraphStyle("H1", parent=s["Title"], alignment=0, fontSize=22, leading=26, textColor=colors.HexColor("#222"))
    H2 = ParagraphStyle("H2", parent=s["Heading2"], fontSize=16, leading=20, textColor=colors.HexColor("#311B92"))
    SMALL = ParagraphStyle("SMALL", parent=s["Normal"], fontSize=9, textColor=colors.HexColor("#555"))
    NORMAL = s["Normal"]

    story = []

    # ====== PAGE 1: Branded Cover with Client details ======
    # Header band with logo + title (table layout)
    header_data = []
    left_cell = []
    if logo:
        left_cell.append(Image(io.BytesIO(logo), width=90, height=90))
    header_table = Table([
        [left_cell, Paragraph("<b>Soulful Academy – Chakra & Personality Report</b>", H1)]
    ], colWidths=[3.2*cm, 13.8*cm], hAlign="LEFT")
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))
    story += [header_table, Spacer(1, 4),
              Paragraph("A diagnostic template for your clients. Fill → download → email.", SMALL),
              Spacer(1, 16)]

    # Client info band
    ci = [
        ["Client", meta.get("client","—")],
        ["Coach / Healer", meta.get("coach","—")],
        ["Session Date", meta.get("date","—")],
        ["Gender", meta.get("gender","—")],
        ["Intent / Focus", meta.get("intent","—")],
    ]
    ci_tbl = Table(ci, colWidths=[3.5*cm, 13.5*cm])
    ci_tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#DDDDDD")),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F7F5FD")),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#311B92")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (1,0), (1,-1), [colors.whitesmoke, colors.HexColor("#FAFAFA")]),
    ]))
    story += [ci_tbl, Spacer(1, 10),
              Paragraph("Generated by Soulful Academy | What You Seek is Seeking You.", SMALL),
              PageBreak()]

    # ====== PAGE 2: Personality Profile ======
    story += [Paragraph("Personality Profile (Big Five style)", H2), Spacer(1, 8)]
    pdata = [["Trait", "Score (-3..+3)", "Summary"]]
    for t, v in traits.items():
        pdata.append([t, f"{v:.2f}", summarize_trait(t, v)])
    ptable = Table(pdata, colWidths=[3*cm, 4*cm, 9.5*cm])
    ptable.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EDE7F6")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#311B92")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#CCCCCC")),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor("#FAFAFA")]),
    ]))
    story += [ptable, Spacer(1, 6),
              Paragraph("Scores are centered at 0 (balanced). Higher/lower describe tendencies, not limits.", SMALL),
              PageBreak()]

    # ====== PAGE 3: Personality Growth Tips ======
    story += [Paragraph("Growth Insights", H2)]
    tips = [
        "Balance creativity with grounded actions.",
        "Use 2 anchor habits (sleep window, 30-min deep work) to support consistency.",
        "If Extraversion is high, schedule solo reflection; if low, plan one meaningful social slot.",
        "Balance Agreeableness with clear boundaries and ‘no’ practice."
    ]
    for t in tips:
        story.append(Paragraph("• " + t, NORMAL))
    story.append(PageBreak())

    # ====== PAGES 4–6: Chakra Scan ======
    items = list(chakras.items())

    def chakra_table(title_txt: str, subset: List[Tuple[str,float]]):
        story.append(Paragraph(title_txt, H2))
        data = [["Chakra", "Avg (1–7)", "Status", "MyAuraBliss Crystals", "Remedy"]]
        for ch, val in subset:
            stat = chakra_status(val)
            crystals = ", ".join(MYAURABLISS.get(ch, []))
            data.append([ch, f"{val:.1f}", stat, crystals, chakra_remedy(stat, ch)])
        tbl = Table(data, colWidths=[3*cm, 2.7*cm, 3*cm, 5*cm, 4*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EAF6")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#1A237E")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#CCCCCC")),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.whitesmoke, colors.HexColor("#FAFAFA")]),
        ]))
        story.append(tbl)

    chakra_table("Chakra Scan — Part 1", items[:3]); story.append(PageBreak())
    chakra_table("Chakra Scan — Part 2", items[3:5]); story.append(PageBreak())
    chakra_table("Chakra Scan — Part 3", items[5:])

    doc.build(story)
    return buf.getvalue()

# ------------------- Results & Download -------------------
if st.button("📊 Generate Full Report", type="primary"):
    traits = score_personality(responses)
    chakras = score_chakras(chakra_scores)

    meta = {
        "client": client_name.strip() or "—",
        "coach": coach_name.strip() or "—",
        "date": session_date.strip() or "—",
        "gender": gender,
        "intent": intent.strip() or "—",
    }

    pdf_bytes = build_pdf(traits, chakras, logo_bytes, meta)
    st.success("Report ready.")
    st.download_button("📄 Download PDF", data=pdf_bytes, file_name=f"SoulfulAcademy_Report_{meta['client'] or 'Client'}.pdf", mime="application/pdf")
