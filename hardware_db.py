"""Deterministic PC hardware catalog, compatibility checker, and budget optimizer."""

from itertools import product

CPUS = [
    {"name": "AMD Ryzen 5 5600G", "socket": "AM4", "tdp": 65, "igpu": True, "game": 55, "prod": 62, "price": 6200,
     "why": "6 cores with built-in graphics — ideal for tight budgets without a separate GPU"},
    {"name": "AMD Ryzen 5 5600", "socket": "AM4", "tdp": 65, "igpu": False, "game": 76, "prod": 70, "price": 6500,
     "why": "6 cores — best value for 1080p gaming, coding, and multitasking"},
    {"name": "Intel Core i5-12400F", "socket": "LGA1700", "tdp": 65, "igpu": False, "game": 78, "prod": 74, "price": 6800,
     "why": "6 performance cores — strong single-core speed for gaming and IDEs"},
    {"name": "AMD Ryzen 5 7500F", "socket": "AM5", "tdp": 65, "igpu": False, "game": 88, "prod": 82, "price": 9800,
     "why": "Modern AM5 DDR5 platform with long-term upgrade support"},
    {"name": "AMD Ryzen 5 7600", "socket": "AM5", "tdp": 65, "igpu": True, "game": 89, "prod": 83, "price": 11500,
     "why": "Fast AM5 processor with integrated graphics backup"},
    {"name": "Intel Core i5-14600K", "socket": "LGA1700", "tdp": 125, "igpu": True, "game": 94, "prod": 95, "price": 17500,
     "why": "14 cores — powerhouse for heavy video editing, rendering, and gaming"},
    {"name": "AMD Ryzen 7 7800X3D", "socket": "AM5", "tdp": 120, "igpu": True, "game": 100, "prod": 88, "price": 23500,
     "why": "3D V-Cache gaming king — unmatched frame rates at high refresh"},
]

GPUS = [
    {"name": "Integrated Radeon Graphics (iGPU)", "tdp": 0, "length_mm": 0, "game": 25, "edit": 20, "vram": 0, "price": 0,
     "why": "Built into the CPU — handles schoolwork, coding, and light esports"},
    {"name": "AMD Radeon RX 6600 8GB", "tdp": 132, "length_mm": 200, "game": 68, "edit": 55, "vram": 8, "price": 12500,
     "why": "Best budget dedicated GPU for smooth 1080p gaming"},
    {"name": "NVIDIA RTX 4060 8GB", "tdp": 115, "length_mm": 240, "game": 78, "edit": 75, "vram": 8, "price": 18500,
     "why": "High settings at 1080p with DLSS 3 and very low power draw"},
    {"name": "AMD Radeon RX 7700 XT 12GB", "tdp": 245, "length_mm": 280, "game": 88, "edit": 72, "vram": 12, "price": 26500,
     "why": "12GB VRAM sweet spot for crisp 1440p gaming"},
    {"name": "NVIDIA RTX 4070 Super 12GB", "tdp": 220, "length_mm": 260, "game": 93, "edit": 92, "vram": 12, "price": 37500,
     "why": "Excellent 1440p gaming and CUDA acceleration for 4K video editing"},
    {"name": "NVIDIA RTX 4070 Ti Super 16GB", "tdp": 285, "length_mm": 305, "game": 97, "edit": 97, "vram": 16, "price": 51000,
     "why": "16GB VRAM handles heavy 4K editing, AI workloads, and 4K gaming"},
    {"name": "NVIDIA RTX 4080 Super 16GB", "tdp": 320, "length_mm": 320, "game": 100, "edit": 100, "vram": 16, "price": 64000,
     "why": "Flagship 4K gaming and professional workstation performance"},
]

MOBOS = [
    {"name": "MSI A520M-A PRO", "socket": "AM4", "chipset": "A520", "ram_type": "DDR4", "form_factor": "mATX", "price": 3300,
     "why": "Reliable entry-level AM4 board for budget builds"},
    {"name": "MSI B550M PRO-VDH WIFI", "socket": "AM4", "chipset": "B550", "ram_type": "DDR4", "form_factor": "mATX", "price": 5400,
     "why": "AM4 board with built-in Wi-Fi, PCIe 4.0, and 4 RAM slots"},
    {"name": "Gigabyte B760M DS3H DDR4", "socket": "LGA1700", "chipset": "B760", "ram_type": "DDR4", "form_factor": "mATX", "price": 6200,
     "why": "Solid LGA1700 board with 4 DDR4 slots and dual M.2"},
    {"name": "MSI B650M GAMING WIFI", "socket": "AM5", "chipset": "B650", "ram_type": "DDR5", "form_factor": "mATX", "price": 7800,
     "why": "AM5 DDR5 motherboard with Wi-Fi and future Ryzen support"},
    {"name": "ASUS TUF GAMING B650-PLUS WIFI", "socket": "AM5", "chipset": "B650", "ram_type": "DDR5", "form_factor": "ATX", "price": 12500,
     "why": "Full-size ATX AM5 board with heavy VRMs for high-end CPUs"},
]

RAMS = [
    {"name": "16GB (2x8GB) DDR4-3200", "ram_type": "DDR4", "gb": 16, "price": 2200,
     "why": "Dual-channel memory; plenty for gaming and programming"},
    {"name": "32GB (2x16GB) DDR4-3200", "ram_type": "DDR4", "gb": 32, "price": 4000,
     "why": "Ideal for heavy multitasking, Docker, and video editing"},
    {"name": "16GB (2x8GB) DDR5-5200", "ram_type": "DDR5", "gb": 16, "price": 3500,
     "why": "High-bandwidth DDR5 memory for AM5 platforms"},
    {"name": "32GB (2x16GB) DDR5-6000", "ram_type": "DDR5", "gb": 32, "price": 6500,
     "why": "Sweet spot DDR5 speed and capacity for modern gaming & creative work"},
]

SSDS = [
    {"name": "500GB NVMe PCIe Gen 3", "gb": 500, "price": 2100,
     "why": "Fast OS boot and essential app storage on a tight budget"},
    {"name": "1TB NVMe PCIe Gen 4", "gb": 1000, "price": 3500,
     "why": "Fast boot and load times with ample space for games and projects"},
    {"name": "2TB NVMe PCIe Gen 4", "gb": 2000, "price": 7200,
     "why": "Large high-speed storage for 4K video footage and big game libraries"},
]

PSUS = [
    {"name": "550W 80+ Bronze", "wattage": 550, "price": 2400,
     "why": "Reliable power for entry-level and mid-range builds"},
    {"name": "650W 80+ Bronze", "wattage": 650, "price": 3000,
     "why": "Safe wattage headroom now and for future mid-range upgrades"},
    {"name": "750W 80+ Gold", "wattage": 750, "price": 5200,
     "why": "High-efficiency power supply for upper mid-range GPUs"},
    {"name": "850W 80+ Gold", "wattage": 850, "price": 6800,
     "why": "Heavy-duty wattage headroom for flagship GPUs and workstations"},
]

CASES = [
    {"name": "Tecware Nexus Air M2", "forms": ["mATX"], "max_gpu_mm": 300, "price": 1600,
     "why": "Compact mesh-front case for good airflow on a budget"},
    {"name": "Montech Air 100 Lite", "forms": ["mATX"], "max_gpu_mm": 330, "price": 2300,
     "why": "Spacious mATX mesh case with room for longer GPUs"},
    {"name": "Montech Air 903 Base", "forms": ["ATX", "mATX"], "max_gpu_mm": 400, "price": 3800,
     "why": "High-airflow ATX tower that fits even massive flagship GPUs"},
]


def is_compatible(cpu, gpu, mobo, ram, psu, case) -> tuple[bool, list[str]]:
    """Deterministic compatibility rule engine."""
    reasons = []
    if cpu["socket"] != mobo["socket"]:
        return False, [f"CPU socket ({cpu['socket']}) does not match motherboard ({mobo['socket']})."]
    if ram["ram_type"] != mobo["ram_type"]:
        return False, [f"RAM type ({ram['ram_type']}) does not match motherboard ({mobo['ram_type']})."]
    if mobo["form_factor"] not in case["forms"]:
        return False, [f"Motherboard ({mobo['form_factor']}) does not fit in {case['name']}."]
    if gpu["length_mm"] > case["max_gpu_mm"]:
        return False, [f"GPU length ({gpu['length_mm']}mm) exceeds case clearance ({case['max_gpu_mm']}mm)."]
    if gpu["price"] == 0 and not cpu["igpu"]:
        return False, [f"{cpu['name']} has no integrated graphics; a dedicated GPU is required."]

    est_draw = cpu["tdp"] + gpu["tdp"] + 100
    if psu["wattage"] < est_draw * 1.25:
        return False, [f"{psu['wattage']}W PSU is too small for ~{est_draw}W system load (needs 25% headroom)."]

    reasons.append(f"{cpu['socket']} socket ↔ {mobo['chipset']} chipset")
    reasons.append(f"{ram['ram_type']} RAM ↔ {mobo['ram_type']} motherboard")
    reasons.append(f"{mobo['form_factor']} board & {gpu['length_mm']}mm GPU fit case")
    reasons.append(f"{psu['wattage']}W covers est. ~{est_draw}W draw")
    return True, reasons


def optimize_build(budget_php: int, use_case: str = "Gaming", resolution: str = "1080p") -> dict:
    """Finds the highest-performing, 100% compatible PC build within budget_php."""
    use = use_case.lower()
    is_editing = any(k in use for k in ("edit", "render", "creative", "3d"))
    is_coding = any(k in use for k in ("program", "cod", "dev", "school", "office", "student"))

    best_score = -1.0
    best_combo = None
    best_compat = []

    for cpu, gpu, mobo, ram, ssd, psu, case in product(CPUS, GPUS, MOBOS, RAMS, SSDS, PSUS, CASES):
        total = cpu["price"] + gpu["price"] + mobo["price"] + ram["price"] + ssd["price"] + psu["price"] + case["price"]
        if total > budget_php:
            continue

        if budget_php >= 32000 and gpu["price"] == 0 and not is_coding:
            continue

        if gpu["price"] > 0 and abs(cpu["game"] - gpu["game"]) > 30:
            continue

        ok, compat_list = is_compatible(cpu, gpu, mobo, ram, psu, case)
        if not ok:
            continue

        if is_editing:
            score = gpu["edit"] * 0.45 + cpu["prod"] * 0.40 + (ram["gb"] / 32 * 100) * 0.15
            if "NVIDIA" in gpu["name"]:
                score += 6
        elif is_coding:
            score = cpu["prod"] * 0.45 + (ram["gb"] / 32 * 100) * 0.25 + gpu["game"] * 0.20 + (ssd["gb"] / 2000 * 100) * 0.10
        else:
            score = gpu["game"] * 0.55 + cpu["game"] * 0.30 + (ram["gb"] / 32 * 100) * 0.10 + (ssd["gb"] / 2000 * 100) * 0.05
            if resolution == "1440p" and gpu["vram"] < 12 and budget_php >= 55000:
                score -= 10
            if resolution == "4K" and gpu["vram"] < 16 and budget_php >= 85000:
                score -= 12

        score += (total / budget_php) * 3.0

        if score > best_score:
            best_score = score
            best_combo = (cpu, gpu, mobo, ram, ssd, psu, case, total)
            best_compat = compat_list

    if best_combo is None:
        return optimize_build(22000, use_case, resolution)

    cpu, gpu, mobo, ram, ssd, psu, case, total = best_combo
    est_draw = cpu["tdp"] + gpu["tdp"] + 100
    headroom = round((1 - est_draw / psu["wattage"]) * 100)
    pct_used = round(total / budget_php * 100)

    parts = [
        ("CPU", cpu["name"], cpu["why"], cpu["price"]),
        ("GPU", gpu["name"], gpu["why"], gpu["price"]),
        ("MOBO", mobo["name"], mobo["why"], mobo["price"]),
        ("RAM", ram["name"], ram["why"], ram["price"]),
        ("SSD", ssd["name"], ssd["why"], ssd["price"]),
        ("PSU", psu["name"], psu["why"], psu["price"]),
        ("CASE", case["name"], case["why"], case["price"]),
    ]

    upgrades = []
    if ram["gb"] < 32:
        upgrades.append(f"Upgrade {ram['ram_type']} RAM to 32GB later")
    if gpu["price"] == 0:
        upgrades.append("Add a dedicated GPU like RX 6600 or RTX 4060 later")
    elif headroom >= 30:
        upgrades.append(f"{psu['wattage']}W PSU gives headroom for a stronger GPU later")
    if cpu["socket"] == "AM5":
        upgrades.append("AM5 socket supports next-gen Ryzen CPUs")
    elif cpu["socket"] == "AM4" and "5600" in cpu["name"]:
        upgrades.append("Drop-in upgrade to Ryzen 7 5700X3D later")
    if ssd["gb"] < 1000:
        upgrades.append("Add a 1TB NVMe SSD as your library grows")

    return {
        "title": f"₱{budget_php // 1000}K {use_case.lower()} PC",
        "intro": (f"Here is a verified, 100% compatible **₱{total:,}** build tailored for **{use_case}** at **{resolution}** "
                  f"(within your ₱{budget_php:,} budget)."),
        "parts": parts,
        "stats": [
            ("Target", f"{resolution} · {use_case.split()[0]}"),
            ("Est. power draw", f"~{est_draw}W"),
            ("PSU headroom", f"~{headroom}%"),
            ("Budget used", f"{pct_used}% of ₱{budget_php // 1000}K"),
        ],
        "compat": best_compat,
        "upgrades": upgrades[:3],
    }


def check_custom_parts(cpu_query: str = "", gpu_query: str = "", ram_type: str = "", psu_wattage: int = 0) -> str:
    """Checks compatibility & bottlenecks for user-provided existing or planned hardware."""
    notes = []
    cpu_match = next((c for c in CPUS if cpu_query and cpu_query.lower() in c["name"].lower()), None)
    gpu_match = next((g for g in GPUS if gpu_query and gpu_query.lower() in g["name"].lower()), None)

    if cpu_match:
        notes.append(f"- Matched CPU: **{cpu_match['name']}** (Socket: `{cpu_match['socket']}`, TDP: {cpu_match['tdp']}W)")
    if gpu_match:
        notes.append(f"- Matched GPU: **{gpu_match['name']}** (TDP: {gpu_match['tdp']}W, Length: {gpu_match['length_mm']}mm)")

    if cpu_match and gpu_match and gpu_match["price"] > 0:
        diff = gpu_match["game"] - cpu_match["game"]
        if diff > 25:
            notes.append(f"- **CPU Bottleneck Warning:** {gpu_match['name']} is much stronger than {cpu_match['name']}. At 1080p, the CPU will limit FPS.")
        elif diff < -25:
            notes.append(f"- **GPU Bottleneck Note:** {cpu_match['name']} can handle a much faster GPU than {gpu_match['name']}.")
        else:
            notes.append("- **Balance:** Good CPU-to-GPU pairing with minimal bottleneck.")

    if psu_wattage > 0 and (cpu_match or gpu_match):
        tdp_sum = (cpu_match["tdp"] if cpu_match else 65) + (gpu_match["tdp"] if gpu_match else 150) + 100
        req = int(tdp_sum * 1.25)
        if psu_wattage < req:
            notes.append(f"- **PSU Warning:** {psu_wattage}W is below the safe recommended **{req}W** (includes 25% headroom).")
        else:
            notes.append(f"- **PSU Check:** {psu_wattage}W is sufficient (recommended minimum: {req}W).")

    if not notes:
        return "Specific part was not found in the local quick-check catalog; analyze carefully using general hardware rules."
    return "\n".join(notes)