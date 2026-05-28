import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "bloodstrike"
__HELP__ = """
<blockquote><b>Game Blood Strike (Mini)</b>

- <code>.bsstart</code> → buat akun
- <code>.bsprofil</code> → profil
- <code>.bsdaily</code> → bonus harian (1x/hari)

<b>Match</b>
- <code>.bsmatch</code> → match default (BR)
- <code>.bsmatch br</code> → battle royale
- <code>.bsmatch arena</code> → arena/tdm

<b>Loadout</b>
- <code>.bsloadout</code> → lihat loadout
- <code>.bsloadout assault</code> / <code>smg</code> / <code>sniper</code> → pilih

<b>Shop</b>
- <code>.bsshop</code> → toko perk
- <code>.bsbuy id</code> → beli perk

<b>Leaderboard</b>
- <code>.bstop</code> → top BP</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

MATCH_CD = 170

BS_SHOP = [
    {"id": 1, "name": "💉 Stim Pack (+win chance 2 match)", "price": 240, "type": "win_boost", "value": 2},
    {"id": 2, "name": "🛡 Second Life (batalin kalah 1x)", "price": 360, "type": "anti_loss", "value": 1},
    {"id": 3, "name": "🎯 Recoil Drill (+BP bonus 2x menang)", "price": 320, "type": "bp_boost", "value": 2},
    {"id": 4, "name": "🎫 Voucher Diskon 20% (1x beli)", "price": 200, "type": "voucher", "value": 0.20},
]

LOADOUTS = {
    "assault": {"name": "Assault", "bonus_win": 2, "bonus_k": (1, 3)},
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
        db["users"][uid] = {"uang": 0, "bloodstrike": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("bloodstrike", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 140)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _tier_from_bp(bp: int) -> str:
    if bp < 100: return "Rookie"
    if bp < 220: return "Bronze"
    if bp < 360: return "Silver"
    if bp < 520: return "Gold"
    if bp < 700: return "Platinum"
    if bp < 900: return "Diamond"
    return "Master"

def _ensure_bs(u):
    if u.get("bloodstrike") is None:
        u["bloodstrike"] = {
            "exp": 0,
            "bp": 0,
            "win": 0,
            "lose": 0,
            "matches": 0,
            "kills": 0,
            "deaths": 0,
            "loadout": "assault",
            "last_match": 0,
            "last_daily": None,
            "buff": {"win_boost": 0, "anti_loss": 0, "bp_boost": 0, "voucher": 0.0},
        }
    else:
        b = u["bloodstrike"]
        b.setdefault("loadout", "assault")
        b.setdefault("buff", {"win_boost": 0, "anti_loss": 0, "bp_boost": 0, "voucher": 0.0})
        b["buff"].setdefault("win_boost", 0)
        b["buff"].setdefault("anti_loss", 0)
        b["buff"].setdefault("bp_boost", 0)
        b["buff"].setdefault("voucher", 0.0)

def _mode_stats(mode: str):
    # (name, win_bonus, bp_win_rng, bp_loss_rng, exp_rng, uang_rng, k_rng, d_rng)
    mode = (mode or "br").lower()
    if mode in ["arena", "tdm", "deathmatch"]:
        return ("Arena", +3, (10, 22), (8, 18), (18, 50), (18, 70), (6, 22), (5, 20))
    return ("Battle Royale", 0, (14, 28), (10, 22), (20, 55), (25, 90), (2, 14), (0, 8))

@PY.UBOT("bsstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bs(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ BLOOD STRIKE GAME AKTIF</b>
{message.from_user.mention}

Pilih loadout: <code>.bsloadout</code>
Main: <code>.bsmatch br</code> / <code>.bsmatch arena</code></blockquote>
""")

@PY.UBOT("bsprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bs(u)
    s = u["bloodstrike"]
    lvl = _lvl_from_exp(int(s["exp"]))
    tier = _tier_from_bp(int(s["bp"]))
    ld = LOADOUTS.get(s.get("loadout", "assault"), LOADOUTS["assault"])
    b = s.get("buff", {})

    kd = (s["kills"] / s["deaths"]) if int(s["deaths"]) > 0 else float(s["kills"])
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🩸 PROFIL BLOOD STRIKE</b>
{message.from_user.mention}

<b>Tier:</b> <code>{tier}</code> | <b>BP:</b> <code>{s['bp']}</code>
<b>Level:</b> <code>{lvl}</code> | <b>EXP:</b> <code>{s['exp']}</code>
<b>Win:</b> <code>{s['win']}</code> | <b>Lose:</b> <code>{s['lose']}</code> | <b>Match:</b> <code>{s['matches']}</code>

<b>Kills:</b> <code>{s['kills']}</code> | <b>Deaths:</b> <code>{s['deaths']}</code> | <b>K/D:</b> <code>{kd:.2f}</code>
<b>Loadout:</b> <code>{ld['name']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Stim Pack: <code>{int(b.get('win_boost',0))}x</code>
- Second Life: <code>{int(b.get('anti_loss',0))}x</code>
- Recoil Drill: <code>{int(b.get('bp_boost',0))}x</code></blockquote>
""")

@PY.UBOT("bsdaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bs(u)
    s = u["bloodstrike"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if s.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Blood Strike sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(90, 180)
    bonus_exp = random.randint(30, 70)
    bonus_bp = random.randint(5, 15)

    u["uang"] = int(u["uang"]) + bonus_uang
    s["exp"] = int(s["exp"]) + bonus_exp
    s["bp"] = int(s["bp"]) + bonus_bp
    s["last_daily"] = today

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 BLOOD STRIKE DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>
<b>BP +</b> <code>{bonus_bp}</code>

BP: <code>{s['bp']}</code> | Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("bsloadout")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bs(u)
    s = u["bloodstrike"]

    if len(args) == 1:
        cur = s.get("loadout", "assault")
        lines = []
        for k, v in LOADOUTS.items():
            tag = "✅" if k == cur else "•"
            lines.append(f"{tag} <code>{k}</code> — {v['name']}")
        _save_db(db)
        return await message.reply("<blockquote><b>🎒 LOADOUT</b>\n\n" + "\n".join(lines) +
                                   "\n\nPilih: <code>.bsloadout assault</code> / <code>smg</code> / <code>sniper</code></blockquote>")

    pick = args[1].strip().lower()
    if pick not in LOADOUTS:
        _save_db(db)
        return await message.reply("<blockquote>Loadout tidak ada. Pilih: <code>assault</code>/<code>smg</code>/<code>sniper</code></blockquote>")

    s["loadout"] = pick
    _save_db(db)
    await message.reply(f"<blockquote>✅ Loadout sekarang: <b>{LOADOUTS[pick]['name']}</b></blockquote>")

@PY.UBOT("bsmatch")
async def _(client, message):
    mode_arg = (message.text or "").split(maxsplit=1)
    mode = mode_arg[1].strip().lower() if len(mode_arg) > 1 else "br"
    mode_name, win_bonus, bp_win_rng, bp_loss_rng, exp_rng, uang_rng, k_rng, d_rng = _mode_stats(mode)

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bs(u)
    s = u["bloodstrike"]
    b = s["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(s.get("last_match", 0))
    if now_ts - last < MATCH_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown match. Coba lagi <b>{_fmt_cd(MATCH_CD - (now_ts-last))}</b>.</blockquote>")

    ld = LOADOUTS.get(s.get("loadout", "assault"), LOADOUTS["assault"])
    lvl = _lvl_from_exp(int(s["exp"]))

    base_win = min(90, 45 + lvl * 2) + win_bonus + int(ld["bonus_win"])

    perk_note = ""
    if int(b.get("win_boost", 0)) > 0:
        base_win = min(95, base_win + 10)
        b["win_boost"] = int(b["win_boost"]) - 1
        perk_note = f"💉 Stim Pack aktif (+10% win) (sisa {b['win_boost']}x)"

    win = random.randint(1, 100) <= base_win

    kills = random.randint(k_rng[0], k_rng[1]) + random.randint(ld["bonus_k"][0], ld["bonus_k"][1])
    deaths = random.randint(d_rng[0], d_rng[1])
    exp_gain = random.randint(exp_rng[0], exp_rng[1])
    uang_gain = random.randint(uang_rng[0], uang_rng[1])

    bp_change = 0
    events = []

    e = random.randint(1, 100)
    if e <= 10:
        events.append("🩸 BLOOD RUSH! kill kamu meledak.")
        exp_gain += 16
        kills += 4
    elif e <= 18:
        events.append("💣 Grenade multi-kill!")
        bp_change += 4
        kills += 2
    elif e <= 24:
        events.append("📶 Lag parah...")
        deaths += 2
        bp_change -= 3

    if win:
        bp_change += random.randint(bp_win_rng[0], bp_win_rng[1])
        s["win"] = int(s["win"]) + 1
        events.append(f"🏆 MENANG ({mode_name})!")
        if int(b.get("bp_boost", 0)) > 0:
            bonus = random.randint(5, 12)
            bp_change += bonus
            b["bp_boost"] = int(b["bp_boost"]) - 1
            events.append(f"🎯 Recoil Drill: +{bonus} BP (sisa {b['bp_boost']}x)")
    else:
        bp_change -= random.randint(bp_loss_rng[0], bp_loss_rng[1])
        s["lose"] = int(s["lose"]) + 1
        events.append(f"💀 KALAH ({mode_name})!")
        if int(b.get("anti_loss", 0)) > 0 and random.randint(1, 100) <= 55:
            b["anti_loss"] = int(b["anti_loss"]) - 1
            s["lose"] = max(0, int(s["lose"]) - 1)
            s["win"] = int(s["win"]) + 1
            win = True
            bp_change = random.randint(6, 14)
            uang_gain = max(uang_gain, random.randint(20, 60))
            events.append(f"🛡 Second Life aktif! Dibalik jadi menang kecil (sisa {b['anti_loss']}x)")

    s["bp"] = max(0, int(s["bp"]) + bp_change)
    s["exp"] = int(s["exp"]) + exp_gain
    s["kills"] = int(s["kills"]) + kills
    s["deaths"] = int(s["deaths"]) + deaths
    s["matches"] = int(s["matches"]) + 1
    s["last_match"] = now_ts
    u["uang"] = int(u["uang"]) + uang_gain

    tier = _tier_from_bp(int(s["bp"]))
    lvl2 = _lvl_from_exp(int(s["exp"]))
    _save_db(db)

    ev = "\n".join([f"- {x}" for x in ([perk_note] if perk_note else []) + events if x])

    await message.reply(f"""
<blockquote><b>🩸 BLOOD STRIKE MATCH</b>
{message.from_user.mention}

<b>Mode:</b> <code>{mode_name}</code>
<b>Loadout:</b> <code>{ld['name']}</code>
<b>Hasil:</b> {"✅ MENANG" if win else "❌ KALAH"}

<b>BP:</b> <code>{bp_change:+d}</code> → <code>{s['bp']}</code> (<b>{tier}</b>)
<b>K/D:</b> <code>+{kills}</code>/<code>+{deaths}</code>
<b>EXP +</b> <code>{exp_gain}</code> → <code>Lv {lvl2}</code>
<b>Uang +</b> <code>{uang_gain}</code>

<b>Event:</b>
{ev}

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("bsshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in BS_SHOP]
    await message.reply(
        "<blockquote><b>🛒 BLOOD STRIKE SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.bsbuy id</code>\nContoh: <code>.bsbuy 1</code></blockquote>"
    )

@PY.UBOT("bsbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.bsbuy id</code>\nContoh: <code>.bsbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in BS_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.bsshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_bs(u)
    s = u["bloodstrike"]
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
<b>Harga:</b> <code>{final_price}</code>
<b>Saldo:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("bstop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        s = (data or {}).get("bloodstrike")
        if not s:
            continue
        bp = int(s.get("bp", 0))
        if bp > 0:
            ranking.append((int(uid_str), bp))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP BLOOD STRIKE</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, bp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{bp}</code> BP ({_tier_from_bp(bp)})")

    await message.reply("<blockquote><b>🏆 TOP BLOOD STRIKE</b>\n\n" + "\n".join(lines) + "</blockquote>")
