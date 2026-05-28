import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "zonacacing"
__HELP__ = """
<blockquote><b>Game Zona Cacing</b>

- <code>.zcstart</code> → buat akun
- <code>.zc</code> → status kamu

<b>Aktivitas</b>
- <code>.zchunt</code> → cari makanan (cooldown)
- <code>.zcboost</code> → boost hunt (biaya uang)

<b>Duel</b>
- <code>.zcfight @user</code> / reply → duel zona (risk/reward)

<b>Shop</b>
- <code>.zcshop</code> → toko item
- <code>.zcbuy id qty</code> → beli item

<b>Leaderboard</b>
- <code>.zctop</code> → top panjang</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

HUNT_CD = 120
FIGHT_CD = 180

ZC_SHOP = [
    {"id": 1, "name": "🍀 Lucky Leaf (+win chance 2x fight)", "price": 220, "key": "luck", "value": 2},
    {"id": 2, "name": "🛡 Slime Shield (anti kalah 1x)", "price": 340, "key": "shield", "value": 1},
    {"id": 3, "name": "🥩 Meat Magnet (+food bonus 3x hunt)", "price": 260, "key": "magnet", "value": 3},
    {"id": 4, "name": "⚡ Speed Boost (hunt cooldown -40% 2x)", "price": 300, "key": "speed", "value": 2},
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
        db["users"][uid] = {"uang": 0, "zonacacing": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("zonacacing", None)
    return u

def _ensure_zc(u):
    if u.get("zonacacing") is None:
        u["zonacacing"] = {
            "exp": 0,
            "len": 5,
            "food": 0,
            "win": 0,
            "lose": 0,
            "last_hunt": 0,
            "last_fight": 0,
            "items": {"luck": 0, "shield": 0, "magnet": 0, "speed": 0},
        }
    else:
        z = u["zonacacing"]
        z.setdefault("exp", 0)
        z.setdefault("len", 5)
        z.setdefault("food", 0)
        z.setdefault("win", 0)
        z.setdefault("lose", 0)
        z.setdefault("last_hunt", 0)
        z.setdefault("last_fight", 0)
        z.setdefault("items", {"luck": 0, "shield": 0, "magnet": 0, "speed": 0})
        for k in ["luck", "shield", "magnet", "speed"]:
            z["items"].setdefault(k, 0)

def _lvl(exp: int) -> int:
    return 1 + (exp // 120)

def _ts():
    return int(datetime.now(TZ).timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

async def _extract_target(client, message):
    if getattr(message, "reply_to_message", None) and getattr(message.reply_to_message, "from_user", None):
        return message.reply_to_message.from_user
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return None
    raw = parts[1].strip()
    try:
        return await client.get_users(raw)
    except:
        try:
            return await client.get_users(int(raw))
        except:
            return None

@PY.UBOT("zcstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_zc(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ ZONA CACING AKTIF</b>
{message.from_user.mention}

Cek status: <code>.zc</code>
Hunt: <code>.zchunt</code>
Duel: <code>.zcfight @user</code></blockquote>
""")

@PY.UBOT("zc")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_zc(u)
    z = u["zonacacing"]
    it = z["items"]
    now = _ts()

    hunt_cd = max(0, int(z["last_hunt"]) + HUNT_CD - now)
    fight_cd = max(0, int(z["last_fight"]) + FIGHT_CD - now)

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🐛 ZONA CACING — STATUS</b>
{message.from_user.mention}

<b>Level:</b> <code>{_lvl(z['exp'])}</code> | <b>EXP:</b> <code>{z['exp']}</code>
<b>Panjang:</b> <code>{z['len']}</code>
<b>Food:</b> <code>{z['food']}</code>
<b>Win/Lose:</b> <code>{z['win']}</code>/<code>{z['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Cooldown:</b>
- Hunt: <code>{_fmt_cd(hunt_cd) if hunt_cd else "ready ✅"}</code>
- Fight: <code>{_fmt_cd(fight_cd) if fight_cd else "ready ✅"}</code>

<b>Item:</b>
- 🍀 Luck: <code>{it.get('luck',0)}</code>
- 🛡 Shield: <code>{it.get('shield',0)}</code>
- 🥩 Magnet: <code>{it.get('magnet',0)}</code>
- ⚡ Speed: <code>{it.get('speed',0)}</code></blockquote>
""")

@PY.UBOT("zchunt")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_zc(u)
    z = u["zonacacing"]
    it = z["items"]
    now = _ts()

    cd = HUNT_CD
    if int(it.get("speed", 0)) > 0:
        cd = int(HUNT_CD * 0.6)  # -40%
    left = int(z["last_hunt"]) + cd - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Hunt cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    # hasil hunt
    food_gain = random.randint(12, 38)
    uang_gain = random.randint(15, 55)
    exp_gain = random.randint(10, 26)

    event = "✅ Kamu nemu makanan di zona."

    # magnet bonus
    if int(it.get("magnet", 0)) > 0:
        bonus = random.randint(8, 25)
        food_gain += bonus
        it["magnet"] = int(it["magnet"]) - 1
        event += f" 🥩 Magnet aktif (+{bonus} food)."

    # speed consume (per hunt)
    if int(it.get("speed", 0)) > 0:
        it["speed"] = int(it["speed"]) - 1
        event += f" ⚡ Speed terpakai (sisa {it['speed']})."

    # random danger
    danger = random.randint(1, 100)
    if danger <= 10:
        lost = random.randint(10, 35)
        food_gain = max(0, food_gain - lost)
        event += " ⚠️ Kena trap, food berkurang."

    z["food"] = int(z["food"]) + food_gain
    u["uang"] = int(u["uang"]) + uang_gain
    z["exp"] = int(z["exp"]) + exp_gain
    z["len"] = int(z["len"]) + (food_gain // 25)
    z["last_hunt"] = now

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🐛 HUNT BERHASIL</b>
{message.from_user.mention}

<b>Food +</b> <code>{food_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>EXP +</b> <code>{exp_gain}</code>
<b>Event:</b> {event}

<b>Panjang:</b> <code>{z['len']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("zcboost")
async def _(client, message):
    BOOST_COST = 140
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_zc(u)
    z = u["zonacacing"]

    if int(u["uang"]) < BOOST_COST:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang. Butuh <code>{BOOST_COST}</code>.</blockquote>")

    u["uang"] = int(u["uang"]) - BOOST_COST

    # boost = langsung kasih bonus hunt instant
    food_gain = random.randint(35, 85)
    uang_gain = random.randint(40, 120)
    exp_gain = random.randint(20, 55)

    # risk kecil
    if random.randint(1, 100) <= 12:
        lose = random.randint(20, 60)
        uang_gain = max(0, uang_gain - lose)
        note = f"⚠️ Kena zona panas, uang bonus berkurang."
    else:
        note = "🚀 Boost sukses!"

    z["food"] = int(z["food"]) + food_gain
    u["uang"] = int(u["uang"]) + uang_gain
    z["exp"] = int(z["exp"]) + exp_gain
    z["len"] = int(z["len"]) + (food_gain // 22)

    _save_db(db)
    await message.reply(f"""
<blockquote><b>⚡ BOOST HUNT</b>
{message.from_user.mention}

<b>Biaya:</b> <code>-{BOOST_COST}</code>
<b>Food +</b> <code>{food_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>EXP +</b> <code>{exp_gain}</code>
<b>Catatan:</b> {note}

<b>Panjang:</b> <code>{z['len']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("zcfight")
async def _(client, message):
    db = _load_db()
    me = _get_user(db, message.from_user.id)
    _ensure_zc(me)
    z1 = me["zonacacing"]
    it1 = z1["items"]
    now = _ts()

    cd = int(z1["last_fight"]) + FIGHT_CD - now
    if cd > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Fight cooldown: <b>{_fmt_cd(cd)}</b></blockquote>")

    target = await _extract_target(client, message)
    if not target:
        _save_db(db)
        return await message.reply("<blockquote>Format: <code>.zcfight @user</code> atau reply pesan target.</blockquote>")
    if target.is_bot or target.id == message.from_user.id:
        _save_db(db)
        return await message.reply("<blockquote>❌ Target tidak valid.</blockquote>")

    opp = _get_user(db, int(target.id))
    _ensure_zc(opp)
    z2 = opp["zonacacing"]
    it2 = z2["items"]

    # shield lawan
    if int(it2.get("shield", 0)) > 0:
        it2["shield"] = int(it2["shield"]) - 1
        z1["last_fight"] = now
        _save_db(db)
        return await message.reply(f"<blockquote>🛡 Duel gagal! Target pakai Shield.\nSisa shield target: <code>{it2['shield']}</code></blockquote>")

    # win chance
    base = 50
    base += min(18, (int(z1["len"]) - int(z2["len"])) // 2)
    base += min(10, (_lvl(z1["exp"]) - _lvl(z2["exp"])) * 2)

    luck_note = ""
    if int(it1.get("luck", 0)) > 0:
        base = min(90, base + 10)
        it1["luck"] = int(it1["luck"]) - 1
        luck_note = f"🍀 Lucky Leaf aktif (+10%) (sisa {it1['luck']})"

    base = max(10, min(90, base))
    win = random.randint(1, 100) <= base

    # hasil duel
    steal_uang = min(int(opp["uang"]), random.randint(25, 140))
    steal_food = min(int(z2["food"]), random.randint(20, 90))

    if win:
        opp["uang"] = int(opp["uang"]) - steal_uang
        me["uang"] = int(me["uang"]) + steal_uang
        z2["food"] = int(z2["food"]) - steal_food
        z1["food"] = int(z1["food"]) + steal_food

        z1["win"] = int(z1["win"]) + 1
        z2["lose"] = int(z2["lose"]) + 1

        z1["len"] = int(z1["len"]) + (steal_food // 25)
        z1["exp"] = int(z1["exp"]) + random.randint(12, 30)
        msg = f"✅ Kamu menang duel! Dapat <code>+{steal_uang}</code> uang & <code>+{steal_food}</code> food."
    else:
        # kalau kalah, kena denda kecil
        fine = random.randint(20, 90)
        me["uang"] = max(0, int(me["uang"]) - fine)
        z1["lose"] = int(z1["lose"]) + 1
        z2["win"] = int(z2["win"]) + 1
        msg = f"❌ Kamu kalah duel! Kena denda <code>-{fine}</code> uang."

    z1["last_fight"] = now
    _save_db(db)

    await message.reply(f"""
<blockquote><b>⚔️ DUEL ZONA CACING</b>
Pelaku: {message.from_user.mention}
Target: {target.mention}

<b>Chance:</b> <code>{base}%</code>
{luck_note if luck_note else ""}

{msg}

<b>Saldo kamu:</b> <code>{me['uang']}</code>
<b>Panjang kamu:</b> <code>{z1['len']}</code></blockquote>
""")

@PY.UBOT("zcshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in ZC_SHOP]
    await message.reply(
        "<blockquote><b>🛒 ZONA CACING SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.zcbuy id qty</code> (qty opsional)</blockquote>"
    )

@PY.UBOT("zcbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.zcbuy id qty</code>\nContoh: <code>.zcbuy 1 2</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    it = next((x for x in ZC_SHOP if x["id"] == item_id), None)
    if not it:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.zcshop</code></blockquote>")

    total = int(it["price"]) * qty
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_zc(u)
    z = u["zonacacing"]

    if int(u["uang"]) < total:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - total
    z["items"][it["key"]] = int(z["items"].get(it["key"], 0)) + (int(it["value"]) * qty)

    _save_db(db)
    await message.reply(f"<blockquote>✅ Beli <b>{it['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("zctop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})
    ranking = []

    for uid_str, data in users.items():
        z = (data or {}).get("zonacacing")
        if not z:
            continue
        ln = int(z.get("len", 0))
        if ln > 0:
            ranking.append((int(uid_str), ln))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP ZONA CACING</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, ln) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{ln}</code> panjang")

    await message.reply("<blockquote><b>🏆 TOP ZONA CACING</b>\n\n" + "\n".join(lines) + "</blockquote>")
