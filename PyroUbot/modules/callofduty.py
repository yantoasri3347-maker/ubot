import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "cod"
__HELP__ = """
<blockquote><b>Game Call of Duty (Mini)</b>

- <code>.codstart</code> → buat akun
- <code>.codprofil</code> → profil
- <code>.coddaily</code> → bonus harian (1x/hari)

<b>Match</b>
- <code>.codmatch</code> → match default (MP)
- <code>.codmatch mp</code> → multiplayer
- <code>.codmatch br</code> → battle royale

<b>Loadout</b>
- <code>.codloadout</code> → lihat loadout
- <code>.codloadout ar</code> / <code>smg</code> / <code>sniper</code> → pilih

<b>Shop</b>
- <code>.codshop</code> → toko perk
- <code>.codbuy id</code> → beli perk

<b>Leaderboard</b>
- <code>.codtop</code> → top SR</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

MATCH_CD = 180  # cooldown match

COD_SHOP = [
    {"id": 1, "name": "💉 Quick Fix (+win chance 2 match)", "price": 240, "type": "win_boost", "value": 2},
    {"id": 2, "name": "🛡 Last Stand (batalin kalah 1x)", "price": 360, "type": "anti_loss", "value": 1},
    {"id": 3, "name": "🎯 Aim Assist Drill (+SR bonus 2x menang)", "price": 320, "type": "sr_boost", "value": 2},
    {"id": 4, "name": "🎫 Voucher Diskon 20% (1x beli)", "price": 200, "type": "voucher", "value": 0.20},
]

LOADOUTS = {
    "ar": {"name": "AR (Assault)", "bonus_win": 2, "bonus_k": (1, 3)},
    "smg": {"name": "SMG (Rusher)", "bonus_win": 3, "bonus_k": (2, 5)},
    "sniper": {"name": "Sniper", "bonus_win": 1, "bonus_k": (0, 6)},
}

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
        db["users"][uid] = {"uang": 0, "cod": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("cod", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 140)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank_from_sr(sr: int) -> str:
    if sr < 100: return "Rookie"
    if sr < 220: return "Veteran"
    if sr < 360: return "Elite"
    if sr < 520: return "Pro"
    if sr < 700: return "Master"
    if sr < 900: return "Grandmaster"
    return "Legendary"

def _ensure_cod(u):
    if u.get("cod") is None:
        u["cod"] = {
            "exp": 0,
            "sr": 0,        # skill rating
            "win": 0,
            "lose": 0,
            "matches": 0,
            "kills": 0,
            "deaths": 0,
            "loadout": "ar",
            "last_match": 0,
            "last_daily": None,
            "buff": {"win_boost": 0, "anti_loss": 0, "sr_boost": 0, "voucher": 0.0},
        }
    else:
        c = u["cod"]
        c.setdefault("loadout", "ar")
        c.setdefault("buff", {"win_boost": 0, "anti_loss": 0, "sr_boost": 0, "voucher": 0.0})
        c["buff"].setdefault("win_boost", 0)
        c["buff"].setdefault("anti_loss", 0)
        c["buff"].setdefault("sr_boost", 0)
        c["buff"].setdefault("voucher", 0.0)

def _mode_stats(mode: str):
    # (name, win_bonus, sr_win_rng, sr_loss_rng, exp_rng, uang_rng, k_rng, d_rng)
    mode = (mode or "mp").lower()
    if mode in ["br", "battle", "royale"]:
        return ("Battle Royale", +2, (10, 22), (8, 18), (18, 55), (25, 90), (2, 12), (0, 6))
    return ("Multiplayer", 0, (14, 28), (10, 22), (20, 55), (20, 80), (4, 18), (3, 16))

@PY.UBOT("codstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_cod(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ COD GAME AKTIF</b>
{message.from_user.mention}

Pilih loadout: <code>.codloadout</code>
Main: <code>.codmatch mp</code> / <code>.codmatch br</code></blockquote>
""")

@PY.UBOT("codprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_cod(u)
    c = u["cod"]
    lvl = _lvl_from_exp(int(c["exp"]))
    rank = _rank_from_sr(int(c["sr"]))
    ld = LOADOUTS.get(c.get("loadout", "ar"), LOADOUTS["ar"])
    b = c.get("buff", {})

    kd = (c["kills"] / c["deaths"]) if int(c["deaths"]) > 0 else float(c["kills"])
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🔫 PROFIL CALL OF DUTY</b>
{message.from_user.mention}

<b>Rank:</b> <code>{rank}</code> | <b>SR:</b> <code>{c['sr']}</code>
<b>Level:</b> <code>{lvl}</code> | <b>EXP:</b> <code>{c['exp']}</code>
<b>Win:</b> <code>{c['win']}</code> | <b>Lose:</b> <code>{c['lose']}</code> | <b>Match:</b> <code>{c['matches']}</code>

<b>Kills:</b> <code>{c['kills']}</code> | <b>Deaths:</b> <code>{c['deaths']}</code> | <b>K/D:</b> <code>{kd:.2f}</code>
<b>Loadout:</b> <code>{ld['name']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Quick Fix: <code>{int(b.get('win_boost',0))}x</code>
- Last Stand: <code>{int(b.get('anti_loss',0))}x</code>
- Aim Drill: <code>{int(b.get('sr_boost',0))}x</code></blockquote>
""")

@PY.UBOT("coddaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_cod(u)
    c = u["cod"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if c.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily COD sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(90, 180)
    bonus_exp = random.randint(30, 70)
    bonus_sr = random.randint(5, 15)

    u["uang"] = int(u["uang"]) + bonus_uang
    c["exp"] = int(c["exp"]) + bonus_exp
    c["sr"] = int(c["sr"]) + bonus_sr
    c["last_daily"] = today

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 COD DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>
<b>SR +</b> <code>{bonus_sr}</code>

SR: <code>{c['sr']}</code> | Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("codloadout")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_cod(u)
    c = u["cod"]

    if len(args) == 1:
        cur = c.get("loadout", "ar")
        lines = []
        for k, v in LOADOUTS.items():
            tag = "✅" if k == cur else "•"
            lines.append(f"{tag} <code>{k}</code> — {v['name']}")
        _save_db(db)
        return await message.reply("<blockquote><b>🎒 LOADOUT</b>\n\n" + "\n".join(lines) +
                                   "\n\nPilih: <code>.codloadout ar</code> / <code>smg</code> / <code>sniper</code></blockquote>")

    pick = args[1].strip().lower()
    if pick not in LOADOUTS:
        _save_db(db)
        return await message.reply("<blockquote>Loadout tidak ada. Pilih: <code>ar</code>/<code>smg</code>/<code>sniper</code></blockquote>")

    c["loadout"] = pick
    _save_db(db)
    await message.reply(f"<blockquote>✅ Loadout sekarang: <b>{LOADOUTS[pick]['name']}</b></blockquote>")

@PY.UBOT("codmatch")
async def _(client, message):
    mode_arg = (message.text or "").split(maxsplit=1)
    mode = mode_arg[1].strip().lower() if len(mode_arg) > 1 else "mp"
    mode_name, win_bonus, sr_win_rng, sr_loss_rng, exp_rng, uang_rng, k_rng, d_rng = _mode_stats(mode)

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_cod(u)
    c = u["cod"]
    b = c["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(c.get("last_match", 0))
    if now_ts - last < MATCH_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown match. Coba lagi <b>{_fmt_cd(MATCH_CD - (now_ts-last))}</b>.</blockquote>")

    ld = LOADOUTS.get(c.get("loadout", "ar"), LOADOUTS["ar"])
    lvl = _lvl_from_exp(int(c["exp"]))

    base_win = min(85, 45 + lvl * 2) + win_bonus + int(ld["bonus_win"])

    perk_note = ""
    if int(b.get("win_boost", 0)) > 0:
        base_win = min(92, base_win + 10)
        b["win_boost"] = int(b["win_boost"]) - 1
        perk_note = f"💉 Quick Fix aktif (+10% win) (sisa {b['win_boost']}x)"

    win = random.randint(1, 100) <= base_win

    kills = random.randint(k_rng[0], k_rng[1]) + random.randint(ld["bonus_k"][0], ld["bonus_k"][1])
    deaths = random.randint(d_rng[0], d_rng[1])
    exp_gain = random.randint(exp_rng[0], exp_rng[1])
    uang_gain = random.randint(uang_rng[0], uang_rng[1])

    sr_change = 0
    events = []

    # event random
    e = random.randint(1, 100)
    if e <= 10:
        events.append("🔥 MVP! kamu carry tim.")
        exp_gain += 18
        kills += 3
    elif e <= 18:
        events.append("💥 Killstreak!")
        sr_change += 4
        kills += 2
    elif e <= 24:
        events.append("🧯 Bad connection...")
        deaths += 2
        sr_change -= 3

    if win:
        sr_change += random.randint(sr_win_rng[0], sr_win_rng[1])
        c["win"] = int(c["win"]) + 1
        events.append(f"🏆 MENANG ({mode_name})!")
        if int(b.get("sr_boost", 0)) > 0:
            bonus = random.randint(5, 12)
            sr_change += bonus
            b["sr_boost"] = int(b["sr_boost"]) - 1
            events.append(f"🎯 Aim Drill: +{bonus} SR (sisa {b['sr_boost']}x)")
    else:
        sr_change -= random.randint(sr_loss_rng[0], sr_loss_rng[1])
        c["lose"] = int(c["lose"]) + 1
        events.append(f"💀 KALAH ({mode_name})!")
        if int(b.get("anti_loss", 0)) > 0 and random.randint(1, 100) <= 55:
            b["anti_loss"] = int(b["anti_loss"]) - 1
            c["lose"] = max(0, int(c["lose"]) - 1)
            c["win"] = int(c["win"]) + 1
            win = True
            sr_change = random.randint(6, 14)
            uang_gain = max(uang_gain, random.randint(20, 60))
            events.append(f"🛡 Last Stand aktif! Dibalik jadi menang kecil (sisa {b['anti_loss']}x)")

    c["sr"] = max(0, int(c["sr"]) + sr_change)
    c["exp"] = int(c["exp"]) + exp_gain
    c["kills"] = int(c["kills"]) + kills
    c["deaths"] = int(c["deaths"]) + deaths
    c["matches"] = int(c["matches"]) + 1
    c["last_match"] = now_ts
    u["uang"] = int(u["uang"]) + uang_gain

    rank = _rank_from_sr(int(c["sr"]))
    lvl2 = _lvl_from_exp(int(c["exp"]))
    _save_db(db)

    ev = "\n".join([f"- {x}" for x in ([perk_note] if perk_note else []) + events if x])

    await message.reply(f"""
<blockquote><b>🔫 COD MATCH</b>
{message.from_user.mention}

<b>Mode:</b> <code>{mode_name}</code>
<b>Loadout:</b> <code>{ld['name']}</code>
<b>Hasil:</b> {"✅ MENANG" if win else "❌ KALAH"}

<b>SR:</b> <code>{sr_change:+d}</code> → <code>{c['sr']}</code> (<b>{rank}</b>)
<b>K/D:</b> <code>+{kills}</code>/<code>+{deaths}</code>
<b>EXP +</b> <code>{exp_gain}</code> → <code>Lv {lvl2}</code>
<b>Uang +</b> <code>{uang_gain}</code>

<b>Event:</b>
{ev}

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("codshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in COD_SHOP]
    await message.reply(
        "<blockquote><b>🛒 COD SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.codbuy id</code>\nContoh: <code>.codbuy 1</code></blockquote>"
    )

@PY.UBOT("codbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.codbuy id</code>\nContoh: <code>.codbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in COD_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.codshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_cod(u)
    c = u["cod"]
    b = c["buff"]

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
<b>Harga:</b> <code>{final_price}</code>
<b>Saldo:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("codtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        c = (data or {}).get("cod")
        if not c:
            continue
        sr = int(c.get("sr", 0))
        if sr > 0:
            ranking.append((int(uid_str), sr))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP COD</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, sr) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{sr}</code> SR ({_rank_from_sr(sr)})")

    await message.reply("<blockquote><b>🏆 TOP COD</b>\n\n" + "\n".join(lines) + "</blockquote>")
