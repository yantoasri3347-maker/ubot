import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "pou"
__HELP__ = """
<blockquote><b>Game Pou (Mini)</b>

- <code>.poustart</code> → buat Pou
- <code>.pou</code> / <code>.poustatus</code> → cek status Pou
- <code>.poufeed</code> → kasih makan (pakai uang)
- <code>.pouplay</code> → main (dapat exp + uang)
- <code>.pousleep</code> → tidur (naik energi)
- <code>.pouclean</code> → mandi/bikin bersih (pakai uang)
- <code>.poudaily</code> → bonus harian (1x/hari)
- <code>.poushop</code> → toko item Pou
- <code>.poubuy id</code> → beli item (buff)
- <code>.poutop</code> → leaderboard level</blockquote>
"""

TZ = timezone("Asia/Jakarta")

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")  # nyatu sama uang/gacha/ojol/ff/ml/dll
os.makedirs(DATA_DIR, exist_ok=True)

# cooldown detik
PLAY_CD = 90
SLEEP_CD = 120
FEED_CD = 45
CLEAN_CD = 60

# ===== SHOP (buff) =====
# buff effect:
# - snack: feed lebih besar 1x (sekali pakai)
# - vitamin: exp bonus 2x untuk 3 aksi play
# - perfume: hygiene bonus besar 1x (sekali pakai)
POU_SHOP = [
    {"id": 1, "name": "🍪 Snack Pou (+Hunger besar 1x)", "price": 120, "type": "snack"},
    {"id": 2, "name": "💊 Vitamin (+EXP bonus 3x play)", "price": 220, "type": "vitamin", "value": 3},
    {"id": 3, "name": "🧴 Perfume (+Hygiene besar 1x)", "price": 140, "type": "perfume"},
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
        db["users"][uid] = {"uang": 0, "pou": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("pou", None)
    return u

def _lvl_from_exp(exp: int) -> int:
    return 1 + (exp // 100)

def _clamp(v: int, a: int = 0, b: int = 100) -> int:
    return max(a, min(b, int(v)))

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _ensure_pou(u):
    if u.get("pou") is None:
        u["pou"] = {
            "exp": 0,
            "hunger": 80,   # 0-100
            "fun": 70,
            "energy": 70,
            "hygiene": 70,
            "last_play": 0,
            "last_sleep": 0,
            "last_feed": 0,
            "last_clean": 0,
            "last_daily": None,   # YYYY-MM-DD
            "buff": {
                "snack": 0,       # 1 = siap dipakai
                "vitamin": 0,     # sisa play bonus
                "perfume": 0,     # 1 = siap dipakai
            },
        }
    else:
        u["pou"].setdefault("buff", {"snack": 0, "vitamin": 0, "perfume": 0})
        u["pou"]["buff"].setdefault("snack", 0)
        u["pou"]["buff"].setdefault("vitamin", 0)
        u["pou"]["buff"].setdefault("perfume", 0)

def _tick_decay(p):
    """
    Biar realistis: setiap aksi, stat turun sedikit.
    (nggak pakai real-time, supaya simpel)
    """
    p["hunger"] = _clamp(p["hunger"] - random.randint(2, 6))
    p["fun"] = _clamp(p["fun"] - random.randint(1, 5))
    p["energy"] = _clamp(p["energy"] - random.randint(1, 4))
    p["hygiene"] = _clamp(p["hygiene"] - random.randint(1, 5))

def _mood(p) -> str:
    # mood berdasarkan rata-rata 4 stat
    avg = (p["hunger"] + p["fun"] + p["energy"] + p["hygiene"]) / 4
    if avg >= 85: return "😁 Bahagia"
    if avg >= 65: return "🙂 Oke"
    if avg >= 45: return "😕 Rewel"
    if avg >= 25: return "😫 Lelah"
    return "💀 Kritikal"

def _bar(x: int) -> str:
    # bar 10 kotak
    x = _clamp(x, 0, 100)
    filled = x // 10
    return "█" * filled + "░" * (10 - filled)

@PY.UBOT("poustart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ POU AKTIF</b>
{message.from_user.mention}

Cek status: <code>.pou</code>
Kasih makan: <code>.poufeed</code>
Main: <code>.pouplay</code></blockquote>
""")

@PY.UBOT("pou")
@PY.UBOT("poustatus")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    lvl = _lvl_from_exp(int(p["exp"]))
    mood = _mood(p)

    b = p.get("buff", {})
    snack = "aktif ✅" if int(b.get("snack", 0)) > 0 else "off"
    perfume = "aktif ✅" if int(b.get("perfume", 0)) > 0 else "off"
    vitamin = int(b.get("vitamin", 0))

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🐣 POU STATUS</b>
{message.from_user.mention}

<b>Level:</b> <code>{lvl}</code> | <b>EXP:</b> <code>{p['exp']}</code>
<b>Mood:</b> {mood}
<b>Uang:</b> <code>{u['uang']}</code>

<b>Hunger:</b> <code>{p['hunger']}</code> {_bar(p['hunger'])}
<b>Fun:</b> <code>{p['fun']}</code> {_bar(p['fun'])}
<b>Energy:</b> <code>{p['energy']}</code> {_bar(p['energy'])}
<b>Hygiene:</b> <code>{p['hygiene']}</code> {_bar(p['hygiene'])}

<b>Buff:</b>
- Snack: <code>{snack}</code>
- Perfume: <code>{perfume}</code>
- Vitamin play bonus: <code>{vitamin}x</code></blockquote>
""")

@PY.UBOT("poudaily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    if p.get("last_daily") == today:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Daily Pou sudah diambil hari ini. Besok lagi ya.</blockquote>")

    bonus_uang = random.randint(70, 160)
    bonus_exp = random.randint(20, 60)

    u["uang"] = int(u["uang"]) + bonus_uang
    p["exp"] = int(p["exp"]) + bonus_exp
    p["hunger"] = _clamp(p["hunger"] + random.randint(5, 15))
    p["fun"] = _clamp(p["fun"] + random.randint(5, 15))
    p["last_daily"] = today

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎁 POU DAILY</b>
{message.from_user.mention}

<b>Uang +</b> <code>{bonus_uang}</code>
<b>EXP +</b> <code>{bonus_exp}</code>
<b>Bonus:</b> Hunger & Fun naik sedikit

Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("pouplay")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(p.get("last_play", 0))
    if now_ts - last < PLAY_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Pou masih capek main. Coba lagi <b>{_fmt_cd(PLAY_CD - (now_ts-last))}</b>.</blockquote>")

    _tick_decay(p)

    exp_gain = random.randint(18, 40)
    uang_gain = random.randint(10, 30)
    fun_gain = random.randint(12, 28)
    energy_cost = random.randint(6, 14)

    note = "✅ Main biasa."
    # Vitamin bonus
    if int(p["buff"].get("vitamin", 0)) > 0:
        bonus = random.randint(10, 22)
        exp_gain += bonus
        p["buff"]["vitamin"] = int(p["buff"]["vitamin"]) - 1
        note = f"💊 Vitamin aktif! Bonus EXP +{bonus} (sisa {p['buff']['vitamin']}x)"

    # event random
    r = random.randint(1, 100)
    if r <= 10:
        uang_gain += 20
        note += "\n🎁 Dapat hadiah kecil dari mini-game!"
    elif r <= 18:
        fun_gain += 10
        note += "\n🤣 Pou ketawa ngakak, Fun naik besar!"

    p["exp"] = int(p["exp"]) + exp_gain
    u["uang"] = int(u["uang"]) + uang_gain
    p["fun"] = _clamp(p["fun"] + fun_gain)
    p["energy"] = _clamp(p["energy"] - energy_cost)
    p["last_play"] = now_ts

    lvl = _lvl_from_exp(int(p["exp"]))
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🎮 POU MAIN</b>
{message.from_user.mention}

<b>EXP +</b> <code>{exp_gain}</code>
<b>Uang +</b> <code>{uang_gain}</code>
<b>Fun +</b> <code>{fun_gain}</code>
<b>Energy -</b> <code>{energy_cost}</code>

{note}

<b>Level:</b> <code>{lvl}</code> | <b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("pousleep")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(p.get("last_sleep", 0))
    if now_ts - last < SLEEP_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Pou baru tidur. Coba lagi <b>{_fmt_cd(SLEEP_CD - (now_ts-last))}</b>.</blockquote>")

    _tick_decay(p)

    energy_gain = random.randint(20, 45)
    hygiene_cost = random.randint(2, 7)
    fun_cost = random.randint(1, 6)

    p["energy"] = _clamp(p["energy"] + energy_gain)
    p["hygiene"] = _clamp(p["hygiene"] - hygiene_cost)
    p["fun"] = _clamp(p["fun"] - fun_cost)
    p["last_sleep"] = now_ts

    _save_db(db)
    await message.reply(f"""
<blockquote><b>😴 POU TIDUR</b>
{message.from_user.mention}

<b>Energy +</b> <code>{energy_gain}</code>
<b>Hygiene -</b> <code>{hygiene_cost}</code>
<b>Fun -</b> <code>{fun_cost}</code>

Sekarang cek: <code>.pou</code></blockquote>
""")

@PY.UBOT("poufeed")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(p.get("last_feed", 0))
    if now_ts - last < FEED_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Tunggu dulu. Kasih makan lagi <b>{_fmt_cd(FEED_CD - (now_ts-last))}</b>.</blockquote>")

    # biaya makan
    cost = random.randint(15, 35)
    if int(u["uang"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kamu kurang buat beli makanan.\nButuh: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    _tick_decay(p)

    hunger_gain = random.randint(18, 35)
    note = "🍚 Pou makan kenyang."

    # snack buff (sekali pakai)
    if int(p["buff"].get("snack", 0)) > 0:
        hunger_gain += random.randint(15, 30)
        p["buff"]["snack"] = 0
        note = "🍪 Snack dipakai! Hunger naik besar (1x)."

    u["uang"] = int(u["uang"]) - cost
    p["hunger"] = _clamp(p["hunger"] + hunger_gain)
    p["last_feed"] = now_ts

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🍽 POU MAKAN</b>
{message.from_user.mention}

<b>Biaya:</b> <code>-{cost}</code>
<b>Hunger +</b> <code>{hunger_gain}</code>

{note}
Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("pouclean")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    now_ts = int(datetime.now(TZ).timestamp())
    last = int(p.get("last_clean", 0))
    if now_ts - last < CLEAN_CD:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Pou baru mandi. Coba lagi <b>{_fmt_cd(CLEAN_CD - (now_ts-last))}</b>.</blockquote>")

    cost = random.randint(12, 28)
    if int(u["uang"]) < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang buat sabun/shampoo.\nButuh: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    _tick_decay(p)

    hygiene_gain = random.randint(20, 40)
    note = "🚿 Pou jadi bersih."

    # perfume buff (sekali pakai)
    if int(p["buff"].get("perfume", 0)) > 0:
        hygiene_gain += random.randint(15, 30)
        p["buff"]["perfume"] = 0
        note = "🧴 Perfume dipakai! Hygiene naik besar (1x)."

    u["uang"] = int(u["uang"]) - cost
    p["hygiene"] = _clamp(p["hygiene"] + hygiene_gain)
    p["last_clean"] = now_ts

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🚿 POU MANDI</b>
{message.from_user.mention}

<b>Biaya:</b> <code>-{cost}</code>
<b>Hygiene +</b> <code>{hygiene_gain}</code>

{note}
Saldo: <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("poushop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in POU_SHOP]
    await message.reply(
        "<blockquote><b>🛒 POU SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.poubuy id</code>\nContoh: <code>.poubuy 2</code></blockquote>"
    )

@PY.UBOT("poubuy")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>Format: <code>.poubuy id</code>\nContoh: <code>.poubuy 1</code></blockquote>")

    try:
        item_id = int(args[1].strip())
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    item = next((x for x in POU_SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ditemukan. Cek: <code>.poushop</code></blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_pou(u)
    p = u["pou"]

    price = int(item["price"])
    if int(u["uang"]) < price:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{price}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - price

    note = ""
    if item["type"] == "snack":
        p["buff"]["snack"] = 1
        note = "🍪 Snack siap dipakai saat <code>.poufeed</code> (sekali)."
    elif item["type"] == "vitamin":
        p["buff"]["vitamin"] = int(p["buff"].get("vitamin", 0)) + int(item.get("value", 3))
        note = f"💊 Vitamin aktif untuk <b>{item.get('value', 3)}</b> kali <code>.pouplay</code>."
    elif item["type"] == "perfume":
        p["buff"]["perfume"] = 1
        note = "🧴 Perfume siap dipakai saat <code>.pouclean</code> (sekali)."
    else:
        note = "✅ Item dibeli."

    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ BELI BERHASIL</b>
{message.from_user.mention}

<b>Item:</b> {item['name']}
<b>Harga:</b> <code>-{price}</code>
<b>Saldo:</b> <code>{u['uang']}</code>

{note}</blockquote>
""")

@PY.UBOT("poutop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    ranking = []
    for uid_str, data in users.items():
        p = (data or {}).get("pou")
        if not p:
            continue
        exp = int(p.get("exp", 0))
        lvl = _lvl_from_exp(exp)
        ranking.append((int(uid_str), lvl, exp))

    ranking.sort(key=lambda x: (x[1], x[2]), reverse=True)
    ranking = ranking[:10]

    if not ranking:
        return await message.reply("<blockquote><b>🏆 TOP POU</b>\nBelum ada yang punya Pou.</blockquote>")

    lines = []
    for i, (uid, lvl, exp) in enumerate(ranking, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>Lv {lvl}</code> (EXP {exp})")

    await message.reply("<blockquote><b>🏆 TOP POU</b>\n\n" + "\n".join(lines) + "</blockquote>")
