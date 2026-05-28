import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "roberty"
__HELP__ = """
<blockquote><b>Game Roberty (Heist Simulator)</b>

- <code>.rbstart</code> → aktifkan game
- <code>.rb</code> → status
- <code>.rbplan</code> → lihat/pilih rencana
- <code>.rbplan pick</code> / <code>store</code> / <code>bank</code> → set rencana
- <code>.rbgo</code> → jalankan aksi (cooldown)
- <code>.rbhide</code> → turunkan heat (cooldown)
- <code>.rbshop</code> → shop alat
- <code>.rbbuy id qty</code> → beli
- <code>.rbbail</code> → keluar penjara
- <code>.rbtop</code> → leaderboard total hasil</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

GO_CD = 200
HIDE_CD = 160
JAIL_TIME = 210

SHOP = [
    {"id": 1, "name": "🎭 Mask (+win chance 2x)", "price": 240, "key": "mask", "value": 2},
    {"id": 2, "name": "🧤 Gloves (kurangi heat + bonus loot 2x)", "price": 280, "key": "gloves", "value": 2},
    {"id": 3, "name": "📡 Jammer (batalin jail 1x)", "price": 420, "key": "jammer", "value": 1},
    {"id": 4, "name": "💳 Bail Pass (diskon bail 35% 1x)", "price": 200, "key": "bailpass", "value": 1},
]

PLANS = {
    "pick":  {"name": "Pickpocket", "win": 60, "loot": (40, 120), "heat": (6, 16), "loss": (20, 80)},
    "store": {"name": "Store Heist", "win": 52, "loot": (90, 220), "heat": (10, 24), "loss": (40, 120)},
    "bank":  {"name": "Bank Job",    "win": 45, "loot": (180, 520), "heat": (18, 40), "loss": (80, 210)},
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
        db["users"][uid] = {"uang": 0, "roberty": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("roberty", None)
    return u

def _ts():
    return int(datetime.now(TZ).timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _lvl(exp: int) -> int:
    return 1 + (exp // 140)

def _ensure_rb(u):
    if u.get("roberty") is None:
        u["roberty"] = {
            "exp": 0,
            "heat": 0,
            "plan": "pick",
            "wins": 0,
            "fails": 0,
            "total": 0,
            "last_go": 0,
            "last_hide": 0,
            "jail_until": 0,
            "items": {"mask": 0, "gloves": 0, "jammer": 0, "bailpass": 0},
        }
    else:
        r = u["roberty"]
        r.setdefault("exp", 0)
        r.setdefault("heat", 0)
        r.setdefault("plan", "pick")
        r.setdefault("wins", 0)
        r.setdefault("fails", 0)
        r.setdefault("total", 0)
        r.setdefault("last_go", 0)
        r.setdefault("last_hide", 0)
        r.setdefault("jail_until", 0)
        r.setdefault("items", {"mask": 0, "gloves": 0, "jammer": 0, "bailpass": 0})
        for k in ["mask", "gloves", "jammer", "bailpass"]:
            r["items"].setdefault(k, 0)

def _bail_cost(r):
    # heat mempengaruhi bail
    return min(650, 200 + int(r["heat"]) * 4 + int(r["fails"]) * 6)

@PY.UBOT("rbstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ ROBERTY GAME AKTIF</b>
{message.from_user.mention}

Pilih rencana: <code>.rbplan</code>
Mulai aksi: <code>.rbgo</code></blockquote>
""")

@PY.UBOT("rb")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    r = u["roberty"]
    now = _ts()

    jail_left = max(0, int(r["jail_until"]) - now)
    go_cd = max(0, int(r["last_go"]) + GO_CD - now)
    hide_cd = max(0, int(r["last_hide"]) + HIDE_CD - now)

    plan = PLANS.get(r["plan"], PLANS["pick"])
    it = r["items"]

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🕶 ROBERTY — STATUS</b>
{message.from_user.mention}

<b>Level:</b> <code>{_lvl(r['exp'])}</code> | <b>EXP:</b> <code>{r['exp']}</code>
<b>Plan:</b> <code>{plan['name']}</code>
<b>Heat:</b> <code>{r['heat']}</code> 🔥
<b>Win/Lose:</b> <code>{r['wins']}</code>/<code>{r['fails']}</code>
<b>Total hasil:</b> <code>{r['total']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Cooldown:</b>
- Go: <code>{_fmt_cd(go_cd) if go_cd else "ready ✅"}</code>
- Hide: <code>{_fmt_cd(hide_cd) if hide_cd else "ready ✅"}</code>
- Jail: <code>{_fmt_cd(jail_left) if jail_left else "bebas ✅"}</code>

<b>Tools:</b>
- 🎭 Mask: <code>{it.get('mask',0)}</code>
- 🧤 Gloves: <code>{it.get('gloves',0)}</code>
- 📡 Jammer: <code>{it.get('jammer',0)}</code>
- 💳 Bail Pass: <code>{it.get('bailpass',0)}</code></blockquote>
""")

@PY.UBOT("rbplan")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    r = u["roberty"]

    if len(args) == 1:
        lines = []
        for k, p in PLANS.items():
            tag = "✅" if r["plan"] == k else "•"
            lines.append(
                f"{tag} <code>{k}</code> — <b>{p['name']}</b> | win ~{p['win']}% | loot {p['loot'][0]}-{p['loot'][1]}"
            )
        _save_db(db)
        return await message.reply(
            "<blockquote><b>📋 PILIH RENCANA</b>\n\n" + "\n".join(lines) +
            "\n\nSet: <code>.rbplan pick</code> / <code>store</code> / <code>bank</code></blockquote>"
        )

    pick = args[1].strip().lower()
    if pick not in PLANS:
        _save_db(db)
        return await message.reply("<blockquote>Plan tidak ada. Pilih: <code>pick</code>/<code>store</code>/<code>bank</code></blockquote>")

    r["plan"] = pick
    _save_db(db)
    await message.reply(f"<blockquote>✅ Plan sekarang: <b>{PLANS[pick]['name']}</b></blockquote>")

@PY.UBOT("rbhide")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    r = u["roberty"]
    now = _ts()

    if int(r["jail_until"]) > now:
        _save_db(db)
        return await message.reply("<blockquote>🚫 Kamu lagi di penjara, nggak bisa hide.</blockquote>")

    cd = int(r["last_hide"]) + HIDE_CD - now
    if cd > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Hide cooldown: <b>{_fmt_cd(cd)}</b></blockquote>")

    reduce = random.randint(10, 24)
    # gloves bantu lebih efektif
    if int(r["items"].get("gloves", 0)) > 0 and random.randint(1, 100) <= 60:
        extra = random.randint(6, 12)
        reduce += extra
        r["items"]["gloves"] = int(r["items"]["gloves"]) - 1
        note = f"🧤 Gloves membantu (-{extra} heat ekstra)."
    else:
        note = "😶‍🌫️ Kamu berhasil ngilang dari radar."

    r["heat"] = max(0, int(r["heat"]) - reduce)
    r["last_hide"] = now
    _save_db(db)

    await message.reply(f"<blockquote><b>🫥 HIDE BERHASIL</b>\n{message.from_user.mention}\n\n<b>Heat -</b> <code>{reduce}</code>\n{note}\nHeat sekarang: <code>{r['heat']}</code></blockquote>")

@PY.UBOT("rbshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in SHOP]
    await message.reply(
        "<blockquote><b>🛒 ROBERTY SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.rbbuy id qty</code> (qty opsional)</blockquote>"
    )

@PY.UBOT("rbbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.rbbuy id qty</code>\nContoh: <code>.rbbuy 1 2</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    it = next((x for x in SHOP if x["id"] == item_id), None)
    if not it:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.rbshop</code></blockquote>")

    total = int(it["price"]) * qty
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    r = u["roberty"]

    if int(u["uang"]) < total:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - total
    r["items"][it["key"]] = int(r["items"].get(it["key"], 0)) + (int(it["value"]) * qty)

    _save_db(db)
    await message.reply(f"<blockquote>✅ Beli <b>{it['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("rbbail")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    r = u["roberty"]
    now = _ts()

    if int(r["jail_until"]) <= now:
        _save_db(db)
        return await message.reply("<blockquote>Kamu tidak di penjara.</blockquote>")

    cost = _bail_cost(r)
    if int(r["items"].get("bailpass", 0)) > 0:
        cost = int(cost * 0.65)
        r["items"]["bailpass"] = int(r["items"]["bailpass"]) - 1

    if int(u["uang"]) < cost:
        left = int(r["jail_until"]) - now
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nBiaya bail: <code>{cost}</code>\nSaldo: <code>{u['uang']}</code>\nSisa penjara: <code>{_fmt_cd(left)}</code></blockquote>")

    u["uang"] = int(u["uang"]) - cost
    r["jail_until"] = 0
    r["heat"] = max(0, int(r["heat"]) - random.randint(8, 18))

    _save_db(db)
    await message.reply(f"<blockquote>✅ Kamu bebas!\nBiaya: <code>{cost}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("rbgo")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_rb(u)
    r = u["roberty"]
    now = _ts()

    if int(r["jail_until"]) > now:
        left = int(r["jail_until"]) - now
        _save_db(db)
        return await message.reply(f"<blockquote>🚫 Kamu lagi di penjara.\nSisa: <b>{_fmt_cd(left)}</b>\nBail: <code>.rbbail</code></blockquote>")

    cd = int(r["last_go"]) + GO_CD - now
    if cd > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Go cooldown: <b>{_fmt_cd(cd)}</b></blockquote>")

    plan = PLANS.get(r["plan"], PLANS["pick"])
    base = int(plan["win"])

    # heat bikin makin susah
    base -= min(20, int(r["heat"]) // 7)

    # mask buff
    mask_note = ""
    if int(r["items"].get("mask", 0)) > 0:
        base = min(92, base + 10)
        r["items"]["mask"] = int(r["items"]["mask"]) - 1
        mask_note = f"🎭 Mask aktif (+10%) (sisa {r['items']['mask']})"

    base = max(10, min(92, base))
    win = random.randint(1, 100) <= base

    loot = random.randint(plan["loot"][0], plan["loot"][1])
    heat_add = random.randint(plan["heat"][0], plan["heat"][1])
    exp_gain = random.randint(18, 55)

    # gloves bonus loot + reduce heat chance
    gloves_note = ""
    if int(r["items"].get("gloves", 0)) > 0 and random.randint(1, 100) <= 55:
        bonus = int(loot * 0.20)
        loot += bonus
        heat_add = max(1, heat_add - random.randint(4, 10))
        r["items"]["gloves"] = int(r["items"]["gloves"]) - 1
        gloves_note = f"🧤 Gloves aktif (+{bonus} loot & heat lebih kecil) (sisa {r['items']['gloves']})"

    r["last_go"] = now

    if win:
        u["uang"] = int(u["uang"]) + loot
        r["exp"] = int(r["exp"]) + exp_gain
        r["heat"] = int(r["heat"]) + heat_add
        r["wins"] = int(r["wins"]) + 1
        r["total"] = int(r["total"]) + loot
        result = f"✅ Berhasil! Dapat <code>+{loot}</code> uang."
    else:
        loss = random.randint(plan["loss"][0], plan["loss"][1])
        u["uang"] = max(0, int(u["uang"]) - loss)
        r["fails"] = int(r["fails"]) + 1
        r["heat"] = int(r["heat"]) + heat_add + random.randint(4, 12)

        # chance jail (heat tinggi = lebih sering)
        jail_chance = 45 + min(30, int(r["heat"]) // 10)
        if int(r["items"].get("jammer", 0)) > 0 and random.randint(1, 100) <= 50:
            r["items"]["jammer"] = int(r["items"]["jammer"]) - 1
            jail = False
            jail_note = f"📡 Jammer menyelamatkan kamu dari penjara! (sisa {r['items']['jammer']})"
        else:
            jail = random.randint(1, 100) <= jail_chance
            jail_note = ""

        if jail:
            r["jail_until"] = now + JAIL_TIME
            jail_note = f"🚔 Kamu ketangkep! Penjara <b>{_fmt_cd(JAIL_TIME)}</b>. Bail: <code>.rbbail</code>"

        result = f"❌ Gagal! Kehilangan <code>-{loss}</code> uang.\n{jail_note}".strip()

    lvl = _lvl(r["exp"])
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🕶 ROBERTY GO</b>
{message.from_user.mention}

<b>Plan:</b> <code>{plan['name']}</code>
<b>Chance:</b> <code>{base}%</code>
{mask_note if mask_note else ""}
{gloves_note if gloves_note else ""}

<b>Hasil:</b> {result}

<b>Heat:</b> <code>{r['heat']}</code>
<b>Level:</b> <code>{lvl}</code>
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("rbtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        r = (data or {}).get("roberty")
        if not r:
            continue
        total = int(r.get("total", 0))
        if total > 0:
            rank.append((int(uid_str), total))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP ROBERTY</b>\nBelum ada yang bermain.</blockquote>")

    lines = []
    for i, (uid, total) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{total}</code> uang")

    await message.reply("<blockquote><b>🏆 TOP ROBERTY</b>\n\n" + "\n".join(lines) + "</blockquote>")
