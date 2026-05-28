import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "gacha"
__HELP__ = """
<blockquote><b>Bantuan untuk Gacha</b>
- <code>.daily</code> → klaim saldo harian
- <code>.gacha</code> / <code>.gacha 10</code> → roll
- <code>.cekgacha</code> → cek inventory
- <code>.jual 12</code> → jual item ID 12
- <code>.uang</code> → cek saldo
</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ===== CONFIG =====
ROLL_COST = 50
MAX_ROLL = 10

# Pity SSR: kalau 49x gak SSR, roll ke-50 pasti SSR
PITY_SSR_AT = 50

RARITY_WEIGHTS = [
    ("SSR", 2),   # 2%
    ("SR",  8),   # 8%
    ("R",   25),  # 25%
    ("N",   65),  # 65%
]

SELL_PRICE = {"SSR": 500, "SR": 150, "R": 40, "N": 10}

POOL = {
    "SSR": ["🔥 Phoenix Blade", "🌌 Star Crown", "⚡ Thunder Spear", "🦊 Kitsune Mask"],
    "SR":  ["🟣 Shadow Dagger", "🛡 Guardian Shield", "🎯 Hunter Bow", "🧪 Mystic Potion"],
    "R":   ["🔵 Iron Axe", "🪖 Steel Helm", "🧤 Warrior Gloves", "🥾 Swift Boots"],
    "N":   ["⚪ Bread", "🪵 Wood Stick", "🧱 Stone", "🧢 Cap", "🧴 Small Potion"],
}

EMOJI = {"SSR": "💎", "SR": "🟣", "R": "🔵", "N": "⚪"}

# ===== STORAGE =====
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
        db["users"][uid] = {
            "uang": 0,
            "pity_ssr_miss": 0,
            "inv": [],  # list of {id, item, rarity, ts}
            "last_daily": None,  # YYYY-MM-DD
            "next_item_id": 1,
        }
    return db["users"][uid]

def _roll_rarity():
    r = random.randint(1, 100)
    s = 0
    for name, w in RARITY_WEIGHTS:
        s += w
        if r <= s:
            return name
    return "N"

def _now_iso():
    return datetime.now(TZ).isoformat()

# =========================
# COMMAND: .uang
# =========================
@PY.UBOT("uang")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _save_db(db)

    await message.reply(f"""
<blockquote><b>💰 UANG</b>
{message.from_user.mention}

<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

# =========================
# COMMAND: .daily
# =========================
@PY.UBOT("daily")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)

    today = datetime.now(TZ).strftime("%Y-%m-%d")

    if u["last_daily"] == today:
        _save_db(db)
        return await message.reply("<blockquote><b>⏳ DAILY</b>\nKamu sudah klaim hari ini. Coba besok ya.</blockquote>")

    reward = random.randint(80, 150)
    u["uang"] += reward
    u["last_daily"] = today
    _save_db(db)

    await message.reply(f"""
<blockquote><b>🎁 DAILY CLAIM</b>
{message.from_user.mention}

<b>Uang +</b> <code>{reward}</code>
<b>Saldo sekarang</b> <code>{u['uang']}</code>

Ketik <code>.gacha</code> buat roll 🎰</blockquote>
""")

# =========================
# COMMAND: .gacha / .gacha 10
# =========================
@PY.UBOT("gacha")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)

    n = 1
    if len(args) > 1:
        try:
            n = int(args[1])
        except:
            n = 1

    if n < 1:
        n = 1
    if n > MAX_ROLL:
        n = MAX_ROLL

    db = _load_db()
    udata = _get_user(db, message.from_user.id)

    total_cost = ROLL_COST * n
    if udata["uang"] < total_cost:
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>❌ UANG KURANG</b>
<b>Saldo kamu:</b> <code>{udata['uang']}</code>
<b>Butuh:</b> <code>{total_cost}</code>

Tips: klaim <code>.daily</code></blockquote>
""")

    msg = await message.reply("⏳ sedang gacha...")

    # potong uang
    udata["uang"] -= total_cost

    results = []
    pity = int(udata.get("pity_ssr_miss", 0))

    for _i in range(n):
        pity += 1

        # pity SSR
        if pity >= PITY_SSR_AT:
            rarity = "SSR"
            pity = 0
        else:
            rarity = _roll_rarity()
            if rarity == "SSR":
                pity = 0

        item = random.choice(POOL.get(rarity, ["Unknown Item"]))
        item_id = int(udata["next_item_id"])
        udata["next_item_id"] = item_id + 1

        udata["inv"].append({
            "id": item_id,
            "item": item,
            "rarity": rarity,
            "ts": _now_iso(),
        })
        results.append((item_id, rarity, item))

    udata["pity_ssr_miss"] = pity
    _save_db(db)

    lines = []
    for item_id, rarity, item in results:
        lines.append(f"• <code>{item_id}</code> {EMOJI.get(rarity,'🎁')} <b>{rarity}</b> — {item}")

    await msg.edit(f"""
<blockquote><b>🎰 GACHA RESULT</b>
{message.from_user.mention}

<b>Roll:</b> <code>x{n}</code>
<b>Cost:</b> <code>{total_cost}</code>
<b>Sisa saldo:</b> <code>{udata['uang']}</code>
<b>Pity:</b> <code>{pity}/{PITY_SSR_AT-1}</code>

{chr(10).join(lines)}

<b>Cek gacha:</b> <code>.cekgacha</code>
<b>Jual item:</b> <code>.jual id</code></blockquote>
""")

# =========================
# COMMAND: .cekgacha
# =========================
@PY.UBOT("cekgacha")
async def _(client, message):
    db = _load_db()
    udata = _get_user(db, message.from_user.id)

    inv = list(reversed(udata["inv"]))  # terbaru dulu
    if not inv:
        _save_db(db)
        return await message.reply("""
<blockquote><b>🎒 CEK GACHA</b>
<i>kosong</i>

Roll dulu: <code>.gacha</code></blockquote>
""")

    show = inv[:30]
    lines = []
    for it in show:
        rarity = it["rarity"]
        lines.append(f"• <code>{it['id']}</code> {EMOJI.get(rarity,'🎁')} <b>{rarity}</b> — {it['item']}")

    _save_db(db)

    await message.reply(f"""
<blockquote><b>🎒 CEK GACHA</b>
<b>Total item:</b> <code>{len(udata['inv'])}</code>
(menampilkan 30 terbaru)

{chr(10).join(lines)}

<b>Jual item:</b> <code>.jual id</code>
Contoh: <code>.jual 12</code></blockquote>
""")

# =========================
# COMMAND: .jual <id>
# =========================
@PY.UBOT("jual")
async def _(client, message):
    args = (message.text or "").split(maxsplit=1)
    if len(args) < 2:
        return await message.reply("<blockquote>pakai: <code>.jual id</code>\ncontoh: <code>.jual 12</code></blockquote>")

    try:
        item_id = int(args[1])
    except:
        return await message.reply("<blockquote>ID harus angka.</blockquote>")

    db = _load_db()
    udata = _get_user(db, message.from_user.id)

    idx = None
    rarity = None
    for i, it in enumerate(udata["inv"]):
        if int(it.get("id", -1)) == item_id:
            idx = i
            rarity = it.get("rarity", "N")
            break

    if idx is None:
        _save_db(db)
        return await message.reply("<blockquote><b>❌</b> item tidak ditemukan.</blockquote>")

    # hapus item
    udata["inv"].pop(idx)

    harga = int(SELL_PRICE.get(rarity, 5))
    udata["uang"] += harga
    _save_db(db)

    await message.reply(f"""
<blockquote><b>✅ ITEM BERHASIL DIJUAL</b>

<b>ID:</b> <code>{item_id}</code>
<b>Rarity:</b> <code>{rarity}</code>
<b>Uang masuk:</b> <code>+{harga}</code>

<b>Saldo sekarang:</b> <code>{udata['uang']}</code></blockquote>
""")
