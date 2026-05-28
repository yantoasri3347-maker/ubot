import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "roblox"
__HELP__ = """
<blockquote><b>Game Roblox (Mini)</b>

- <code>.rbxstart</code> → buat akun Roblox mini
- <code>.rbxprofil</code> → profil
- <code>.rbxdaily</code> → bonus harian
- <code>.rbxdev</code> → dev game (cooldown) dapat EXP+Robux
- <code>.rbxtrade</code> → trade Robux (cooldown) bisa profit/loss
- <code>.rbxgamepass</code> → bikin gamepass (pakai Robux → dapat uang)
- <code>.rbxshop</code> → toko boost
- <code>.rbxbuy id</code> → beli boost
- <code>.rbxtop</code> → leaderboard Robux</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

DEV_CD = 120
TRADE_CD = 180

RBX_SHOP = [
    {"id": 1, "name": "🧠 Dev Booster (3x dev)", "price": 240, "type": "dev_boost", "value": 3},
    {"id": 2, "name": "📈 Trade Insurance (anti rugi 1x)", "price": 320, "type": "insure", "value": 1},
    {"id": 3, "name": "🎫 Voucher Diskon 20% (1x beli)", "price": 200, "type": "voucher", "value": 0.20},
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
        db["users"][uid] = {"uang": 0, "roblox": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("roblox", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 140)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _ensure_rbx(u):
    if u.get("roblox") is None:
        u["roblox"] = {
            "exp": 0,
            "robux": 0,
            "dev_done": 0,
            "trade_done": 0,
            "gamepass": 0,
            "last_dev": 0,
            "last_trade": 0,
            "last_daily": None,
            "buff": {"dev_boost": 0, "insure": 0, "voucher": 0.0},
        }
    else:
        u["roblox"].setdefault("buff", {"dev_boost": 0, "insure": 0, "voucher": 0.0})
        u["roblox"]["buff"].setdefault("dev_boost", 0)
        u["roblox"]["buff"].setdefault("insure", 0)
        u["roblox"]["buff"].setdefault("voucher", 0.0)

@PY.UBOT("rbxstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ ROBLOX GAME AKTIF</b>
{message.from_user.mention}

Main:
<code>.rbxdev</code> / <code>.rbxtrade</code> / <code>.rbxprofil</code> / <code>.rbxshop</code></blockquote>
""")

@PY.UBOT("rbxprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    r = u["roblox"]
    lvl = _lvl_from_exp(int(r["exp"]))
    b = r.get("buff", {})
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🟦 ROBLOX PROFIL</b>
{message.from_user.mention}

<b>Dev Level:</b> <code>{lvl}</code> (<b>EXP:</b> <code>{r['exp']}</code>)
<b>Robux:</b> <code>{r['robux']}</code>
<b>Dev done:</b> <code>{r['dev_done']}</code>
<b>Trade done:</b> <code>{r['trade_done']}</code>
<b>Gamepass dibuat:</b> <code>{r['gamepass']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Dev Booster: <code>{int(b.get('dev_boost',0))}x</code>
- Insurance: <code>{int(b.get('insure',0))}x</code></blockquote>
""")

@PY.UBOT("rbxdaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    r = u["roblox"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if r.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Roblox sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_robux = random.randint(20, 60)
    bonus_uang = random.randint(70, 160)
    r["robux"] = int(r["robux"]) + bonus_robux
    u["uang"] = int(u["uang"]) + bonus_uang
    r["last_daily"] = today

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 ROBLOX DAILY</b>
{message.from_user.mention}

<b>Robux +</b> <code>{bonus_robux}</code>
<b>Uang +</b> <code>{bonus_uang}</code>

Robux: <code>{r['robux']}</code> | Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("rbxdev")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    r = u["roblox"]
    b = r["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(r.get("last_dev", 0))
    if now_ts - last < DEV_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown dev. Coba lagi <b>{_fmt_cd(DEV_CD - (now_ts-last))}</b>.</blockquote>")

    exp_gain = random.randint(25, 65)
    robux_gain = random.randint(10, 30)
    event = "✅ Kamu update map & scripting."

    roll = random.randint(1, 100)
    if roll <= 12:
        robux_gain += random.randint(10, 25)
        event = "🔥 Game kamu trending! Robux naik besar."
    elif roll <= 22:
        exp_gain += random.randint(10, 25)
        event = "🧠 Dapet ide baru! Bonus EXP."

    boost_note = ""
    if int(b.get("dev_boost", 0)) > 0:
        bonus = random.randint(12, 28)
        exp_gain += bonus
        b["dev_boost"] = int(b["dev_boost"]) - 1
        boost_note = f"🧠 Dev Booster: +{bonus} EXP (sisa {b['dev_boost']}x)"

    r["exp"] = int(r["exp"]) + exp_gain
    r["robux"] = int(r["robux"]) + robux_gain
    r["dev_done"] = int(r["dev_done"]) + 1
    r["last_dev"] = now_ts

    lvl = _lvl_from_exp(int(r["exp"]))
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🛠 ROBLOX DEV</b>
{message.from_user.mention}

<b>EXP +</b> <code>{exp_gain}</code>
<b>Robux +</b> <code>{robux_gain}</code>
<b>Event:</b> {event}{extra}

<b>Level:</b> <code>{lvl}</code> | <b>Robux:</b> <code>{r['robux']}</code></blockquote>
""")

@PY.UBOT("rbxtrade")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    r = u["roblox"]
    b = r["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(r.get("last_trade", 0))
    if now_ts - last < TRADE_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown trade. Coba lagi <b>{_fmt_cd(TRADE_CD - (now_ts-last))}</b>.</blockquote>")

    if int(r["robux"]) < 15:
        _save_db(db)
        return await message.reply("<blockquote>❌ Robux kamu minim. Kumpulin dulu lewat <code>.rbxdev</code> / <code>.rbxdaily</code>.</blockquote>")

    modal = random.randint(10, 30)
    modal = min(modal, int(r["robux"]))
    outcome = random.randint(1, 100)

    delta = 0
    event = ""

    if outcome <= 55:
        # profit
        profit = random.randint(5, 25)
        delta = profit
        event = f"📈 Profit! Kamu untung +{profit} robux."
    else:
        # loss
        loss = random.randint(5, 25)
        delta = -loss
        event = f"📉 Rugi! Kamu minus {loss} robux."

    insure_note = ""
    if delta < 0 and int(b.get("insure", 0)) > 0:
        # cancel loss
        b["insure"] = int(b["insure"]) - 1
        delta = 0
        insure_note = "🛡 Insurance aktif! Rugi dibatalkan (1x)."

    r["robux"] = max(0, int(r["robux"]) + delta)
    r["trade_done"] = int(r["trade_done"]) + 1
    r["last_trade"] = now_ts

    _save_db(db)

    extra = f"\n{insure_note}" if insure_note else ""
    await message.reply(f"""
<blockquote><b>🔁 ROBLOX TRADE</b>
{message.from_user.mention}

<b>Modal:</b> <code>{modal} robux</code>
<b>Perubahan:</b> <code>{delta:+d}</code> robux
<b>Hasil:</b> {event}{extra}

<b>Robux sekarang:</b> <code>{r['robux']}</code></blockquote>
""")

@PY.UBOT("rbxgamepass")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    r = u["roblox"]

    cost = random.randint(25, 55)
    if int(r["robux"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Robux kurang buat bikin gamepass.\nButuh: <code>{cost}</code> | Robux kamu: <code>{r['robux']}</code></blockquote>")

    # payout uang dari gamepass (anggap hasil jual)
    payout = random.randint(90, 240)

    r["robux"] = int(r["robux"]) - cost
    u["uang"] = int(u["uang"]) + payout
    r["gamepass"] = int(r["gamepass"]) + 1

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎟 ROBLOX GAMEPASS</b>
{message.from_user.mention}

<b>Biaya:</b> <code>-{cost} robux</code>
<b>Hasil jual:</b> <code>+{payout} uang</code>

Robux: <code>{r['robux']}</code> | Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("rbxshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in RBX_SHOP]
    await message.reply(
        "<blockquote><b>🛒 ROBLOX SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.rbxbuy id</code>\nContoh: <code>.rbxbuy 1</code></blockquote>"
    )

@PY.UBOT("rbxbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.rbxbuy id</code>\nContoh: <code>.rbxbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in RBX_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.rbxshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rbx(u)
    r = u["roblox"]
    b = r["buff"]

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

@PY.UBOT("rbxtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        r = (data or {}).get("roblox")
        if not r:
            continue
        robux = int(r.get("robux", 0))
        if robux > 0:
            ranking.append((int(uid_str), robux))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP ROBLOX</b>\nBelum ada yang punya Robux.</blockquote>")

    lines = []
    for i, (uid, robux) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{robux}</code> robux")

    await message.reply("<blockquote><b>🏆 TOP ROBLOX</b>\n\n" + "\n".join(lines) + "</blockquote>")
