import os
import json
import random
from datetime import datetime, timedelta
from pytz import timezone

from PyroUbot import *

__MODULE__ = "growgarden"
__HELP__ = """
<blockquote><b>Game Grow Garden</b>

- <code>.ggstart</code> → buat kebun
- <code>.gg</code> → lihat kebun
- <code>.ggshop</code> → toko benih
- <code>.ggbuy id qty</code> → beli (qty opsional)
- <code>.ggplant seed_id slot</code> → tanam
- <code>.ggwater slot</code> / <code>all</code> → siram (percepat)
- <code>.ggharvest slot</code> / <code>all</code> → panen
- <code>.ggupgrade</code> → tambah slot lahan
- <code>.ggtop</code> → leaderboard XP panen</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Seeds shop: grow_min/max (minutes), sell_min/max, xp
SEEDS = [
    {"id": 1, "name": "🥕 Wortel", "price": 40, "grow": (3, 5), "sell": (55, 85), "xp": 6},
    {"id": 2, "name": "🍅 Tomat", "price": 60, "grow": (5, 7), "sell": (85, 130), "xp": 9},
    {"id": 3, "name": "🌽 Jagung", "price": 85, "grow": (7, 10), "sell": (130, 190), "xp": 12},
    {"id": 4, "name": "🍓 Stroberi", "price": 120, "grow": (9, 13), "sell": (190, 280), "xp": 17},
    {"id": 5, "name": "🍇 Anggur", "price": 180, "grow": (12, 16), "sell": (280, 420), "xp": 25},
]

ITEMS = [
    {"id": 101, "name": "💧 Pupuk Air (skip 2 menit)", "price": 90, "type": "water_boost", "value": 2},
    {"id": 102, "name": "🧪 Fertilizer (bonus hasil +20% 3x panen)", "price": 220, "type": "yield_boost", "value": 3},
]

BASE_SLOTS = 4
UPGRADE_BASE_COST = 300  # naik tiap upgrade
WATER_CD_SEC = 45        # cooldown siram

def _load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"users": {}}

def _save_db(db):
    tmp = DB_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DB_FILE)

def _get_user(db, user_id: int):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"uang": 0, "garden": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("garden", None)
    return u

def _lvl_from_xp(xp: int) -> int:
    return 1 + (xp // 120)

def _seed_by_id(seed_id: int):
    return next((s for s in SEEDS if s["id"] == seed_id), None)

def _item_by_id(item_id: int):
    return next((i for i in ITEMS if i["id"] == item_id), None)

def _ensure_garden(u):
    if u.get("garden") is None:
        u["garden"] = {
            "xp": 0,
            "slots": BASE_SLOTS,
            "plots": {},      # slot(str)-> plot dict
            "inv": {},        # seed_id(str)-> qty
            "items": {"water_boost": 0, "yield_boost": 0},
            "last_water_ts": 0,
        }
    else:
        g = u["garden"]
        g.setdefault("xp", 0)
        g.setdefault("slots", BASE_SLOTS)
        g.setdefault("plots", {})
        g.setdefault("inv", {})
        g.setdefault("items", {"water_boost": 0, "yield_boost": 0})
        g["items"].setdefault("water_boost", 0)
        g["items"].setdefault("yield_boost", 0)
        g.setdefault("last_water_ts", 0)

def _now():
    return datetime.now(TZ)

def _fmt_dt(dt: datetime) -> str:
    return dt.strftime("%d-%m %H:%M:%S")

def _remaining_sec(ready_iso: str) -> int:
    try:
        ready = datetime.fromisoformat(ready_iso)
    except:
        return 0
    return int((ready - _now()).total_seconds())

def _plot_status(plot):
    if not plot:
        return "kosong"
    if plot.get("harvested"):
        return "kosong"
    sec = _remaining_sec(plot["ready_at"])
    if sec <= 0:
        return "siap panen ✅"
    m, s = divmod(sec, 60)
    return f"tumbuh ⏳ {m}m {s}s"

def _make_plot(seed, slot: int):
    grow_min, grow_max = seed["grow"]
    minutes = random.randint(grow_min, grow_max)
    ready_at = _now() + timedelta(minutes=minutes)
    return {
        "seed_id": seed["id"],
        "name": seed["name"],
        "ready_at": ready_at.isoformat(),
        "base_sell_min": seed["sell"][0],
        "base_sell_max": seed["sell"][1],
        "xp": seed["xp"],
        "slot": slot,
        "harvested": False,
    }

def _can_water(g):
    now_ts = int(_now().timestamp())
    last = int(g.get("last_water_ts", 0))
    return (now_ts - last) >= WATER_CD_SEC

def _upgrade_cost(g):
    # cost naik sesuai jumlah slot
    extra = max(0, int(g.get("slots", BASE_SLOTS)) - BASE_SLOTS)
    return UPGRADE_BASE_COST + extra * 180

@PY.UBOT("ggstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ GROW GARDEN AKTIF</b>
{message.from_user.mention}

Cek kebun: <code>.gg</code>
Beli benih: <code>.ggshop</code> lalu <code>.ggbuy id qty</code>
Tanam: <code>.ggplant seed_id slot</code></blockquote>
""")

@PY.UBOT("gg")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    g = u["garden"]

    lvl = _lvl_from_xp(int(g["xp"]))
    slots = int(g["slots"])
    plots = g.get("plots", {})
    inv = g.get("inv", {})

    inv_lines = []
    for sid, qty in sorted(inv.items(), key=lambda x: int(x[0])):
        seed = _seed_by_id(int(sid))
        if seed and int(qty) > 0:
            inv_lines.append(f"- {seed['name']} x<code>{qty}</code>")
    if not inv_lines:
        inv_lines = ["- (kosong)"]

    plot_lines = []
    for i in range(1, slots + 1):
        p = plots.get(str(i))
        if not p or p.get("harvested"):
            plot_lines.append(f"{i}. ⬜ kosong")
        else:
            st = _plot_status(p)
            plot_lines.append(f"{i}. {p['name']} — <b>{st}</b>")

    items = g.get("items", {})
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🌱 KEBUN</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code> | <b>XP:</b> <code>{g['xp']}</code>
<b>Slot:</b> <code>{slots}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Benih:</b>
{chr(10).join(inv_lines)}

<b>Lahan:</b>
{chr(10).join(plot_lines)}

<b>Item:</b>
- 💧 Water Boost: <code>{int(items.get('water_boost',0))}</code>
- 🧪 Yield Boost: <code>{int(items.get('yield_boost',0))}</code>

Upgrade slot: <code>.ggupgrade</code> (biaya: <code>{_upgrade_cost(g)}</code>)</blockquote>
""")

@PY.UBOT("ggshop")
async def _(client, message):
    seed_lines = [f"{s['id']}. {s['name']} — <code>{s['price']}</code> uang | grow ~{s['grow'][0]}-{s['grow'][1]}m" for s in SEEDS]
    item_lines = [f"{i['id']}. {i['name']} — <code>{i['price']}</code> uang" for i in ITEMS]
    await message.reply(
        "<blockquote><b>🛒 GARDEN SHOP</b>\n\n"
        "<b>Benih</b>\n" + "\n".join(seed_lines) +
        "\n\n<b>Item</b>\n" + "\n".join(item_lines) +
        "\n\nBeli: <code>.ggbuy id qty</code> (qty opsional, default 1)</blockquote>"
    )

@PY.UBOT("ggbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.ggbuy id qty</code>\nContoh: <code>.ggbuy 2 3</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    seed = _seed_by_id(item_id)
    it = _item_by_id(item_id)
    if not seed and not it:
        return await message.reply("<blockquote>ID tidak ditemukan. Cek: <code>.ggshop</code></blockquote>")

    price = (seed["price"] if seed else it["price"]) * qty

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    g = u["garden"]

    if int(u["uang"]) < price:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{price}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - price

    if seed:
        inv = g["inv"]
        inv[str(seed["id"])] = int(inv.get(str(seed["id"]), 0)) + qty
        note = f"✅ Beli {seed['name']} x<code>{qty}</code>"
    else:
        g["items"][it["type"]] = int(g["items"].get(it["type"], 0)) + qty
        note = f"✅ Beli {it['name']} x<code>{qty}</code>"

    _save_db(db)
    await message.reply(f"<blockquote>{note}\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("ggplant")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 3:
        return await message.reply("<blockquote>Format: <code>.ggplant seed_id slot</code>\nContoh: <code>.ggplant 1 2</code></blockquote>")
    try:
        seed_id = int(parts[1])
        slot = int(parts[2])
    except:
        return await message.reply("<blockquote>Seed/slot harus angka.</blockquote>")

    seed = _seed_by_id(seed_id)
    if not seed:
        return await message.reply("<blockquote>Seed tidak ada. Cek: <code>.ggshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    g = u["garden"]

    if slot < 1 or slot > int(g["slots"]):
        _save_db(db)
        return await message.reply("<blockquote>Slot tidak valid. Cek slot di <code>.gg</code></blockquote>")

    plots = g["plots"]
    existing = plots.get(str(slot))
    if existing and not existing.get("harvested"):
        _save_db(db)
        return await message.reply("<blockquote>Slot itu masih terpakai. Panen dulu.</blockquote>")

    inv = g["inv"]
    if int(inv.get(str(seed_id), 0)) <= 0:
        _save_db(db)
        return await message.reply("<blockquote>Benih kamu habis. Beli dulu: <code>.ggshop</code></blockquote>")

    inv[str(seed_id)] = int(inv.get(str(seed_id), 0)) - 1
    plot = _make_plot(seed, slot)
    plots[str(slot)] = plot

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🌱 BERHASIL TANAM</b>
{message.from_user.mention}

<b>Tanaman:</b> {seed['name']}
<b>Slot:</b> <code>{slot}</code>
<b>Siap panen:</b> <code>{_fmt_dt(datetime.fromisoformat(plot['ready_at']))}</code>

Cek kebun: <code>.gg</code></blockquote>
""")

@PY.UBOT("ggwater")
async def _(client, message):
    parts = (message.text or "").split(maxsplit=1)
    target = parts[1].strip().lower() if len(parts) > 1 else ""
    if not target:
        return await message.reply("<blockquote>Format: <code>.ggwater slot</code> atau <code>.ggwater all</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    g = u["garden"]

    if not _can_water(g):
        now_ts = int(_now().timestamp())
        last = int(g.get("last_water_ts", 0))
        sisa = WATER_CD_SEC - (now_ts - last)
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown siram. Coba lagi <b>{sisa}s</b>.</blockquote>")

    boost_min = 1
    # kalau punya water_boost, pakai 1 untuk mempercepat lebih jauh
    extra = 0
    if int(g["items"].get("water_boost", 0)) > 0:
        extra = 2
        g["items"]["water_boost"] = int(g["items"]["water_boost"]) - 1

    reduce = boost_min + extra  # menit dipercepat

    plots = g["plots"]
    affected = 0

    def apply(slot_str):
        nonlocal affected
        p = plots.get(slot_str)
        if not p or p.get("harvested"):
            return
        ready = datetime.fromisoformat(p["ready_at"]) - timedelta(minutes=reduce)
        p["ready_at"] = ready.isoformat()
        affected += 1

    if target == "all":
        for i in range(1, int(g["slots"]) + 1):
            apply(str(i))
    else:
        try:
            slot = int(target)
        except:
            _save_db(db)
            return await message.reply("<blockquote>Slot harus angka atau 'all'.</blockquote>")
        if slot < 1 or slot > int(g["slots"]):
            _save_db(db)
            return await message.reply("<blockquote>Slot tidak valid.</blockquote>")
        apply(str(slot))

    g["last_water_ts"] = int(_now().timestamp())
    _save_db(db)

    note = f"✅ Siram berhasil, mempercepat <code>{reduce} menit</code>."
    if extra:
        note += " (pakai 1 Water Boost)"
    await message.reply(f"<blockquote>{note}\nTerpengaruh: <code>{affected}</code> lahan.\nCek: <code>.gg</code></blockquote>")

@PY.UBOT("ggharvest")
async def _(client, message):
    parts = (message.text or "").split(maxsplit=1)
    target = parts[1].strip().lower() if len(parts) > 1 else ""
    if not target:
        return await message.reply("<blockquote>Format: <code>.ggharvest slot</code> atau <code>.ggharvest all</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    g = u["garden"]
    plots = g["plots"]

    yield_boost = int(g["items"].get("yield_boost", 0))

    def harvest_one(slot_str):
        nonlocal yield_boost
        p = plots.get(slot_str)
        if not p or p.get("harvested"):
            return (0, 0, 0, None, "kosong")
        sec = _remaining_sec(p["ready_at"])
        if sec > 0:
            return (0, 0, 0, p, "belum")
        base = random.randint(int(p["base_sell_min"]), int(p["base_sell_max"]))
        if yield_boost > 0:
            base = int(base * 1.2)
            yield_boost -= 1
        xp = int(p["xp"])
        p["harvested"] = True
        return (base, xp, 1, p, "ok")

    total_uang = 0
    total_xp = 0
    total_ok = 0
    not_ready = 0
    empty = 0

    if target == "all":
        for i in range(1, int(g["slots"]) + 1):
            uang, xp, ok, p, st = harvest_one(str(i))
            total_uang += uang
            total_xp += xp
            total_ok += ok
            if st == "belum": not_ready += 1
            if st == "kosong": empty += 1
    else:
        try:
            slot = int(target)
        except:
            _save_db(db)
            return await message.reply("<blockquote>Slot harus angka atau 'all'.</blockquote>")
        if slot < 1 or slot > int(g["slots"]):
            _save_db(db)
            return await message.reply("<blockquote>Slot tidak valid.</blockquote>")
        uang, xp, ok, p, st = harvest_one(str(slot))
        total_uang, total_xp, total_ok = uang, xp, ok
        if st == "belum": not_ready = 1
        if st == "kosong": empty = 1

    # update yield_boost remaining
    g["items"]["yield_boost"] = yield_boost

    if total_ok == 0:
        _save_db(db)
        msg = "❌ Tidak ada yang bisa dipanen."
        if not_ready:
            msg += " Masih ada yang belum siap."
        return await message.reply(f"<blockquote>{msg}\nCek: <code>.gg</code></blockquote>")

    u["uang"] = int(u["uang"]) + total_uang
    g["xp"] = int(g["xp"]) + total_xp

    _save_db(db)

    lvl = _lvl_from_xp(int(g["xp"]))
    bonus_note = ""
    if total_ok and total_ok >= 3 and random.randint(1,100) <= 18:
        # random bonus seed
        seed = random.choice(SEEDS)
        g["inv"][str(seed["id"])] = int(g["inv"].get(str(seed["id"]), 0)) + 1
        _save_db(db)
        bonus_note = f"\n🎁 Bonus benih: {seed['name']} x<code>1</code>"

    await message.reply(f"""
<blockquote><b>🌾 PANEN BERHASIL</b>
{message.from_user.mention}

<b>Panen:</b> <code>{total_ok}</code> lahan
<b>Uang +</b> <code>{total_uang}</code>
<b>XP +</b> <code>{total_xp}</code> → <code>Lv {lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code>{bonus_note}

Cek kebun: <code>.gg</code></blockquote>
""")

@PY.UBOT("ggupgrade")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_garden(u)
    g = u["garden"]

    cost = _upgrade_cost(g)
    if int(u["uang"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nBiaya: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - cost
    g["slots"] = int(g["slots"]) + 1
    _save_db(db)

    await message.reply(f"<blockquote>✅ Slot kebun bertambah!\nSlot sekarang: <code>{g['slots']}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("ggtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})
    ranking = []

    for uid_str, data in users.items():
        g = (data or {}).get("garden")
        if not g:
            continue
        xp = int(g.get("xp", 0))
        if xp > 0:
            ranking.append((int(uid_str), xp))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP GROW GARDEN</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, xp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{xp}</code> XP (Lv {_lvl_from_xp(xp)})")

    await message.reply("<blockquote><b>🏆 TOP GROW GARDEN</b>\n\n" + "\n".join(lines) + "</blockquote>")
    