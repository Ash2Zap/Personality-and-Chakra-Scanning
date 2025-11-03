# app.py — Personality + Chakra Scan (Streamlit Cloud–safe)
# ------------------------------------------------------------
# • No JS hacks. Radio-as-dots via CSS only (stable on Cloud)
# • Public-domain Big Five–style items (IPIP-inspired)
# • Chakra scan (7×3 items) + MyAuraBliss crystal tips
# • 5-page PDF: 2 pages Personality + 3 pages Chakras (forced breaks)
# • Soulful Academy theme + optional logo in UI and PDF

import io
import base64
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image, PageBreak
)

# ---------------------------- BRAND THEME ---------------------------------
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE  = "#6E3CBC"
LAVENDER       = "#D9B2FF"
SOFT_GOLD_BG   = "#FFE6D9"
CTA_GOLD_1     = "#FFD86F"
CTA_GOLD_2     = "#FFB347"
TEXT_VIOLET    = "#2D033B"

st.set_page_config(page_title="Personality + Chakra Scan", page_icon="🔮", layout="centered")

CUSTOM_HEAD = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@800&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
<style>
body {{ background: linear-gradient(135deg, {LAVENDER}, {SOFT_GOLD_BG}); }}
section.main > div {{ max-width: 980px; }}
:root {{ --accent:{ACCENT_PURPLE}; --purple:{PRIMARY_PURPLE}; --violet:{TEXT_VIOLET}; }}

/* Header */
.header-band {{
  background: linear-gradient(90deg, var(--accent), var(--purple));
  color:#fff; padding:22px 24px; border-radius:16px; margin-bottom:18px;
  box-shadow:0 12px 36px rgba(78,0,130,.35); border:1px solid rgba(255,255,255,.15);
  position:relative; overflow:hidden;
}}
.header-band h1 {{
  margin:0; font-family:'Playfair Display',serif; letter-spacing:.6px; font-weight:800;
  text-transform:uppercase; text-shadow:0 0 10px rgba(255,255,255,.2);
}}
.header-band p {{ margin:6px 0 0 0; opacity:.95; font-family:'Poppins',sans-serif; }}
.header-logo {{ position:absolute; right:18px; top:14px; width:84px; height:84px; border-radius:12px;
  box-shadow:0 8px 22px rgba(0,0,0,.2); background-size:cover; background-position:center; }}

/* Cards */
.item-row {{ border:1px solid #f0dffb; border-left:6px solid var(--accent); border-radius:14px; padding:12px 14px; margin-bottom:12px; background:#fff; }}
.left-label, .right-label {{ font-size:14px; color:#5a4a72; font-family:'Poppins',sans-serif; line-height:1.35; }}

/* Radio as dots */
.stRadio > div {{ display:flex; gap:10px; }}
.stRadio div[role='radiogroup'] {{ display:flex; gap:10px; justify-content:center; }}
.stRadio input[type="radio"] {{ opacity:0; width:0; height:0; position:absolute; }}
.stRadio label {{
  width:20px; height:20px; border-radius:50%;
  border:2px solid var(--accent); cursor:pointer;
  display:inline-flex; align-items:center; justify-content:center;
  color:transparent !important; /* hide 1..7 text */
}}
.stRadio label:hover {{ transform:scale(1.08); }}
.stRadio input[type="radio"]:checked + div > span::after,
.stRadio input[type="radio"]:checked + span::after {{
  content:""; width:10px; height:10px; background:var(--purple); border-radius:50%; position:absolute;
}}

/* CTA */
.stButton > button {{
  background:linear-gradient(135deg,{CTA_GOLD_1},{CTA_GOLD_2});
  color:{PRIMARY_PURPLE}; border:none; font-weight:700; border-radius:999px; padding:10px 20px;
  box-shadow:0 10px 24px rgba(255,184,71,.35); font-family:'Poppins',sans-serif; text-transform:uppercase; letter-spacing:.4px;
}}

/* Aura box */
.aura-box {{ position:relative; padding:18px; border-radius:16px; background:#ffffffcc; border:1px solid #f0dffb; margin:10px 0 18px; }}
.aura-box::before {{ content:''; position:absolute; inset:-40px; z-index:-1;
  background: radial-gradient(closest-side, rgba(110,60,188,.30), transparent 70%),
              radial-gradient(closest-side, rgba(255,216,111,.25), transparent 70%);
  filter: blur(20px); }}

html, body, p, div, span {{ font-family:'Poppins',sans-serif; color:{TEXT_VIOLET}; }}
</style>
"""
st.markdown(CUSTOM_HEAD, unsafe_allow_html=True)

# ---------------------------- HEADER ---------------------------------
logo_file = st.file_uploader("Upload your Soulful Academy logo (PNG/JPG)", type=["png","jpg","jpeg"])
logo_bytes: Optional[bytes] = None
logo_style = ""
if logo_file is not None:
    logo_bytes = logo_file.getvalue()
    mime = logo_file.type or "image/png"
    b64  = base64.b64encode(logo_bytes).decode("utf-8")
    logo_style = f"<div class='header-logo' style=\"background-image:url(data:{mime};base64,{b64})\"></div>"

st.markdown(f"""
<div class='header-band'>
  <h1>🔮 Personality + Chakra Scan</h1>
  <p>Choose the option that fits you best for each pair. Then download your combined report.</p>
  {logo_style}
</div>
""", unsafe_allow_html=True)

# ------------------------- DATA DEFINITIONS ----------------------------
@dataclass
class Item:
    left: str
    right: str
    trait: str  # O C E A N
    reverse: bool = False

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

MYAURABLISS = {
    "Root": ["Red Jasper", "Hematite", "Black Tourmaline"],
    "Sacral": ["Carnelian", "Orange Calcite", "Moonstone"],
    "Solar Plexus": ["Citrine", "Tiger's Eye", "Yellow Aventurine"],
    "Heart": ["Rose Quartz", "Green Aventurine", "Malachite"],
    "Throat": ["Sodalite", "Blue Apatite", "Aquamarine"],
    "Third Eye": ["Amethyst", "Lapis Lazuli", "Lepidolite"],
    "Crown": ["Clear Quartz", "Amethyst", "Selenite"],
}

# ------------------------- RADIO-AS-DOTS ------------------------------
def dot_radio(key: str, default: int = 4) -> int:
    opts = list(range(1,8))
    idx = opts.index(st.session_state.get(key, default))
    v = st.radio("", opts, index=idx, key=f"_r_{key}", horizontal=True, label_visibility="collapsed")
    st.session_state[key] = v
    return v

# ------------------------- FORM RENDERING ------------------------------
st.header("Part 1 · Personality")
st.caption("From each pair, choose the one that describes you best. 1 = left, 7 = right.")

responses: List[Tuple[Item, int]] = []
for i, item in enumerate(PERSONALITY_ITEMS, start=1):
    st.markdown("<div class='item-row'>", unsafe_allow_html=True)
    lcol, rcol = st.columns(2)
    with lcol:  st.markdown(f"<div class='left-label'>{item.left}</div>", unsafe_allow_html=True)
    with rcol:  st.markdown(f"<div class='right-label' style='text-align:right'>{item.right}</div>", unsafe_allow_html=True)
    responses.append((item, dot_radio(f"q{i}", 4)))
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='aura-box'><b>Benefits</b>: Instant insights, chakra remedies, and a branded PDF report for your clients. ✅</div>", unsafe_allow_html=True)

st.divider()
st.header("Part 2 · Chakra Scan")
st.caption("Rate each statement (1 = Strongly Disagree, 7 = Strongly Agree). Higher is healthier.")

chakra_scores: Dict[str, List[int]] = {k: [] for k in CHAKRA_QUESTIONS}
for ch, qs in CHAKRA_QUESTIONS.items():
    st.subheader(ch)
    for j, q in enumerate(qs, start=1):
        st.write(q)
        chakra_scores[ch].append(dot_radio(f"{ch}_{j}", 4))
    st.markdown("---")

# ----------------------- SCORING & SUMMARIES ---------------------------
@st.cache_data
def score_personality(items: List[Tuple[Item, int]]) -> Dict[str, float]:
    vals: Dict[str, List[float]] = {t: [] for t in "OCEAN"}
    for it, raw in items:
        v = (raw - 4)  # -3..+3 center
        if it.reverse: v = -v
        vals[it.trait].append(v)
    return {t: float(np.mean(v)) if v else 0.0 for t, v in vals.items()}

@st.cache_data
def summarize_trait(name: str, score: float) -> str:
    bands = [(-3,-1.6,"Low"), (-1.6,-0.5,"Below Average"), (-0.5,0.5,"Balanced"), (0.5,1.6,"High"), (1.6,3.1,"Very High")]
    label = next(lbl for lo,hi,lbl in bands if lo <= score < hi)
    notes = {
        "O": {"Low":"Prefer the familiar; add gentle novelty.", "Below Average":"Practical; add small explorations.", "Balanced":"Curiosity + pragmatism.", "High":"Imaginative; ground ideas.", "Very High":"Visionary; add structure."},
        "C": {"Low":"Flexible; add routines.", "Below Average":"Works in bursts; create anchors.", "Balanced":"Flow + discipline.", "High":"Organized; watch perfectionism.", "Very High":"Very structured; schedule play."},
        "E": {"Low":"Reflective; protect energy.", "Below Average":"Selective socially; plan 1:1s.", "Balanced":"Ok alone or with people.", "High":"Outgoing; include solitude.", "Very High":"Very social; block deep focus."},
        "A": {"Low":"Direct; add empathy.", "Below Average":"Honest; practice listening.", "Balanced":"Warm and fair.", "High":"Kind; hold boundaries.", "Very High":"Accommodating; protect needs."},
        "N": {"Low":"Calm and steady.", "Below Average":"Usually grounded.", "Balanced":"Healthy awareness.", "High":"Sensitive to stress; soothe.", "Very High":"Reactive; nervous-system care."},
    }
    return f"**{label}** – {notes.get(name, {}).get(label, '')}"

@st.cache_data
def score_chakras(scores: Dict[str, List[int]]) -> Dict[str, float]:
    return {k: float(np.mean(v)) if v else 0.0 for k, v in scores.items()}

def chakra_status(v: float) -> str:
    return "Balanced" if 3.8 <= v <= 5.8 else ("Overactive" if v > 5.8 else "Blocked")

def chakra_remedy_block(status: str, chakra: str) -> str:
    base = {
        "Root": "Grounding walk barefoot, 4-7-8 breathing, red foods.",
        "Sacral": "Creative play, water ritual, forgiveness journal.",
        "Solar Plexus": "Power postures, small wins list, daily ‘No’.",
        "Heart": "Loving-kindness meditation, gratitude letters.",
        "Throat": "Humming/singing, write and read your needs.",
        "Third Eye": "10-min visualization, dream notes, less night screen-light.",
        "Crown": "Morning silence, seva, read a wisdom text.",
    }.get(chakra, "")
    crystals = ", ".join(MYAURABLISS.get(chakra, []))
    return f"{status}: {base}  •  Crystals: {crystals}"

# ----------------------- RESULTS + PDF --------------------------------
if st.button("📊 Calculate Results", type="primary"):
    trait_scores = score_personality(responses)
    chakra_avg   = score_chakras(chakra_scores)

    st.subheader("Personality Summary (Big Five style)")
    st.dataframe(pd.DataFrame({"Trait": list(trait_scores.keys()), "Score (-3..+3)": list(trait_scores.values())}), use_container_width=True)
    for t, s in trait_scores.items():
        st.markdown(f"**{t}**: {summarize_trait(t, s)}")

    st.subheader("Chakra Status (1–7)")
    st.dataframe(pd.DataFrame({"Chakra": list(chakra_avg.keys()), "Avg": list(chakra_avg.values())}).sort_values("Chakra"), use_container_width=True)

    st.markdown("#### Remedies & Tips")
    for ch, v in chakra_avg.items():
        chip = f"<span style='background:{CHAKRA_COLORS.get(ch,'#666')};color:#fff;padding:4px 10px;border-radius:999px;font-size:12px;margin-right:6px'>{ch}</span>"
        st.markdown(chip + f" **{chakra_status(v)}** · Avg {v:.1f} — {chakra_remedy_block(chakra_status(v), ch)}", unsafe_allow_html=True)

    # ---------------------- PDF BUILD ----------------------
    def build_pdf(traits: Dict[str, float], chakras: Dict[str, float], logo_bytes: Optional[bytes]) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        if logo_bytes:
            try:
                story.append(Image(io.BytesIO(logo_bytes), width=80, height=80))
                story.append(Spacer(1, 6))
            except Exception:
                pass

        def title(txt: str):
            # Use built-in font (Helvetica) to avoid ReportLab mapping errors
            return Paragraph(f"<para align='center'><b>{txt}</b></para>", styles["Title"])

        # Page 1: Personality Overview
        story.append(title("Personality Profile (Big Five style)"))
        story.append(Spacer(1, 12))
        pdata = [["Trait", "Score (-3..+3)", "Summary"]]
        for t, s in traits.items():
            pdata.append([t, f"{s:.2f}", summarize_trait(t, s)])
        ptable = Table(pdata, colWidths=[3*cm, 4*cm, 9*cm])
        ptable.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EDE7F6")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#311B92")),
            ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
        ]))
        story.append(ptable)
        story.append(Spacer(1, 24))
        story.append(Paragraph("Scores are centered at 0 (balanced). Higher/lower describe tendencies, not limits.", styles["Normal"]))

        story.append(PageBreak())  # Force Page 1 end

        # Page 2: Personality Tips
        story.append(title("Growth Suggestions"))
        tips = [
            "Pair high Openness with weekly shipping goals.",
            "Support low Conscientiousness with two anchor habits (sleep window, 30-min focus).",
            "If Extraversion is high, book solo reflection; if low, plan one meaningful social slot.",
            "Balance Agreeableness with clear boundaries.",
        ]
        for t in tips:
            story.append(Paragraph("• " + t, styles["Normal"]))

        story.append(PageBreak())  # Force Page 2 end

        # Pages 3–5: Chakras in 3 parts
        ch_items = list(chakras.items())

        def chakra_table(title_txt: str, subset: List[Tuple[str, float]]):
            story.append(Paragraph(f"<b>{title_txt}</b>", styles["Heading2"]))
            data = [["Chakra", "Avg (1–7)", "Status", "MyAuraBliss Crystals", "Remedy"]]
            for ch, val in subset:
                stat = chakra_status(val)
                crystals = ", ".join(MYAURABLISS.get(ch, []))
                data.append([ch, f"{val:.1f}", stat, crystals, chakra_remedy_block(stat, ch)])
            tbl = Table(data, colWidths=[3*cm, 2.7*cm, 3*cm, 5*cm, 4*cm])
            tbl.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8EAF6")),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID", (0,0), (-1,-1), 0.25, colors.grey),
            ]))
            story.append(tbl)

        chakra_table("Chakra Scan — Part 1", ch_items[:3])
        story.append(PageBreak())
        chakra_table("Chakra Scan — Part 2", ch_items[3:5])
        story.append(PageBreak())
        chakra_table("Chakra Scan — Part 3", ch_items[5:])

        doc.build(story)
        return buf.getvalue()

    pdf_bytes = build_pdf(trait_scores, chakra_avg, logo_bytes)
    st.download_button("📄 Download Full Report (PDF)", data=pdf_bytes, file_name="personality_chakra_report.pdf", mime="application/pdf")
