import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "padel"
__HELP__ = """
<blockquote><b>Game Padel (Mini)</b>

- <code>.padelstart</code> → buat akun padel
- <code>.padelprofil</code> → lihat profil
- <code>.padeldaily</code> → bonus harian (1x/hari)
- <code>.padellatih</code> → latihan exp + uang (cooldown)
- <code>.padelmatch</code> → tanding (cooldown) naik/turun ranking
- <code>.padelshop</code> → toko item
- <code>.padelbuy id</code> → beli item (pakai uang)
- <code>.padeltop</code> → leaderboard ranking

Catatan: Ini mini-game Telegram.</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

LATIH_CD = 120
MATCH_CD = 180

PADEL_SHOP = [
    {"id": 1, "name": "🎫 Voucher Diskon 20%", "price": 200, "type": "voucher", "value": 0.20},
    {"id": 2, "name": "🏋️ Boost EXP (3x Latih)", "price": 240, "type": "exp_boost", "value": 3},
    {"id": 3, "name": "🎾 Boost Ranking (2x Menang)", "price": 380, "type": "rp_boost", "value": 2},
    {"id": 4, "name": "🧤 Grip Premium (Cosmetic)", "price": 180, "type": "cosmetic", "value": "grip"},
    {"id": 5, "name": "🎽 Outfit Court (Cosmetic)", "price": 320, "type": "cosmetic", "value": "outfit"},
]

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
        db["users"][uid] = {"uang": 0, "padel": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("padel", None)
    return u

def _level_from_exp(exp: int) -> int:
    return 1 + (exp // 120)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank_name(rp: int) -> str:
    if rp < 100: return "Rookie"
    if rp < 250: return "Beginner"
    if rp < 450: return "Intermediate"
    if rp < 700: return "Pro"
    if rp < 1000: return "Elite"
    return "Champion"

def _ensure_padel(u):
    if u.get("padel") is None:
        u["padel"] = {
            "exp": 0,
            "rp": 0,
            "win": 0,
            "lose": 0,
            "last_latih": 0,
            "last_match": 0,
            "last_daily": None,
            "bag": [],
            "buff": {"voucher": 0.0, "exp_boost": 0, "rp_boost": 0},
        }
    else:
        u["padel"].setdefault("bag", [])
        u["padel"].setdefault("buff", {"voucher": 0.0, "exp_boost": 0, "rp_boost": 0})
        u["padel"]["buff"].setdefault("voucher", 0.0)
        u["padel"]["buff"].setdefault("exp_boost", 0)
        u["padel"]["buff"].setdefault("rp_boost", 0)

@PY.UBOT("padelstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_padel(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ PADEL GAME AKTIF</b>
{message.from_user.mention}

Main:
<code>.padellatih</code> / <code>.padelmatch</code> / <code>.padelprofil</code> / <code>.padelshop</code></blockquote>
""")

@PY.UBOT("padelprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_padel(u)
    p = u["padel"]

    exp = int(p["exp"])
    lvl = _level_from_exp(exp)
    rp = int(p["rp"])
    rank = _rank_name(rp)

    bf = p.get("buff", {})
    voucher = int(float(bf.get("voucher", 0.0)) * 100)
    expb = int(bf.get("exp_boost", 0))
    rpb = int(bf.get("rp_boost", 0))

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎾 PROFIL PADEL</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code> (<b>EXP:</b> <code>{exp}</code>)
<b>Rank:</b> <code>{rank}</code> (<b>RP:</b> <code>{rp}</code>)
<b>Win:</b> <code>{p['win']}</code> | <b>Lose:</b> <code>{p['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Voucher: <code>{voucher}%</code>
- EXP Boost: <code>{expb}x</code>
- Rank Boost: <code>{rpb}x</code></blockquote>
""")

@PY.UBOT("padeldaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_padel(u)
    p = u["padel"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if p.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Padel sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(80, 170)
    bonus_exp = random.randint(30, 70)

    u["uang"] = int(u["uang"]) + bonus_uang
    p["exp"] = int(p["exp"]) + bonus_exp
    p["last_daily"] = today

    _save_db(db)
    lvl = _level_from_exp(int(p["exp"]))
    await message.reply(f"""
<blockquote><b>🎁 PADEL DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>

<b>Level sekarang:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("padellatih")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_padel(u)
    p = u["padel"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(p.get("last_latih", 0))
    if now_ts - last < LATIH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Masih cooldown latihan. Coba lagi <b>{_fmt_cd(LATIH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    exp_gain = random.randint(25, 60)
    uang_gain = random.randint(20, 55)

    roll = random.randint(1, 100)
    event = "✅ Latihan volley & positioning lancar."
    if roll <= 15:
        event = "💥 Drill keras! Bonus EXP."
        exp_gain += random.randint(10, 25)
    elif roll <= 25:
        event = "🩹 Salah baca bola. EXP kecil."
        exp_gain = max(10, exp_gain - random.randint(5, 15))

    boost_note = ""
    left = int(p["buff"].get("exp_boost", 0))
    if left > 0:
        bonus = random.randint(15, 35)
        exp_gain += bonus
        p["buff"]["exp_boost"] = left - 1
        boost_note = f"🏋️ Boost EXP: +{bonus} (sisa {p['buff']['exp_boost']}x)"

    p["exp"] = int(p["exp"]) + exp_gain
    u["uang"] = int(u["uang"]) + uang_gain
    p["last_latih"] = now_ts

    lvl = _level_from_exp(int(p["exp"]))
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🏋️ PADEL LATIH</b>
{message.from_user.mention}

<b>EXP +</b> <code>{exp_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Event:</b> {event}{extra}

<b>Level:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("padelmatch")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_padel(u)
    p = u["padel"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(p.get("last_match", 0))
    if now_ts - last < MATCH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Tunggu dulu. Match lagi <b>{_fmt_cd(MATCH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    lvl = _level_from_exp(int(p["exp"]))
    win_chance = min(80, 45 + (lvl * 2))
    r = random.randint(1, 100)

    rp_change = 0
    uang_change = 0
    result = ""

    if r <= win_chance:
        rp_change = random.randint(12, 30)
        uang_change = random.randint(25, 80)
        p["win"] = int(p["win"]) + 1
        result = "🏆 MENANG! Smash + lob mantap!"
        if random.randint(1, 100) <= 12:
            bonus = random.randint(10, 25)
            rp_change += bonus
            result += f" ⭐ Bonus RP +{bonus}"
    else:
        rp_change = -random.randint(8, 22)
        uang_change = random.randint(10, 40)
        p["lose"] = int(p["lose"]) + 1
        result = "💀 KALAH! Kena placement."

    boost_note = ""
    left = int(p["buff"].get("rp_boost", 0))
    if left > 0 and rp_change > 0:
        bonus_rp = random.randint(5, 15)
        rp_change += bonus_rp
        p["buff"]["rp_boost"] = left - 1
        boost_note = f"🎾 Boost Ranking: +{bonus_rp} (sisa {p['buff']['rp_boost']}x)"

    p["rp"] = max(0, int(p["rp"]) + rp_change)
    u["uang"] = int(u["uang"]) + uang_change
    p["last_match"] = now_ts

    rp_now = int(p["rp"])
    rank = _rank_name(rp_now)
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🎾 PADEL MATCH</b>
{message.from_user.mention}

<b>Hasil:</b> {result}{extra}
<b>RP:</b> <code>{rp_change:+d}</code> → <code>{rp_now}</code> (<b>{rank}</b>)
<b>Uang +</b> <code>{uang_change}</code>

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("padelshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in PADEL_SHOP]
    await message.reply(
        "<blockquote><b>🛒 PADEL SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.padelbuy id</code>\nContoh: <code>.padelbuy 2</code></blockquote>"
    )

@PY.UBOT("padelbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.padelbuy id</code>\nContoh: <code>.padelbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in PADEL_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek dulu: <code>.padelshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_padel(u)
    p = u["padel"]

    price = int(item["price"])
    voucher = float(p["buff"].get("voucher", 0.0))
    final_price = int(price * (1.0 - voucher)) if voucher > 0 else price

    if int(u["uang"]) < final_price:
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>❌ UANG KURANG</b>
<b>Harga:</b> <code>{final_price}</code>
<b>Saldo kamu:</b> <code>{u['uang']}</code></blockquote>
""")

    u["uang"] = int(u["uang"]) - final_price
    p["bag"].append({"name": item["name"], "type": item["type"], "ts": datetime.now(TZ).isoformat()})

    note = ""
    if item["type"] == "voucher":
        p["buff"]["voucher"] = float(item["value"])
        note = f"✅ Voucher aktif: diskon <b>{int(item['value']*100)}%</b> untuk pembelian berikutnya."
    elif item["type"] == "exp_boost":
        p["buff"]["exp_boost"] = int(p["buff"].get("exp_boost", 0)) + int(item["value"])
        note = f"✅ Boost EXP aktif untuk <b>{item['value']}</b> kali latihan."
    elif item["type"] == "rp_boost":
        p["buff"]["rp_boost"] = int(p["buff"].get("rp_boost", 0)) + int(item["value"])
        note = f"✅ Boost Ranking aktif untuk <b>{item['value']}</b> kali menang."
    else:
        note = "✅ Item cosmetic tersimpan di inventory."

    if voucher > 0:
        p["buff"]["voucher"] = 0.0

    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ PEMBELIAN BERHASIL</b>
{message.from_user.mention}

<b>Item:</b> {item['name']}
<b>Harga dibayar:</b> <code>{final_price}</code>
<b>Saldo sekarang:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("padeltop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        p = (data or {}).get("padel")
        if not p:
            continue
        rp = int(p.get("rp", 0))
        if rp > 0:
            ranking.append((int(uid_str), rp))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP PADEL</b>\nBelum ada yang match.</blockquote>")

    lines = []
    for i, (uid, rp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{rp}</code> RP ({_rank_name(rp)})")

    await message.reply("<blockquote><b>🏆 TOP PADEL</b>\n\n" + "\n".join(lines) + "</blockquote>")
