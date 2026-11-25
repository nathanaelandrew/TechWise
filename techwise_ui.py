"""TechWise UI layer: theme CSS and HTML building blocks for Streamlit.

Everything visual lives here so app.py stays about logic.
Change ACCENT to re-color the whole app (also update primaryColor in
.streamlit/config.toml so native widgets match).
"""

ACCENT = "#B8F25A"  # lime. Alternatives: violet #A78BFA, cyan #67E8F9, orange #FDBA74


def _rgb(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


RGB = _rgb(ACCENT)

LOGO_SVG = f"""<svg width="16" height="16" viewBox="0 0 7 7" shape-rendering="crispEdges" aria-hidden="true">
<rect x="1" y="1" width="1" height="1" fill="{ACCENT}"/><rect x="3" y="1" width="1" height="1" fill="{ACCENT}"/>
<rect x="5" y="1" width="1" height="1" fill="{ACCENT}"/><rect x="2" y="3" width="3" height="1" fill="#EDEDEF"/>
<rect x="1" y="5" width="1" height="1" fill="{ACCENT}"/><rect x="3" y="5" width="1" height="1" fill="{ACCENT}"/>
<rect x="5" y="5" width="1" height="1" fill="{ACCENT}"/></svg>"""

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&family=Doto:wght@900&display=swap');

:root {{
  --tw-accent: {ACCENT};
  --tw-glow: rgba({RGB},0.32);
  --tw-glow-soft: rgba({RGB},0.45);
  --tw-bg: #09090B;
  --tw-panel: #0F0F12;
  --tw-surface: #141417;
  --tw-surface-2: #18181C;
  --tw-line: rgba(255,255,255,.08);
  --tw-text: #EDEDEF;
  --tw-muted: #A1A1AA;
  --tw-faint: #8B8B94;
}}

/* ---------- base ---------- */
.stApp {{ background: var(--tw-bg); font-family: 'Geist', system-ui, sans-serif; }}
.stApp p, .stApp li, .stApp label, .stApp input, .stApp textarea, .stApp button,
.stApp h1, .stApp h2, .stApp h3, .stApp td, .stApp th {{ font-family: 'Geist', system-ui, sans-serif; }}
.stApp h1, .stApp h2, .stApp h3 {{ letter-spacing: -0.035em; }}
code, .tw-mono {{ font-family: 'Geist Mono', monospace !important; }}

/* soft-fading square-dot grid behind the page */
.stApp::before {{
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image: radial-gradient(rgba(255,255,255,.11) 1.2px, transparent 1.4px);
  background-size: 22px 22px;
  -webkit-mask-image: radial-gradient(ellipse 70% 55% at 50% 0%, #000 15%, transparent 80%);
          mask-image: radial-gradient(ellipse 70% 55% at 50% 0%, #000 15%, transparent 80%);
}}

/* hide Streamlit chrome */
#MainMenu, footer, [data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stHeader"] {{ background: transparent; }}
.block-container {{ padding-top: 2.2rem; max-width: 1200px; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ background: var(--tw-panel); border-right: 1px solid rgba(255,255,255,.06); }}
[data-testid="stSidebar"] .stButton > button {{
  justify-content: flex-start; background: transparent; border: 1px solid transparent;
  color: #C9C9CF; border-radius: 10px; min-height: 40px; font-weight: 400;
}}
[data-testid="stSidebar"] .stButton > button:hover {{ background: var(--tw-surface-2); color: var(--tw-text); border-color: transparent; }}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
  background: var(--tw-surface-2); border: 1px solid rgba(255,255,255,.1); color: var(--tw-text); font-weight: 500;
}}
.tw-side-label {{ font-size: 12px; color: var(--tw-faint); margin: 18px 0 4px 4px; }}

/* ---------- buttons ---------- */
.stButton > button, .stFormSubmitButton > button {{
  border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: var(--tw-surface);
  color: var(--tw-text); transition: border-color .2s, background .2s;
}}
.stButton > button:hover {{ border-color: rgba(255,255,255,.22); background: #1E1E23; color: #fff; }}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
  background: var(--tw-accent); color: #09090B; border: 0; font-weight: 600; box-shadow: 0 0 22px var(--tw-glow);
}}
.stButton > button[kind="primary"]:hover {{ background: var(--tw-accent); color: #09090B; filter: brightness(1.06); }}

/* ---------- inputs ---------- */
[data-testid="stTextInput"] input, [data-testid="stChatInput"] textarea {{ font-size: 15px; }}
[data-testid="stTextInput"] > div > div, [data-testid="stChatInput"] > div {{
  background: var(--tw-surface) !important; border: 1px solid rgba(255,255,255,.12) !important; border-radius: 16px !important;
}}
[data-testid="stChatInput"] button {{ background: var(--tw-accent) !important; border-radius: 10px !important; }}
[data-testid="stChatInput"] button svg {{ fill: #09090B !important; color: #09090B !important; }}
[data-testid="stBottom"] > div {{ background: var(--tw-bg); }}

/* ---------- chat messages ---------- */
[data-testid="stChatMessage"] {{ background: transparent; padding: 6px 0; gap: 14px; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{ flex-direction: row-reverse; }}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {{
  background: linear-gradient(180deg,#232329,#1B1B20); border: 1px solid rgba(255,255,255,.1);
  border-radius: 20px 20px 6px 20px; padding: 12px 16px; max-width: 520px; margin-left: auto; flex: 0 1 auto;
}}
[data-testid="stChatMessageAvatarUser"] {{ display: none; }}
[data-testid="stChatMessageContent"] p {{ font-size: 15px; line-height: 1.6; color: #D4D4D8; }}

/* markdown tables from the model (system prompt asks for a parts table) */
[data-testid="stChatMessageContent"] table {{
  width: 100%; border-collapse: separate; border-spacing: 0; font-size: 13px;
  background: var(--tw-surface); border: 1px solid var(--tw-line); border-radius: 16px; overflow: hidden;
}}
[data-testid="stChatMessageContent"] th {{ color: var(--tw-faint); font-weight: 500; font-size: 12px; text-align: left; padding: 12px 14px; border: 0; }}
[data-testid="stChatMessageContent"] td {{ padding: 10px 14px; border: 0; border-top: 1px solid rgba(255,255,255,.06); color: #C9C9CF; }}

/* ---------- reusable HTML pieces ---------- */
.tw-surf {{
  background: var(--tw-surface); border: 1px solid var(--tw-line); border-radius: 18px;
  background-image: linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,0) 45%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06);
}}
.tw-logo {{ display:flex; align-items:center; gap:10px; font-weight:600; font-size:18px; letter-spacing:-0.02em; color: var(--tw-text); }}
.tw-logo-mark {{ width:30px; height:30px; border-radius:9px; background:var(--tw-surface-2); border:1px solid rgba(255,255,255,.1);
  display:flex; align-items:center; justify-content:center; box-shadow:0 0 18px var(--tw-glow); }}
.tw-eyebrow {{ font-family:'Geist Mono',monospace; font-size:12px; letter-spacing:.1em; color:var(--tw-accent); }}
.tw-pill {{ display:inline-flex; align-items:center; gap:8px; font-size:13px; color:#C9C9CF; background:var(--tw-surface);
  border:1px solid rgba(255,255,255,.1); padding:5px 12px 5px 5px; border-radius:999px; }}
.tw-pill b {{ font-family:'Geist Mono',monospace; font-weight:500; font-size:11px; color:#09090B; background:var(--tw-accent); padding:3px 8px; border-radius:999px; }}
.tw-hero {{ text-align:center; display:flex; flex-direction:column; align-items:center; gap:22px; padding: 40px 0 8px; position: relative; }}
.tw-hero::before {{ content:""; position:absolute; left:50%; top:-200px; width:900px; height:480px; margin-left:-450px;
  background: radial-gradient(closest-side, var(--tw-glow), transparent); z-index:-1; }}
.tw-hero h1 {{ font-size: 80px !important; line-height: 1 !important; font-weight: 600 !important; letter-spacing: -0.05em !important; margin: 0 !important; padding: 0 !important; }}
.tw-dots {{ font-family:'Doto','Geist Mono',monospace !important; font-weight:900; letter-spacing:-0.02em; color:var(--tw-accent); text-shadow:0 0 36px var(--tw-glow); }}
.tw-sub {{ font-size:19px; line-height:1.6; color:var(--tw-muted); max-width:600px; margin:0; }}
.tw-row {{ display:flex; align-items:center; gap:12px; padding:8px 0; border-bottom:1px solid rgba(255,255,255,.06); font-size:13px; }}
.tw-row:last-child {{ border-bottom:0; }}
.tw-k {{ width:44px; font-family:'Geist Mono',monospace; font-size:11px; color:var(--tw-faint); }}
.tw-num {{ font-variant-numeric: tabular-nums; }}
.tw-card {{ padding: 24px; display:flex; flex-direction:column; gap:10px; height:100%; box-sizing:border-box; }}
.tw-card h3 {{ font-size:19px !important; font-weight:600 !important; margin:0 !important; padding:0 !important; }}
.tw-card p {{ font-size:14px; line-height:1.6; color:var(--tw-muted); margin:0; }}
.tw-tag {{ font-family:'Geist Mono',monospace; font-size:12px; color:var(--tw-faint); }}
.tw-check {{ display:flex; gap:8px; align-items:center; font-size:13px; color:#C9C9CF; padding:3px 0; }}
.tw-stat {{ padding:12px 14px; display:flex; flex-direction:column; gap:4px; }}
.tw-stat span:first-child {{ font-size:12px; color:var(--tw-faint); }}
.tw-stat span:last-child {{ font-size:18px; font-weight:600; letter-spacing:-0.02em; font-variant-numeric: tabular-nums; }}
.tw-bar {{ display:flex; gap:3px; height:14px; margin:10px 0; }}
.tw-bar span {{ border-radius:4px; }}
.tw-legend {{ display:flex; flex-wrap:wrap; gap:6px 16px; font-size:12px; color:var(--tw-muted); }}
.tw-legend i {{ display:inline-block; width:8px; height:8px; border-radius:2px; margin-right:6px; }}
.tw-decoder {{ padding:14px; border-color: var(--tw-glow-soft); box-shadow: 0 0 24px var(--tw-glow); }}
.tw-decoder .head {{ display:flex; justify-content:space-between; font-size:12px; margin-bottom:6px; }}
.tw-decoder .head b {{ font-family:'Geist Mono',monospace; font-weight:500; color:var(--tw-accent); }}
.tw-decoder p {{ font-size:13px; line-height:1.55; color:#C9C9CF; margin:0; }}
.tw-note {{ padding:14px; font-size:12px; line-height:1.6; color:var(--tw-muted); }}
.tw-note b {{ color: var(--tw-text); font-size:13px; }}
/* closing call-to-action card (st.container(key="tw_cta")) */
.st-key-tw_cta {{
  margin-top: 40px; padding: 64px 32px 56px; border-radius: 28px; gap: 20px;
  background: var(--tw-surface); border: 1px solid rgba(255,255,255,.1);
  background-image: radial-gradient(ellipse 50% 60% at 50% 0%, rgba({RGB},0.14), transparent 70%),
                    linear-gradient(180deg, rgba(255,255,255,.045), rgba(255,255,255,0) 45%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,.06);
}}
.tw-fine {{ font-size:12px; color:var(--tw-faint); text-align:center; }}
.tw-empty {{ text-align:center; display:flex; flex-direction:column; align-items:center; gap:12px; padding:24px 0 8px; }}
.tw-empty .tw-logo-mark {{ width:60px; height:60px; border-radius:18px; box-shadow:0 0 50px var(--tw-glow); }}
.tw-empty h2 {{ font-size:30px !important; font-weight:600 !important; line-height:1.2 !important; margin:0 !important; padding:0 !important; }}
.tw-budget {{ font-size:28px; font-weight:600; letter-spacing:-0.03em; color:var(--tw-accent); font-variant-numeric: tabular-nums; text-shadow:0 0 24px var(--tw-glow); }}

/* pills / segmented control (Streamlit >= 1.40) */
[data-testid="stButtonGroup"] button {{ border-radius: 999px !important; }}
[data-testid="stButtonGroup"] button[aria-checked="true"], [data-testid="stButtonGroup"] button[kind$="Active"] {{
  background: rgba({RGB},0.12) !important; border-color: rgba({RGB},0.6) !important; color: var(--tw-accent) !important;
}}
[data-testid="stSlider"] [role="slider"] {{ box-shadow: 0 0 14px var(--tw-glow); }}

@media (max-width: 860px) {{ .tw-hero h1 {{ font-size: 46px !important; }} }}
</style>
"""


def logo(size: str = "") -> str:
    return f'<div class="tw-logo"><span class="tw-logo-mark">{LOGO_SVG}</span>TechWise</div>'


def check_icon(color: str = ACCENT) -> str:
    return (f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            'stroke-width="2.8" aria-hidden="true"><path d="M5 12l5 5L20 7"/></svg>')