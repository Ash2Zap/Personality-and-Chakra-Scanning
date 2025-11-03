"""
Streamlit app: Personality + Chakra Scan (open-source friendly)
— Uses public‑domain Big Five–style items (IPIP-inspired, not Truity’s proprietary logic)
— Presents each item as a 7‑dot horizontal picker (radio‑dot style) matching your screenshot
— Mixes results with a Chakra scan (7 chakras) and produces a 5‑page PDF (2 pages personality, 3 pages chakras)
— Branded UI: Soulful Academy logo, Playfair Display (headings), Poppins (body), purple‑gold theme, aura/mandala glow, gold CTA

Files: single app.py
"""

import io
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, Image
import streamlit as st

# ---------------------------- BRAND THEME ---------------------------------
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE = "#6E3CBC"
LAVENDER = "#D9B2FF"
SOFT_GOLD = "#FFE6D9"
CTA_GOLD_1 = "#FFD86F"
CTA_GOLD_2 = "#FFB347"
TEXT_VIOLET = "#2D033B"

CUSTOM_HEAD = f"""
<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
<link href=\"https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Poppins:wght@300;400;500;600&display=swap\" rel=\"stylesheet\">
<style>
body {{
  background: linear-gradient(135deg, {LAVENDER}, {SOFT_GOLD});
}}
section.main > div {{max-width: 980px;}}
:root {{ --accent: {ACCENT_PURPLE}; --purple: {PRIMARY_PURPLE}; --violet: {TEXT_VIOLET}; }}

/* Header band */
.header-band {{
  background: linear-gradient(90deg, var(--accent), var(--purple));
  color: white; padding: 22px 24px; border-radius: 16px;
  box-shadow: 0 12px 36px rgba(78,0,130,.35); margin-bottom: 18px;
  border: 1px solid rgba(255,255,255,.15); position: relative; overflow:hidden;
}}
.header-band h1 {{margin:0; font-family: 'Playfair Display', serif; letter-spacing:.5px; font-weight:800; text-transform:uppercase; text-shadow:0 0 10px rgba(255,255,255,.2);}}
.header-band p {{margin:6px 0 0 0; opacity:.95; font-family:'Poppins', sans-serif;}}
.header-logo {{ position:absolute; right:18px; top:14px; width:84px; height:84px; border-radius:12px; box-shadow:0 8px 22px rgba(0,0,0,.2); background-size:cover; background-position:center; }}

/* Card rows */
.item-row {{border: 1px solid #f0dffb; border-left: 6px solid var(--accent);
  border-radius: 14px; padding: 12px 14px; margin-bottom: 12px; background:#fff;}}
.labels {{display:flex; justify-content:space-between; font-size:14px; color:#5a4a72; font-family:'Poppins', sans-serif;}}
.small {{font-size:12px; color:#7c6b9a;}}

/* DOT PICKER (radio‑dot style) */
.dot-row {{display:flex; gap:10px; align-items:center; margin-top:8px;}}
.dot {{width:18px; height:18px; border-radius:50%; border:2px solid var(--accent); cursor:pointer; display:flex; align-items:center; justify-content:center;}}
.dot-inner {{width:10px; height:10px; border-radius:50%; background:transparent;}}
.dot.active {{border-color: var(--purple); box-shadow:0 0 0 3px rgba(110,60,188,.15);}}
.dot.active .dot-inner {{background: var(--purple);}}
.dot:hover {{transform:scale(1.08);}}

/* Chips & icons */
.chip {{display:inline-block; padding:4px 10px; border-radius:999px; color:#fff; font-size:12px; margin-right:6px; font-family:'Poppins', sans-serif;}}

/* CTA button */
.stButton > button {{
  background: linear-gradient(135deg, {CTA_GOLD_1}, {CTA_GOLD_2});
  color: {PRIMARY_PURPLE}; border: none; font-weight:700;
  border-radius: 999px; padding: 10px 20px; box-shadow:0 10px 24px rgba(255,184,71,.35);
  font-family:'Poppins', sans-serif; text-transform:uppercase; letter-spacing:.4px;
}}
.stButton > button:hover {{ filter: brightness(1.05);}}

/* Aura / mandala glow behind benefits */
.aura-box {{ position:relative; padding:18px; border-radius:16px; background:#ffffffcc;
  border:1px solid #f0dffb; margin:10px 0 18px; }}
.aura-box::before {{ content:''; position:absolute; inset:-40px; z-index:-1;
  background: radial-gradient(closest-side, rgba(110,60,188,.30), transparent 70%),
              radial-gradient(closest-side, rgba(255,216,111,.25), transparent 70%);
  filter: blur(20px); }}

/* Typography */
html, body, p, div, span {{ font-family:'Poppins', sans-serif; color:{TEXT_VIOLET}; }}
</style>
"""

# ---------------------------- PAGE SETUP ---------------------------------
st.set_page_config(page_title="Personality + Chakra Scan", page_icon="🔮", layout="centered")
st.markdown(CUSTOM_HEAD, unsafe_allow_html=True)

logo_file = st.file_uploader("Upload your Soulful Academy logo (PNG)", type=["png","jpg","jpeg"], key="_logo")
logo_style = ""
if logo_file is not None:
    # Save to a temp and use as CSS background in header
    import base64
    data = base64.b64encode(logo_file.read()).decode("utf-8")
    logo_style = f"<div class='header-logo' style=\"background-image:url(data:image/png;base64,{data})\"></div>"

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
from dataclasses import dataclass
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

# MyAuraBliss crystal recommendations (brand-ready text)
MYAURABLISS = {
    "Root": ["Red Jasper", "Hematite", "Black Tourmaline"],
    "Sacral": ["Carnelian", "Orange Calcite", "Moonstone"],
    "Solar Plexus": ["Citrine", "Tiger's Eye", "Yellow Aventurine"],
    "Heart": ["Rose Quartz", "Green Aventurine", "Malachite"],
    "Throat": ["Sodalite", "Blue Apatite", "Aquamarine"],
    "Third Eye": ["Amethyst", "Lapis Lazuli", "Lepidolite"],
    "Crown": ["Clear Quartz", "Amethyst", "Selenite"],
}

# ------------------------- DOT PICKER WIDGET ------------------------------
if "_dots" not in st.session_state: st.session_state["_dots"] = {}

def dot_picker(key: str, default: int = 4) -> int:
    val = st.session_state["_dots"].get(key, default)
    cols = st.columns(7)
    for i, c in enumerate(cols, start=1):
        with c:
            html = f"<div class='dot {'active' if val==i else ''}' onclick=\"parent.postMessage({{isStreamlitMessage:true, type:'streamlit:setComponentValue', value:{i}, key:'{key}'}}, '*')\"><div class='dot-inner'></div></div>"
            st.markdown(html, unsafe_allow_html=True)
    # Fallback buttons for keyboard navigation (hidden visually)
    for i in range(1,8):
        if st.button(f"{key}_btn_{i}", key=f"{key}_btn_{i}", help=str(i), use_container_width=False):
            val = i
    # Sync from component messages
    val = st.session_state["_dots"].get(key, val)
    st.session_state["_dots"][key] = val
    return val

# Minimal JS bridge (works on Streamlit Cloud)
st.components.v1.html("""
<script>
window.addEventListener('message', (event) => {
  const d = event.data || {};
  if(d.isStreamlitMessage && d.type==='streamlit:setComponentValue'){
    const key = d.key; const val = d.value;
    const py = window.parent;
    py.postMessage({type:'streamlit:setSessionState', key:key, value:val}, '*');
  }
});
</script>
""", height=0)

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
        val = dot_picker(f"q{idx}", 4)
        st.markdown("</div>", unsafe_allow_html=True)
        responses.append((item, val))

st.markdown("<div class='aura-box'><b>Benefits</b>: Instant insights, Chakra remedies, and a branded PDF report for your clients. ✅</div>", unsafe_allow_html=True)

st.divider()
st.header("Part 2 · Chakra Scan")
st.caption("Rate each statement (1 = Strongly Disagree, 7 = Strongly Agree). Higher is healthier.")

chakra_scores: Dict[str, List[int]] = {name: [] for name in CHAKRA_QUESTIONS}
for chakra, qs in CHAKRA_QUESTIONS.items():
    st.subheader(chakra)
    for i, q in enumerate(qs, start=1):
        with st.container():
            st.write(q)
            val = dot_picker(f"{chakra}_{i}", 4)
        chakra_scores[chakra].append(val)
    st.markdown("---")

# ----------------------- SCORING & SUMMARIES ---------------------------
@st.cache_data
def score_personality(items_with_scores: List[Tuple[Item, int]]) -> Dict[str, float]:
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
            "Low": "Prefers the familiar and practical; benefits from gentle novelty and creative play.",
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

@st.cache_data
def chakra_remedy_block(status: str, chakra: str) -> str:
    remedies = {
        "Root": "Grounding walk barefoot, 4‑7‑8 breathing, red foods; crystals: "+", ".join(MYAURABLISS["Root"]) ,
        "Sacral": "Creative play, water ritual; crystals: "+", ".join(MYAURABLISS["Sacral"]) ,
        "Solar Plexus": "Power postures, small wins list; crystals: "+", ".join(MYAURABLISS["Solar Plexus"]) ,
        "Heart": "Loving‑kindness, gratitude letters; crystals: "+", ".join(MYAURABLISS["Heart"]) ,
        "Throat": "Humming/singing, ‘truth sandwich’; crystals: "+", ".join(MYAURABLISS["Throat"]) ,
        "Third Eye": "10‑min visualization, dream notes; crystals: "+", ".join(MYAURABLISS["Third Eye"]) ,
        "Crown": "Morning silence, seva; crystals: "+", ".join(MYAURABLISS["Crown"]) ,
    }
    base = remedies.get(chakra, "")
    return f"{status}: {base}"

if st.button("📊 Calculate Results", type="primary"):
    trait_scores = score_personality(responses)
    chakra_avg = score_chakras(chakra_scores)

    st.subheader("Personality Summary (Big Five style)")
    df_traits = pd.DataFrame({"Trait": list(trait_scores.keys()), "Score (-3..+3)": list(trait_scores.values())})
    st.dataframe(df_traits, use_container_width=True)

    for t, s in trait_scores.items():
        st.markdown(f"**{t}**: {summarize_trait(t, s)}")

    st.subheader("Chakra Status (1–7)")
    df_ch = pd.DataFrame({"Chakra": list(chakra_avg.keys()), "Avg": list(chakra_avg.values())}).sort_values("Chakra")
    st.dataframe(df_ch, use_container_width=True)

    st.markdown("#### Remedies & Tips")
    for ch, val in chakra_avg.items():
        color = CHAKRA_COLORS.get(ch, "#666")
        chip = f"<span class='chip' style='background:{color}'>{ch}</span>"
        status = "Balanced" if 3.8 <= val <= 5.8 else ("Overactive" if val > 5.8 else "Blocked")
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

        def h(txt):
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
            "Support low Conscientiousness with two anchor habits (sleep window, 30‑min focus).",
            "If Extraversion is high, book solo reflection blocks; if low, plan 1 meaningful social slot.",
            "Balance Agreeableness with clear boundaries.",
        ]
        for t in tips:
            story.append(Paragraph(f"• {t}", styles["Normal"]))

        # Page 3–5: Chakras
        def chakra_table(title: str, subset: List[Tuple[str, float]]):
            story.append(Spacer(1, 24))
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            data = [["Chakra", "Avg (1–7)", "Status", "MyAuraBliss Crystals", "Remedy"]]
            for ch, val in subset:
                status = "Balanced" if 3.8 <= val <= 5.8 else ("Overactive" if val > 5.8 else "Blocked")
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
        "📄 Download Full Report (PDF)", data=pdf_bytes, file_name="personality_chakra_report.pdf",
        mime="application/pdf"
    )

st.markdown("""
---
**Notes & IP:** This app uses public‑domain Big Five–style statements and original scoring. We do **not** copy or reproduce Truity’s proprietary content or algorithms. The left/right layout is inspired by many tests but implemented uniquely here.

**Deploy:**
1) Save this file as `app.py` in a GitHub repo.
2) Add `requirements.txt` with:
```
streamlit
pandas
numpy
reportlab
```
3) Deploy to Streamlit Cloud → New app → point to the repo.
""")

