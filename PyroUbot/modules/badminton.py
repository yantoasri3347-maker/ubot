import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "badminton"
__HELP__ = """
<blockquote><b>Game Badminton (Mini)</b>

- <code>.bdstart</code> → buat akun badminton
- <code>.bdprofil</code> → lihat profil
- <code>.bddaily</code> → bonus harian (1x/hari)
- <code>.bdlatih</code> → latihan exp + uang (cooldown)
- <code>.bdmatch</code> → tanding (cooldown) naik/turun ranking
- <code>.bdshop</code> → toko item
- <code>.bdbuy id</code> → beli item (pakai uang)
- <code>.bdtop</code> → leaderboard ranking

Catatan: Ini mini-game Telegram.</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

LATIH_CD = 120
MATCH_CD = 180

BD_SHOP = [
    {"id": 1, "name": "🎫 Voucher Diskon 20%", "price": 200, "type": "voucher", "value": 0.20},
    {"id": 2, "name": "🏋️ Boost EXP (3x Latih)", "price": 230, "type": "exp_boost", "value": 3},
    {"id": 3, "name": "🏸 Boost Ranking (2x Menang)", "price": 360, "type": "rp_boost", "value": 2},
    {"id": 4, "name": "🎽 Grip Premium (Cosmetic)", "price": 170, "type": "cosmetic", "value": "grip"},
    {"id": 5, "name": "🪶 Shuttle Pro (Cosmetic)", "price": 310, "type": "cosmetic", "value": "shuttle"},
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
        db["users"][uid] = {"uang": 0, "bd": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("bd", None)
    return u

def _level_from_exp(exp: int) -> int:
    return 1 + (exp // 120)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank_name(rp: int) -> str:
    if rp < 100: return "Beginner"
    if rp < 250: return "Intermediate"
    if rp < 450: return "Advanced"
    if rp < 700: return "Pro"
    if rp < 1000: return "Elite"
    return "Champion"

def _ensure_bd(u):
    if u.get("bd") is None:
        u["bd"] = {
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
        u["bd"].setdefault("bag", [])
        u["bd"].setdefault("buff", {"voucher": 0.0, "exp_boost": 0, "rp_boost": 0})
        u["bd"]["buff"].setdefault("voucher", 0.0)
        u["bd"]["buff"].setdefault("exp_boost", 0)
        u["bd"]["buff"].setdefault("rp_boost", 0)

@PY.UBOT("bdstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bd(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ BADMINTON GAME AKTIF</b>
{message.from_user.mention}

Main:
<code>.bdlatih</code> / <code>.bdmatch</code> / <code>.bdprofil</code> / <code>.bdshop</code></blockquote>
""")

@PY.UBOT("bdprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bd(u)
    b = u["bd"]

    exp = int(b["exp"])
    lvl = _level_from_exp(exp)
    rp = int(b["rp"])
    rank = _rank_name(rp)

    bf = b.get("buff", {})
    voucher = int(float(bf.get("voucher", 0.0)) * 100)
    expb = int(bf.get("exp_boost", 0))
    rpb = int(bf.get("rp_boost", 0))

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🏸 PROFIL BADMINTON</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code> (<b>EXP:</b> <code>{exp}</code>)
<b>Rank:</b> <code>{rank}</code> (<b>RP:</b> <code>{rp}</code>)
<b>Win:</b> <code>{b['win']}</code> | <b>Lose:</b> <code>{b['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Voucher: <code>{voucher}%</code>
- EXP Boost: <code>{expb}x</code>
- Rank Boost: <code>{rpb}x</code></blockquote>
""")

@PY.UBOT("bddaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bd(u)
    b = u["bd"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if b.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Badminton sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(80, 170)
    bonus_exp = random.randint(30, 70)

    u["uang"] = int(u["uang"]) + bonus_uang
    b["exp"] = int(b["exp"]) + bonus_exp
    b["last_daily"] = today

    _save_db(db)
    lvl = _level_from_exp(int(b["exp"]))
    await message.reply(f"""
<blockquote><b>🎁 BD DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>

<b>Level sekarang:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("bdlatih")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bd(u)
    b = u["bd"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(b.get("last_latih", 0))
    if now_ts - last < LATIH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Masih cooldown latihan. Coba lagi <b>{_fmt_cd(LATIH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    exp_gain = random.randint(25, 60)
    uang_gain = random.randint(20, 55)

    roll = random.randint(1, 100)
    event = "✅ Latihan footwork & smash lancar."
    if roll <= 15:
        event = "💥 Drill smash! Bonus EXP."
        exp_gain += random.randint(10, 25)
    elif roll <= 25:
        event = "🩹 Salah timing. EXP kecil."
        exp_gain = max(10, exp_gain - random.randint(5, 15))

    boost_note = ""
    left = int(b["buff"].get("exp_boost", 0))
    if left > 0:
        bonus = random.randint(15, 35)
        exp_gain += bonus
        b["buff"]["exp_boost"] = left - 1
        boost_note = f"🏋️ Boost EXP: +{bonus} (sisa {b['buff']['exp_boost']}x)"

    b["exp"] = int(b["exp"]) + exp_gain
    u["uang"] = int(u["uang"]) + uang_gain
    b["last_latih"] = now_ts

    lvl = _level_from_exp(int(b["exp"]))
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🏋️ BD LATIH</b>
{message.from_user.mention}

<b>EXP +</b> <code>{exp_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Event:</b> {event}{extra}

<b>Level:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("bdmatch")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bd(u)
    b = u["bd"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(b.get("last_match", 0))
    if now_ts - last < MATCH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Tunggu dulu. Match lagi <b>{_fmt_cd(MATCH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    lvl = _level_from_exp(int(b["exp"]))
    win_chance = min(80, 45 + (lvl * 2))
    r = random.randint(1, 100)

    rp_change = 0
    uang_change = 0
    result = ""

    if r <= win_chance:
        rp_change = random.randint(12, 30)
        uang_change = random.randint(25, 80)
        b["win"] = int(b["win"]) + 1
        result = "🏆 MENANG! Netting rapi!"
        if random.randint(1, 100) <= 12:
            bonus = random.randint(10, 25)
            rp_change += bonus
            result += f" ⭐ Bonus RP +{bonus}"
    else:
        rp_change = -random.randint(8, 22)
        uang_change = random.randint(10, 40)
        b["lose"] = int(b["lose"]) + 1
        result = "💀 KALAH! Kena drop shot."

    boost_note = ""
    left = int(b["buff"].get("rp_boost", 0))
    if left > 0 and rp_change > 0:
        bonus_rp = random.randint(5, 15)
        rp_change += bonus_rp
        b["buff"]["rp_boost"] = left - 1
        boost_note = f"🏸 Boost Ranking: +{bonus_rp} (sisa {b['buff']['rp_boost']}x)"

    b["rp"] = max(0, int(b["rp"]) + rp_change)
    u["uang"] = int(u["uang"]) + uang_change
    b["last_match"] = now_ts

    rp_now = int(b["rp"])
    rank = _rank_name(rp_now)
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🏸 BD MATCH</b>
{message.from_user.mention}

<b>Hasil:</b> {result}{extra}
<b>RP:</b> <code>{rp_change:+d}</code> → <code>{rp_now}</code> (<b>{rank}</b>)
<b>Uang +</b> <code>{uang_change}</code>

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("bdshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in BD_SHOP]
    await message.reply(
        "<blockquote><b>🛒 BD SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.bdbuy id</code>\nContoh: <code>.bdbuy 2</code></blockquote>"
    )

@PY.UBOT("bdbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.bdbuy id</code>\nContoh: <code>.bdbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in BD_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek dulu: <code>.bdshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bd(u)
    b = u["bd"]

    price = int(item["price"])
    voucher = float(b["buff"].get("voucher", 0.0))
    final_price = int(price * (1.0 - voucher)) if voucher > 0 else price

    if int(u["uang"]) < final_price:
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>❌ UANG KURANG</b>
<b>Harga:</b> <code>{final_price}</code>
<b>Saldo kamu:</b> <code>{u['uang']}</code></blockquote>
""")

    u["uang"] = int(u["uang"]) - final_price
    b["bag"].append({"name": item["name"], "type": item["type"], "ts": datetime.now(TZ).isoformat()})

    note = ""
    if item["type"] == "voucher":
        b["buff"]["voucher"] = float(item["value"])
        note = f"✅ Voucher aktif: diskon <b>{int(item['value']*100)}%</b> untuk pembelian berikutnya."
    elif item["type"] == "exp_boost":
        b["buff"]["exp_boost"] = int(b["buff"].get("exp_boost", 0)) + int(item["value"])
        note = f"✅ Boost EXP aktif untuk <b>{item['value']}</b> kali latihan."
    elif item["type"] == "rp_boost":
        b["buff"]["rp_boost"] = int(b["buff"].get("rp_boost", 0)) + int(item["value"])
        note = f"✅ Boost Ranking aktif untuk <b>{item['value']}</b> kali menang."
    else:
        note = "✅ Item cosmetic tersimpan di inventory."

    if voucher > 0:
        b["buff"]["voucher"] = 0.0

    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ PEMBELIAN BERHASIL</b>
{message.from_user.mention}

<b>Item:</b> {item['name']}
<b>Harga dibayar:</b> <code>{final_price}</code>
<b>Saldo sekarang:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("bdtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        b = (data or {}).get("bd")
        if not b:
            continue
        rp = int(b.get("rp", 0))
        if rp > 0:
            ranking.append((int(uid_str), rp))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP BADMINTON</b>\nBelum ada yang match.</blockquote>")

    lines = []
    for i, (uid, rp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{rp}</code> RP ({_rank_name(rp)})")

    await message.reply("<blockquote><b>🏆 TOP BADMINTON</b>\n\n" + "\n".join(lines) + "</blockquote>")
    