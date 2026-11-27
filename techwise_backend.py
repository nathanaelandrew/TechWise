"""TechWise LLM Agent connecting system prompt, RAG, Search API, Deterministic Builder, and Offline Fallback.
Uses ONLY free-tier models (Gemini Flash / Flash-Lite / Neon / Hydrogen and Groq Llama).
"""

import json
import os
import re
import requests
import streamlit as st
from openai import OpenAI

import hardware_db as hw
import rag_engine as rag

SYSTEM_PROMPT = """You are TechWise, an expert, approachable, and objective AI hardware consultant developed by Group Veveco. Your mission is to help students, gamers, professionals, and beginners find the right computers, laptops, gadgets, and PC components tailored to their budget and practical needs.

1. Core Persona & Tone:
- Tone: Friendly, patient, objective, and encouraging.
- Communication Style: Clear and educational. Avoid gatekeeping or unnecessary technical elitism.

2. Capabilities & Tools (ALWAYS use your tools when relevant):
- `build_pc_within_budget`: Call this whenever the user asks for a desktop PC build or setup for a budget, OR when they ask to add a monitor/peripherals to a build. Set `include_peripherals=True` whenever they want a monitor, keyboard, mouse, headset, or full setup included in the budget. When you call this tool, the app automatically renders an interactive parts table, budget breakdown, compatibility check, and upgrade path below your message—so keep your text response as a helpful, concise explanation and DO NOT repeat a giant Markdown table in text!
- `check_parts_compatibility`: Call this when a user asks about upgrading an existing PC, checking bottlenecks, or whether parts work together.
- `search_tech_knowledge`: Call this to retrieve verified hardware explanations, VRAM/DDR/PSU guidelines, and buying advice from TechWise's RAG knowledge base.
- `web_search_prices_and_gadgets`: Call this when recommending laptops, smartphones, tablets, peripherals, or checking current live Philippine prices (e.g., Shopee/Lazada/Datablitz/Bermor) and latest releases.

3. Strict Guardrails & Constraints:
- Do NOT invent specifications, benchmark figures, or exact store stock listings.
- Do NOT guarantee live prices; always state that prices are estimates and vary by store/region.
- Do NOT recommend incompatible PC components.
- Do NOT carry out purchases or exhibit brand bias.
- Do NOT give dangerous repair instructions (e.g., opening a PSU or handling live high voltage); advise seeing a certified technician.
- Remind users that real-world performance varies by thermals, drivers, and background tasks.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "build_pc_within_budget",
            "description": "Generates a 100% compatible, budget-optimized desktop PC parts list (with optional monitor & peripherals) in Philippine Pesos (₱).",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget_php": {"type": "integer", "description": "User's budget in Philippine Pesos (e.g. 60000)."},
                    "use_case": {"type": "string", "description": "Primary use (e.g. Gaming, Programming, Gaming & Programming, Video editing, or School & office)."},
                    "resolution": {"type": "string", "description": "Target display resolution: 1080p, 1440p, or 4K."},
                    "include_peripherals": {"type": "boolean", "description": "Set true if the user wants a monitor, keyboard, mouse, or peripherals included in the budget."}
                },
                "required": ["budget_php"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_parts_compatibility",
            "description": "Checks CPU/GPU bottlenecks and PSU wattage compatibility for user-provided parts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "cpu_query": {"type": "string", "description": "CPU name or model if mentioned."},
                    "gpu_query": {"type": "string", "description": "GPU name or model if mentioned."},
                    "psu_wattage": {"type": "integer", "description": "Power supply wattage if mentioned."}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tech_knowledge",
            "description": "Searches the internal ChromaDB RAG knowledge base for verified tech rules, specs guides, and explanations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Concept or buying question to look up."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search_prices_and_gadgets",
            "description": "Searches the live web for current laptop, smartphone, tablet recommendations, or live PH component prices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Specific search query (include 'Philippines price' when checking local pricing)."}
                },
                "required": ["query"]
            }
        }
    }
]

_DEAD_MODELS: set[str] = set()


def _clean_err(err: Exception | str) -> str:
    return re.sub(r"key=[^&\s'\"]+", "key=***", str(err))


def _get_secret(name: str) -> str | None:
    try:
        if name in st.secrets:
            val = str(st.secrets[name]).strip()
            if val and not val.startswith("your-"):
                return val
    except Exception:
        pass
    return os.getenv(name)


def _execute_tool(fn_name: str, args: dict, tavily_key: str | None) -> tuple[str, dict | None]:
    """Runs the requested Python tool and returns (result_string, optional_build_dict)."""
    if fn_name == "build_pc_within_budget":
        build = hw.optimize_build(
            budget_php=int(args.get("budget_php", 40000)),
            use_case=args.get("use_case", "Gaming"),
            resolution=args.get("resolution", "1080p"),
            include_peripherals=bool(args.get("include_peripherals", False)),
        )
        return json.dumps(build, ensure_ascii=False), build

    if fn_name == "check_parts_compatibility":
        out = hw.check_custom_parts(
            cpu_query=args.get("cpu_query", ""),
            gpu_query=args.get("gpu_query", ""),
            psu_wattage=int(args.get("psu_wattage", 0)),
        )
        return out, None

    if fn_name == "search_tech_knowledge":
        return rag.query_rag(args.get("query", "")), None

    if fn_name == "web_search_prices_and_gadgets":
        return rag.live_web_search(args.get("query", ""), tavily_api_key=tavily_key), None

    return "Unknown tool.", None


def _extract_budget(text: str) -> int | None:
    if m := re.search(r"(\d+(?:\.\d+)?)\s*k\b", text, re.I):
        return int(float(m.group(1)) * 1000)
    if m := re.search(r"\b(\d{2,3}(?:,\d{3})+|\d{5,6})\b", text):
        return int(m.group(1).replace(",", ""))
    return None


def _local_smart_fallback(messages: list[dict], category: str | None = None, reason: str = "") -> dict:
    """Handles user prompts locally via Deterministic Builder + ChromaDB RAG if cloud AI fails."""
    user_text = messages[-1]["content"]
    low = user_text.lower()
    budget = _extract_budget(user_text)
    note = f"\n\n*(Local fallback active — reason: `{reason[:140]}`)*" if reason else ""

    wants_periph = any(k in low for k in ("monitor", "peripheral", "keyboard", "mouse", "headset", "full set", "complete set"))
    if budget is None and wants_periph:
        for m in reversed(messages[:-1]):
            if m["role"] == "user":
                if prev_b := _extract_budget(m["content"]):
                    budget = prev_b
                    break

    wants_pc = any(k in low for k in ("pc", "build", "desktop", "rig", "system unit", "setup")) or wants_periph
    not_pc = any(k in low for k in ("laptop", "phone", "smartphone", "tablet", "ipad", "fps", "valo"))
    if (wants_pc or budget) and not not_pc:
        use_parts = []
        if any(k in low for k in ("gam", "fps", "esport")):
            use_parts.append("Gaming")
        if any(k in low for k in ("program", "cod", "dev", "android", "studio", "school")):
            use_parts.append("Programming")
        if any(k in low for k in ("edit", "render", "video", "premiere")):
            use_parts.append("Video editing")
        use_case = " & ".join(use_parts) if use_parts else (category or "Gaming")

        res = "4K" if "4k" in low else ("1440p" if "1440" in low else "1080p")
        build = hw.optimize_build(
            budget_php=budget or 40000,
            use_case=use_case,
            resolution=res,
            include_peripherals=wants_periph,
        )
        rag_tips = rag.query_rag(user_text, n_results=2)
        return {"content": f"{build['intro']}\n\n**Key Hardware Notes:**\n{rag_tips}{note}", "build": build}

    if any(k in low for k in ("bottleneck", "compatib", "upgrade", "psu", "watt")):
        psu_match = re.search(r"(\d{3,4})\s*w\b", low)
        compat_out = hw.check_custom_parts(
            cpu_query=user_text,
            gpu_query=user_text,
            psu_wattage=int(psu_match.group(1)) if psu_match else 0,
        )
        rag_tips = rag.query_rag(user_text, n_results=2)
        return {"content": f"**Compatibility & Upgrade Check:**\n{compat_out}\n\n**Hardware Guidelines:**\n{rag_tips}{note}"}

    rag_tips = rag.query_rag(user_text, n_results=3)
    return {"content": f"Here is what I found from TechWise's hardware knowledge base:\n\n{rag_tips}{note}"}


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_free_gemini_models(api_key: str) -> list[str]:
    """Fetches and ranks ONLY free-tier Gemini models (Flash, Flash-Lite, Neon, Hydrogen); excludes paid Pro/Ultra."""
    r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=15)
    if not r.ok:
        raise RuntimeError(f"Gemini key check failed (HTTP {r.status_code}): {r.text[:300]}")

    skip_words = ("embedding", "imagen", "veo", "tts", "audio", "robotics", "computer-use", "aqa", "live", "deep-research")
    discovered = []
    for m in r.json().get("models", []):
        if "generateContent" not in m.get("supportedGenerationMethods", []):
            continue
        name = m["name"].removeprefix("models/")
        low = name.lower()
        if "gemini" not in low or any(w in low for w in skip_words):
            continue
        if re.search(r"(^|[-_/])(pro|ultra)([-_/]|$)", low):
            continue
        discovered.append(name)

    def _rank(name: str) -> tuple:
        low = name.lower()
        ver_match = re.search(r"gemini-(\d+(?:\.\d+)?)", low)
        ver = float(ver_match.group(1)) if ver_match else 0.0
        is_fast_free = 3 if ("flash" in low and "lite" not in low) else (2 if ("flash-lite" in low or "neon" in low) else 1)
        is_stable = 1 if ("exp" not in low and "preview" not in low) else 0
        return (is_fast_free, ver, is_stable, name)

    return sorted(discovered, key=_rank, reverse=True)


def _get_gemini_candidates(api_key: str) -> list[str]:
    """Returns real, free-tier Gemini models in priority order."""
    discovered = _fetch_free_gemini_models(api_key)
    preferred = ["gemini-3.8-flash", "gemini-4-neon", "gemini-2.5-flash-lite", "gemini-2.0-flash", "gemini-4-hydrogen"]

    ordered = []
    cached = st.session_state.get("_gemini_model")
    if cached and cached in discovered and cached not in _DEAD_MODELS:
        ordered.append(cached)

    for m in preferred + discovered:
        if m in discovered and m not in _DEAD_MODELS and m not in ordered:
            ordered.append(m)

    if not ordered:
        raise RuntimeError("No free-tier Gemini models available for this API key.")
    return ordered


def _post_gemini_with_fallback(api_key: str, candidates: list[str], payload: dict) -> tuple[dict, str]:
    """Posts to Gemini generateContent, skipping dead 404s and falling back on timeouts/429/503."""
    tried = []
    last_msg = ""
    for model in candidates[:10]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            r = requests.post(url, json=payload, timeout=15)
        except requests.exceptions.Timeout:
            if st.session_state.get("_gemini_model") == model:
                st.session_state.pop("_gemini_model", None)
            tried.append(f"{model} (timeout)")
            last_msg = f"Timed out waiting for {model}"
            continue
        if r.ok:
            st.session_state["_gemini_model"] = model
            return r.json(), model
        if st.session_state.get("_gemini_model") == model:
            st.session_state.pop("_gemini_model", None)
        if r.status_code == 404:
            _DEAD_MODELS.add(model)
            tried.append(f"{model} (404)")
            if not last_msg:
                last_msg = f"HTTP 404 ({model}): {r.text[:200]}"
            continue
        if r.status_code in (400, 429, 500, 503) and "API_KEY" not in r.text:
            tried.append(f"{model} ({r.status_code})")
            last_msg = f"HTTP {r.status_code} ({model}): {r.text[:200]}"
            continue
        raise RuntimeError(f"HTTP {r.status_code} ({model}): {r.text[:300]}")

    raise RuntimeError(f"Tried {', '.join(tried)}. {last_msg}")


def _run_gemini(api_key: str, system_text: str, messages: list[dict], tavily_key: str | None) -> dict:
    """Uses Google's native Gemini REST API with function calling and automatic free-model fallback."""
    candidates = _get_gemini_candidates(api_key)

    contents = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
        for m in messages
    ]
    func_decls = [t["function"] for t in TOOLS]
    generated_build = None

    for _ in range(4):
        payload = {
            "systemInstruction": {"parts": [{"text": system_text}]},
            "contents": contents,
            "tools": [{"functionDeclarations": func_decls}],
            "generationConfig": {"temperature": 0.3},
        }
        data, active_model = _post_gemini_with_fallback(api_key, candidates, payload)
        candidates = [active_model] + [c for c in candidates if c != active_model]

        cand_list = data.get("candidates", [])
        if not cand_list:
            return {"content": "I couldn't generate a response for that prompt. Please try rephrasing.", "build": generated_build}

        cand_content = cand_list[0].get("content", {})
        parts = cand_content.get("parts", [])
        calls = [p["functionCall"] for p in parts if "functionCall" in p]

        if not calls:
            texts = [p["text"] for p in parts if "text" in p and not p.get("thought")]
            return {"content": "\n".join(texts).strip() or "How can I help with your tech setup?", "build": generated_build}

        contents.append(cand_content)
        func_responses = []
        for fc in calls:
            fn_name = fc["name"]
            args = fc.get("args", {})
            tool_out, maybe_build = _execute_tool(fn_name, args, tavily_key)
            if maybe_build is not None:
                generated_build = maybe_build
            func_responses.append({"functionResponse": {"name": fn_name, "response": {"result": tool_out}}})

        contents.append({"role": "user", "parts": func_responses})

    return {"content": "I ran into too many lookup steps. Could you rephrase your question?", "build": generated_build}


def _run_groq(api_key: str, system_text: str, messages: list[dict], tavily_key: str | None) -> dict:
    """Runs tool-calling loop using Groq's free tier."""
    client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
    convo = [{"role": "system", "content": system_text}] + messages
    generated_build = None

    for _ in range(4):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=convo,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return {"content": msg.content or "How can I help with your tech setup?", "build": generated_build}

        convo.append(msg)
        for tc in msg.tool_calls:
            fn_name = tc.function.name
            args = json.loads(tc.function.arguments or "{}")
            tool_out, maybe_build = _execute_tool(fn_name, args, tavily_key)
            if maybe_build is not None:
                generated_build = maybe_build
            convo.append({"role": "tool", "tool_call_id": tc.id, "content": tool_out})

    return {"content": "I ran into too many lookup steps. Could you rephrase your question?", "build": generated_build}


def get_techwise_reply(messages: list[dict], beginner_mode: bool = True, category: str | None = None) -> dict:
    mode_note = (
        "\n[UI Setting: Beginner mode is ON — explain technical terms simply using plain analogies.]"
        if beginner_mode
        else "\n[UI Setting: Beginner mode is OFF — user is comfortable with technical specs and metrics.]"
    )
    cat_note = f"\n[Selected sidebar category: {category}]" if category else ""
    system_text = SYSTEM_PROMPT + mode_note + cat_note
    tavily_key = _get_secret("TAVILY_API_KEY")

    errors = []
    if key := _get_secret("GEMINI_API_KEY"):
        try:
            return _run_gemini(key, system_text, messages, tavily_key)
        except Exception as e:
            errors.append(f"Gemini: {_clean_err(e)}")

    if key := _get_secret("GROQ_API_KEY"):
        try:
            return _run_groq(key, system_text, messages, tavily_key)
        except Exception as e:
            errors.append(f"Groq: {_clean_err(e)}")

    reason = " | ".join(errors) if errors else "No free API key configured"
    print(f"[TechWise fallback triggered]: {reason}")
    return _local_smart_fallback(messages, category, reason=reason)