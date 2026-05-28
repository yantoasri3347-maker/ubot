import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "listsaga"
__HELP__ = """
<blockquote><b>Game List Saga</b>

- <code>.sagastart</code> → aktifkan
- <code>.saga</code> → status
- <code>.sagasummon</code> / <code>.sagasummon 10</code> → summon saga
- <code>.sagalist</code> → koleksi & dupe
- <code>.sagaequip id1 id2 id3</code> → equip 3 saga
- <code>.sagaup id</code> → upgrade saga (butuh dupe + uang)
- <code>.sagajual id qty</code> → jual dupe
- <code>.sagatop</code> → top power</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

# summon economy
SUMMON_COST = 120
SUMMON10_COST = 1100  # diskon
UPGRADE_COST = {"C": 80, "B": 120, "A": 170, "S": 240, "SS": 340}
SELL_PRICE = {"C": 30, "B": 55, "A": 90, "S": 150, "SS": 230}

# rarity rates
RARITY_RATE = [
    ("SS", 3),
    ("S", 8),
    ("A", 20),
    ("B", 29),
    ("C", 40),
]

# saga pool
SAGAS = [
    {"id": 1, "name": "🔥 Saga Inferno", "type": "ATK"},
    {"id": 2, "name": "🌊 Saga Tidal", "type": "DEF"},
    {"id": 3, "name": "🌪 Saga Tempest", "type": "SPD"},
    {"id": 4, "name": "🌿 Saga Verdant", "type": "HP"},
    {"id": 5, "name": "⚡ Saga Volt", "type": "ATK"},
    {"id": 6, "name": "🛡 Saga Bastion", "type": "DEF"},
    {"id": 7, "name": "🧠 Saga Oracle", "type": "CRIT"},
    {"id": 8, "name": "🗡 Saga Rogue", "type": "SPD"},
    {"id": 9, "name": "💎 Saga Aegis", "type": "HP"},
    {"id": 10, "name": "🌙 Saga Eclipse", "type": "CRIT"},
]

TYPE_BONUS = {
    "ATK": 18,
    "DEF": 16,
    "SPD": 14,
    "HP": 15,
    "CRIT": 17,
}

TIER_ORDER = ["C", "B", "A", "S", "SS"]

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
        db["users"][uid] = {"uang": 0, "saga": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("saga", None)
    return u

def _ensure_saga(u):
    if u.get("saga") is None:
        u["saga"] = {
            "owned": {},     # saga_id -> {"tier":"C","lvl":1,"dupe":0}
            "equip": [],     # [id,id,id]
            "summon": 0,
            "power": 0,
        }
    else:
        s = u["saga"]
        s.setdefault("owned", {})
        s.setdefault("equip", [])
        s.setdefault("summon", 0)
        s.setdefault("power", 0)

def _pick_rarity():
    total = sum(w for _, w in RARITY_RATE)
    r = random.randint(1, total)
    cur = 0
    for rr, w in RARITY_RATE:
        cur += w
        if r <= cur:
            return rr
    return "C"

def _saga_by_id(sid: int):
    for x in SAGAS:
        if int(x["id"]) == int(sid):
            return x
    return None

def _calc_power(sdata):
    owned = sdata["owned"]
    equip = sdata.get("equip", [])
    power = 0

    # base power dari semua owned (koleksi)
    for sid_str, info in owned.items():
        tier = info.get("tier", "C")
        lvl = int(info.get("lvl", 1))
        base = {"C": 18, "B": 28, "A": 42, "S": 62, "SS": 90}[tier]
        power += base + (lvl * 3)

    # equip bonus
    equip_types = []
    for sid in equip[:3]:
        sg = _saga_by_id(int(sid))
        if sg:
            equip_types.append(sg["type"])
            # bonus equip per kartu
            info = owned.get(str(sid))
            if info:
                tier = info.get("tier", "C")
                lvl = int(info.get("lvl", 1))
                power += {"C": 10, "B": 14, "A": 18, "S": 26, "SS": 35}[tier] + (lvl * 2)

    # set bonus kalau 2/3 type sama
    if len(equip_types) >= 2:
        for t in set(equip_types):
            cnt = equip_types.count(t)
            if cnt == 2:
                power += TYPE_BONUS.get(t, 12)
            elif cnt >= 3:
                power += TYPE_BONUS.get(t, 12) * 2

    return int(power)

def _ensure_owned_slot(owned, sid: int):
    key = str(sid)
    if key not in owned:
        owned[key] = {"tier": "C", "lvl": 1, "dupe": 0}
    owned[key].setdefault("tier", "C")
    owned[key].setdefault("lvl", 1)
    owned[key].setdefault("dupe", 0)

@PY.UBOT("sagastart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    u["saga"]["power"] = _calc_power(u["saga"])
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ LIST SAGA AKTIF</b>
{message.from_user.mention}

Summon: <code>.sagasummon</code>
Koleksi: <code>.sagalist</code></blockquote>
""")

@PY.UBOT("saga")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    s = u["saga"]
    s["power"] = _calc_power(s)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>📜 LIST SAGA — STATUS</b>
{message.from_user.mention}

<b>Summon:</b> <code>{s['summon']}</code>
<b>Owned:</b> <code>{len(s['owned'])}</code>/<code>{len(SAGAS)}</code>
<b>Equip:</b> <code>{' '.join([str(x) for x in s.get('equip', [])[:3]]) or '-'}</code>
<b>Power:</b> <code>{s['power']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

Summon 1: <code>{SUMMON_COST}</code> | Summon 10: <code>{SUMMON10_COST}</code></blockquote>
""")

@PY.UBOT("sagasummon")
async def _(client, message):
    parts = (message.text or "").split()
    times = 1
    if len(parts) >= 2:
        try:
            times = int(parts[1])
        except:
            times = 1
    times = 10 if times >= 10 else 1

    cost = SUMMON10_COST if times == 10 else SUMMON_COST

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    s = u["saga"]

    if int(u["uang"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] -= cost
    s["summon"] += times

    results = []
    for _ in range(times):
        pick = random.choice(SAGAS)
        rar = _pick_rarity()
        sid = int(pick["id"])
        _ensure_owned_slot(s["owned"], sid)

        info = s["owned"][str(sid)]
        if info["tier"] == "C" and info["lvl"] == 1 and info["dupe"] == 0 and info.get("first", True):
            # first time: set tier
            info["tier"] = rar
            info["first"] = False
        else:
            # dupe: tambah dupe, dan kalau rar lebih tinggi dari tier sekarang, upgrade tier langsung
            info["dupe"] += 1
            if TIER_ORDER.index(rar) > TIER_ORDER.index(info["tier"]):
                info["tier"] = rar

        results.append(f"- <b>{pick['name']}</b> (<code>{rar}</code>)")

    s["power"] = _calc_power(s)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🎲 SAGASUMMON x{times}</b>
{message.from_user.mention}

{chr(10).join(results)}

<b>Power:</b> <code>{s['power']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("sagalist")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    s = u["saga"]

    if not s["owned"]:
        _save_db(db)
        return await message.reply("<blockquote>Koleksi kosong. Summon dulu: <code>.sagasummon</code></blockquote>")

    lines = []
    for sg in SAGAS:
        sid = str(sg["id"])
        if sid in s["owned"]:
            info = s["owned"][sid]
            lines.append(f"• <code>{sg['id']}</code> {sg['name']} [{sg['type']}] — tier <code>{info['tier']}</code> | lvl <code>{info['lvl']}</code> | dupe <code>{info['dupe']}</code>")
        else:
            lines.append(f"• <code>{sg['id']}</code> {sg['name']} [{sg['type']}] — <i>belum punya</i>")

    s["power"] = _calc_power(s)
    _save_db(db)

    await message.reply("<blockquote><b>📚 KOLEKSI SAGA</b>\n\n" + "\n".join(lines) +
                        "\n\nEquip: <code>.sagaequip id1 id2 id3</code>\nUpgrade: <code>.sagaup id</code>\nJual dupe: <code>.sagajual id qty</code></blockquote>")

@PY.UBOT("sagaequip")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 4:
        return await message.reply("<blockquote>Format: <code>.sagaequip id1 id2 id3</code></blockquote>")
    try:
        ids = [int(parts[1]), int(parts[2]), int(parts[3])]
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    s = u["saga"]

    for sid in ids:
        if str(sid) not in s["owned"]:
            _save_db(db)
            return await message.reply(f"<blockquote>❌ Kamu belum punya saga id <code>{sid}</code>. Cek: <code>.sagalist</code></blockquote>")

    s["equip"] = ids[:3]
    s["power"] = _calc_power(s)
    _save_db(db)

    await message.reply(f"<blockquote>✅ Equip berhasil: <code>{ids[0]}</code> <code>{ids[1]}</code> <code>{ids[2]}</code>\nPower: <code>{s['power']}</code></blockquote>")

@PY.UBOT("sagaup")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.sagaup id</code></blockquote>")
    try:
        sid = int(parts[1])
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    s = u["saga"]

    if str(sid) not in s["owned"]:
        _save_db(db)
        return await message.reply("<blockquote>❌ Saga belum kamu punya.</blockquote>")

    info = s["owned"][str(sid)]
    tier = info.get("tier", "C")
    lvl = int(info.get("lvl", 1))
    dupe = int(info.get("dupe", 0))

    need_dupe = max(1, 1 + (lvl // 2))  # makin tinggi lvl makin mahal
    cost = int(UPGRADE_COST[tier]) + (lvl * 25)

    if dupe < need_dupe:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Dupe kurang untuk upgrade.\nButuh dupe: <code>{need_dupe}</code> | Kamu punya: <code>{dupe}</code></blockquote>")

    if int(u["uang"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nBiaya: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    info["dupe"] -= need_dupe
    info["lvl"] = lvl + 1

    # chance naik tier (kecil) saat lvl tertentu
    note = []
    if info["lvl"] in (3, 5, 8, 12) and random.randint(1, 100) <= 18:
        idx = TIER_ORDER.index(info["tier"])
        if idx < len(TIER_ORDER) - 1:
            info["tier"] = TIER_ORDER[idx + 1]
            note.append(f"⬆️ Tier naik jadi <code>{info['tier']}</code>!")

    u["uang"] -= cost
    s["power"] = _calc_power(s)
    _save_db(db)

    sg = _saga_by_id(sid)
    name = sg["name"] if sg else f"Saga {sid}"
    await message.reply(f"<blockquote>✅ Upgrade <b>{name}</b>\nLvl: <code>{lvl} → {info['lvl']}</code>\nDupe terpakai: <code>{need_dupe}</code>\nBiaya: <code>{cost}</code>\n{' '.join(note) if note else ''}\nPower: <code>{s['power']}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("sagajual")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.sagajual id qty</code></blockquote>")
    try:
        sid = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_saga(u)
    s = u["saga"]

    if str(sid) not in s["owned"]:
        _save_db(db)
        return await message.reply("<blockquote>❌ Saga belum kamu punya.</blockquote>")

    info = s["owned"][str(sid)]
    dupe = int(info.get("dupe", 0))
    if dupe < qty:
        _save_db(db)
        return await message.reply("<blockquote>❌ Dupe kamu kurang.</blockquote>")

    tier = info.get("tier", "C")
    gain = int(SELL_PRICE[tier]) * qty
    info["dupe"] = dupe - qty
    u["uang"] += gain

    s["power"] = _calc_power(s)
    _save_db(db)

    sg = _saga_by_id(sid)
    name = sg["name"] if sg else f"Saga {sid}"
    await message.reply(f"<blockquote>✅ Terjual dupe <b>{name}</b> x<code>{qty}</code>\nUang +<code>{gain}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("sagatop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        s = (data or {}).get("saga")
        if not s:
            continue
        power = 0
        try:
            power = _calc_power(s)
        except:
            power = int(s.get("power", 0))
        if power > 0:
            rank.append((int(uid_str), power))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP LIST SAGA</b>\nBelum ada pemain.</blockquote>")

    lines = []
    for i, (uid, power) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{power}</code> power")

    await message.reply("<blockquote><b>🏆 TOP LIST SAGA</b>\n\n" + "\n".join(lines) + "</blockquote>")
