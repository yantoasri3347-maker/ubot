import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "sigmax"
__HELP__ = """
<blockquote><b>Game Sigma X</b>

- <code>.sigstart</code> → aktifkan
- <code>.sig</code> → status
- <code>.sigwork</code> → kerja dapat uang (cooldown)
- <code>.sigtrain</code> → latihan dapat xp (cooldown)
- <code>.sigup atk/def/aura jumlah</code> → upgrade stat
- <code>.sigshop</code> → toko item
- <code>.sigbuy id qty</code> → beli item
- <code>.sigfight</code> → duel vs bot (cooldown)
- <code>.sigtop</code> → top power</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

WORK_CD = 180
TRAIN_CD = 160
FIGHT_CD = 220

# economy
UP_COST = {"atk": 120, "def": 120, "aura": 160}  # per +1 stat
ENERGY_MAX = 100

SHOP = [
    {"id": 1, "name": "🥤 Energy Drink (+35 energy)", "price": 140, "key": "drink", "value": 35},
    {"id": 2, "name": "📘 Skill Book (+1.4x XP next train)", "price": 220, "key": "xpboost", "value": 1},
    {"id": 3, "name": "🧿 Lucky Charm (+bonus uang saat win)", "price": 260, "key": "luck", "value": 1},
    {"id": 4, "name": "🛡 Shield Token (batalin kalah 1x)", "price": 360, "key": "shield", "value": 1},
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
        db["users"][uid] = {"uang": 0, "sigmax": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("sigmax", None)
    return u

def _ensure_sigma(u):
    if u.get("sigmax") is None:
        u["sigmax"] = {
            "lvl": 1,
            "xp": 0,
            "atk": 1,
            "def": 1,
            "aura": 1,
            "energy": ENERGY_MAX,
            "win": 0,
            "lose": 0,
            "last_work": 0,
            "last_train": 0,
            "last_fight": 0,
            "items": {"drink": 0, "xpboost": 0, "luck": 0, "shield": 0},
            "power": 0,
        }
    else:
        s = u["sigmax"]
        s.setdefault("lvl", 1)
        s.setdefault("xp", 0)
        s.setdefault("atk", 1)
        s.setdefault("def", 1)
        s.setdefault("aura", 1)
        s.setdefault("energy", ENERGY_MAX)
        s.setdefault("win", 0)
        s.setdefault("lose", 0)
        s.setdefault("last_work", 0)
        s.setdefault("last_train", 0)
        s.setdefault("last_fight", 0)
        s.setdefault("items", {"drink": 0, "xpboost": 0, "luck": 0, "shield": 0})
        for k in ["drink", "xpboost", "luck", "shield"]:
            s["items"].setdefault(k, 0)
        s.setdefault("power", 0)

def _ts():
    return int(datetime.now(TZ).timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _need_xp(lvl: int) -> int:
    # kebutuhan XP naik level
    return 80 + (lvl * 35)

def _recalc_power(s):
    # power simple, tapi kerasa
    s["power"] = int((s["atk"] * 18) + (s["def"] * 14) + (s["aura"] * 22) + (s["lvl"] * 10))

def _level_up(s):
    changed = False
    while s["xp"] >= _need_xp(int(s["lvl"])):
        s["xp"] -= _need_xp(int(s["lvl"]))
        s["lvl"] += 1
        s["energy"] = min(ENERGY_MAX, int(s["energy"]) + 25)
        changed = True
    return changed

def _rank_name(power: int) -> str:
    if power < 120: return "Rookie"
    if power < 260: return "Grinder"
    if power < 420: return "Sigma"
    if power < 650: return "Alpha Sigma"
    if power < 900: return "Omega"
    return "Sigma X"

@PY.UBOT("sigstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    _recalc_power(u["sigmax"])
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ SIGMA X AKTIF</b>
{message.from_user.mention}

Mulai grind:
- <code>.sigwork</code> / <code>.sigtrain</code>
Duel:
- <code>.sigfight</code></blockquote>
""")

@PY.UBOT("sig")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]
    _recalc_power(s)

    now = _ts()
    cdw = max(0, int(s["last_work"]) + WORK_CD - now)
    cdt = max(0, int(s["last_train"]) + TRAIN_CD - now)
    cdf = max(0, int(s["last_fight"]) + FIGHT_CD - now)

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🧬 SIGMA X — STATUS</b>
{message.from_user.mention}

<b>Rank:</b> <code>{_rank_name(int(s['power']))}</code>
<b>Level:</b> <code>{s['lvl']}</code> | <b>XP:</b> <code>{s['xp']}/{_need_xp(int(s['lvl']))}</code>
<b>Power:</b> <code>{s['power']}</code>

<b>ATK/DEF/AURA:</b> <code>{s['atk']}</code>/<code>{s['def']}</code>/<code>{s['aura']}</code>
<b>Energy:</b> <code>{s['energy']}/{ENERGY_MAX}</code>

<b>Win/Lose:</b> <code>{s['win']}</code>/<code>{s['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Cooldown:</b>
- Work: <code>{_fmt_cd(cdw) if cdw else "ready ✅"}</code>
- Train: <code>{_fmt_cd(cdt) if cdt else "ready ✅"}</code>
- Fight: <code>{_fmt_cd(cdf) if cdf else "ready ✅"}</code>

<b>Item:</b>
- 🥤 Drink: <code>{s['items'].get('drink',0)}</code>
- 📘 XPBoost: <code>{s['items'].get('xpboost',0)}</code>
- 🧿 Luck: <code>{s['items'].get('luck',0)}</code>
- 🛡 Shield: <code>{s['items'].get('shield',0)}</code></blockquote>
""")

@PY.UBOT("sigwork")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]
    now = _ts()

    left = int(s["last_work"]) + WORK_CD - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Work cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    if s["energy"] < 15:
        _save_db(db)
        return await message.reply("<blockquote>❌ Energy kurang. Beli: <code>.sigshop</code> (Energy Drink)</blockquote>")

    s["last_work"] = now
    s["energy"] = max(0, int(s["energy"]) - random.randint(10, 18))

    base = random.randint(60, 160)
    bonus = min(90, int(s["aura"]) * random.randint(2, 6))
    earn = base + bonus
    u["uang"] += earn

    _recalc_power(s)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🧱 SIGMA WORK</b>
{message.from_user.mention}

<b>Dapat uang:</b> <code>+{earn}</code>
<b>Energy:</b> <code>{s['energy']}/{ENERGY_MAX}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("sigtrain")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]
    now = _ts()

    left = int(s["last_train"]) + TRAIN_CD - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Train cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    if s["energy"] < 18:
        _save_db(db)
        return await message.reply("<blockquote>❌ Energy kurang. Beli: <code>.sigshop</code></blockquote>")

    s["last_train"] = now
    s["energy"] = max(0, int(s["energy"]) - random.randint(12, 22))

    xp = random.randint(22, 55)
    note = []

    if int(s["items"].get("xpboost", 0)) > 0:
        s["items"]["xpboost"] -= 1
        xp = int(xp * 1.4)
        note.append("📘 XPBoost aktif (x1.4)")

    xp += min(12, int(s["atk"]) // 2)
    s["xp"] += xp

    leveled = _level_up(s)
    _recalc_power(s)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🏋️ SIGMA TRAIN</b>
{message.from_user.mention}

<b>XP:</b> <code>+{xp}</code>
<b>Level:</b> <code>{s['lvl']}</code> {"(LEVEL UP ✅)" if leveled else ""}
<b>Energy:</b> <code>{s['energy']}/{ENERGY_MAX}</code>

<b>Catatan:</b> {"; ".join(note) if note else "—"}
<b>Power:</b> <code>{s['power']}</code></blockquote>
""")

@PY.UBOT("sigup")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 3:
        return await message.reply("<blockquote>Format: <code>.sigup atk/def/aura jumlah</code>\nContoh: <code>.sigup atk 2</code></blockquote>")

    stat = parts[1].strip().lower()
    if stat not in ("atk", "def", "aura"):
        return await message.reply("<blockquote>Stat hanya: <code>atk</code>, <code>def</code>, <code>aura</code></blockquote>")

    try:
        qty = int(parts[2])
    except:
        return await message.reply("<blockquote>Jumlah harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Jumlah minimal 1.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]

    cost = int(UP_COST[stat]) * qty
    if int(u["uang"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] -= cost
    s[stat] = int(s[stat]) + qty
    _recalc_power(s)
    _save_db(db)

    await message.reply(f"<blockquote>✅ Upgrade <b>{stat.upper()}</b> +<code>{qty}</code>\nBiaya: <code>{cost}</code>\nPower: <code>{s['power']}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("sigshop")
async def _(client, message):
    lines = [f"{x['id']}. {x['name']} — <code>{x['price']}</code> uang" for x in SHOP]
    await message.reply("<blockquote><b>🛒 SIGMA SHOP</b>\n\n" + "\n".join(lines) +
                        "\n\nBeli: <code>.sigbuy id qty</code></blockquote>")

@PY.UBOT("sigbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.sigbuy id qty</code>\nContoh: <code>.sigbuy 1 2</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    item = next((x for x in SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.sigshop</code></blockquote>")

    total = int(item["price"]) * qty
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]

    if int(u["uang"]) < total:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] -= total

    key = item["key"]
    if key == "drink":
        # langsung pakai atau simpan? kita simpan itemnya dulu
        s["items"]["drink"] = int(s["items"].get("drink", 0)) + qty
    else:
        s["items"][key] = int(s["items"].get(key, 0)) + qty

    _save_db(db)
    await message.reply(f"<blockquote>✅ Beli <b>{item['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("sigdrink")
async def _(client, message):
    # optional: pakai energy drink
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]

    if int(s["items"].get("drink", 0)) <= 0:
        _save_db(db)
        return await message.reply("<blockquote>❌ Kamu tidak punya Energy Drink. Beli: <code>.sigshop</code></blockquote>")

    # pakai 1
    s["items"]["drink"] -= 1
    gain = 35
    s["energy"] = min(ENERGY_MAX, int(s["energy"]) + gain)

    _save_db(db)
    await message.reply(f"<blockquote>🥤 Energy Drink dipakai!\nEnergy +<code>{gain}</code> → <code>{s['energy']}/{ENERGY_MAX}</code></blockquote>")

@PY.UBOT("sigfight")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sigma(u)
    s = u["sigmax"]
    _recalc_power(s)

    now = _ts()
    left = int(s["last_fight"]) + FIGHT_CD - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Fight cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    if s["energy"] < 22:
        _save_db(db)
        return await message.reply("<blockquote>❌ Energy kurang untuk duel. Pakai <code>.sigdrink</code> atau kerja/train dulu.</blockquote>")

    s["last_fight"] = now
    s["energy"] = max(0, int(s["energy"]) - random.randint(16, 26))

    # enemy scaling by player power
    enemy_pow = max(60, int(s["power"]) + random.randint(-90, 90))
    enemy_rank = _rank_name(enemy_pow)

    # win chance
    chance = 50
    chance += min(18, (int(s["power"]) - enemy_pow) // 8)
    chance += min(8, int(s["lvl"]) // 4)
    chance = max(12, min(88, chance))

    note = []
    win = random.randint(1, 100) <= chance

    # shield: cancel loss
    if not win and int(s["items"].get("shield", 0)) > 0 and random.randint(1, 100) <= 55:
        s["items"]["shield"] -= 1
        win = True
        note.append("🛡 Shield aktif! kalah dibatalkan")

    if win:
        s["win"] += 1
        xp = random.randint(18, 45) + min(18, int(enemy_pow) // 60)
        uang = random.randint(120, 260)

        if int(s["items"].get("luck", 0)) > 0:
            s["items"]["luck"] -= 1
            bonus = random.randint(60, 140)
            uang += bonus
            note.append(f"🧿 Lucky Charm aktif +{bonus} uang")

        s["xp"] += xp
        _level_up(s)
        u["uang"] += uang
        result = f"🏆 MENANG vs <b>{enemy_rank}</b> (pow <code>{enemy_pow}</code>)"
        gainline = f"<b>Uang:</b> <code>+{uang}</code>\n<b>XP:</b> <code>+{xp}</code>"
    else:
        s["lose"] += 1
        loss = random.randint(40, 120)
        u["uang"] = max(0, int(u["uang"]) - loss)
        result = f"❌ KALAH vs <b>{enemy_rank}</b> (pow <code>{enemy_pow}</code>)"
        gainline = f"<b>Uang:</b> <code>-{loss}</code>\n<b>XP:</b> <code>+0</code>"

    _recalc_power(s)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🥊 SIGMA FIGHT</b>
{message.from_user.mention}

<b>Chance:</b> <code>{chance}%</code>
<b>Hasil:</b> {result}

{gainline}
<b>Energy:</b> <code>{s['energy']}/{ENERGY_MAX}</code>
<b>Power:</b> <code>{s['power']}</code>
<b>Saldo:</b> <code>{u['uang']}</code>

<b>Catatan:</b> {"; ".join(note) if note else "—"}</blockquote>
""")

@PY.UBOT("sigtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        s = (data or {}).get("sigmax")
        if not s:
            continue
        # recalc quick without mutating too much
        power = int((int(s.get("atk",1))*18) + (int(s.get("def",1))*14) + (int(s.get("aura",1))*22) + (int(s.get("lvl",1))*10))
        if power > 0:
            rank.append((int(uid_str), power))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP SIGMA X</b>\nBelum ada pemain.</blockquote>")

    lines = []
    for i, (uid, power) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{power}</code> power ({_rank_name(power)})")

    await message.reply("<blockquote><b>🏆 TOP SIGMA X</b>\n\n" + "\n".join(lines) + "</blockquote>")
