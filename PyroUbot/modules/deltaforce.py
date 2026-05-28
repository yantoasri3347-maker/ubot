import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "deltaforce"
__HELP__ = """
<blockquote><b>Game Delta Force (Mini Tactical Ops)</b>

- <code>.dfstart</code> → buat akun
- <code>.dfprofil</code> → profil
- <code>.dfdaily</code> → bonus harian (1x/hari)

<b>Operasi</b>
- <code>.dfops</code> → operasi default (raid)
- <code>.dfops raid</code> → raid / extraction
- <code>.dfops defense</code> → defend / escort

<b>Loadout</b>
- <code>.dfloadout</code> → lihat loadout
- <code>.dfloadout ar</code> / <code>smg</code> / <code>sniper</code> / <code>lmg</code> → pilih

<b>Shop</b>
- <code>.dfshop</code> → toko perk
- <code>.dfbuy id</code> → beli perk

<b>Leaderboard</b>
- <code>.dftop</code> → top DR</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

OPS_CD = 190  # cooldown operasi (detik)

DF_SHOP = [
    {"id": 1, "name": "🧠 Intel Brief (+win chance 2 ops)", "price": 260, "type": "win_boost", "value": 2},
    {"id": 2, "name": "🛡 Armor Plate (batalin kalah 1x)", "price": 380, "type": "anti_loss", "value": 1},
    {"id": 3, "name": "🎯 Recoil Training (+DR bonus 2x menang)", "price": 340, "type": "dr_boost", "value": 2},
    {"id": 4, "name": "🎫 Voucher Diskon 20% (1x beli)", "price": 220, "type": "voucher", "value": 0.20},
]

LOADOUTS = {
    "ar": {"name": "AR (All-rounder)", "bonus_win": 2, "bonus_k": (1, 3)},
    "smg": {"name": "SMG (Close combat)", "bonus_win": 3, "bonus_k": (2, 5)},
    "sniper": {"name": "Sniper (Long range)", "bonus_win": 1, "bonus_k": (0, 7)},
    "lmg": {"name": "LMG (Suppressor)", "bonus_win": 2, "bonus_k": (1, 4)},
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
        db["users"][uid] = {"uang": 0, "deltaforce": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("deltaforce", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 150)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank_from_dr(dr: int) -> str:
    if dr < 100: return "Recruit"
    if dr < 230: return "Operative"
    if dr < 380: return "Elite"
    if dr < 560: return "Veteran"
    if dr < 760: return "SpecOps"
    if dr < 980: return "TaskForce"
    return "Delta Legend"

def _ensure_df(u):
    if u.get("deltaforce") is None:
        u["deltaforce"] = {
            "exp": 0,
            "dr": 0,
            "win": 0,
            "lose": 0,
            "ops": 0,
            "kills": 0,
            "deaths": 0,
            "loadout": "ar",
            "last_ops": 0,
            "last_daily": None,
            "buff": {"win_boost": 0, "anti_loss": 0, "dr_boost": 0, "voucher": 0.0},
            "loot": {"intel": 0, "medkit": 0, "ammo": 0},
        }
    else:
        d = u["deltaforce"]
        d.setdefault("loadout", "ar")
        d.setdefault("last_ops", 0)
        d.setdefault("last_daily", None)
        d.setdefault("buff", {"win_boost": 0, "anti_loss": 0, "dr_boost": 0, "voucher": 0.0})
        d["buff"].setdefault("win_boost", 0)
        d["buff"].setdefault("anti_loss", 0)
        d["buff"].setdefault("dr_boost", 0)
        d["buff"].setdefault("voucher", 0.0)
        d.setdefault("loot", {"intel": 0, "medkit": 0, "ammo": 0})
        d["loot"].setdefault("intel", 0)
        d["loot"].setdefault("medkit", 0)
        d["loot"].setdefault("ammo", 0)

def _ops_stats(mode: str):
    # (name, win_bonus, dr_win_rng, dr_loss_rng, exp_rng, uang_rng, k_rng, d_rng)
    mode = (mode or "raid").lower()
    if mode in ["def", "defense", "escort"]:
        return ("Defense Ops", +2, (10, 22), (8, 18), (18, 52), (22, 85), (3, 14), (2, 14))
    return ("Raid / Extraction", 0, (14, 28), (10, 24), (20, 60), (28, 110), (4, 18), (2, 16))

def _roll_loot():
    # loot kecil untuk flavor
    loot = {"intel": 0, "medkit": 0, "ammo": 0}
    r = random.randint(1, 100)
    if r <= 35:
        loot["ammo"] = 1
    elif r <= 60:
        loot["medkit"] = 1
    elif r <= 78:
        loot["intel"] = 1
    elif r <= 90:
        loot["ammo"] = 2
    else:
        loot["intel"] = 2
    return loot

@PY.UBOT("dfstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_df(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ DELTA FORCE GAME AKTIF</b>
{message.from_user.mention}

Main operasi: <code>.dfops raid</code> / <code>.dfops defense</code>
Loadout: <code>.dfloadout</code></blockquote>
""")

@PY.UBOT("dfprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_df(u)
    d = u["deltaforce"]

    lvl = _lvl_from_exp(int(d["exp"]))
    rank = _rank_from_dr(int(d["dr"]))
    ld = LOADOUTS.get(d.get("loadout", "ar"), LOADOUTS["ar"])
    b = d.get("buff", {})
    loot = d.get("loot", {})
    kd = (d["kills"] / d["deaths"]) if int(d["deaths"]) > 0 else float(d["kills"])

    _save_db(db)

    await message.reply(f"""
<blockquote><b>🪖 PROFIL DELTA FORCE</b>
{message.from_user.mention}

<b>Rank:</b> <code>{rank}</code> | <b>DR:</b> <code>{d['dr']}</code>
<b>Level:</b> <code>{lvl}</code> | <b>EXP:</b> <code>{d['exp']}</code>
<b>Win:</b> <code>{d['win']}</code> | <b>Lose:</b> <code>{d['lose']}</code> | <b>Ops:</b> <code>{d['ops']}</code>

<b>Kills:</b> <code>{d['kills']}</code> | <b>Deaths:</b> <code>{d['deaths']}</code> | <b>K/D:</b> <code>{kd:.2f}</code>
<b>Loadout:</b> <code>{ld['name']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- 🧠 Intel Brief: <code>{int(b.get('win_boost',0))}x</code>
- 🛡 Armor Plate: <code>{int(b.get('anti_loss',0))}x</code>
- 🎯 Recoil Training: <code>{int(b.get('dr_boost',0))}x</code>

<b>Loot:</b>
- 📄 Intel: <code>{int(loot.get('intel',0))}</code>
- 🩹 Medkit: <code>{int(loot.get('medkit',0))}</code>
- 🔫 Ammo: <code>{int(loot.get('ammo',0))}</code></blockquote>
""")

@PY.UBOT("dfdaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_df(u)
    d = u["deltaforce"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if d.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Delta Force sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(90, 180)
    bonus_exp = random.randint(30, 75)
    bonus_dr = random.randint(5, 16)

    u["uang"] = int(u["uang"]) + bonus_uang
    d["exp"] = int(d["exp"]) + bonus_exp
    d["dr"] = int(d["dr"]) + bonus_dr
    d["last_daily"] = today

    # small loot chance
    if random.randint(1, 100) <= 25:
        lt = _roll_loot()
        for k, v in lt.items():
            d["loot"][k] = int(d["loot"].get(k, 0)) + int(v)

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 DELTA FORCE DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>
<b>DR +</b> <code>{bonus_dr}</code>

DR: <code>{d['dr']}</code> | Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("dfloadout")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_df(u)
    d = u["deltaforce"]

    if len(args) == 1:
        cur = d.get("loadout", "ar")
        lines = []
        for k, v in LOADOUTS.items():
            tag = "✅" if k == cur else "•"
            lines.append(f"{tag} <code>{k}</code> — {v['name']}")
        _save_db(db)
        return await message.reply("<blockquote><b>🎒 LOADOUT</b>\n\n" + "\n".join(lines) +
                                   "\n\nPilih: <code>.dfloadout ar</code> / <code>smg</code> / <code>sniper</code> / <code>lmg</code></blockquote>")

    pick = args[1].strip().lower()
    if pick not in LOADOUTS:
        _save_db(db)
        return await message.reply("<blockquote>Loadout tidak ada. Pilih: <code>ar</code>/<code>smg</code>/<code>sniper</code>/<code>lmg</code></blockquote>")

    d["loadout"] = pick
    _save_db(db)
    await message.reply(f"<blockquote>✅ Loadout sekarang: <b>{LOADOUTS[pick]['name']}</b></blockquote>")

@PY.UBOT("dfops")
async def _(client, message):
    mode_arg = (message.text or "").split(maxsplit=1)
    mode = mode_arg[1].strip().lower() if len(mode_arg) > 1 else "raid"
    mode_name, win_bonus, dr_win_rng, dr_loss_rng, exp_rng, uang_rng, k_rng, d_rng = _ops_stats(mode)

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_df(u)
    d = u["deltaforce"]
    b = d["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(d.get("last_ops", 0))
    if now_ts - last < OPS_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown ops. Coba lagi <b>{_fmt_cd(OPS_CD - (now_ts-last))}</b>.</blockquote>")

    ld = LOADOUTS.get(d.get("loadout", "ar"), LOADOUTS["ar"])
    lvl = _lvl_from_exp(int(d["exp"]))

    base_win = min(88, 46 + lvl * 2) + win_bonus + int(ld["bonus_win"])

    perk_note = ""
    if int(b.get("win_boost", 0)) > 0:
        base_win = min(93, base_win + 10)
        b["win_boost"] = int(b["win_boost"]) - 1
        perk_note = f"🧠 Intel Brief aktif (+10% win) (sisa {b['win_boost']}x)"

    win = random.randint(1, 100) <= base_win

    kills = random.randint(k_rng[0], k_rng[1]) + random.randint(ld["bonus_k"][0], ld["bonus_k"][1])
    deaths = random.randint(d_rng[0], d_rng[1])
    exp_gain = random.randint(exp_rng[0], exp_rng[1])
    uang_gain = random.randint(uang_rng[0], uang_rng[1])

    dr_change = 0
    events = []

    # random events
    e = random.randint(1, 100)
    if e <= 9:
        events.append("📡 UAV intel: kamu nemu jalur aman.")
        dr_change += 4
    elif e <= 16:
        events.append("💥 Breach sukses! kamu entry first.")
        kills += 3
        exp_gain += 12
    elif e <= 22:
        events.append("⚠️ Ambush! tim kamu kena flank.")
        deaths += 2
        dr_change -= 3

    loot_gain = {"intel": 0, "medkit": 0, "ammo": 0}
    # loot chance lebih tinggi kalau menang
    if random.randint(1, 100) <= (65 if win else 35):
        loot_gain = _roll_loot()

    if win:
        dr_change += random.randint(dr_win_rng[0], dr_win_rng[1])
        d["win"] = int(d["win"]) + 1
        events.append(f"✅ OPS BERHASIL ({mode_name})")
        if int(b.get("dr_boost", 0)) > 0:
            bonus = random.randint(5, 12)
            dr_change += bonus
            b["dr_boost"] = int(b["dr_boost"]) - 1
            events.append(f"🎯 Recoil Training: +{bonus} DR (sisa {b['dr_boost']}x)")
    else:
        dr_change -= random.randint(dr_loss_rng[0], dr_loss_rng[1])
        d["lose"] = int(d["lose"]) + 1
        events.append(f"❌ OPS GAGAL ({mode_name})")
        if int(b.get("anti_loss", 0)) > 0 and random.randint(1, 100) <= 55:
            b["anti_loss"] = int(b["anti_loss"]) - 1
            d["lose"] = max(0, int(d["lose"]) - 1)
            d["win"] = int(d["win"]) + 1
            win = True
            dr_change = random.randint(6, 14)
            uang_gain = max(uang_gain, random.randint(18, 55))
            events.append(f"🛡 Armor Plate aktif! Diselamatkan (sisa {b['anti_loss']}x)")

    d["dr"] = max(0, int(d["dr"]) + dr_change)
    d["exp"] = int(d["exp"]) + exp_gain
    d["kills"] = int(d["kills"]) + kills
    d["deaths"] = int(d["deaths"]) + deaths
    d["ops"] = int(d["ops"]) + 1
    d["last_ops"] = now_ts
    u["uang"] = int(u["uang"]) + uang_gain

    # add loot
    for k, v in loot_gain.items():
        d["loot"][k] = int(d["loot"].get(k, 0)) + int(v)

    rank = _rank_from_dr(int(d["dr"]))
    lvl2 = _lvl_from_exp(int(d["exp"]))

    _save_db(db)

    ev = "\n".join([f"- {x}" for x in ([perk_note] if perk_note else []) + events if x])
    loot_txt = ", ".join([f"{k}:{v}" for k, v in loot_gain.items() if v]) or "—"

    await message.reply(f"""
<blockquote><b>🪖 DELTA FORCE OPS</b>
{message.from_user.mention}

<b>Mode:</b> <code>{mode_name}</code>
<b>Loadout:</b> <code>{ld['name']}</code>
<b>Hasil:</b> {"✅ BERHASIL" if win else "❌ GAGAL"}

<b>DR:</b> <code>{dr_change:+d}</code> → <code>{d['dr']}</code> (<b>{rank}</b>)
<b>K/D:</b> <code>+{kills}</code>/<code>+{deaths}</code>
<b>EXP +</b> <code>{exp_gain}</code> → <code>Lv {lvl2}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Loot:</b> <code>{loot_txt}</code>

<b>Event:</b>
{ev}

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("dfshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in DF_SHOP]
    await message.reply(
        "<blockquote><b>🛒 DELTA SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.dfbuy id</code>\nContoh: <code>.dfbuy 2</code></blockquote>"
    )

@PY.UBOT("dfbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.dfbuy id</code>\nContoh: <code>.dfbuy 1</code></blockquote>")
    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in DF_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.dfshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_df(u)
    d = u["deltaforce"]
    b = d["buff"]

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

@PY.UBOT("dftop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        d = (data or {}).get("deltaforce")
        if not d:
            continue
        dr = int(d.get("dr", 0))
        if dr > 0:
            ranking.append((int(uid_str), dr))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP DELTA FORCE</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, dr) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{dr}</code> DR ({_rank_from_dr(dr)})")

    await message.reply("<blockquote><b>🏆 TOP DELTA FORCE</b>\n\n" + "\n".join(lines) + "</blockquote>")
