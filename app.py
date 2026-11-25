import streamlit as st
import techwise_ui as ui

st.set_page_config(page_title="TechWise", page_icon="🖥️", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown(ui.CSS, unsafe_allow_html=True)


def html(s: str) -> None:
    """Render raw HTML. Lines are left-stripped so Markdown never turns them into code blocks."""
    st.markdown("\n".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


# data
SAMPLE_BUILD = {
    "title": "₱40K student gaming PC",
    "intro": ("₱40,000 is a great sweet spot for a student rig. This build handles schoolwork, "
              "programming and 1080p gaming without a major bottleneck between the CPU and GPU."),
    "parts": [  # key, part, why, est. price (₱)  — placeholder prices, replace with real ones
        ("CPU", "AMD Ryzen 5 5600", "6 cores — smooth for games, coding and multitasking", 6500),
        ("GPU", "NVIDIA RTX 4060 8GB", "High settings at 1080p, efficient on power", 18500),
        ("MOBO", "MSI B550M PRO-VDH WIFI", "AM4 board with built-in Wi-Fi, room to upgrade", 5200),
        ("RAM", "16GB (2×8GB) DDR4-3200", "Dual-channel; plenty for IDEs plus a game", 2300),
        ("SSD", "1TB NVMe PCIe Gen 4", "Fast boot and load times, space for games", 3400),
        ("PSU", "650W 80+ Bronze", "Safe headroom now and for a future GPU", 2900),
        ("CASE", "Tecware Nexus Air M", "Mesh front for good airflow on a budget", 1200),
    ],
    "stats": [("Target", "1080p · High"), ("Est. power draw", "~350W"),
              ("PSU headroom", "~46%"), ("Budget used", "100% of ₱40K")],
    "compat": ["AM4 socket ↔ B550 chipset", "DDR4 RAM ↔ B550 board",
               "Micro-ATX board fits the case", "650W covers est. ~350W draw"],
    "upgrades": ["Add 2×8GB later for 32GB", "Drop-in AM4 CPU upgrade", "PSU has room for a bigger GPU"],
}

DECODER = {
    "CPU": ("Processor", "The “brain” of your computer. It follows instructions and runs your apps — more cores means it can juggle more tasks at once."),
    "GPU": ("Graphics card", "The artist that draws every frame you see. It matters most for games and video editing."),
    "RAM": ("Memory", "Your desk space. More RAM lets you keep more programs open without things slowing down."),
    "SSD": ("Storage", "A very fast filing cabinet. It decides how quickly the PC boots and games load."),
    "PSU": ("Power supply", "Feeds power to every part. Extra wattage “headroom” keeps it cool, quiet and upgrade-ready."),
    "MOBO": ("Motherboard", "The city streets connecting every part. It decides which CPU and RAM types fit."),
    "VRAM": ("Video memory", "The graphics card’s own workspace — like a painter’s palette. More of it holds sharper textures."),
    "TDP": ("Thermal design power", "Roughly how much heat a chip makes under load — a hint for how big a cooler and PSU you need."),
}

CATEGORIES = [("Gaming", ":material/sports_esports:"), ("Programming", ":material/code:"),
              ("Video editing", ":material/movie:"), ("Office work", ":material/work:"),
              ("Phones & tablets", ":material/smartphone:")]

QUICK_STARTS = ["Gaming PC under ₱40K", "Laptop for coding", "Best GPU for my budget", "Upgrade my PC"]


# state
ss = st.session_state
ss.setdefault("page", "landing")
ss.setdefault("messages", [])        # [{"role": "user"|"assistant", "content": str, "build": dict|None}]
ss.setdefault("decoder_term", "GPU")
ss.setdefault("category", None)


def go_chat(first_prompt: str | None = None) -> None:
    ss.page = "chat"
    if first_prompt:
        ss.pending_prompt = first_prompt


def new_chat() -> None:
    ss.messages = []
    ss.page = "chat"


# model hook
def get_techwise_reply(messages: list[dict]) -> dict:
    """Replace this with your LLM call (OpenAI, Gemini, Claude, …) using your system prompt.

    `messages` is the chat history as [{"role", "content"}]. Return a dict:
      {"content": "<markdown answer>", "build": <optional dict shaped like SAMPLE_BUILD>}
    If your model returns plain markdown (including the parts table from your system prompt),
    just return {"content": text} — the CSS styles markdown tables to match the design.
    """
    last = messages[-1]["content"].lower()
    if any(w in last for w in ("pc", "build", "₱", "budget", "gaming")):
        return {"content": SAMPLE_BUILD["intro"], "build": SAMPLE_BUILD}
    return {"content": ("I can help with PC builds, laptops, phones and tablets, comparisons, "
                        "or explaining any spec simply. What’s your budget and what will you use it for?")}


# render: build card
def render_build(build: dict) -> None:
    accent_rgb = ui.RGB
    total = sum(p[3] for p in build["parts"])

    stats = "".join(f'<div class="tw-surf tw-stat"><span>{l}</span><span>{v}</span></div>' for l, v in build["stats"])
    html(f'<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:4px 0 14px">{stats}</div>')

    rows = "".join(
        f'<tr><td><span class="tw-mono" style="font-size:11px;background:#1E1E23;border:1px solid rgba(255,255,255,.1);'
        f'padding:4px 8px;border-radius:8px">{k}</span></td><td style="color:#EDEDEF;font-weight:500">{p}</td>'
        f'<td>{w}</td><td class="tw-mono tw-num" style="text-align:right;white-space:nowrap">₱{c:,}</td></tr>'
        for k, p, w, c in build["parts"])
    html(f"""
<table>
<thead><tr><th>Part</th><th>Recommended</th><th>Why it’s here</th><th style="text-align:right">Est. price</th></tr></thead>
<tbody>{rows}
<tr><td colspan="3" style="color:#EDEDEF;font-weight:500">Estimated total</td>
<td class="tw-num" style="text-align:right;font-size:20px;font-weight:600;color:{ui.ACCENT}">₱{total:,}</td></tr>
</tbody></table>""")

    shares = sorted(build["parts"], key=lambda p: -p[3])
    alphas = [1, .78, .6, .46, .34, .24, .16]
    bar = "".join(f'<span style="width:{p[3] / total * 100:.1f}%;background:rgba({accent_rgb},{alphas[i % 7]})"></span>'
                  for i, p in enumerate(shares))
    legend = "".join(f'<span><i style="background:rgba({accent_rgb},{alphas[i % 7]})"></i>{p[0]} '
                     f'<b class="tw-num" style="color:#EDEDEF">{round(p[3] / total * 100)}%</b></span>'
                     for i, p in enumerate(shares))
    html(f"""
<div class="tw-surf" style="padding:16px;margin:14px 0">
<div style="display:flex;justify-content:space-between;font-size:13px;flex-wrap:wrap;gap:8px">
<b>Where your money goes</b><span style="color:#8B8B94">GPU gets the biggest share — right for gaming</span></div>
<div class="tw-bar">{bar}</div><div class="tw-legend">{legend}</div></div>""")

    checks = "".join(f'<div class="tw-check">{ui.check_icon()}{c}</div>' for c in build["compat"])
    ups = "".join(f'<div class="tw-check"><span class="tw-mono" style="font-size:11px;color:#8B8B94">0{i + 1}</span>{u}</div>'
                  for i, u in enumerate(build["upgrades"]))
    html(f"""
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px">
<div class="tw-surf" style="padding:16px"><b style="font-size:13px">Compatibility check</b><div style="margin-top:8px">{checks}</div></div>
<div class="tw-surf" style="padding:16px"><b style="font-size:13px">Upgrade path</b><div style="margin-top:8px">{ups}</div></div>
</div>""")
    st.write("Want me to add a monitor and peripherals, or tweak the budget?")


# page: landing
def landing() -> None:
    nav_l, nav_r = st.columns([4, 1])
    with nav_l:
        html(ui.logo())
    with nav_r:
        st.button("Open app →", type="primary", use_container_width=True, on_click=go_chat)

    html("""
<div class="tw-hero">
<span class="tw-pill"><b>NEW</b>Budget builds in Philippine pesos</span>
<h1>Smarter tech choices.<br><span class="tw-dots">Built around you.</span></h1>
<p class="tw-sub">Cut through the specs and endless reviews. Tell TechWise your needs and budget — get a clear, compatible recommendation in seconds.</p>
</div>""")

    _, mid, _ = st.columns([1, 3, 1])
    with mid:
        with st.form("hero_ask", border=False):
            c1, c2 = st.columns([6, 1])
            q = c1.text_input("Ask", placeholder="What technology are you looking for today?", label_visibility="collapsed")
            if c2.form_submit_button("Ask →", type="primary", use_container_width=True) and q.strip():
                go_chat(q.strip())
                st.rerun()
        cols = st.columns(len(QUICK_STARTS))
        for col, label in zip(cols, QUICK_STARTS):
            col.button(label, use_container_width=True, on_click=go_chat, args=(label,), key=f"qs_{label}")

    # product preview
    parts = "".join(f'<div class="tw-row"><span class="tw-k">{k}</span><span style="flex:1">{p}</span>'
                    f'<span class="tw-mono tw-num" style="color:#C9C9CF">₱{c:,}</span></div>'
                    for k, p, _, c in SAMPLE_BUILD["parts"])
    dots = "".join(f'<span style="aspect-ratio:1;border-radius:2px;background:{ui.ACCENT};opacity:{0.3 + i / 13 * 0.7:.2f}"></span>'
                   for i in range(14))
    html(f"""
<div style="position:relative;margin-top:36px">
<div style="position:absolute;left:10%;right:10%;top:40px;height:280px;background:{ui.ACCENT};opacity:.12;filter:blur(90px)"></div>
<div style="position:relative;background:#0F0F12;border:1px solid rgba(255,255,255,.1);border-radius:22px;box-shadow:0 40px 120px rgba(0,0,0,.8);overflow:hidden">
<div style="display:flex;align-items:center;gap:8px;padding:12px 16px;border-bottom:1px solid rgba(255,255,255,.06)">
<span style="width:10px;height:10px;border-radius:50%;background:#2A2A30"></span><span style="width:10px;height:10px;border-radius:50%;background:#2A2A30"></span><span style="width:10px;height:10px;border-radius:50%;background:#2A2A30"></span>
<span style="margin:0 auto;font-size:12px;color:#8B8B94;background:#18181C;padding:4px 40px;border-radius:8px">techwise.ai</span></div>
<div style="padding:24px 28px;display:flex;flex-direction:column;gap:16px">
<div style="align-self:flex-end;background:#1E1E23;padding:10px 14px;border-radius:16px 16px 4px 16px;font-size:14px">Gaming PC for school, ₱40K</div>
<div style="display:flex;flex-wrap:wrap;gap:16px">
<div class="tw-surf" style="flex:1 1 360px;padding:6px 16px">{parts}</div>
<div style="flex:1 1 220px;display:flex;flex-direction:column;gap:12px">
<div class="tw-surf" style="padding:16px"><div style="font-size:12px;color:#8B8B94">Estimated total</div>
<div class="tw-num" style="font-size:36px;font-weight:600;letter-spacing:-0.03em;color:{ui.ACCENT}">₱40,000</div></div>
<div class="tw-surf" style="padding:16px;display:flex;flex-direction:column;gap:10px">
<div style="display:flex;justify-content:space-between;font-size:12px"><span style="color:#8B8B94">Compatibility</span><span style="color:{ui.ACCENT}">7/7</span></div>
<div style="display:grid;grid-template-columns:repeat(14,1fr);gap:3px">{dots}</div>
<div style="display:flex;justify-content:space-between;font-size:12px"><span style="color:#8B8B94">PSU headroom</span><span>~46%</span></div>
</div></div></div></div></div></div>""")

    # how it works
    html('<div style="height:56px"></div><div class="tw-eyebrow">HOW IT WORKS</div><h2 style="font-size:40px;margin:6px 0 18px">From budget to build in three steps</h2>')
    steps = [("01", "Tell us your budget & needs", "Gaming, coding, editing or school — plus how much you want to spend. Plain words are fine."),
             ("02", "Get a build that fits", "A complete, compatible list with estimated prices, power headroom and a future upgrade path."),
             ("03", "Understand every part", "Tap any term and the Tech Decoder explains it simply — so you buy with confidence.")]
    for col, (n, t, d) in zip(st.columns(3), steps):
        with col:
            html(f'<div class="tw-surf tw-card"><span class="tw-mono" style="align-self:flex-start;font-size:13px;color:{ui.ACCENT};'
                 f'background:#1E1E23;padding:6px 10px;border-radius:8px">{n}</span><h3>{t}</h3><p>{d}</p></div>')

    # features
    html('<div style="height:56px"></div><div class="tw-eyebrow">FEATURES</div><h2 style="font-size:40px;margin:6px 0 18px">Six tools. One honest advisor.</h2>')
    feats = [("01 · CONFIGURATOR", "Complete builds for any budget", "Balanced part lists — CPU to case — tuned to your budget and target resolution (1080p, 1440p or 4K)."),
             ("02 · COMPATIBILITY", "Nothing that won’t fit", "Checks sockets, chipsets, DDR4 vs DDR5, form factors and PSU wattage before you buy."),
             ("03 · TECH DECODER", "Jargon, translated", "TDP, VRAM, PCIe Gen 4, IPS vs OLED — explained with plain, everyday analogies."),
             ("04 · COMPARE", "Head-to-head, side by side", "Specs, pros, cons and performance per peso for two or more products."),
             ("05 · BOTTLENECK", "Find what holds you back", "Spots what limits your setup and plans the most cost-effective upgrade order."),
             ("06 · ALTERNATIVES", "Over budget? Keep the performance.", "High-value and previous-gen picks whenever a part blows past your ceiling.")]
    for row in (feats[:3], feats[3:]):
        for col, (tag, t, d) in zip(st.columns(3), row):
            with col:
                html(f'<div class="tw-surf tw-card" style="margin-bottom:16px"><span class="tw-tag">{tag}</span><h3>{t}</h3><p>{d}</p></div>')

    # closing CTA
    html("""
<div class="tw-surf" style="margin-top:40px;padding:64px 32px;text-align:center;border-radius:28px">
<h2 style="font-size:48px;line-height:1.05;margin:0">Stop guessing.<br><span class="tw-dots">Start building.</span></h2>
<p style="color:#A1A1AA;margin:14px 0 0">Free to use. No sign-up needed to ask your first question.</p></div>""")
    _, c, _ = st.columns([2, 1, 2])
    c.button("Ask TechWise →", type="primary", use_container_width=True, on_click=go_chat, key="cta")
    html('<div style="height:24px"></div><p class="tw-fine">TechWise — a CS365 project by Group Veveco · Estimates only. Verify prices &amp; availability with official sources.</p>')


# page: chat
def sidebar() -> None:
    with st.sidebar:
        html(ui.logo())
        st.write("")
        st.button("New chat", icon=":material/add:", type="primary", use_container_width=True, on_click=new_chat)
        html('<div class="tw-side-label">Categories</div>')
        for name, icon in CATEGORIES:
            if st.button(name, icon=icon, use_container_width=True, key=f"cat_{name}"):
                ss.category = name
        html('<div class="tw-side-label">Navigate</div>')
        st.button("Home", icon=":material/home:", use_container_width=True,
                  on_click=lambda: ss.update(page="landing"))
        st.write("")
        html(f"""<div class="tw-surf tw-note"><b>ⓘ Good to know</b><br>
Prices are estimates, not guaranteed<br>No purchases are made in chat<br>Recommendations are unsponsored</div>""")


def empty_state() -> None:
    html(f"""<div class="tw-empty"><span class="tw-logo-mark">{ui.LOGO_SVG.replace('width="16" height="16"', 'width="28" height="28"')}</span>
<h2>Hi, I’m TechWise.<br><span style="color:#A1A1AA">Let’s find tech that fits your budget.</span></h2></div>""")
    _, mid, _ = st.columns([1, 4, 1])
    with mid, st.container(border=True):
        top_l, top_r = st.columns([1, 1])
        top_l.markdown("**Quick setup**")
        budget = ss.get("qs_budget", 40000)
        top_r.markdown(f'<div style="text-align:right" class="tw-budget">₱{budget:,}</div>', unsafe_allow_html=True)
        st.slider("Budget", 20000, 150000, 40000, 5000, key="qs_budget", format="₱%d")
        use = st.pills("Mostly for", ["Gaming", "Programming", "Video editing", "School & office"], default="Gaming", key="qs_use")
        res = st.segmented_control("Target resolution", ["1080p", "1440p", "4K"], default="1080p", key="qs_res")
        if st.button("Generate my build →", type="primary", use_container_width=True):
            ss.pending_prompt = (f"Build me a PC for {use or 'general use'} at {res or '1080p'} "
                                 f"with a budget of ₱{ss.qs_budget:,}.")
            st.rerun()


def decoder_panel() -> None:
    html('<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">'
         f'<b style="font-size:14px">Tech Decoder</b><span style="font-size:12px;color:#8B8B94">{len(DECODER)} terms</span></div>')
    term = st.pills("Term", list(DECODER), key="decoder_term", label_visibility="collapsed")
    if term:
        full, desc = DECODER[term]
        html(f'<div class="tw-surf tw-decoder"><div class="head"><b>{term}</b><span style="color:#8B8B94">{full}</span></div><p>{desc}</p></div>')
    else:
        html('<div class="tw-surf tw-note" style="border-style:dashed;text-align:center">Pick a term to see it explained in plain language.</div>')


def chat() -> None:
    sidebar()
    title = next((m["build"]["title"] for m in ss.messages if m.get("build")), "New chat")
    h_l, h_r = st.columns([3, 1])
    h_l.markdown(f'<div style="font-size:15px;color:#C9C9CF;font-weight:500">{title}</div>', unsafe_allow_html=True)
    h_r.toggle("Beginner mode", value=True, key="beginner")
    st.divider()

    main, side = st.columns([3, 1], gap="large")
    with side:
        decoder_panel()
    with main:
        if not ss.messages and "pending_prompt" not in ss:
            empty_state()
        for m in ss.messages:
            with st.chat_message(m["role"], avatar=None if m["role"] == "user" else ":material/memory:"):
                st.markdown(m["content"])
                if m.get("build"):
                    render_build(m["build"])

        prompt = ss.pop("pending_prompt", None)
        if prompt:
            ss.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar=":material/memory:"), st.spinner("Thinking…"):
                reply = get_techwise_reply([{"role": m["role"], "content": m["content"]} for m in ss.messages])
            ss.messages.append({"role": "assistant", "content": reply["content"], "build": reply.get("build")})
            st.rerun()

    if q := st.chat_input("Ask about budget, specs, or compare products…"):
        ss.pending_prompt = q
        st.rerun()
    st.caption("TechWise can make mistakes. Verify prices, availability and specs with official sources.")


# router
if ss.page == "landing":
    landing()
else:
    chat()