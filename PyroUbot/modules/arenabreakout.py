import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "arenabreakout"
__HELP__ = """
<blockquote><b>Game Arena Breakout</b>

- <code>.abstart</code> → aktifkan
- <code>.ab</code> → status
- <code>.abraid</code> → masuk raid (cooldown)
- <code>.abinsure</code> → aktifkan asuransi 1 raid
- <code>.abstash</code> → lihat stash
- <code>.absell id qty</code> → jual loot ke uang

<b>Shop</b>
- <code>.abshop</code> → toko
- <code>.abbuy id qty</code> → beli gear</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

AB_CD = 220  # cooldown raid

# item loot (drop di raid)
LOOT_TABLE = [
    {"id": 101, "name": "🔩 Scrap Metal", "price": 25, "rarity": 55},
    {"id": 102, "name": "🧰 Tool Kit", "price": 65, "rarity": 35},
    {"id": 103, "name": "💾 CPU Board", "price": 120, "rarity": 24},
    {"id": 104, "name": "📦 Supply Crate", "price": 180, "rarity": 18},
    {"id": 105, "name": "💎 Gold Watch", "price": 340, "rarity": 10},
    {"id": 106, "name": "🧪 Rare Injector", "price": 420, "rarity": 7},
    {"id": 107, "name": "📀 Encrypted Drive", "price": 520, "rarity": 5},
]

# shop gear (buff raid)
SHOP = [
    {"id": 1, "name": "🩹 Medkit (tambah survive chance)", "price": 160, "key": "medkit", "value": 1},
    {"id": 2, "name": "🦺 Armor (kurangi chance mati)", "price": 280, "key": "armor", "value": 1},
    {"id": 3, "name": "🔫 Ammo Pack (bonus loot)", "price": 220, "key": "ammo", "value": 1},
    {"id": 4, "name": "🎒 Bigger Bag (loot +1 item)", "price": 260, "key": "bag", "value": 1},
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
        db["users"][uid] = {"uang": 0, "ab": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("ab", None)
    return u

def _ensure_ab(u):
    if u.get("ab") is None:
        u["ab"] = {
            "rank": 0,          # exp-like
            "raid": 0,
            "survive": 0,
            "death": 0,
            "kills": 0,
            "down": 0,
            "last_raid": 0,
            "insure_next": False,
            "stash": [],        # list of {"id":, "name":, "price":, "qty":}
            "gear": {"medkit": 0, "armor": 0, "ammo": 0, "bag": 0},
            "total_money": 0,   # total uang dari raid
        }
    else:
        a = u["ab"]
        a.setdefault("rank", 0)
        a.setdefault("raid", 0)
        a.setdefault("survive", 0)
        a.setdefault("death", 0)
        a.setdefault("kills", 0)
        a.setdefault("down", 0)
        a.setdefault("last_raid", 0)
        a.setdefault("insure_next", False)
        a.setdefault("stash", [])
        a.setdefault("gear", {"medkit": 0, "armor": 0, "ammo": 0, "bag": 0})
        for k in ["medkit", "armor", "ammo", "bag"]:
            a["gear"].setdefault(k, 0)
        a.setdefault("total_money", 0)

def _ts():
    return int(datetime.now(TZ).timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _rank_name(rank: int) -> str:
    if rank < 120: return "Rookie"
    if rank < 260: return "Scout"
    if rank < 450: return "Operator"
    if rank < 700: return "Veteran"
    if rank < 1000: return "Elite"
    return "Legend"

def _pick_loot():
    # weighted by rarity
    total = sum(x["rarity"] for x in LOOT_TABLE)
    r = random.randint(1, total)
    cur = 0
    for it in LOOT_TABLE:
        cur += it["rarity"]
        if r <= cur:
            return dict(it)
    return dict(LOOT_TABLE[0])

def _add_stash(ab, item, qty=1):
    for s in ab["stash"]:
        if int(s["id"]) == int(item["id"]):
            s["qty"] = int(s.get("qty", 0)) + qty
            return
    ab["stash"].append({"id": item["id"], "name": item["name"], "price": item["price"], "qty": qty})

def _take_stash(ab, item_id: int, qty: int):
    for s in ab["stash"]:
        if int(s["id"]) == int(item_id):
            have = int(s.get("qty", 0))
            if have < qty:
                return False
            s["qty"] = have - qty
            return True
    return False

def _clean_stash(ab):
    ab["stash"] = [x for x in ab["stash"] if int(x.get("qty", 0)) > 0]

@PY.UBOT("abstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ ARENA BREAKOUT AKTIF</b>
{message.from_user.mention}

Mulai raid: <code>.abraid</code>
Status: <code>.ab</code></blockquote>
""")

@PY.UBOT("ab")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    ab = u["ab"]

    now = _ts()
    cd = max(0, int(ab["last_raid"]) + AB_CD - now)

    kd = (ab["kills"] / ab["down"]) if ab["down"] else float(ab["kills"])
    insure = "ON ✅" if ab.get("insure_next") else "OFF"

    _save_db(db)
    await message.reply(f"""
<blockquote><b>🎯 ARENA BREAKOUT — STATUS</b>
{message.from_user.mention}

<b>Rank:</b> <code>{_rank_name(int(ab['rank']))}</code> | <b>RP:</b> <code>{ab['rank']}</code>
<b>Raid:</b> <code>{ab['raid']}</code> | <b>Survive/Death:</b> <code>{ab['survive']}</code>/<code>{ab['death']}</code>
<b>K/D:</b> <code>{ab['kills']}</code>/<code>{ab['down']}</code> (KD <code>{kd:.2f}</code>)
<b>Total uang raid:</b> <code>{ab['total_money']}</code>
<b>Uang:</b> <code>{u['uang']}</code>

<b>Cooldown raid:</b> <code>{_fmt_cd(cd) if cd else "ready ✅"}</code>
<b>Insurance:</b> <code>{insure}</code>

<b>Gear:</b>
- 🩹 Medkit: <code>{ab['gear'].get('medkit',0)}</code>
- 🦺 Armor: <code>{ab['gear'].get('armor',0)}</code>
- 🔫 Ammo: <code>{ab['gear'].get('ammo',0)}</code>
- 🎒 Bag: <code>{ab['gear'].get('bag',0)}</code></blockquote>
""")

@PY.UBOT("abinsure")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    ab = u["ab"]

    cost = 140
    if u["uang"] < cost:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nInsurance: <code>{cost}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    if ab.get("insure_next"):
        _save_db(db)
        return await message.reply("<blockquote>✅ Insurance sudah ON untuk raid berikutnya.</blockquote>")

    u["uang"] -= cost
    ab["insure_next"] = True
    _save_db(db)
    await message.reply(f"<blockquote>✅ Insurance ON (raid berikutnya)\nBiaya: <code>{cost}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("abraid")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    ab = u["ab"]

    now = _ts()
    left = int(ab["last_raid"]) + AB_CD - now
    if left > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Raid cooldown: <b>{_fmt_cd(left)}</b></blockquote>")

    ab["last_raid"] = now
    ab["raid"] += 1

    # base chances
    survive_chance = 55
    death_chance = 20   # sisanya "extract with wound/partial"

    # gear effects
    if ab["gear"].get("medkit", 0) > 0:
        survive_chance += 8
    if ab["gear"].get("armor", 0) > 0:
        death_chance -= 6

    # rank effect: makin tinggi makin stabil
    survive_chance += min(8, int(ab["rank"]) // 180)
    death_chance -= min(6, int(ab["rank"]) // 250)

    survive_chance = max(20, min(80, survive_chance))
    death_chance = max(5, min(35, death_chance))

    # simulate combat
    kills = random.randint(0, 5) + (1 if random.randint(1, 100) <= 18 else 0)
    downs = random.randint(0, 4)
    ab["kills"] += kills
    ab["down"] += downs

    # loot count
    loot_count = 1
    if ab["gear"].get("bag", 0) > 0:
        loot_count += 1
    if ab["gear"].get("ammo", 0) > 0 and random.randint(1, 100) <= 55:
        loot_count += 1

    loot_items = []
    total_loot_value = 0
    for _ in range(loot_count):
        it = _pick_loot()
        qty = 1 if it["id"] >= 105 else random.randint(1, 2)
        loot_items.append((it, qty))
        total_loot_value += int(it["price"]) * qty

    # outcome roll
    roll = random.randint(1, 100)
    outcome = ""
    note = []

    # consume some gear per raid (chance)
    if ab["gear"].get("medkit", 0) > 0 and random.randint(1, 100) <= 35:
        ab["gear"]["medkit"] -= 1
        note.append("🩹 Medkit terpakai (-1)")
    if ab["gear"].get("armor", 0) > 0 and random.randint(1, 100) <= 22:
        ab["gear"]["armor"] -= 1
        note.append("🦺 Armor rusak (-1)")
    if ab["gear"].get("ammo", 0) > 0 and random.randint(1, 100) <= 40:
        ab["gear"]["ammo"] -= 1
        note.append("🔫 Ammo habis (-1)")
    if ab["gear"].get("bag", 0) > 0 and random.randint(1, 100) <= 18:
        ab["gear"]["bag"] -= 1
        note.append("🎒 Bag sobek (-1)")

    insured = bool(ab.get("insure_next"))
    ab["insure_next"] = False

    if roll <= death_chance:
        # death: lose most loot, maybe insurance returns some
        ab["death"] += 1
        lost = total_loot_value
        back_value = 0

        if insured:
            # return 40-65% value as "recovered"
            back_value = int(lost * random.uniform(0.40, 0.65))
            u["uang"] += back_value
            ab["total_money"] += back_value
            outcome = f"💀 Kamu mati di raid… tapi insurance balikin <code>+{back_value}</code> uang."
        else:
            # small pity money
            pity = random.randint(15, 55)
            u["uang"] += pity
            ab["total_money"] += pity
            outcome = f"💀 Kamu mati di raid… uang hiburan <code>+{pity}</code>."

        rp = random.randint(8, 22)
        ab["rank"] = max(0, int(ab["rank"]) - random.randint(4, 10))  # turun sedikit saat mati
        note.append(f"RP +{rp} (combat exp)")

    else:
        # survive/extract
        ab["survive"] += 1

        # add loot to stash (bukan langsung uang)
        for it, qty in loot_items:
            _add_stash(ab, it, qty)

        rp = random.randint(16, 34) + (kills * 2)
        ab["rank"] += rp
        outcome = "✅ Kamu berhasil extract! Loot masuk ke stash."
        note.append(f"RP +{rp}")

        # bonus uang kecil dari barter cepat
        quick = random.randint(20, 70)
        u["uang"] += quick
        ab["total_money"] += quick
        note.append(f"Quick cash +{quick}")

    _save_db(db)

    loot_text = "\n".join([f"- {it['name']} x<code>{qty}</code> (≈{it['price']*qty})" for it, qty in loot_items])
    note_text = "\n".join([f"- {x}" for x in note]) if note else "- —"

    await message.reply(f"""
<blockquote><b>🪖 ARENA BREAKOUT — RAID</b>
{message.from_user.mention}

<b>Combat:</b> kills <code>{kills}</code> | down <code>{downs}</code>
<b>Loot ditemukan:</b>
{loot_text}

<b>Hasil:</b> {outcome}

<b>Catatan:</b>
{note_text}

<b>Uang:</b> <code>{u['uang']}</code>
Cek stash: <code>.abstash</code></blockquote>
""")

@PY.UBOT("abstash")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    ab = u["ab"]

    _clean_stash(ab)
    if not ab["stash"]:
        _save_db(db)
        return await message.reply("<blockquote>📦 Stash kamu kosong.\nMain raid: <code>.abraid</code></blockquote>")

    lines = []
    for i, it in enumerate(ab["stash"], start=1):
        lines.append(f"{i}. <b>{it['name']}</b> — id <code>{it['id']}</code> | qty <code>{it['qty']}</code> | sell <code>{it['price']}</code>")

    _save_db(db)
    await message.reply("<blockquote><b>📦 STASH</b>\n\n" + "\n".join(lines) +
                        "\n\nJual: <code>.absell id qty</code></blockquote>")

@PY.UBOT("absell")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.absell id qty</code>\nContoh: <code>.absell 105 1</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    ab = u["ab"]

    # find item
    item = None
    for s in ab["stash"]:
        if int(s["id"]) == item_id:
            item = s
            break
    if not item:
        _save_db(db)
        return await message.reply("<blockquote>Item tidak ada di stash.</blockquote>")

    if int(item.get("qty", 0)) < qty:
        _save_db(db)
        return await message.reply("<blockquote>Qty kamu kurang.</blockquote>")

    gain = int(item["price"]) * qty
    ok = _take_stash(ab, item_id, qty)
    if not ok:
        _save_db(db)
        return await message.reply("<blockquote>Gagal jual (qty kurang).</blockquote>")

    _clean_stash(ab)
    u["uang"] += gain
    ab["total_money"] += gain

    _save_db(db)
    await message.reply(f"<blockquote>✅ Terjual <b>{item['name']}</b> x<code>{qty}</code>\nUang <code>+{gain}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("abshop")
async def _(client, message):
    lines = [f"{x['id']}. {x['name']} — <code>{x['price']}</code> uang" for x in SHOP]
    await message.reply("<blockquote><b>🛒 AB SHOP</b>\n\n" + "\n".join(lines) +
                        "\n\nBeli: <code>.abbuy id qty</code></blockquote>")

@PY.UBOT("abbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.abbuy id qty</code>\nContoh: <code>.abbuy 2 1</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    item = next((x for x in SHOP if x["id"] == item_id), None)
    if not item:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.abshop</code></blockquote>")

    total = int(item["price"]) * qty

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_ab(u)
    ab = u["ab"]

    if int(u["uang"]) < total:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] -= total
    ab["gear"][item["key"]] = int(ab["gear"].get(item["key"], 0)) + (int(item["value"]) * qty)

    _save_db(db)
    await message.reply(f"<blockquote>✅ Beli <b>{item['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("abtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        ab = (data or {}).get("ab")
        if not ab:
            continue
        total = int(ab.get("total_money", 0))
        if total > 0:
            rank.append((int(uid_str), total))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP ARENA BREAKOUT</b>\nBelum ada yang raid.</blockquote>")

    lines = []
    for i, (uid, total) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — <code>{total}</code> uang")

    await message.reply("<blockquote><b>🏆 TOP ARENA BREAKOUT</b>\n\n" + "\n".join(lines) + "</blockquote>")
