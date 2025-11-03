# app.py — Personality + Chakra Scan (Soulful Academy Final Version)
# - Logo auto-loaded from /assets/soulful_logo.png
# - Clean purple-gold design
# - Centered radio dots
# - 5-page Personality + Chakra report

import io, base64, os
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image, PageBreak

# ------------------- Theme -------------------
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE  = "#6E3CBC"
LAVENDER       = "#D9B2FF"
SOFT_GOLD_BG   = "#FFE6D9"
CTA_GOLD_1     = "#FFD86F"
CTA_GOLD_2     = "#FFB347"
TEXT_VIOLET    = "#2D033B"

st.set_page_config(page_title="Soulful Academy — Personality + Chakra Scan", page_icon="🔮", layout="centered")

# ------------------- Load Logo -------------------
LOGO_PATH = "assets/soulful_logo.png"  # put your logo here inside /assets folder

logo_bytes: Optional[bytes] = None
if os.path.exists(LOGO_PATH):
    with open(LOGO_PATH, "rb") as f:
        logo_bytes = f.read()
        b64 = base64.b64encode(logo_bytes).decode("utf-8")
        logo_html = f"<div class='header-logo' style=\"background-image:url(data:image/png;base64,{b64})\"></div>"
else:
    logo_html = ""

# ------------------- CSS -------------------
st.markdown(f"""
<style>
body {{
  background: linear-gradient(135deg, {LAVENDER}, {SOFT_GOLD_BG});
  font-family: 'Poppins', sans-serif;
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
.header-band h1 {{
  margin:0; font-weight:800; text-transform:uppercase; letter-spacing:.6px;
}}
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
.stRadio [role="radio"] {{
  transform: scale(1.3);
  accent-color: var(--accent);
}}
.stRadio label {{
  color: var(--purple);
  font-weight: 500;
  font-size: 15px;
}}

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

# ------------------- Data -------------------
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

CHAKRA_QUESTIONS = {
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

# ------------------- Radio Function -------------------
def dot_radio(key: str, default: int = 4) -> int:
    opts = list(range(1,8))
    idx = opts.index(st.session_state.get(key, default))
    val = st.radio("", opts, index=idx, key=f"_r_{key}", horizontal=True, label_visibility="collapsed")
    st.session_state[key] = val
    return val

# ------------------- Personality Form -------------------
st.header("Part 1 · Personality")
st.caption("For each pair: 1 = left statement, 7 = right statement.")

responses: List[Tuple[Item,int]] = []
for i, item in enumerate(PERSONALITY_ITEMS, start=1):
    lc, rc = st.columns(2)
    with lc: st.write(item.left)
    with rc: st.write(f"<div style='text-align:right'>{item.right}</div>", unsafe_allow_html=True)
    responses.append((item, dot_radio(f"q{i}", 4)))
    st.divider()

# ------------------- Chakra Form -------------------
st.header("Part 2 · Chakra Scan")
st.caption("Rate each (1 = Strongly Disagree, 7 = Strongly Agree).")

chakra_scores = {k: [] for k in CHAKRA_QUESTIONS}
for ch, qs in CHAKRA_QUESTIONS.items():
    st.subheader(ch)
    for j, q in enumerate(qs, start=1):
        st.write(q)
        chakra_scores[ch].append(dot_radio(f"{ch}_{j}", 4))
    st.markdown("---")

# ------------------- Scoring Functions -------------------
@st.cache_data
def score_personality(items: List[Tuple[Item,int]]) -> Dict[str,float]:
    vals={t:[] for t in "OCEAN"}
    for it,val in items:
        v=(val-4)
        if it.reverse: v=-v
        vals[it.trait].append(v)
    return {t: float(np.mean(v)) if v else 0 for t,v in vals.items()}

def summarize_trait(name:str,score:float)->str:
    bands=[(-3,-1.6,"Low"),(-1.6,-0.5,"Below Avg"),(-0.5,0.5,"Balanced"),(0.5,1.6,"High"),(1.6,3.1,"Very High")]
    label=next(lbl for lo,hi,lbl in bands if lo<=score<hi)
    return f"**{label}**"

def score_chakras(scores:Dict[str,List[int]])->Dict[str,float]:
    return {k:float(np.mean(v)) if v else 0 for k,v in scores.items()}

def chakra_status(v:float)->str:
    return "Balanced" if 3.8<=v<=5.8 else ("Overactive" if v>5.8 else "Blocked")

def chakra_remedy(status:str,chakra:str)->str:
    base={"Root":"Grounding walk, red foods.","Sacral":"Creative play, water ritual.","Solar Plexus":"Power poses, small wins.","Heart":"Gratitude meditation.","Throat":"Sing or journal truth.","Third Eye":"Visualization & journaling.","Crown":"Silence & service."}
    crystals=", ".join(MYAURABLISS.get(chakra,[]))
    return f"{status}: {base.get(chakra,'')} • Crystals: {crystals}"

# ------------------- Results + PDF -------------------
if st.button("📊 Generate Full Report", type="primary"):
    traits = score_personality(responses)
    chakras = score_chakras(chakra_scores)

    def build_pdf(traits, chakras, logo):
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        s = getSampleStyleSheet()
        story = []
        if logo:
            story += [Image(io.BytesIO(logo), width=80, height=80), Spacer(1, 10)]
        def title(txt): return Paragraph(f"<para align='center'><b>{txt}</b></para>", s["Title"])

        # Page 1 – Personality Overview
        story += [title("Personality Profile"), Spacer(1, 12)]
        data = [["Trait","Score","Summary"]] + [[t,f"{v:.2f}",summarize_trait(t,v)] for t,v in traits.items()]
        t = Table(data, colWidths=[3*cm,3*cm,10*cm])
        t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#EDE7F6")),("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
        story += [t, Spacer(1, 24), PageBreak()]

        # Page 2 – Growth Tips
        story += [title("Growth Insights")]
        for tip in ["Balance creativity with grounded actions.","Nurture self-worth through small daily wins.","Open communication strengthens all chakras."]:
            story.append(Paragraph("• " + tip, s["Normal"]))
        story.append(PageBreak())

        # Pages 3–5 – Chakras
        items = list(chakras.items())
        def table(title_text, subset):
            story.append(Paragraph(f"<b>{title_text}</b>", s["Heading2"]))
            data=[["Chakra","Avg","Status","Crystals","Remedy"]]
            for c,v in subset:
                stat=chakra_status(v)
                data.append([c,f"{v:.1f}",stat,", ".join(MYAURABLISS.get(c,[])),chakra_remedy(stat,c)])
            tb=Table(data,colWidths=[3*cm,2*cm,3*cm,5*cm,5*cm])
            tb.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8EAF6")),("GRID",(0,0),(-1,-1),0.25,colors.grey)]))
            story.append(tb)
        table("Chakra Scan — Part 1", items[:3]); story.append(PageBreak())
        table("Chakra Scan — Part 2", items[3:5]); story.append(PageBreak())
        table("Chakra Scan — Part 3", items[5:])
        doc.build(story)
        return buf.getvalue()

    pdf_bytes = build_pdf(traits, chakras, logo_bytes)
    st.download_button("📄 Download Full Report (PDF)", data=pdf_bytes, file_name="SoulfulAcademy_Report.pdf", mime="application/pdf")
