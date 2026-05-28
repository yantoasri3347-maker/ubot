import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "sufway"
__HELP__ = """
<blockquote><b>Game Sufway Surfing (Mini)</b>

- <code>.sufstart</code> → buat akun
- <code>.sufprofil</code> → lihat profil
- <code>.sufrun</code> → lari (cooldown) dapat score+uang+exp
- <code>.sufdaily</code> → bonus harian (1x/hari)
- <code>.sufshop</code> → toko power-up
- <code>.sufbuy id</code> → beli power-up
- <code>.suftop</code> → leaderboard score</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

RUN_CD = 90

SUFWAY_SHOP = [
    {"id": 1, "name": "🧲 Magnet (aktif 3x run)", "price": 220, "type": "magnet", "value": 3},
    {"id": 2, "name": "🚀 Jetpack (aktif 2x run)", "price": 280, "type": "jetpack", "value": 2},
    {"id": 3, "name": "🛡 Hoverboard (anti jatuh 1x)", "price": 260, "type": "hover", "value": 1},
    {"id": 4, "name": "🎫 Voucher Diskon 20% (1x beli)", "price": 200, "type": "voucher", "value": 0.20},
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
        db["users"][uid] = {"uang": 0, "sufway": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("sufway", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 120)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _ensure_sufway(u):
    if u.get("sufway") is None:
        u["sufway"] = {
            "exp": 0,
            "score": 0,
            "best": 0,
            "streak": 0,
            "runs": 0,
            "last_run": 0,
            "last_daily": None,
            "buff": {"magnet": 0, "jetpack": 0, "hover": 0, "voucher": 0.0},
        }
    else:
        u["sufway"].setdefault("buff", {"magnet": 0, "jetpack": 0, "hover": 0, "voucher": 0.0})
        u["sufway"]["buff"].setdefault("magnet", 0)
        u["sufway"]["buff"].setdefault("jetpack", 0)
        u["sufway"]["buff"].setdefault("hover", 0)
        u["sufway"]["buff"].setdefault("voucher", 0.0)

@PY.UBOT("sufstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sufway(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ SUFWAY GAME AKTIF</b>
{message.from_user.mention}

Main:
<code>.sufrun</code> / <code>.sufprofil</code> / <code>.sufshop</code></blockquote>
""")

@PY.UBOT("sufprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sufway(u)
    s = u["sufway"]

    lvl = _lvl_from_exp(int(s["exp"]))
    b = s.get("buff", {})

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🚇 PROFIL SUFWAY</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code> | <b>EXP:</b> <code>{s['exp']}</code>
<b>Total Score:</b> <code>{s['score']}</code>
<b>Best Run:</b> <code>{s['best']}</code>
<b>Streak:</b> <code>{s['streak']}</code>
<b>Total Run:</b> <code>{s['runs']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Power-up:</b>
- Magnet: <code>{int(b.get('magnet',0))}x</code>
- Jetpack: <code>{int(b.get('jetpack',0))}x</code>
- Hoverboard: <code>{int(b.get('hover',0))}x</code></blockquote>
""")

@PY.UBOT("sufdaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sufway(u)
    s = u["sufway"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if s.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Sufway sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(90, 190)
    bonus_exp = random.randint(30, 75)
    bonus_score = random.randint(100, 250)

    u["uang"] = int(u["uang"]) + bonus_uang
    s["exp"] = int(s["exp"]) + bonus_exp
    s["score"] = int(s["score"]) + bonus_score
    s["last_daily"] = today

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 SUFWAY DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>
<b>Score +</b> <code>{bonus_score}</code>

Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("sufrun")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sufway(u)
    s = u["sufway"]
    b = s["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(s.get("last_run", 0))
    if now_ts - last < RUN_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Masih cooldown run. Coba lagi <b>{_fmt_cd(RUN_CD - (now_ts-last))}</b>.</blockquote>")

    base_score = random.randint(120, 320)
    base_uang = random.randint(18, 45)
    exp_gain = random.randint(20, 55)

    event_lines = []
    crashed = False

    if int(b.get("jetpack", 0)) > 0:
        boost = random.randint(120, 260)
        base_score += boost
        b["jetpack"] = int(b["jetpack"]) - 1
        event_lines.append(f"🚀 Jetpack: +{boost} score (sisa {b['jetpack']}x)")

    if int(b.get("magnet", 0)) > 0:
        bonus_coin = random.randint(25, 70)
        base_uang += bonus_coin
        b["magnet"] = int(b["magnet"]) - 1
        event_lines.append(f"🧲 Magnet: +{bonus_coin} uang (sisa {b['magnet']}x)")

    roll = random.randint(1, 100)
    if roll <= 10:
        crashed = True
        event_lines.append("💥 Nabrak! Run gagal.")
    elif roll <= 20:
        bonus = random.randint(40, 110)
        base_uang += bonus
        event_lines.append(f"🪙 Coin Rush: +{bonus} uang")
    elif roll <= 30:
        bonus = random.randint(80, 180)
        base_score += bonus
        event_lines.append(f"✨ Super Jump: +{bonus} score")
    else:
        event_lines.append("✅ Lari lancar.")

    if crashed and int(b.get("hover", 0)) > 0:
        crashed = False
        b["hover"] = int(b["hover"]) - 1
        base_score = max(60, base_score // 2)
        base_uang = max(10, base_uang // 2)
        exp_gain = max(10, exp_gain // 2)
        event_lines.append(f"🛡 Hoverboard nyelametin kamu! (sisa {b['hover']}x)")

    if crashed:
        s["streak"] = 0
        gain_score = 0
        gain_uang = 0
        gain_exp = max(5, exp_gain // 3)
    else:
        s["streak"] = int(s["streak"]) + 1
        streak_bonus = min(120, s["streak"] * 10)
        base_score += streak_bonus
        event_lines.append(f"🔥 Streak bonus: +{streak_bonus} score")
        gain_score = base_score
        gain_uang = base_uang
        gain_exp = exp_gain

    s["score"] = int(s["score"]) + gain_score
    s["exp"] = int(s["exp"]) + gain_exp
    u["uang"] = int(u["uang"]) + gain_uang
    s["runs"] = int(s["runs"]) + 1
    s["last_run"] = now_ts
    s["best"] = max(int(s.get("best", 0)), gain_score)

    lvl = _lvl_from_exp(int(s["exp"]))
    _save_db(db)

    ev = "\n".join([f"- {x}" for x in event_lines])

    await message.reply(f"""
<blockquote><b>🏃‍♂️ SUFWAY RUN</b>
{message.from_user.mention}

<b>Hasil:</b> {"❌ Gagal" if crashed else "✅ Sukses"}
<b>Score +</b> <code>{gain_score}</code>
<b>Uang +</b> <code>{gain_uang}</code>
<b>EXP +</b> <code>{gain_exp}</code>

<b>Event:</b>
{ev}

<b>Level:</b> <code>{lvl}</code>
<b>Total Score:</b> <code>{s['score']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("sufshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in SUFWAY_SHOP]
    await message.reply(
        "<blockquote><b>🛒 SUFWAY SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.sufbuy id</code>\nContoh: <code>.sufbuy 1</code></blockquote>"
    )

@PY.UBOT("sufbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.sufbuy id</code>\nContoh: <code>.sufbuy 1</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in SUFWAY_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.sufshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sufway(u)
    s = u["sufway"]
    b = s["buff"]

    price = int(item["price"])
    voucher = float(b.get("voucher", 0.0))
    final_price = int(price * (1.0 - voucher)) if voucher > 0 else price

    if int(u["uang"]) < final_price:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{final_price}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - final_price

    if item["type"] == "voucher":
        b["voucher"] = float(item["value"])
        note = f"🎫 Voucher aktif: diskon <b>{int(item['value']*100)}%</b> untuk pembelian berikutnya."
    else:
        b[item["type"]] = int(b.get(item["type"], 0)) + int(item.get("value", 1))
        note = f"✅ {item['name']} ditambahkan."

    if voucher > 0:
        b["voucher"] = 0.0

    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ BELI BERHASIL</b>
{message.from_user.mention}

<b>Item:</b> {item['name']}
<b>Harga dibayar:</b> <code>{final_price}</code>
<b>Saldo:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("suftop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        s = (data or {}).get("sufway")
        if not s:
            continue
        score = int(s.get("score", 0))
        if score > 0:
            ranking.append((int(uid_str), score))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP SUFWAY</b>\nBelum ada yang lari.</blockquote>")

    lines = []
    for i, (uid, score) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{score}</code> score")

    await message.reply("<blockquote><b>🏆 TOP SUFWAY</b>\n\n" + "\n".join(lines) + "</blockquote>")
    