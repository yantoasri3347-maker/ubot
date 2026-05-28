import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "valorant"
__HELP__ = """
<blockquote><b>Game Valorant (Mini)</b>

<b>Start & Profil</b>
- <code>.valstart</code> → buat akun
- <code>.valprofil</code> → profil (rank/RR/agent/skin)
- <code>.valagent</code> → list agent
- <code>.valpick 3</code> → pilih agent id

<b>Match</b>
- <code>.valqueue</code> → main (default: comp)
- <code>.valqueue unrated</code> → unrated
- <code>.valqueue spike</code> → spike rush
- <code>.valqueue comp</code> → competitive

<b>Skin</b>
- <code>.valskins</code> → inventory skin
- <code>.valjual 2</code> → jual skin ID 2 jadi uang

<b>Daily & Shop</b>
- <code>.valdaily</code> → bonus harian (1x/hari)
- <code>.valshop</code> → toko buff
- <code>.valbuy id</code> → beli buff

<b>Leaderboard</b>
- <code>.valtop</code> → top RR</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

QUEUE_CD = 180

VAL_SHOP = [
    {"id": 1, "name": "🎧 Comms Boost (+win chance 2 match)", "price": 240, "type": "comms", "value": 2},
    {"id": 2, "name": "🛡 Anti-Throw (batalin kalah 1x)", "price": 360, "type": "antithrow", "value": 1},
    {"id": 3, "name": "🔥 Aim Routine (+RR bonus 2x menang)", "price": 320, "type": "aim", "value": 2},
    {"id": 4, "name": "🎫 Voucher Diskon 20% (1x beli)", "price": 200, "type": "voucher", "value": 0.20},
]

AGENTS = [
    {"id": 1, "name": "Jett", "role": "Duelist", "bonus": {"win": 3, "rr_win": 2}},
    {"id": 2, "name": "Reyna", "role": "Duelist", "bonus": {"win": 2, "exp": 6}},
    {"id": 3, "name": "Sage", "role": "Sentinel", "bonus": {"anti_loss": 2}},
    {"id": 4, "name": "Omen", "role": "Controller", "bonus": {"rr_win": 3}},
    {"id": 5, "name": "Sova", "role": "Initiator", "bonus": {"exp": 10}},
    {"id": 6, "name": "Killjoy", "role": "Sentinel", "bonus": {"win": 2, "anti_loss": 1}},
    {"id": 7, "name": "Brimstone", "role": "Controller", "bonus": {"rr_win": 2, "exp": 4}},
]

SKIN_POOL = [
    # rarity: common/rare/epic/legend
    {"name": "Classic | Black", "rarity": "common", "sell": (35, 55)},
    {"name": "Spectre | Neon", "rarity": "common", "sell": (40, 65)},
    {"name": "Vandal | Artisan", "rarity": "rare", "sell": (80, 130)},
    {"name": "Phantom | Pulse", "rarity": "rare", "sell": (90, 150)},
    {"name": "Operator | Glacier", "rarity": "epic", "sell": (170, 260)},
    {"name": "Knife | Ember", "rarity": "epic", "sell": (190, 300)},
    {"name": "Vandal | Dragon", "rarity": "legend", "sell": (320, 520)},
    {"name": "Knife | Celestial", "rarity": "legend", "sell": (350, 560)},
]

RARITY_CHANCE = [
    ("common", 72),
    ("rare", 20),
    ("epic", 7),
    ("legend", 1),
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
        db["users"][uid] = {"uang": 0, "valorant": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("valorant", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 140)

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank_from_rr(rr: int) -> str:
    if rr < 100: return "Iron"
    if rr < 200: return "Bronze"
    if rr < 350: return "Silver"
    if rr < 520: return "Gold"
    if rr < 700: return "Platinum"
    if rr < 880: return "Diamond"
    if rr < 1050: return "Ascendant"
    if rr < 1250: return "Immortal"
    return "Radiant"

def _ensure_val(u):
    if u.get("valorant") is None:
        u["valorant"] = {
            "exp": 0,
            "rr": 0,
            "win": 0,
            "lose": 0,
            "matches": 0,
            "last_queue": 0,
            "last_daily": None,
            "agent": 1,   # default Jett
            "skins": [],  # list of dict: {name, rarity, sell_min, sell_max, ts}
            "buff": {"comms": 0, "antithrow": 0, "aim": 0, "voucher": 0.0},
        }
    else:
        v = u["valorant"]
        v.setdefault("agent", 1)
        v.setdefault("skins", [])
        v.setdefault("buff", {"comms": 0, "antithrow": 0, "aim": 0, "voucher": 0.0})
        v["buff"].setdefault("comms", 0)
        v["buff"].setdefault("antithrow", 0)
        v["buff"].setdefault("aim", 0)
        v["buff"].setdefault("voucher", 0.0)

def _get_agent(agent_id: int):
    return next((a for a in AGENTS if a["id"] == agent_id), AGENTS[0])

def _roll_rarity() -> str:
    r = random.randint(1, 100)
    s = 0
    for name, chance in RARITY_CHANCE:
        s += chance
        if r <= s:
            return name
    return "common"

def _roll_skin():
    rarity = _roll_rarity()
    pool = [x for x in SKIN_POOL if x["rarity"] == rarity]
    pick = random.choice(pool) if pool else random.choice(SKIN_POOL)
    return pick

def _mode_stats(mode: str):
    # returns: (name, win_bonus, rr_win_range, rr_loss_range, exp_range, uang_range, skin_drop_chance)
    mode = (mode or "comp").lower()
    if mode in ["unrated", "ur"]:
        return ("Unrated", -2, (8, 16), (6, 14), (18, 45), (18, 55), 18)
    if mode in ["spike", "spikerush", "sr"]:
        return ("Spike Rush", +4, (6, 14), (5, 12), (15, 38), (15, 45), 14)
    return ("Competitive", 0, (14, 28), (10, 22), (20, 55), (25, 80), 22)

@PY.UBOT("valstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ VALORANT GAME AKTIF</b>
{message.from_user.mention}

Pilih agent: <code>.valagent</code> lalu <code>.valpick id</code>
Main: <code>.valqueue</code> / <code>.valprofil</code> / <code>.valskins</code></blockquote>
""")

@PY.UBOT("valagent")
async def _(client, message):
    lines = [f"{a['id']}. <b>{a['name']}</b> — {a['role']}" for a in AGENTS]
    await message.reply("<blockquote><b>🧩 LIST AGENT</b>\n\n" + "\n".join(lines) +
                        "\n\nPilih: <code>.valpick id</code></blockquote>")

@PY.UBOT("valpick")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.valpick id</code>\nContoh: <code>.valpick 3</code></blockquote>")
    try:
        agent_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID agent harus angka.</blockquote>")

    if not any(a["id"] == agent_id for a in AGENTS):
        return await message.reply("<blockquote>Agent tidak ada. Cek: <code>.valagent</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    u["valorant"]["agent"] = agent_id
    _save_db(db)

    a = _get_agent(agent_id)
    await message.reply(f"<blockquote>✅ Agent kamu sekarang: <b>{a['name']}</b> ({a['role']})</blockquote>")

@PY.UBOT("valprofil")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    v = u["valorant"]

    lvl = _lvl_from_exp(int(v["exp"]))
    rank = _rank_from_rr(int(v["rr"]))
    a = _get_agent(int(v.get("agent", 1)))
    b = v.get("buff", {})
    skin_count = len(v.get("skins", []))

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎯 PROFIL VALORANT</b>
{message.from_user.mention}

<b>Agent:</b> <code>{a['name']}</code> ({a['role']})
<b>Rank:</b> <code>{rank}</code> | <b>RR:</b> <code>{v['rr']}</code>
<b>Level:</b> <code>{lvl}</code> | <b>EXP:</b> <code>{v['exp']}</code>
<b>Win:</b> <code>{v['win']}</code> | <b>Lose:</b> <code>{v['lose']}</code> | <b>Match:</b> <code>{v['matches']}</code>
<b>Skin:</b> <code>{skin_count}</code> item
<b>Uang:</b> <code>{u['uang']}</code>

<b>Buff:</b>
- Comms: <code>{int(b.get('comms',0))}x</code>
- Anti-Throw: <code>{int(b.get('antithrow',0))}x</code>
- Aim: <code>{int(b.get('aim',0))}x</code></blockquote>
""")

@PY.UBOT("valskins")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    skins = u["valorant"].get("skins", [])

    if not skins:
        _save_db(db)
        return await message.reply("<blockquote>Inventory skin kosong. Main dulu: <code>.valqueue</code></blockquote>")

    lines = []
    for i, sk in enumerate(skins, start=1):
        lines.append(f"{i}. <b>{sk['name']}</b> — <code>{sk['rarity']}</code>")
    _save_db(db)

    await message.reply("<blockquote><b>🎨 INVENTORY SKIN</b>\n\n" +
                        "\n".join(lines) +
                        "\n\nJual: <code>.valjual nomor</code></blockquote>")

@PY.UBOT("valjual")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.valjual nomor</code>\nContoh: <code>.valjual 2</code></blockquote>")
    try:
        idx = int(args[1].strip())
    except:
        return await message.reply("<blockquote>Nomor harus angka.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    skins = u["valorant"].get("skins", [])

    if idx < 1 or idx > len(skins):
        _save_db(db)
        return await message.reply("<blockquote>Nomor skin tidak valid. Cek: <code>.valskins</code></blockquote>")

    sk = skins.pop(idx - 1)
    payout = random.randint(int(sk["sell_min"]), int(sk["sell_max"]))
    u["uang"] = int(u["uang"]) + payout
    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ SKIN TERJUAL</b>
{message.from_user.mention}

<b>Skin:</b> {sk['name']} (<code>{sk['rarity']}</code>)
<b>Uang +</b> <code>{payout}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("valdaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    v = u["valorant"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if v.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Valorant sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(90, 180)
    bonus_exp = random.randint(30, 70)
    bonus_rr = random.randint(5, 15)

    u["uang"] = int(u["uang"]) + bonus_uang
    v["exp"] = int(v["exp"]) + bonus_exp
    v["rr"] = int(v["rr"]) + bonus_rr
    v["last_daily"] = today

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 VALORANT DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>
<b>RR +</b> <code>{bonus_rr}</code>

RR: <code>{v['rr']}</code> | Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("valqueue")
async def _(client, message):
    mode_arg = (message.text or "").split(maxsplit=1)
    mode = mode_arg[1].strip().lower() if len(mode_arg) > 1 else "comp"
    mode_name, win_bonus, rr_win_rng, rr_loss_rng, exp_rng, uang_rng, drop_chance = _mode_stats(mode)

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    v = u["valorant"]
    b = v["buff"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(v.get("last_queue", 0))
    if now_ts - last < QUEUE_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown queue. Coba lagi <b>{_fmt_cd(QUEUE_CD - (now_ts-last))}</b>.</blockquote>")

    a = _get_agent(int(v.get("agent", 1)))
    agent_bonus = a.get("bonus", {})

    lvl = _lvl_from_exp(int(v["exp"]))
    base_win = min(75, 45 + lvl * 2) + win_bonus

    # agent win bonus
    base_win = min(88, base_win + int(agent_bonus.get("win", 0)))

    # comms boost
    comm_note = ""
    if int(b.get("comms", 0)) > 0:
        base_win = min(90, base_win + 10)
        b["comms"] = int(b["comms"]) - 1
        comm_note = f"🎧 Comms Boost (+10% win) (sisa {b['comms']}x)"

    win = random.randint(1, 100) <= base_win

    rr_change = 0
    uang_gain = random.randint(uang_rng[0], uang_rng[1])
    exp_gain = random.randint(exp_rng[0], exp_rng[1]) + int(agent_bonus.get("exp", 0))

    event_lines = []
    e = random.randint(1, 100)
    if e <= 10:
        event_lines.append("⭐ CLUTCH! kamu 1v3.")
        exp_gain += 15
    elif e <= 16:
        event_lines.append("💀 THROW teammate...")
        if win and random.randint(1, 100) <= 50:
            rr_change -= 8
            event_lines.append("📉 Walau menang, RR kepotong.")
    elif e <= 20:
        event_lines.append("🔥 ACE! kamu gas pol.")
        exp_gain += 25

    if win:
        rr_change += random.randint(rr_win_rng[0], rr_win_rng[1])
        rr_change += int(agent_bonus.get("rr_win", 0))
        v["win"] = int(v["win"]) + 1
        event_lines.append(f"🏆 MENANG ({mode_name})!")

        # aim routine bonus RR
        if int(b.get("aim", 0)) > 0:
            bonus = random.randint(5, 12)
            rr_change += bonus
            b["aim"] = int(b["aim"]) - 1
            event_lines.append(f"🔥 Aim Routine: +{bonus} RR (sisa {b['aim']}x)")
    else:
        rr_change -= random.randint(rr_loss_rng[0], rr_loss_rng[1])
        v["lose"] = int(v["lose"]) + 1
        event_lines.append(f"💀 KALAH ({mode_name})!")

        # agent anti loss
        anti = int(agent_bonus.get("anti_loss", 0))
        if anti > 0 and random.randint(1, 100) <= anti * 15:
            cut = random.randint(4, 10)
            rr_change += cut
            event_lines.append(f"🧱 {a['name']} bantu tahan RR: +{cut} (loss diperkecil)")

        # anti-throw item
        if int(b.get("antithrow", 0)) > 0 and random.randint(1, 100) <= 55:
            b["antithrow"] = int(b["antithrow"]) - 1
            v["lose"] = max(0, int(v["lose"]) - 1)
            v["win"] = int(v["win"]) + 1
            win = True
            rr_change = random.randint(6, 14)
            uang_gain = max(uang_gain, random.randint(20, 60))
            event_lines.append(f"🛡 Anti-Throw aktif! Dibalik jadi menang kecil (sisa {b['antithrow']}x)")

    # skin drop chance (lebih tinggi kalau menang)
    drop = False
    drop_roll = random.randint(1, 100)
    chance = drop_chance + (8 if win else 0)
    if drop_roll <= chance:
        sk = _roll_skin()
        v["skins"].append({
            "name": sk["name"],
            "rarity": sk["rarity"],
            "sell_min": sk["sell"][0],
            "sell_max": sk["sell"][1],
            "ts": datetime.now(TZ).isoformat(),
        })
        drop = True
        event_lines.append(f"🎁 DROP SKIN: <b>{sk['name']}</b> (<code>{sk['rarity']}</code>)")

    v["rr"] = max(0, int(v["rr"]) + rr_change)
    v["exp"] = int(v["exp"]) + exp_gain
    u["uang"] = int(u["uang"]) + uang_gain
    v["matches"] = int(v["matches"]) + 1
    v["last_queue"] = now_ts

    rank = _rank_from_rr(int(v["rr"]))
    lvl2 = _lvl_from_exp(int(v["exp"]))
    _save_db(db)

    ev = "\n".join([f"- {x}" for x in ([comm_note] if comm_note else []) + event_lines if x])

    await message.reply(f"""
<blockquote><b>🎮 VALORANT MATCH</b>
{message.from_user.mention}

<b>Mode:</b> <code>{mode_name}</code>
<b>Agent:</b> <code>{a['name']}</code>
<b>Hasil:</b> {"✅ MENANG" if win else "❌ KALAH"}

<b>RR:</b> <code>{rr_change:+d}</code> → <code>{v['rr']}</code> (<b>{rank}</b>)
<b>EXP +</b> <code>{exp_gain}</code> → <code>Lv {lvl2}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Skin Drop:</b> {"✅" if drop else "—"}

<b>Event:</b>
{ev}

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("valshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in VAL_SHOP]
    await message.reply(
        "<blockquote><b>🛒 VALORANT SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.valbuy id</code>\nContoh: <code>.valbuy 1</code></blockquote>"
    )

@PY.UBOT("valbuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.valbuy id</code>\nContoh: <code>.valbuy 2</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in VAL_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.valshop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_val(u)
    v = u["valorant"]
    b = v["buff"]

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

@PY.UBOT("valtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        v = (data or {}).get("valorant")
        if not v:
            continue
        rr = int(v.get("rr", 0))
        if rr > 0:
            ranking.append((int(uid_str), rr))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP VALORANT</b>\nBelum ada yang main.</blockquote>")

    lines = []
    for i, (uid, rr) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{rr}</code> RR ({_rank_from_rr(rr)})")

    await message.reply("<blockquote><b>🏆 TOP VALORANT</b>\n\n" + "\n".join(lines) + "</blockquote>")
