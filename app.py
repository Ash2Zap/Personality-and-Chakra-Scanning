# app.py — Personality + Chakra Scan (Soulful Academy Edition)
# ------------------------------------------------------------
# - Public-domain Big Five–style items (not Truity’s proprietary items/logic)
# - Left↔Right 7-dot selector using native st.radio + CSS (no JS)
# - Chakra scan (21 items), brand theme, logo, gold CTA
# - PDF export: 2 pages personality + 3 pages chakras (with MyAuraBliss crystals)
#
# Requirements (requirements.txt):
# streamlit
# pandas
# numpy
# reportlab

import io
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image

# ---------------------------- BRAND THEME ---------------------------------
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE  = "#6E3CBC"
LAVENDER       = "#D9B2FF"   # bg start
SOFT_GOLD_BG   = "#FFE6D9"   # bg end
CTA_GOLD_1     = "#FFD86F"
CTA_GOLD_2     = "#FFB347"
TEXT_VIOLET    = "#2D033B"

st.set_page_config(page_title="Personality + Chakra Scan", page_icon="🔮", layout="centered")

CUSTOM_HEAD = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Poppins:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
/* Background + layout */
body {{
  background: linear-gradient(135deg, {LAVENDER}, {SOFT_GOLD_BG});
}}
section.main > div {{ max-width: 980px; }}
:root {{ --accent: {ACCENT_PURPLE}; --purple: {PRIMARY_PURPLE}; --violet: {TEXT_VIOLET}; }}

/* Header */
.header-band {{
  background: linear-gradient(90deg, var(--accent), var(--purple));
  color: white; padding: 22px 24px; border-radius: 16px;
  box-shadow: 0 12px 36px rgba(78,0,130,.35); margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,.15); position: relative; overflow:hidden;
}}
.header-band h1 {{
  margin:0; font-family: 'Playfair Display', serif; letter-spacing:.5px;
  font-weight:800; text-transform:uppercase; text-shadow:0 0 10px rgba(255,255,255,.2);
}}
.header-band p {{ margin:6px 0 0 0; opacity:.95; font-family:'Poppins', sans-serif; }}
.header-logo {{ position:absolute; right:18px; top:14px; width:84px; height:84px;
  border-radius:12px; box-shadow:0 8px 22px rgba(0,0,0,.2); background-size:cover; background-position:center; }}

/* Card rows */
.item-row {{
  border: 1px solid #f0dffb; border-left: 6px solid var(--accent);
  border-radius: 14px; padding: 12px 14px; margin-bottom: 12px; background:#fff;
}}
.labels {{ display:flex; justify-content:space-between; font-size:14px; color:#5a4a72; font-family:'Poppins', sans-serif; }}

/* Horizontal radio -> dot style */
.stRadio > div {{ display: flex; gap: 10px; flex-wrap: nowrap; }}
.stRadio label {{ margin-bottom: 0 !important; }}
.stRadio div[role='radiogroup']  {{ display:flex; gap:10px; }}

.stRadio input[type="radio"] {{
  /* hide native */
  opacity: 0; width: 0; height: 0; position: absolute;
}}
.stRadio label span {{ display:none; }} /* hide numbers */

.stRadio label {{
  width: 20px; height: 20px; border-radius: 50%;
  border: 2px solid var(--accent); cursor: pointer;
  position: relative; display: inline-flex; align-items:center; justify-content:center;
}}
.stRadio label:hover {{ transform: scale(1.08); }}

.stRadio input[type="radio"]:checked + div > span::after,
.stRadio input[type="radio"]:checked + span::after {{ /* compat */
  content: "";
  width: 10px; height: 10px; background: var(--purple); border-radius: 50%;
  position: absolute;
}}
/* Fallback check: Streamlit wraps differently across versions; also target label::after when checked */
.stRadio label::after {{ content: ""; width:0; height:0; }}
/* CTA button */
.stButton > button {{
  background: linear-gradient(135deg, {CTA_GOLD_1}, {CTA_GOLD_2});
  color: {PRIMARY_PURPLE}; border: none; font-weight:700;
  border-radius: 999px; padding: 10px 20px; box-shadow:0 10px 24px rgba(255,184,71,.35);
  font-family:'Poppins', sans-serif; text-transform:uppercase; letter-spacing:.4px;
}}
.stButton > button:hover {{ filter: brightness(1.05); }}

/* Aura / mandala glow box */
.aura-box {{
  position:relative; padding:18px; border-radius:16px; background:#ffffffcc;
  border:1px solid #f0dffb; margin:10px 0 18px;
}}
.aura-box::before {{
  content:''; position:absolute; inset:-40px; z-index:-1;
  background: radial-gradient(closest-side, rgba(110,60,188,.30), transparent 70%),
              radial-gradient(closest-side, rgba(255,216,111,.25), transparent 70%);
  filter: blur(20px);
}}

/* Typography */
html, body, p, div, span {{ font-family:'Poppins', sans-serif; color:{TEXT_VIOLET}; }}

#MainMenu {{visibility:hidden}} footer {{visibility:hidden}}
</style>
"""
st.markdown(CUSTOM_HEAD, unsafe_allow_html=True)

# ---------------------------- HEADER ---------------------------------
logo_file = st.file_uploader("Upload your Soulful Academy logo (PNG/JPG)", type=["png","jpg","jpeg"], key="_logo")
logo_style = ""
if logo_file is not None:
    import base64
    data = base64.b64encode(logo_file.read()).decode("utf-8")
    mime = "image/png"
    if logo_file.type == "image/jpeg":
        mime = "image/jpeg"
    logo_style = f"<div class='header-logo' style=\"background-image:url(data:{mime};base64,{data})\"></div>"

st.markdown(
    f"""
<div class='header-band'>
  <h1>🔮 Personality + Chakra Scan</h1>
  <p>Choose the option that fits you best for each pair. Then get a combined report with insights and remedies.</p>
  {logo_style}
</div>
""",
    unsafe_allow_html=True,
)

# ------------------------- DATA DEFINITIONS ----------------------------
@dataclass
class Item:
    left: str
    right: str
    trait: str  # O C E A (N optional)
    reverse: bool = False

# 20 public-domain-style pairs (IPIP-inspired)
PERSONALITY_ITEMS: List[Item] = [
    Item("I am often disorganized", "I keep myself organized", "C"),
    Item("I decide with my head", "I decide with my heart", "A", reverse=True),
    Item("I prefer trusted methods", "I like to innovate", "O", reverse=True),
    Item("I keep thoughts to myself", "I speak up", "E"),
    Item("I avoid attention", "I enjoy attention", "E"),
    Item("I pursue my own goals", "I look for ways to help others", "A", reverse=True),
    Item("I let others start conversations", "I start conversations", "E"),
    Item("I like ideas that are easy", "I like ideas that are complex", "O"),
    Item("I can be careless", "I follow through on tasks", "C"),
    Item("I distrust people easily", "I trust people easily", "A"),
    Item("I like routine", "I like to explore the new", "O"),
    Item("I tire around people", "I feel energized with people", "E"),
    Item("I can be blunt", "I am considerate", "A"),
    Item("I act on impulse", "I think before I act", "C"),
    Item("I stick to what I know", "I am curious and imaginative", "O"),
    Item("I keep to myself", "I am outgoing and sociable", "E"),
    Item("I can be skeptical", "I am cooperative", "A"),
    Item("I miss small details", "I notice small details", "C"),
    Item("I prefer facts only", "I enjoy ideas and metaphors", "O"),
    Item("I speak my mind sharply", "I soften my words with care", "A"),
]

# Chakra questions (3 per chakra)
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

CHAKRA_COLORS = {
    "Root": "#EA4335",
    "Sacral": "#F4A261",
    "Solar Plexus": "#E9C46A",
    "Heart": "#34A853",
    "Throat": "#4285F4",
    "Third Eye": "#7E57C2",
    "Crown": "#B39DDB",
}

# MyAuraBliss crystal recommendations
MYAURABLISS = {
    "Root": ["Red Jasper", "Hematite", "Black Tourmaline"],
    "Sacral": ["Carnelian", "Orange Calcite", "Moonstone"],
    "Solar Plexus": ["Citrine", "Tiger's Eye", "Yellow Aventurine"],
    "Heart": ["Rose Quartz", "Green Aventurine", "Malachite"],
    "Throat": ["Sodalite", "Blue Apatite", "Aquamarine"],
    "Third Eye": ["Amethyst", "Lapis Lazuli", "Lepidolite"],
    "Crown": ["Clear Quartz", "Amethyst", "Selenite"],
}

# ------------------------- HELPERS ------------------------------
def dot_radio(key: str, default: int = 4) -> int:
    """Render a horizontal 1..7 radio that looks like dots (CSS)."""
    # NOTE: we pass labels "1".."7", but CSS hides the text and shows the dot.
    options = list(range(1, 8))
    idx = options.index(default) if key not in st.session_state else options.index(st.session_state.get(key, default))
    val = st.radio("", options=options, index=idx, key=f"_radio_{key}", horizontal=True, label_visibility="collapsed")
    # Keep a simple mirror in session_state for convenience if you need it elsewhere
    st.session_state[key] = val
    return val

@st.cache_data
def score_personality(items_with_scores: List[Tuple[Item, int]]) -> Dict[str, float]:
    # Map 1..7 to -3..+3 scale so midpoint = 0
    trait_values: Dict[str, List[float]] = {t: [] for t in list("OCEAN")}
    for item, raw in items_with_scores:
        val = (raw - 4)  # -3..+3
        if item.reverse:
            val = -val
        trait_values[item.trait].append(val)
    return {t: float(np.mean(v)) if v else 0.0 for t, v in trait_values.items()}

@st.cache_data
def summarize_trait(name: str, score: float) -> str:
    bands = [(-3,-1.6,"Low"), (-1.6,-0.5,"Below Average"), (-0.5,0.5,"Balanced"), (0.5,1.6,"High"), (1.6,3.1,"Very High")]
    label = next(lbl for lo,hi,lbl in bands if lo <= score < hi)
    blurbs = {
        "O": {
            "Low": "Prefers the familiar and practical; try gentle novelty and creative play.",
            "Below Average": "Enjoys practical ideas; add small exploration rituals.",
            "Balanced": "Healthy mix of curiosity and pragmatism.",
            "High": "Imaginative and future-focused; ground ideas into plans.",
            "Very High": "Visionary; pair with structure to ship work.",
        },
        "C": {
            "Low": "Flexible but may be scattered; create simple routines and checklists.",
            "Below Average": "Works in bursts; benefit from 2–3 anchor habits.",
            "Balanced": "Good balance of flow and discipline.",
            "High": "Organized and reliable; watch perfectionism.",
            "Very High": "Highly structured; schedule play and rest.",
        },
        "E": {
            "Low": "Quiet and reflective; protect energy in groups.",
            "Below Average": "Selective with social energy; plan 1:1s.",
            "Balanced": "Comfortable alone or in company.",
            "High": "Outgoing; include solitude for recharge.",
            "Very High": "Highly social; schedule deep-focus windows.",
        },
        "A": {
            "Low": "Direct and independent; add empathy practices.",
            "Below Average": "Honest yet firm; practice active listening.",
            "Balanced": "Warm and fair-minded.",
            "High": "Kind and cooperative; hold boundaries.",
            "Very High": "Very accommodating; protect your needs too.",
        },
        "N": {
            "Low": "Calm and steady.",
            "Below Average": "Usually grounded; stress spikes sometimes.",
            "Balanced": "Healthy awareness of feelings.",
            "High": "Sensitive to stress; build soothing rituals.",
            "Very High": "Intensely reactive; prioritize nervous-system care.",
        },
    }
    return f"**{label}** – {blurbs.get(name, {}).get(label, '')}"

@st.cache_data
def score_chakras(scores: Dict[str, List[int]]) -> Dict[str, float]:
    return {k: float(np.mean(v)) if v else 0.0 for k, v in scores.items()}

def chakra_status(val: float) -> str:
    return "Balanced" if 3.8 <= val <= 5.8 else ("Overactive" if val > 5.8 else "Blocked")

def chakra_remedy_block(status: str, chakra: str) -> str:
    remedies = {
        "Root": "Grounding walk barefoot, 4-7-8 breathing, red foods.",
        "Sacral": "Creative play, water ritual, forgiveness journal.",
        "Solar Plexus": "Power postures, small wins list, daily ‘No’.",
        "Heart": "Loving-kindness meditation, gratitude letters.",
        "Throat": "Humming/singing, write and read your needs.",
        "Third Eye": "10-min visualization, dream notes, screen-light limits at night.",
        "Crown": "Morning silence, seva, study a wisdom text.",
    }
    crystals = ", ".join(MYAURABLISS.get(chakra, []))
    return f"{status}: {remedies.get(chakra,'')}  •  Crystals: {crystals}"

# ------------------------- FORM RENDERING ------------------------------
st.header("Part 1 · Personality")
st.caption("From each pair, choose the one that describes you best. 1 = left, 7 = right.")

responses: List[Tuple[Item, int]] = []
for idx, item in enumerate(PERSONALITY_ITEMS, start=1):
    with st.container():
        st.markdown(f"<div class='item-row'>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='labels'><span>{item.left}</span><span>{item.right}</span></div>",
            unsafe_allow_html=True,
        )
        val = dot_radio(f"q{idx}", 4)
        st.markdown("</div>", unsafe_allow_html=True)
        responses.append((item, val))

st.markdown(
    "<div class='aura-box'><b>Benefits</b>: Instant insights, chakra remedies, and a branded PDF report for your clients. ✅</div>",
    unsafe_allow_html=True,
)

st.divider()
st.header("Part 2 · Chakra Scan")
st.caption("Rate each statement (1 = Strongly Disagree, 7 = Strongly Agree). Higher is healthier.")

chakra_scores: Dict[str, List[int]] = {name: [] for name in CHAKRA_QUESTIONS}
for chakra, qs in CHAKRA_QUESTIONS.items():
    st.subheader(chakra)
    for i, q in enumerate(qs, start=1):
        with st.container():
            st.write(q)
            val = dot_radio(f"{chakra}_{i}", 4)
        chakra_scores[chakra].append(val)
    st.markdown("---")

# ----------------------- RESULTS + PDF --------------------------------
if st.button("📊 Calculate Results", type="primary"):
    trait_scores = score_personality(responses)
    chakra_avg   = score_chakras(chakra_scores)

    st.subheader("Personality Summary (Big Five style)")
    df_traits = pd.DataFrame({"Trait": list(trait_scores.keys()),
                              "Score (-3..+3)": list(trait_scores.values())})
    st.dataframe(df_traits, use_container_width=True)
    for t, s in trait_scores.items():
        st.markdown(f"**{t}**: {summarize_trait(t, s)}")

    st.subheader("Chakra Status (1–7)")
    df_ch = pd.DataFrame({"Chakra": list(chakra_avg.keys()),
                          "Avg": list(chakra_avg.values())}).sort_values("Chakra")
    st.dataframe(df_ch, use_container_width=True)

    st.markdown("#### Remedies & Tips")
    for ch, val in chakra_avg.items():
        color = CHAKRA_COLORS.get(ch, "#666")
        chip  = f"<span class='chip' style='background:{color};padding:4px 10px;border-radius:999px;color:#fff;font-size:12px;margin-right:6px'>{ch}</span>"
        status = chakra_status(val)
        advice = chakra_remedy_block(status, ch)
        st.markdown(chip + f" **{status}** · Avg {val:.1f} — {advice}", unsafe_allow_html=True)

    # ---------------------- PDF BUILD ----------------------
    def build_pdf(traits: Dict[str, float], chakras: Dict[str, float], logo_bytes: Optional[bytes]) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        # Header with logo if available
        if logo_bytes:
            try:
                logo_io = io.BytesIO(logo_bytes)
                story.append(Image(logo_io, width=80, height=80))
            except Exception:
                pass

        def h(txt):  # Title style
            return Paragraph(f"<para align='center'><font face='Playfair Display'><b>{txt}</b></font></para>", styles["Title"])

        # Page 1: Personality Overview
        story.append(h("Personality Profile (Big Five style)"))
        story.append(Spacer(1, 12))
        data = [["Trait", "Score (-3..+3)", "Summary"]]
        for t, s in traits.items():
            data.append([t, f"{s:.2f}", summarize_trait(t, s)])
        table = Table(data, colWidths=[3*cm, 4*cm, 9*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EDE7F6")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#311B92")),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))
        story.append(Paragraph("Scores are centered at 0 (balanced). Higher/lower describe tendencies, not limits.", styles["Normal"]))

        # Page 2: Personality Tips
        story.append(Spacer(1, 36))
        story.append(Paragraph("<b>Growth Suggestions</b>", styles["Heading2"]))
        tips = [
            "Pair high Openness with weekly shipping goals.",
            "Support low Conscientiousness with two anchor habits (sleep window, 30-min focus).",
            "If Extraversion is high, book solo reflection blocks; if low, plan 1 meaningful social slot.",
            "Balance Agreeableness with clear boundaries.",
        ]
        for t in tips:
            story.append(Paragraph(f"• {t}", styles["Normal"]))

        # Pages 3–5: Chakras
        def chakra_table(title: str, subset: List[Tuple[str, float]]):
            story.append(Spacer(1, 24))
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            data = [["Chakra", "Avg (1–7)", "Status", "MyAuraBliss Crystals", "Remedy"]]
            for ch, val in subset:
                status = chakra_status(val)
                crystals = ", ".join(MYAURABLISS.get(ch, []))
                data.append([ch, f"{val:.1f}", status, crystals, chakra_remedy_block(status, ch)])
            tbl = Table(data, colWidths=[3*cm, 2.7*cm, 3*cm, 5*cm, 4*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EAF6")),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ]))
            story.append(tbl)

        ch_items = list(chakras.items())
        chakra_table("Chakra Scan — Part 1", ch_items[:3])
        chakra_table("Chakra Scan — Part 2", ch_items[3:5])
        chakra_table("Chakra Scan — Part 3", ch_items[5:])

        doc.build(story)
        return buf.getvalue()

    logo_bytes = None
    if logo_file is not None:
        logo_bytes = logo_file.getbuffer().tobytes()

    pdf_bytes = build_pdf(trait_scores, chakra_avg, logo_bytes)
    st.download_button(
        "📄 Download Full Report (PDF)",
        data=pdf_bytes,
        file_name="personality_chakra_report.pdf",
        mime="application/pdf",
    )

# ------------------------ Footer Notes ---------------------------------
st.markdown(
    "<p style='text-align:center;color:#6E3CBC;font-family:Poppins;font-size:13px;'>"
    "© Soulful Academy — Created with love & light ✨"
    "</p>",
    unsafe_allow_html=True
)
