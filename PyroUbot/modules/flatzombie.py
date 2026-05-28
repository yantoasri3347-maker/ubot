import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "flatzombie"
__HELP__ = """
<blockquote><b>Game Flat Zombie</b>

- <code>.fzstart</code> → aktifkan
- <code>.fz</code> → status
- <code>.fzraid</code> → lawan zombie (cooldown)
- <code>.fzheal</code> → pakai medkit
- <code>.fzshop</code> → toko
- <code>.fzbuy id qty</code> → beli item
- <code>.fzinv</code> → inventory
- <code>.fztop</code> → top wave</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

RAID_CD = 190
HP_MAX = 100

SHOP = [
    {"id": 1, "name": "🩹 Medkit (+45 HP)", "price": 140, "key": "medkit", "value": 45},
    {"id": 2, "name": "🔫 Ammo Pack (+30 ammo)", "price": 160, "key": "ammo", "value": 30},
    {"id": 3, "name": "🦺 Armor Plate (+1 armor)", "price": 220, "key": "armor", "value": 1},
    {"id": 4, "name": "💣 Grenade (bonus kill)", "price": 260, "key": "nade", "value": 1},
]

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def _load_db():
    return _load_json(DB_FILE, {"users": {}})

def _save_db(db):
    _save_json(DB_FILE, db)

def _get_user(db, user_id: int):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"uang": 0, "fz": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("fz", None)
    return u

def _ensure_fz(u):
    if u.get("fz") is None:
        u["fz"] = {
            "wave": 1,
            "best_wave": 1,
            "hp": HP_MAX,
            "ammo": 20,
            "armor": 0,
            "kills": 0,
            "death": 0,
            "last_raid": 0,
            "inv": {"medkit": 0, "ammo": 0, "armor": 0, "nade": 0},
        }
    else:
        f = u["fz"]
        f.setdefault("wave", 1)
        f.setdefault("best_wave", 1)
        f.setdefault("hp", HP_MAX)
        f.setdefault("ammo", 20)
        f.setdefault("armor", 0)
        f.setdefault("kills", 0)
        f.setdefault("death", 0)
        f.setdefault("last_raid", 0)
        f.setdefault("inv", {"medkit": 0, "ammo": 0, "armor": 0, "nade": 0})
        for k in ["medkit", "ammo", "armor", "nade"]:
            f["inv"].setdefault(k, 0)

def _ts():
    return int(datetime.now(TZ).timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

@PY.UBOT("fzstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_fz(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ FLAT ZOMBIE AKTIF</b>
{message.from_user.mention}

Mulai raid: <code>.fzraid</code>
Shop: <code>.fzshop</code></blockquote>
""")

@PY.UBOT("fz")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_fz(u)
    f = u["fz"]
    now = _ts()
    cd = max(0, int(f["last_raid"]) + RAID_CD - now)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🧟 FLAT ZOMBIE — STATUS</b>
{message.from_user.mention}

<b>Wave:</b> <code>{f['wave']}</code> (best <code>{f['best_wave']}</code>)
<b>HP:</b> <code>{f['hp']}/{HP_MAX}</code>
<b>Ammo:</b> <code>{f['ammo']}</code>
<b>Armor:</b> <code>{f['armor']}</code>

<b>Kills:</b> <code>{f['kills']}</code> | <b>Death:</b> <code>{f['death']}</code>
<b>Uang:</b> <code>{u['uang']}</code>
<b>Cooldown:</b> <code>{_fmt_cd(cd) if cd else "ready ✅"}</code></blockquote>
""")

@PY.UBOT("fzshop")
async def _(client, message):
    lines = [f"{x['id']}. {x['name']} — <code>{x['price']}</code> uang" for x in SHOP]
    await message.reply("<blockquote><b>🛒 FLAT ZOMBIE SHOP</b>\n\n" + "\n".join(lines) +
                        "\n\nBeli: <code>.fzbuy id qty</code></blockquote>")

@PY.UBOT("fzbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.fzbuy id qty</code>\nContoh: <code>.fzbuy 1 2</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    item = next((x for x in SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.fzshop</code></blockquote>")

    total = int(item["price"]) * qty
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_fz(u)
    f = u["fz"]

    if int(u["uang"]) < total:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] -= total
    f["inv"][item["key"]] = int(f["inv"].get(item["key"], 0)) + qty
    _save_db(db)

    await message.reply(f"<blockquote>✅ Beli <b>{item['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("fzinv")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_fz(u)
    inv = u["fz"]["inv"]
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🎒 INVENTORY</b>
🩹 Medkit: <code>{inv.get('medkit',0)}</code>
🔫 Ammo Pack: <code>{inv.get('ammo',0)}</code>
🦺 Armor Plate: <code>{inv.get('armor',0)}</code>
💣 Grenade: <code>{inv.get('nade',0)}</code></blockquote>
""")

@PY.UBOT("fzheal")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_fz(u)
    f = u["fz"]
    inv = f["inv"]

    if inv.get("medkit", 0) <= 0:
        _save_db(db)
        return await message.reply("<blockquote>❌ Kamu tidak punya Medkit. Beli: <code>.fzshop</code></blockquote>")

    inv["medkit"] -= 1
    heal = 45
    f["hp"] = min(HP_MAX, int(f["hp"]) + heal)
    _save_db(db)

    await message.reply(f"<blockquote>🩹 Medkit dipakai! HP +<code>{heal}</code> → <code>{f['hp']}/{HP_MAX}</code></blockquote>")

@PY.UBOT("fzraid")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_fz(u)
    f = u["fz"]

    now = _ts()
    left = int(f["last_raid"]) + RAID_CD - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Raid cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    f["last_raid"] = now

    # wave scaling
    wave = int(f["wave"])
    zombie = random.randint(6, 12) + (wave * random.randint(1, 3))
    dmg = random.randint(12, 25) + (wave * random.randint(1, 2))
    armor_reduce = min(12, int(f["armor"]) * 3)
    dmg_taken = max(0, dmg - armor_reduce)

    # ammo usage
    if f["ammo"] <= 0:
        # kalau ammo habis, lebih sakit
        dmg_taken += random.randint(8, 18)
        shots = 0
    else:
        shots = min(int(f["ammo"]), random.randint(6, 18))
        f["ammo"] -= shots

    # grenade
    bonus_kill = 0
    note = []
    if f["inv"].get("nade", 0) > 0 and random.randint(1, 100) <= 22:
        f["inv"]["nade"] -= 1
        bonus_kill = random.randint(8, 22)
        note.append("💣 Grenade meledak! bonus kill")

    kills = min(zombie, shots + bonus_kill + random.randint(0, 6))
    f["kills"] += kills

    f["hp"] = max(0, int(f["hp"]) - dmg_taken)

    if f["hp"] <= 0:
        f["death"] += 1
        # reset wave turun
        drop = random.randint(1, 2)
        f["wave"] = max(1, wave - drop)
        f["hp"] = HP_MAX
        # penalty uang
        loss = random.randint(40, 120)
        u["uang"] = max(0, int(u["uang"]) - loss)
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>💀 KAMU MATI!</b>
Wave tadi: <code>{wave}</code>
Damage: <code>{dmg_taken}</code>
Penalty uang: <code>-{loss}</code>

Wave turun jadi <code>{f['wave']}</code>
HP direset <code>{f['hp']}/{HP_MAX}</code>
Saldo: <code>{u['uang']}</code></blockquote>
""")

    # survive -> reward + wave up chance
    base_uang = random.randint(60, 150) + (wave * random.randint(8, 14))
    if kills >= zombie * 0.7:
        base_uang += random.randint(30, 90)
        note.append("🔥 Clear bagus! bonus uang")

    # loot ammo/medkit/armor drop
    if random.randint(1, 100) <= 28:
        f["inv"]["ammo"] += 1
        note.append("🔫 Dapat Ammo Pack (+1)")
    if random.randint(1, 100) <= 18:
        f["inv"]["medkit"] += 1
        note.append("🩹 Dapat Medkit (+1)")
    if random.randint(1, 100) <= 10:
        f["inv"]["armor"] += 1
        f["armor"] += 1
        note.append("🦺 Dapat Armor Plate (+1 armor)")

    u["uang"] += base_uang

    # wave progress
    if kills >= max(6, zombie // 2):
        f["wave"] += 1
        f["best_wave"] = max(int(f["best_wave"]), int(f["wave"]))
        note.append("⬆️ Naik wave!")

    _save_db(db)

    await message.reply(f"""
<blockquote><b>🧟 RAID SELESAI</b>
{message.from_user.mention}

<b>Wave:</b> <code>{wave}</code> → <code>{f['wave']}</code>
<b>Zombie:</b> <code>{zombie}</code>
<b>Kills:</b> <code>{kills}</code>
<b>Ammo dipakai:</b> <code>{shots}</code>
<b>Damage:</b> <code>{dmg_taken}</code>
<b>HP:</b> <code>{f['hp']}/{HP_MAX}</code>

<b>Uang:</b> <code>+{base_uang}</code>
<b>Saldo:</b> <code>{u['uang']}</code>

<b>Loot/Note:</b>
{('- ' + chr(10) + '- '.join(note)) if note else '- —'}</blockquote>
""")

@PY.UBOT("fztop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        fz = (data or {}).get("fz")
        if not fz:
            continue
        best = int(fz.get("best_wave", 0))
        if best > 0:
            rank.append((int(uid_str), best))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP FLAT ZOMBIE</b>\nBelum ada pemain.</blockquote>")

    lines = []
    for i, (uid, best) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — best wave <code>{best}</code>")

    await message.reply("<blockquote><b>🏆 TOP FLAT ZOMBIE</b>\n\n" + "\n".join(lines) + "</blockquote>")
