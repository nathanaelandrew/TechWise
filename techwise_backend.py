"""TechWise LLM Agent connecting system prompt, RAG, Search API, and Deterministic Builder."""

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
- `build_pc_within_budget`: Call this whenever the user asks for a desktop PC build or setup for a budget. When you call this tool, the app automatically renders an interactive parts table, budget breakdown, compatibility check, and upgrade path below your message—so keep your text response as a helpful, concise explanation and DO NOT repeat a giant Markdown table in text!
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
            "description": "Generates a 100% compatible, budget-optimized desktop PC parts list in Philippine Pesos (₱).",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget_php": {"type": "integer", "description": "User's budget in Philippine Pesos (e.g. 40000)."},
                    "use_case": {"type": "string", "description": "Primary use: Gaming, Programming, Video editing, or School & office."},
                    "resolution": {"type": "string", "description": "Target display resolution: 1080p, 1440p, or 4K."}
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


def _get_gemini_candidates(api_key: str) -> list[str]:
    """Builds an ordered list of Gemini models, starting with newest 3.x/2.x flash models."""
    explicit_first = [
        "gemini-4-hydrogen",
        "gemini-3.8-flash",
        "gemini-3.0-flash",
        "gemini-3-flash",
        "gemini-3-flash-preview",
        "gemini-2.0-flash",
        "gemini-2.5-flash",
    ]

    r = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=15)
    if not r.ok:
        raise RuntimeError(f"Gemini key check failed (HTTP {r.status_code}): {r.text[:300]}")

    skip_words = ("embedding", "imagen", "veo", "tts", "audio", "robotics", "computer-use", "aqa")
    discovered = []
    for m in r.json().get("models", []):
        if "generateContent" not in m.get("supportedGenerationMethods", []):
            continue
        name = m["name"].removeprefix("models/")
        low = name.lower()
        if "gemini" not in low or any(w in low for w in skip_words):
            continue
        discovered.append(name)

    def _rank(name: str) -> tuple:
        low = name.lower()
        ver_match = re.search(r"gemini-(\d+(?:\.\d+)?)", low)
        ver = float(ver_match.group(1)) if ver_match else 0.0
        is_flash = 2 if ("flash" in low and "lite" not in low) else (1 if "flash" in low else 0)
        is_stable = 1 if ("exp" not in low and "preview" not in low) else 0
        return (ver, is_flash, is_stable, name)

    ordered = []
    cached = st.session_state.get("_gemini_model")
    if cached:
        ordered.append(cached)
    for m in explicit_first + sorted(discovered, key=_rank, reverse=True):
        if m not in ordered:
            ordered.append(m)
    return ordered


def _post_gemini_with_fallback(api_key: str, candidates: list[str], payload: dict) -> tuple[dict, str]:
    """Posts to Gemini generateContent, falling back across models on 404, 429, or 503."""
    tried = []
    last_msg = ""
    for model in candidates[:12]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        r = requests.post(url, json=payload, timeout=45)
        if r.ok:
            st.session_state["_gemini_model"] = model
            return r.json(), model
        if r.status_code in (404, 429, 500, 503):
            tried.append(f"{model} ({r.status_code})")
            # Prefer keeping real 429/503 outage messages over 404 deprecation messages
            if r.status_code != 404 or not last_msg:
                last_msg = f"HTTP {r.status_code} ({model}): {r.text[:250]}"
            continue
        raise RuntimeError(f"HTTP {r.status_code} ({model}): {r.text[:300]}")

    raise RuntimeError(f"No available model succeeded. Tried: {', '.join(tried)}. Details: {last_msg}")


def _run_gemini(api_key: str, system_text: str, messages: list[dict], tavily_key: str | None) -> dict:
    """Uses Google's native Gemini REST API with function calling and automatic model fallback."""
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
        # Lock onto the working model for subsequent tool turns
        candidates = [active_model]

        cand_list = data.get("candidates", [])
        if not cand_list:
            return {"content": "I couldn't generate a response for that prompt. Please try rephrasing.", "build": generated_build}

        cand_content = cand_list[0]["content"]
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


def _run_openai_compat(client: OpenAI, model: str, system_text: str, messages: list[dict], tavily_key: str | None) -> dict:
    """Runs tool-calling loop for Groq or OpenAI."""
    convo = [{"role": "system", "content": system_text}] + messages
    generated_build = None

    for _ in range(4):
        response = client.chat.completions.create(
            model=model,
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

    try:
        if key := _get_secret("GEMINI_API_KEY"):
            return _run_gemini(key, system_text, messages, tavily_key)
        if key := _get_secret("GROQ_API_KEY"):
            return _run_openai_compat(OpenAI(api_key=key, base_url="https://api.groq.com/openai/v1"),
                                      "llama-3.3-70b-versatile", system_text, messages, tavily_key)
        if key := _get_secret("OPENAI_API_KEY"):
            return _run_openai_compat(OpenAI(api_key=key), "gpt-4o-mini", system_text, messages, tavily_key)
        return {"content": "⚠️ **Setup needed:** Add `GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENAI_API_KEY` to `.streamlit/secrets.toml`.", "error": True}
    except Exception as e:
        return {"content": f"⚠️ **API error:** `{e}`", "error": True}