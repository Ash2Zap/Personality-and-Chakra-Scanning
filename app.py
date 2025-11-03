# app.py — Personality + Chakra Scan (Lite, no CSS printing)
# - Minimal CSS (properly enclosed in <style> + unsafe_allow_html=True)
# - Centered radio dots (pure CSS)
# - Logo in header + PDF
# - 5-page PDF with PageBreaks

import io, base64
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

# ---- THEME ----
PRIMARY_PURPLE = "#4B0082"
ACCENT_PURPLE  = "#6E3CBC"
LAVENDER       = "#D9B2FF"
SOFT_GOLD_BG   = "#FFE6D9"
CTA_GOLD_1     = "#FFD86F"
CTA_GOLD_2     = "#FFB347"
TEXT_VIOLET    = "#2D033B"

st.set_page_config(page_title="Personality + Chakra Scan", page_icon="🔮", layout="centered")

# IMPORTANT: wrap CSS inside <style> and set unsafe_allow_html=True
st.markdown(f"""
<style>
/* Minimal styles only */
body {{ background: linear-gradient(135deg, {LAVENDER}, {SOFT_GOLD_BG}); }}
section.main > div {{ max-width: 980px; }}
:root {{ --accent:{ACCENT_PURPLE}; --purple:{PRIMARY_PURPLE}; --violet:{TEXT_VIOLET}; }}
html, body, p, div, span {{ color:{TEXT_VIOLET}; font-family: ui-sans-serif, -apple-system, Segoe UI, Roboto, Arial; }}

/* Header band */
.header-band {{
  background: linear-gradient(90deg, var(--accent), var(--purple));
  color:#fff; padding:20px; border-radius:14px; margin:12px 0 18px;
}}
.header-band h1 {{ margin:0; font-weight:800; letter-spacing:.3px; text-transform:uppercase; }}
.header-band p {{ margin:6px 0 0 0; opacity:.95; }}
.header-logo {{
  float:right; width:72px; height:72px; border-radius:10px;
  background-size:cover; background-position:center; margin-left:10px;
}}

/* Radio as 7 dots centered */
.stRadio div[role='radiogroup'] {{ display:flex; gap:10px; justify-content:center; }}
.stRadio input[type="radio"] {{ opacity:0; width:0; height:0; position:absolute; }}
.stRadio label {{
  width:20px; height:20px; border-radius:50%;
  border:2px solid var(--accent); cursor:pointer;
  display:inline-flex; align-items:center; justify-content:center;
  color:transparent !important; /* hide numbers 1..7 */
}}
.stRadio label:hover {{ transform:scale(1.06); }}
.stRadio input[type="radio"]:checked + div > span::after,
.stRadio input[type="radio"]:checked + span::after {{
  content:""; width:10px; height:10px; background:var(--purple); border-radius:50%; position:absolute;
}}

/* CTA */
.stButton > button {{
  background:linear-gradient(135deg,{CTA_GOLD_1},{CTA_GOLD_2});
  color:{PRIMARY_PURPLE}; border:none; font-weight:700; border-radius:999px; padding:10px 20px;
}}
</style>
""", unsafe_allow_html=True)

# ---- HEADER ----
logo_file = st.file_uploader("Upload your Soulful Academy logo (optional)", type=["png","jpg","jpeg"])
logo_bytes: Optional[bytes] = None
logo_view = ""
if logo_file:
    logo_bytes = logo_file.getvalue()
    mime = logo_file.type or "image/png"
    b64  = base64.b64encode(logo_bytes).decode("utf-8")
    logo_view = f"<div class='header-logo' style=\"background-image:url(data:{mime};base64,{b64})\"></div>"

st.markdown(f"""
<div class='header-band'>
  {logo_view}
  <h1>🔮 Personality + Chakra Scan</h1>
  <p>Choose for each pair (1 = left, 7 = right). Then download your combined report.</p>
</div>
""", unsafe_allow_html=True)

# ---- DATA ----
@dataclass
class Item:
    left: str; right: str; trait: str; reverse: bool=False

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

CHAKRA_COLORS = {"Root":"#EA4335","Sacral":"#F4A261","Solar Plexus":"#E9C46A","Heart":"#34A853","Throat":"#4285F4","Third Eye":"#7E57C2","Crown":"#B39DDB"}
MYAURABLISS = {
    "Root": ["Red Jasper","Hematite","Black Tourmaline"],
    "Sacral": ["Carnelian","Orange Calcite","Moonstone"],
    "Solar Plexus": ["Citrine","Tiger's Eye","Yellow Aventurine"],
    "Heart": ["Rose Quartz","Green Aventurine","Malachite"],
    "Throat": ["Sodalite","Blue Apatite","Aquamarine"],
    "Third Eye": ["Amethyst","Lapis Lazuli","Lepidolite"],
    "Crown": ["Clear Quartz","Amethyst","Selenite"],
}

# ---- RADIO-AS-DOTS ----
def dot_radio(key: str, default: int = 4) -> int:
    opts = list(range(1,8))
    idx = opts.index(st.session_state.get(key, default))
    v = st.radio("", opts, index=idx, key=f"_r_{key}", horizontal=True, label_visibility="collapsed")
    st.session_state[key] = v
    return v

# ---- FORMS ----
st.header("Part 1 · Personality")
st.caption("For each pair: 1 = left statement, 7 = right statement.")

responses: List[Tuple[Item,int]] = []
for i, item in enumerate(PERSONALITY_ITEMS, start=1):
    lc, rc = st.columns(2)
    with lc: st.write(item.left)
    with rc: st.write(f"<div style='text-align:right'>{item.right}</div>", unsafe_allow_html=True)
    responses.append((item, dot_radio(f"q{i}", 4)))
    st.divider()

st.header("Part 2 · Chakra Scan")
st.caption("Rate each (1 = Strongly Disagree, 7 = Strongly Agree).")

chakra_scores: Dict[str,List[int]] = {k:[] for k in CHAKRA_QUESTIONS}
for ch, qs in CHAKRA_QUESTIONS.items():
    st.subheader(ch)
    for j, q in enumerate(qs, start=1):
        st.write(q)
        chakra_scores[ch].append(dot_radio(f"{ch}_{j}", 4))
    st.markdown("---")

# ---- SCORING ----
@st.cache_data
def score_personality(items: List[Tuple[Item,int]]) -> Dict[str,float]:
    vals={t:[] for t in "OCEAN"}
    for it,raw in items:
        v = (raw-4)
        if it.reverse: v = -v
        vals[it.trait].append(v)
    return {t: float(np.mean(v)) if v else 0.0 for t,v in vals.items()}

@st.cache_data
def summarize_trait(name: str, score: float) -> str:
    bands=[(-3,-1.6,"Low"),(-1.6,-0.5,"Below Average"),(-0.5,0.5,"Balanced"),(0.5,1.6,"High"),(1.6,3.1,"Very High")]
    label=next(lbl for lo,hi,lbl in bands if lo<=score<hi)
    notes={"O":{"Low":"Prefer the familiar; add gentle novelty.","Below Average":"Practical; small explorations.","Balanced":"Curiosity + pragmatism.","High":"Imaginative; ground ideas.","Very High":"Visionary; add structure."},
           "C":{"Low":"Flexible; add routines.","Below Average":"Works in bursts; anchors.","Balanced":"Flow + discipline.","High":"Organized; watch perfectionism.","Very High":"Very structured; schedule play."},
           "E":{"Low":"Reflective; protect energy.","Below Average":"Selective socially; plan 1:1s.","Balanced":"Okay alone or with people.","High":"Outgoing; include solitude.","Very High":"Very social; block deep focus."},
           "A":{"Low":"Direct; add empathy.","Below Average":"Honest; practice listening.","Balanced":"Warm and fair.","High":"Kind; hold boundaries.","Very High":"Accommodating; protect needs."},
           "N":{"Low":"Calm and steady.","Below Average":"Usually grounded.","Balanced":"Healthy awareness.","High":"Sensitive to stress; soothe.","Very High":"Reactive; nervous-system care."}}
    return f"**{label}** – {notes.get(name,{}).get(label,'')}"

@st.cache_data
def score_chakras(scores: Dict[str,List[int]]) -> Dict[str,float]:
    return {k: float(np.mean(v)) if v else 0.0 for k,v in scores.items()}

def chakra_status(v: float) -> str:
    return "Balanced" if 3.8 <= v <= 5.8 else ("Overactive" if v > 5.8 else "Blocked")

def chakra_remedy_block(status: str, chakra: str) -> str:
    base={"Root":"Grounding walk barefoot, 4-7-8 breathing, red foods.",
          "Sacral":"Creative play, water ritual, forgiveness journal.",
          "Solar Plexus":"Power postures, small wins list, daily ‘No’.",
          "Heart":"Loving-kindness meditation, gratitude letters.",
          "Throat":"Humming/singing, write and read your needs.",
          "Third Eye":"10-min visualization, dream notes, less night screen-light.",
          "Crown":"Morning silence, seva, read a wisdom text."}.get(chakra,"")
    crystals=", ".join(MYAURABLISS.get(chakra, []))
    return f"{status}: {base}  •  Crystals: {crystals}"

# ---- RESULTS + PDF ----
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
        st.markdown(f"**{ch}** — {chakra_status(v)} · Avg {v:.1f} — {chakra_remedy_block(chakra_status(v), ch)}")

    def build_pdf(traits: Dict[str,float], chakras: Dict[str,float], logo_bytes: Optional[bytes]) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = []

        if logo_bytes:
            try:
                story += [Image(io.BytesIO(logo_bytes), width=80, height=80), Spacer(1, 6)]
            except Exception:
                pass

        def title(txt: str):
            return Paragraph(f"<para align='center'><b>{txt}</b></para>", styles["Title"])

        # Page 1: Personality Overview
        story.append(title("Personality Profile (Big Five style)"))
        story.append(Spacer(1, 12))
        pdata = [["Trait","Score (-3..+3)","Summary"]] + [[t, f"{s:.2f}", summarize_trait(t,s)] for t,s in traits.items()]
        pt = Table(pdata, colWidths=[3*cm, 4*cm, 9*cm])
        pt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#EDE7F6")),
            ("TEXTCOLOR",(0,0),(-1,0), colors.HexColor("#311B92")),
            ("GRID",(0,0),(-1,-1), 0.25, colors.grey),
            ("FONTNAME",(0,0),(-1,0), "Helvetica-Bold"),
            ("VALIGN",(0,0),(-1,-1), "TOP"),
        ]))
        story += [pt, Spacer(1, 24),
                  Paragraph("Scores are centered at 0 (balanced). Higher/lower describe tendencies, not limits.", styles["Normal"]),
                  PageBreak()]

        # Page 2: Personality Tips
        story.append(title("Growth Suggestions"))
        for tip in [
            "Pair high Openness with weekly shipping goals.",
            "Support low Conscientiousness with two anchor habits (sleep window, 30-min focus).",
            "If Extraversion is high, book solo reflection; if low, plan one meaningful social slot.",
            "Balance Agreeableness with clear boundaries.",
        ]:
            story.append(Paragraph("• " + tip, styles["Normal"]))
        story.append(PageBreak())

        # Pages 3–5: Chakras
        items = list(chakras.items())
        def chakra_table(ttl: str, subset: List[Tuple[str,float]]):
            story.append(Paragraph(f"<b>{ttl}</b>", styles["Heading2"]))
            data = [["Chakra","Avg (1–7)","Status","MyAuraBliss Crystals","Remedy"]]
            for ch, val in subset:
                stat = chakra_status(val)
                data.append([ch, f"{val:.1f}", stat, ", ".join(MYAURABLISS.get(ch, [])), chakra_remedy_block(stat, ch)])
            t = Table(data, colWidths=[3*cm, 2.7*cm, 3*cm, 5*cm, 4*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0), colors.HexColor("#E8EAF6")),
                ("FONTNAME",(0,0),(-1,0), "Helvetica-Bold"),
                ("GRID",(0,0),(-1,-1), 0.25, colors.grey),
            ]))
            story.append(t)

        chakra_table("Chakra Scan — Part 1", items[:3]); story.append(PageBreak())
        chakra_table("Chakra Scan — Part 2", items[3:5]); story.append(PageBreak())
        chakra_table("Chakra Scan — Part 3", items[5:])
        doc.build(story)
        return buf.getvalue()

    pdf = build_pdf(trait_scores, chakra_avg, logo_bytes)
    st.download_button("📄 Download Full Report (PDF)", data=pdf, file_name="personality_chakra_report.pdf", mime="application/pdf")
