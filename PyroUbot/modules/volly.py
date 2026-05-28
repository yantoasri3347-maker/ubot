import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "voly"
__HELP__ = """
<blockquote><b>Game Voly (Mini)</b>

- <code>.volystart</code> → buat akun voly
- <code>.volyprofil</code> → lihat profil voly
- <code>.volydaily</code> → bonus harian (1x/hari)
- <code>.volylatih</code> → latihan exp + uang (cooldown)
- <code>.volymatch</code> → tanding (cooldown) naik/turun rank
- <code>.volyshop</code> → toko item voly
- <code>.volybuy id</code> → beli item (pakai uang)
- <code>.volytop</code> → leaderboard rank

Catatan: Ini mini-game Telegram.</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

LATIH_CD = 120
MATCH_CD = 180

VOLY_SHOP = [
    {"id": 1, "name": "🎫 Voucher Diskon 20%", "price": 200, "type": "voucher", "value": 0.20},
    {"id": 2, "name": "🏋️ Boost EXP (3x Latih)", "price": 230, "type": "exp_boost", "value": 3},
    {"id": 3, "name": "🏐 Boost Rank (2x Menang)", "price": 360, "type": "rp_boost", "value": 2},
    {"id": 4, "name": "👟 Sepatu Pro (Cosmetic)", "price": 180, "type": "cosmetic", "value": "shoes"},
    {"id": 5, "name": "🎽 Jersey Tim (Cosmetic)", "price": 320, "type": "cosmetic", "value": "jersey"},
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
        db["users"][uid] = {"uang": 0, "voly": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("voly", None)
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
    if rp < 450: return "Amateur"
    if rp < 700: return "Pro"
    if rp < 1000: return "Elite"
    return "Champion"

def _ensure_voly(u):
    if u.get("voly") is None:
        u["voly"] = {
            "exp": 0,
            "rp": 0,
            "win": 0,
            "lose": 0,
            "last_latih": 0,
            "last_match": 0,
            "last_daily": None,
            "bag": [],
            "buff": {
                "voucher": 0.0,
                "exp_boost": 0,
                "rp_boost": 0,
            },
        }
    else:
        u["voly"].setdefault("bag", [])
        u["voly"].setdefault("buff", {"voucher": 0.0, "exp_boost": 0, "rp_boost": 0})
        u["voly"]["buff"].setdefault("voucher", 0.0)
        u["voly"]["buff"].setdefault("exp_boost", 0)
        u["voly"]["buff"].setdefault("rp_boost", 0)

@PY.UBOT("volystart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_voly(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ VOLY GAME AKTIF</b>
{message.from_user.mention}

Main:
<code>.volylatih</code> / <code>.volymatch</code> / <code>.volyprofil</code> / <code>.volyshop</code></blockquote>
""")

@PY.UBOT("volyprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_voly(u)
    v = u["voly"]

    exp = int(v["exp"])
    lvl = _level_from_exp(exp)
    rp = int(v["rp"])
    rank = _rank_name(rp)

    b = v.get("buff", {})
    voucher = int(float(b.get("voucher", 0.0)) * 100)
    expb = int(b.get("exp_boost", 0))
    rpb = int(b.get("rp_boost", 0))

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🏐 PROFIL VOLY</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code> (<b>EXP:</b> <code>{exp}</code>)
<b>Rank:</b> <code>{rank}</code> (<b>RP:</b> <code>{rp}</code>)
<b>Win:</b> <code>{v['win']}</code> | <b>Lose:</b> <code>{v['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Voucher: <code>{voucher}%</code>
- EXP Boost: <code>{expb}x</code>
- Rank Boost: <code>{rpb}x</code></blockquote>
""")

@PY.UBOT("volydaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_voly(u)
    v = u["voly"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if v.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Voly sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(80, 170)
    bonus_exp = random.randint(30, 70)

    u["uang"] = int(u["uang"]) + bonus_uang
    v["exp"] = int(v["exp"]) + bonus_exp
    v["last_daily"] = today

    _save_db(db)
    lvl = _level_from_exp(int(v["exp"]))
    await message.reply(f"""
<blockquote><b>🎁 VOLY DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>

<b>Level sekarang:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("volylatih")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_voly(u)
    v = u["voly"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(v.get("last_latih", 0))
    if now_ts - last < LATIH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Masih capek latihan. Coba lagi <b>{_fmt_cd(LATIH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    exp_gain = random.randint(25, 60)
    uang_gain = random.randint(20, 55)

    roll = random.randint(1, 100)
    event = "✅ Latihan servis & receive lancar."
    if roll <= 15:
        event = "💥 Latihan ekstra! Bonus EXP."
        exp_gain += random.randint(10, 25)
    elif roll <= 25:
        event = "🩹 Salah landing. EXP kecil."
        exp_gain = max(10, exp_gain - random.randint(5, 15))

    # EXP BOOST
    boost_note = ""
    left = int(v["buff"].get("exp_boost", 0))
    if left > 0:
        bonus = random.randint(15, 35)
        exp_gain += bonus
        v["buff"]["exp_boost"] = left - 1
        boost_note = f"🏋️ Boost EXP: +{bonus} (sisa {v['buff']['exp_boost']}x)"

    v["exp"] = int(v["exp"]) + exp_gain
    u["uang"] = int(u["uang"]) + uang_gain
    v["last_latih"] = now_ts

    lvl = _level_from_exp(int(v["exp"]))
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🏋️ VOLY LATIH</b>
{message.from_user.mention}

<b>EXP +</b> <code>{exp_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Event:</b> {event}{extra}

<b>Level:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("volymatch")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_voly(u)
    v = u["voly"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(v.get("last_match", 0))
    if now_ts - last < MATCH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Tunggu dulu. Match lagi <b>{_fmt_cd(MATCH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    lvl = _level_from_exp(int(v["exp"]))
    win_chance = min(80, 45 + (lvl * 2))
    r = random.randint(1, 100)

    rp_change = 0
    uang_change = 0
    result = ""

    if r <= win_chance:
        rp_change = random.randint(12, 30)
        uang_change = random.randint(25, 80)
        v["win"] = int(v["win"]) + 1
        result = "🏆 MENANG! Smash keras!"
        if random.randint(1, 100) <= 12:
            bonus = random.randint(10, 25)
            rp_change += bonus
            result += f" ⭐ Bonus RP +{bonus}"
    else:
        rp_change = -random.randint(8, 22)
        uang_change = random.randint(10, 40)
        v["lose"] = int(v["lose"]) + 1
        result = "💀 KALAH! Kena comeback."

    # RP BOOST (hanya kalau menang)
    boost_note = ""
    left = int(v["buff"].get("rp_boost", 0))
    if left > 0 and rp_change > 0:
        bonus_rp = random.randint(5, 15)
        rp_change += bonus_rp
        v["buff"]["rp_boost"] = left - 1
        boost_note = f"🏐 Rank Boost: +{bonus_rp} (sisa {v['buff']['rp_boost']}x)"

    v["rp"] = max(0, int(v["rp"]) + rp_change)
    u["uang"] = int(u["uang"]) + uang_change
    v["last_match"] = now_ts

    rp_now = int(v["rp"])
    rank = _rank_name(rp_now)
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🏐 VOLY MATCH</b>
{message.from_user.mention}

<b>Hasil:</b> {result}{extra}
<b>RP:</b> <code>{rp_change:+d}</code> → <code>{rp_now}</code> (<b>{rank}</b>)
<b>Uang +</b> <code>{uang_change}</code>

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("volyshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in VOLY_SHOP]
    await message.reply(
        "<blockquote><b>🛒 VOLY SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.volybuy id</code>\nContoh: <code>.volybuy 2</code></blockquote>"
    )

@PY.UBOT("volybuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.volybuy id</code>\nContoh: <code>.volybuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in VOLY_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek dulu: <code>.volyshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_voly(u)
    v = u["voly"]

    price = int(item["price"])
    voucher = float(v["buff"].get("voucher", 0.0))
    final_price = int(price * (1.0 - voucher)) if voucher > 0 else price

    if int(u["uang"]) < final_price:
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>❌ UANG KURANG</b>
<b>Harga:</b> <code>{final_price}</code>
<b>Saldo kamu:</b> <code>{u['uang']}</code></blockquote>
""")

    u["uang"] = int(u["uang"]) - final_price
    v["bag"].append({"name": item["name"], "type": item["type"], "ts": datetime.now(TZ).isoformat()})

    note = ""
    if item["type"] == "voucher":
        v["buff"]["voucher"] = float(item["value"])
        note = f"✅ Voucher aktif: diskon <b>{int(item['value']*100)}%</b> untuk pembelian berikutnya."
    elif item["type"] == "exp_boost":
        v["buff"]["exp_boost"] = int(v["buff"].get("exp_boost", 0)) + int(item["value"])
        note = f"✅ Boost EXP aktif untuk <b>{item['value']}</b> kali latihan."
    elif item["type"] == "rp_boost":
        v["buff"]["rp_boost"] = int(v["buff"].get("rp_boost", 0)) + int(item["value"])
        note = f"✅ Boost Rank aktif untuk <b>{item['value']}</b> kali menang."
    else:
        note = "✅ Item cosmetic tersimpan di inventory."

    if voucher > 0:
        v["buff"]["voucher"] = 0.0

    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ PEMBELIAN BERHASIL</b>
{message.from_user.mention}

<b>Item:</b> {item['name']}
<b>Harga dibayar:</b> <code>{final_price}</code>
<b>Saldo sekarang:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("volytop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        v = (data or {}).get("voly")
        if not v:
            continue
        rp = int(v.get("rp", 0))
        if rp > 0:
            ranking.append((int(uid_str), rp))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP VOLY</b>\nBelum ada yang match.</blockquote>")

    lines = []
    for i, (uid, rp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{rp}</code> RP ({_rank_name(rp)})")

    await message.reply("<blockquote><b>🏆 TOP VOLY</b>\n\n" + "\n".join(lines) + "</blockquote>")
