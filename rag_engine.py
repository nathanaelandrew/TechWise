"""Hybrid RAG engine: ChromaDB vector store + Tavily/DuckDuckGo live web search."""

import os
import chromadb

# Curated hardware buying guides & beginner explanations indexed in ChromaDB
KNOWLEDGE_DOCS = [
    {
        "id": "ram_programming_vs_gaming",
        "text": ("For programming and CS coursework (IDEs like VS Code, IntelliJ, Docker, browser tabs), "
                 "RAM capacity (at least 16GB, ideally 32GB for Docker/VMs) and multi-core CPU speed matter far more "
                 "than a dedicated GPU. An integrated GPU is enough for coding unless doing 3D game dev or local AI training.")
    },
    {
        "id": "vram_explained",
        "text": ("VRAM (Video RAM) is dedicated memory on the graphics card used for textures, shadows, and frame buffers. "
                 "8GB VRAM is fine for 1080p gaming. 12GB VRAM is recommended for 1440p gaming and light 4K editing. "
                 "16GB+ VRAM is ideal for 4K gaming, heavy 4K timeline editing, and running local AI models.")
    },
    {
        "id": "ddr4_vs_ddr5",
        "text": ("DDR4 and DDR5 are NOT physically interchangeable—their slot notches differ. "
                 "AM4 motherboards only use DDR4. AM5 motherboards only use DDR5. Intel LGA1700 boards come in either "
                 "DDR4 or DDR5 versions depending on the specific motherboard model. Dual-channel (2 sticks, e.g., 2x8GB) "
                 "is noticeably faster than 1 single stick.")
    },
    {
        "id": "psu_headroom",
        "text": ("Power Supply Unit (PSU) wattage should exceed total system TDP (CPU + GPU + ~100W for drives/fans) "
                 "by at least 25% to 35% headroom. This keeps the PSU cool, quiet, efficient (peak efficiency at ~50-60% load), "
                 "and safe for sudden GPU power spikes. Never open a PSU casing—capacitors hold lethal high voltage.")
    },
    {
        "id": "bottleneck_basics",
        "text": ("A hardware bottleneck happens when one component limits the full potential of another. "
                 "Pairing a modern high-end GPU (like RTX 4070) with an old 4-core CPU (like Core i3-9100) causes a CPU bottleneck: "
                 "stuttering and low GPU utilization, especially at 1080p. Raising resolution to 1440p shifts load back to the GPU.")
    },
    {
        "id": "ips_vs_oled",
        "text": ("IPS monitors offer great color accuracy, wide viewing angles, and zero burn-in risk at budget prices. "
                 "OLED panels deliver true infinite blacks, instant pixel response, and vivid HDR, but cost more and carry "
                 "minor burn-in risk on static elements over years.")
    },
    {
        "id": "video_editing_workstation",
        "text": ("For 4K video editing: Apple MacBook Pro (M-series) excels in battery efficiency, ProRes hardware encoders, "
                 "and color-accurate displays on the go. Windows RTX workstations excel in CUDA-accelerated effects in Premiere Pro/"
                 "DaVinci Resolve, upgradable RAM/SSD, and gaming capability.")
    },
    {
        "id": "laptop_buying_ph",
        "text": ("When recommending budget laptops for students in the Philippines (₱25,000–₱45,000): look for at least "
                 "Ryzen 5 / Core i5 (12th gen+ or Ryzen 5000/7000+), 16GB RAM (or 8GB with an empty upgradable SO-DIMM slot), "
                 "512GB NVMe SSD, and an IPS FHD display. Avoid 4GB RAM or eMMC storage laptops.")
    },
]

_collection = None


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path="./chroma_db")
        _collection = client.get_or_create_collection(name="techwise_guides")
        if _collection.count() == 0:
            _collection.add(
                ids=[d["id"] for d in KNOWLEDGE_DOCS],
                documents=[d["text"] for d in KNOWLEDGE_DOCS],
            )
    return _collection


def query_rag(query: str, n_results: int = 3) -> str:
    """Retrieves relevant hardware knowledge chunks from ChromaDB."""
    try:
        col = _get_collection()
        res = col.query(query_texts=[query], n_results=n_results)
        docs = res.get("documents", [[]])[0]
        return "\n\n".join(f"- {d}" for d in docs) if docs else "No relevant guide found."
    except Exception as e:
        return f"RAG lookup unavailable: {e}"


def live_web_search(query: str, tavily_api_key: str | None = None) -> str:
    """Searches live web prices, laptop models, or specs using Tavily (preferred) or DuckDuckGo."""
    api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")

    # 1. Try Tavily API (if key configured)
    if api_key:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=api_key)
            resp = client.search(query=query, max_results=4, search_depth="basic")
            results = resp.get("results", [])
            if results:
                return "\n".join(
                    f"- **{r.get('title', 'Result')}** ({r.get('url', '')}): {r.get('content', '')[:300]}"
                    for r in results
                )
        except Exception:
            pass  # Fall through to DuckDuckGo

    # 2. Fallback: Free DuckDuckGo search (no API key needed)
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
        if results:
            return "\n".join(
                f"- **{r.get('title', 'Result')}** ({r.get('href', '')}): {r.get('body', '')[:300]}"
                for r in results
            )
    except Exception as e:
        return f"Live search failed ({e}). Rely on general estimates and explicitly state prices are estimates."

    return "No live search results found. Clarify that prices are estimates."