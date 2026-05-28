import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "stumbleguys"
__HELP__ = """
<blockquote><b>Game Stumble Guys</b>

- <code>.sgstart</code> → aktifkan
- <code>.sg</code> → status
- <code>.sgplay</code> → main (3 ronde)
- <code>.sgshop</code> → toko item
- <code>.sgbuy id qty</code> → beli item
- <code>.sgtop</code> → top trophy</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

SG_CD = 180

SHOP = [
    {"id": 1, "name": "⚡ Sprint Boost (next run +12% qualify)", "price": 180, "key": "sprint", "value": 1},
    {"id": 2, "name": "🛡 Shield (batalkan eliminate 1x)", "price": 320, "key": "shield", "value": 1},
    {"id": 3, "name": "🧲 Lucky Step (bonus trophy kalau menang)", "price": 260, "key": "lucky", "value": 1},
]

def _load_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return default

def _save_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)

def _load_db():
    return _load_json(DB_FILE, {"users": {}})

def _save_db(db):
    _save_json(DB_FILE, db)

def _get_user(db, user_id: int):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"uang": 0, "stumble": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("stumble", None)
    return u

def _ensure_sg(u):
    if u.get("stumble") is None:
        u["stumble"] = {
            "trophy": 0,
            "win": 0,
            "lose": 0,
            "last_play": 0,
            "items": {"sprint": 0, "shield": 0, "lucky": 0},
            "total_run": 0,
        }
    else:
        s = u["stumble"]
        s.setdefault("trophy", 0)
        s.setdefault("win", 0)
        s.setdefault("lose", 0)
        s.setdefault("last_play", 0)
        s.setdefault("total_run", 0)
        s.setdefault("items", {"sprint": 0, "shield": 0, "lucky": 0})
        for k in ["sprint", "shield", "lucky"]:
            s["items"].setdefault(k, 0)

def _ts():
    return int(datetime.now(TZ).timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank(trophy: int) -> str:
    if trophy < 50: return "Rookie"
    if trophy < 140: return "Runner"
    if trophy < 260: return "Challenger"
    if trophy < 420: return "Elite"
    if trophy < 650: return "Master"
    return "Stumble Legend"

def _qualify_chance(base: int, trophy: int) -> int:
    # sedikit scaling: trophy tinggi sedikit lebih stabil
    return max(10, min(95, base + min(10, trophy // 80)))

@PY.UBOT("sgstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sg(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ STUMBLE GUYS AKTIF</b>
{message.from_user.mention}

Main: <code>.sgplay</code>
Cek: <code>.sg</code></blockquote>
""")

@PY.UBOT("sg")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sg(u)
    s = u["stumble"]
    it = s["items"]
    now = _ts()
    cd = max(0, int(s["last_play"]) + SG_CD - now)

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🧩 STUMBLE STATUS</b>
{message.from_user.mention}

<b>Rank:</b> <code>{_rank(int(s['trophy']))}</code>
<b>Trophy:</b> <code>{s['trophy']}</code>
<b>Run:</b> <code>{s['total_run']}</code>
<b>Win/Lose:</b> <code>{s['win']}</code>/<code>{s['lose']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Cooldown:</b> <code>{_fmt_cd(cd) if cd else "ready ✅"}</code>

<b>Item:</b>
- ⚡ Sprint: <code>{it.get('sprint',0)}</code>
- 🛡 Shield: <code>{it.get('shield',0)}</code>
- 🧲 Lucky: <code>{it.get('lucky',0)}</code></blockquote>
""")

@PY.UBOT("sgplay")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sg(u)
    s = u["stumble"]
    it = s["items"]

    now = _ts()
    left = int(s["last_play"]) + SG_CD - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    trophy = int(s["trophy"])
    sprint_used = False
    shield_used = False
    lucky_used = False

    # ronde 1: Race (qualify 70% base)
    c1 = _qualify_chance(70, trophy)
    if int(it.get("sprint", 0)) > 0:
        c1 = min(95, c1 + 12)
        it["sprint"] -= 1
        sprint_used = True

    r1 = random.randint(1, 100) <= c1
    log = []
    log.append(f"R1 Race — chance {c1}% → {'✅ lolos' if r1 else '❌ jatuh'}")

    if not r1:
        # shield chance save
        if int(it.get("shield", 0)) > 0 and random.randint(1, 100) <= 60:
            it["shield"] -= 1
            shield_used = True
            log.append("🛡 Shield aktif! Kamu terselamatkan.")
            r1 = True

    if not r1:
        s["lose"] += 1
        s["total_run"] += 1
        s["last_play"] = now
        # hadiah hiburan kecil
        uang = random.randint(10, 30)
        u["uang"] += uang
        s["trophy"] = max(0, int(s["trophy"]) - random.randint(4, 9))
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>💥 STUMBLE RUN SELESAI</b>
{message.from_user.mention}

{chr(10).join(['- '+x for x in log])}

<b>Hasil:</b> ❌ Tersingkir di R1
<b>Uang hiburan:</b> <code>+{uang}</code>
<b>Trophy:</b> <code>{s['trophy']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

    # ronde 2: Obstacle (base 62%)
    c2 = _qualify_chance(62, trophy)
    r2 = random.randint(1, 100) <= c2
    log.append(f"R2 Obstacle — chance {c2}% → {'✅ lolos' if r2 else '❌ kelempar'}")

    if not r2:
        if int(it.get("shield", 0)) > 0 and random.randint(1, 100) <= 55:
            it["shield"] -= 1
            shield_used = True
            log.append("🛡 Shield aktif! Kamu tetap lolos.")
            r2 = True

    if not r2:
        s["lose"] += 1
        s["total_run"] += 1
        s["last_play"] = now
        uang = random.randint(18, 45)
        u["uang"] += uang
        s["trophy"] = max(0, int(s["trophy"]) - random.randint(3, 8))
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>💥 STUMBLE RUN SELESAI</b>
{message.from_user.mention}

{chr(10).join(['- '+x for x in log])}

<b>Hasil:</b> ❌ Tersingkir di R2
<b>Uang hiburan:</b> <code>+{uang}</code>
<b>Trophy:</b> <code>{s['trophy']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

    # ronde 3: Final (base 40% menang)
    c3 = _qualify_chance(40, trophy)
    if sprint_used:
        c3 = min(92, c3 + 4)  # efek sprint kecil di final
    win = random.randint(1, 100) <= c3
    log.append(f"R3 Final — chance {c3}% → {'🏆 MENANG' if win else '❌ kalah tipis'}")

    s["total_run"] += 1
    s["last_play"] = now

    if win:
        s["win"] += 1
        trophy_gain = random.randint(12, 28)
        uang_gain = random.randint(90, 220)

        if int(it.get("lucky", 0)) > 0:
            it["lucky"] -= 1
            lucky_used = True
            bonus_t = random.randint(8, 16)
            bonus_u = random.randint(50, 120)
            trophy_gain += bonus_t
            uang_gain += bonus_u
            log.append(f"🧲 Lucky Step aktif! +{bonus_t} trophy & +{bonus_u} uang.")

        s["trophy"] = int(s["trophy"]) + trophy_gain
        u["uang"] = int(u["uang"]) + uang_gain

        note_items = []
        if sprint_used: note_items.append("⚡ Sprint")
        if shield_used: note_items.append("🛡 Shield")
        if lucky_used: note_items.append("🧲 Lucky")
        note = ("Item terpakai: " + ", ".join(note_items)) if note_items else "—"

        _save_db(db)
        return await message.reply(f"""
<blockquote><b>🏆 STUMBLE CHAMPION!</b>
{message.from_user.mention}

{chr(10).join(['- '+x for x in log])}

<b>Hadiah:</b> <code>+{uang_gain}</code> uang
<b>Trophy +</b> <code>{trophy_gain}</code>
<b>{note}</b>

<b>Trophy:</b> <code>{s['trophy']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

    # kalah di final
    s["lose"] += 1
    trophy_loss = random.randint(1, 6)
    s["trophy"] = max(0, int(s["trophy"]) - trophy_loss)
    uang_gain = random.randint(35, 90)
    u["uang"] += uang_gain

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🥲 STUMBLE FINAL</b>
{message.from_user.mention}

{chr(10).join(['- '+x for x in log])}

<b>Hasil:</b> ❌ Kalah di final
<b>Uang:</b> <code>+{uang_gain}</code>
<b>Trophy -</b> <code>{trophy_loss}</code>

<b>Trophy:</b> <code>{s['trophy']}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("sgshop")
async def _(client, message):
    lines = [f"{x['id']}. {x['name']} — <code>{x['price']}</code> uang" for x in SHOP]
    await message.reply("<blockquote><b>🛒 STUMBLE SHOP</b>\n\n" + "\n".join(lines) +
                        "\n\nBeli: <code>.sgbuy id qty</code></blockquote>")

@PY.UBOT("sgbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.sgbuy id qty</code>\nContoh: <code>.sgbuy 1 2</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    item = next((x for x in SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.sgshop</code></blockquote>")

    total = int(item["price"]) * qty

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sg(u)
    s = u["stumble"]

    if int(u["uang"]) < total:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - total
    s["items"][item["key"]] = int(s["items"].get(item["key"], 0)) + (int(item["value"]) * qty)

    _save_db(db)
    await message.reply(f"<blockquote>✅ Beli <b>{item['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("sgtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        s = (data or {}).get("stumble")
        if not s:
            continue
        t = int(s.get("trophy", 0))
        if t > 0:
            rank.append((int(uid_str), t))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP STUMBLE</b>\nBelum ada trophy.</blockquote>")

    lines = []
    for i, (uid, t) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{t}</code> trophy ({_rank(t)})")

    await message.reply("<blockquote><b>🏆 TOP STUMBLE GUYS</b>\n\n" + "\n".join(lines) + "</blockquote>")
