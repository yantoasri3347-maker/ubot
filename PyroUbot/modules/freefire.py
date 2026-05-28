import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "freefire"
__HELP__ = """
<blockquote><b>Game Free Fire (Mini)</b>

- <code>.ffstart</code> → buat akun FF game
- <code>.ffprofil</code> → lihat profil FF
- <code>.fflatih</code> → latihan dapat exp + uang (cooldown)
- <code>.ffpush</code> → push rank (cooldown)
- <code>.ffdaily</code> → bonus harian FF (1x/hari)
- <code>.fftop</code> → leaderboard rank
- <code>.ffshop</code> → toko item FF
- <code>.ffbuy id</code> → beli item FF (pakai uang)

Catatan: Ini mini-game Telegram (bukan cheat/diamond).</blockquote>
"""

TZ = timezone("Asia/Jakarta")

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")  # nyatu sama uang gacha/ojol
os.makedirs(DATA_DIR, exist_ok=True)

LATIH_CD = 120  # 2 menit
PUSH_CD = 180   # 3 menit

# ===== SHOP =====
FF_SHOP = [
    {"id": 1, "name": "🎫 Voucher Diskon 20%", "price": 200, "type": "voucher", "value": 0.20},
    {"id": 2, "name": "⚡ Boost EXP (3x Latih)", "price": 250, "type": "exp_boost", "value": 3},
    {"id": 3, "name": "🔥 Boost RP (2x Push)", "price": 350, "type": "rp_boost", "value": 2},
    {"id": 4, "name": "🐾 Pet Lucu (Cosmetic)", "price": 150, "type": "cosmetic", "value": "pet"},
    {"id": 5, "name": "🎽 Skin Outfit (Cosmetic)", "price": 300, "type": "cosmetic", "value": "skin"},
]

# ===== DB =====
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
        db["users"][uid] = {"uang": 0, "ff": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("ff", None)
    return u

# ===== FF CORE =====
def _rank_name(points: int) -> str:
    if points < 100: return "Bronze"
    if points < 250: return "Silver"
    if points < 450: return "Gold"
    if points < 700: return "Platinum"
    if points < 1000: return "Diamond"
    return "Heroic"

def _level_from_exp(exp: int) -> int:
    return 1 + (exp // 120)

def _ensure_ff(u):
    if u.get("ff") is None:
        u["ff"] = {
            "exp": 0,
            "rp": 0,
            "win": 0,
            "lose": 0,
            "last_latih": 0,
            "last_push": 0,
            "last_daily": None,  # YYYY-MM-DD
            "bag": [],  # inventory FF
            "buff": {   # efek item
                "voucher": 0.0,   # diskon next buy (sekali pakai)
                "exp_boost": 0,   # sisa berapa kali latihan bonus
                "rp_boost": 0,    # sisa berapa kali push bonus (menang saja)
            },
        }
    else:
        u["ff"].setdefault("bag", [])
        u["ff"].setdefault("buff", {"voucher": 0.0, "exp_boost": 0, "rp_boost": 0})
        u["ff"]["buff"].setdefault("voucher", 0.0)
        u["ff"]["buff"].setdefault("exp_boost", 0)
        u["ff"]["buff"].setdefault("rp_boost", 0)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

# ===== COMMANDS =====
@PY.UBOT("ffstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ff(u)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ FF GAME AKTIF</b>
{message.from_user.mention}

Mulai sekarang kamu bisa main:
<code>.fflatih</code> / <code>.ffpush</code> / <code>.ffprofil</code> / <code>.ffshop</code></blockquote>
""")

@PY.UBOT("ffprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ff(u)
    ff = u["ff"]

    exp = int(ff["exp"])
    lvl = _level_from_exp(exp)
    rp = int(ff["rp"])
    rank = _rank_name(rp)

    buff = ff.get("buff", {})
    voucher = int(float(buff.get("voucher", 0.0)) * 100)
    expb = int(buff.get("exp_boost", 0))
    rpb = int(buff.get("rp_boost", 0))

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🔥 PROFIL FREE FIRE</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code>  (<b>EXP:</b> <code>{exp}</code>)
<b>Rank:</b> <code>{rank}</code>  (<b>RP:</b> <code>{rp}</code>)
<b>Win:</b> <code>{ff['win']}</code> | <b>Lose:</b> <code>{ff['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Voucher: <code>{voucher}%</code>
- EXP Boost: <code>{expb}x</code>
- RP Boost: <code>{rpb}x</code>

Shop: <code>.ffshop</code></blockquote>
""")

@PY.UBOT("ffdaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ff(u)
    ff = u["ff"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if ff.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily FF sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(80, 170)
    bonus_exp = random.randint(30, 70)

    u["uang"] = int(u["uang"]) + bonus_uang
    ff["exp"] = int(ff["exp"]) + bonus_exp
    ff["last_daily"] = today

    _save_db(db)
    lvl = _level_from_exp(int(ff["exp"]))
    await message.reply(f"""
<blockquote><b>🎁 FF DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>

<b>Level sekarang:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("fflatih")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ff(u)
    ff = u["ff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(ff.get("last_latih", 0))
    if now_ts - last < LATIH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Masih capek latihan. Coba lagi <b>{_fmt_cd(LATIH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    exp_gain = random.randint(25, 60)
    uang_gain = random.randint(20, 55)

    roll = random.randint(1, 100)
    event = "✅ Latihan lancar."
    if roll <= 15:
        event = "💥 Latihan keras! Bonus EXP."
        exp_gain += random.randint(10, 25)
    elif roll <= 25:
        event = "🩹 Cedera ringan. EXP kecil."
        exp_gain = max(10, exp_gain - random.randint(5, 15))

    # APPLY EXP BOOST
    boost_note = ""
    boost_left = int(ff["buff"].get("exp_boost", 0))
    if boost_left > 0:
        bonus_boost = random.randint(15, 35)
        exp_gain += bonus_boost
        ff["buff"]["exp_boost"] = boost_left - 1
        boost_note = f"⚡ Boost EXP: +{bonus_boost} (sisa {ff['buff']['exp_boost']}x)"

    ff["exp"] = int(ff["exp"]) + exp_gain
    u["uang"] = int(u["uang"]) + uang_gain
    ff["last_latih"] = now_ts

    lvl = _level_from_exp(int(ff["exp"]))
    _save_db(db)

    extra = f"\n<b>Buff:</b> {boost_note}" if boost_note else ""
    await message.reply(f"""
<blockquote><b>🏋️ FF LATIHAN</b>
{message.from_user.mention}

<b>EXP +</b> <code>{exp_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Event:</b> {event}{extra}

<b>Level:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("ffpush")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ff(u)
    ff = u["ff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(ff.get("last_push", 0))
    if now_ts - last < PUSH_CD:
        _save_db(db)
        return await message.reply(
            f"<blockquote>⏳ Tunggu dulu. Push lagi <b>{_fmt_cd(PUSH_CD - (now_ts-last))}</b>.</blockquote>"
        )

    exp = int(ff["exp"])
    lvl = _level_from_exp(exp)

    win_chance = min(80, 45 + (lvl * 2))  # cap 80%
    r = random.randint(1, 100)

    rp_change = 0
    uang_change = 0
    result = ""

    if r <= win_chance:
        rp_change = random.randint(12, 30)
        uang_change = random.randint(25, 80)
        ff["win"] = int(ff["win"]) + 1
        result = "🏆 WIN! Booyah!"
        if random.randint(1, 100) <= 12:
            bonus = random.randint(10, 25)
            rp_change += bonus
            result += f" ⭐ Bonus RP +{bonus}"
    else:
        rp_change = -random.randint(8, 22)
        uang_change = random.randint(10, 40)
        ff["lose"] = int(ff["lose"]) + 1
        result = "💀 LOSE! Turun rank."

    # APPLY RP BOOST (hanya kalau menang / rp_change positif)
    rp_boost_note = ""
    rp_boost_left = int(ff["buff"].get("rp_boost", 0))
    if rp_boost_left > 0 and rp_change > 0:
        bonus_rp = random.randint(5, 15)
        rp_change += bonus_rp
        ff["buff"]["rp_boost"] = rp_boost_left - 1
        rp_boost_note = f"🔥 Boost RP: +{bonus_rp} (sisa {ff['buff']['rp_boost']}x)"

    ff["rp"] = max(0, int(ff["rp"]) + rp_change)
    u["uang"] = int(u["uang"]) + uang_change
    ff["last_push"] = now_ts

    rp_now = int(ff["rp"])
    rank = _rank_name(rp_now)
    _save_db(db)

    extra = f"\n<b>Buff:</b> {rp_boost_note}" if rp_boost_note else ""
    await message.reply(f"""
<blockquote><b>🎮 FF PUSH RANK</b>
{message.from_user.mention}

<b>Hasil:</b> {result}{extra}
<b>RP:</b> <code>{rp_change:+d}</code> → <code>{rp_now}</code> (<b>{rank}</b>)
<b>Uang +</b> <code>{uang_change}</code>

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("fftop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        ff = (data or {}).get("ff")
        if not ff:
            continue
        rp = int(ff.get("rp", 0))
        if rp > 0:
            ranking.append((int(uid_str), rp))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP FF</b>\nBelum ada yang push rank.</blockquote>")

    lines = []
    for i, (uid, rp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{rp}</code> RP ({_rank_name(rp)})")

    await message.reply("<blockquote><b>🏆 TOP FREE FIRE</b>\n\n" + "\n".join(lines) + "</blockquote>")

@PY.UBOT("ffshop")
async def _(client, message):
    lines = []
    for it in FF_SHOP:
        lines.append(f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang")

    await message.reply(
        "<blockquote><b>🛒 FF SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.ffbuy id</code>\nContoh: <code>.ffbuy 2</code></blockquote>"
    )

@PY.UBOT("ffbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.ffbuy id</code>\nContoh: <code>.ffbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in FF_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek dulu: <code>.ffshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ff(u)
    ff = u["ff"]

    price = int(item["price"])
    voucher = float(ff["buff"].get("voucher", 0.0))
    final_price = int(price * (1.0 - voucher)) if voucher > 0 else price

    if int(u["uang"]) < final_price:
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>❌ UANG KURANG</b>
<b>Harga:</b> <code>{final_price}</code>
<b>Saldo kamu:</b> <code>{u['uang']}</code></blockquote>
""")

    # potong uang
    u["uang"] = int(u["uang"]) - final_price

    # simpan inventory
    ff["bag"].append({
        "name": item["name"],
        "type": item["type"],
        "ts": datetime.now(TZ).isoformat(),
    })

    note = ""
    if item["type"] == "voucher":
        ff["buff"]["voucher"] = float(item["value"])
        note = f"✅ Voucher aktif: diskon <b>{int(item['value']*100)}%</b> untuk pembelian berikutnya."
    elif item["type"] == "exp_boost":
        ff["buff"]["exp_boost"] = int(ff["buff"].get("exp_boost", 0)) + int(item["value"])
        note = f"✅ Boost EXP aktif untuk <b>{item['value']}</b> kali latihan."
    elif item["type"] == "rp_boost":
        ff["buff"]["rp_boost"] = int(ff["buff"].get("rp_boost", 0)) + int(item["value"])
        note = f"✅ Boost RP aktif untuk <b>{item['value']}</b> kali push (kalau menang)."
    else:
        note = "✅ Item cosmetic tersimpan di inventory."

    # voucher yang dipakai barusan reset (diskon hanya untuk 1 pembelian)
    if voucher > 0:
        ff["buff"]["voucher"] = 0.0

    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ PEMBELIAN BERHASIL</b>
{message.from_user.mention}

<b>Item:</b> {item['name']}
<b>Harga dibayar:</b> <code>{final_price}</code>
<b>Saldo sekarang:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")
