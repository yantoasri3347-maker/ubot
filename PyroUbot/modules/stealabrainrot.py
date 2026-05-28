import os
import json
import random
from datetime import datetime, timedelta
from pytz import timezone

from PyroUbot import *

__MODULE__ = "brainrot"
__HELP__ = """
<blockquote><b>Game Steal a Brainrot</b>

<b>Start & Status</b>
- <code>.sbrstart</code> → aktifkan game
- <code>.sbr</code> → status kamu (uang, streak, jail, item)

<b>Steal</b>
- <code>.steal @user</code> / reply → coba mencuri uang
- <code>.sbrbail</code> → bayar jaminan keluar penjara

<b>Shop</b>
- <code>.sbrshop</code> → lihat shop item
- <code>.sbrbuy id qty</code> → beli item

<b>Leaderboard</b>
- <code>.sbrtop</code> → top thief (berhasil & total dicuri)</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ==== SETTING GAME ====
STEAL_COOLDOWN = 150          # cooldown pencuri (detik)
VICTIM_PROTECT_CD = 120       # korban dilindungi dari steal berturut2 (detik)
JAIL_TIME = 180               # penjara kalau gagal (detik)
MIN_TARGET_UANG = 120         # minimal uang korban agar bisa dicuri
MIN_THIEF_UANG = 50           # minimal uang pelaku agar bisa aksi (biaya peluang)
STEAL_PERCENT_RANGE = (6, 18) # persen dari saldo target yg bisa dicuri
STEAL_MIN_MAX = (25, 220)     # batas nominal steal
FINE_RANGE = (25, 120)        # denda kalau gagal (uang pelaku berkurang)
MAX_STEAL_PER_HOUR = 12       # rate-limit biar ga spam

SHOP = [
    {"id": 1, "name": "🎭 Mask (naikin win chance 2x)", "price": 220, "key": "mask", "value": 2},
    {"id": 2, "name": "🛡 Shield (anti dicuri 1x)", "price": 260, "key": "shield", "value": 1},
    {"id": 3, "name": "🔒 Lock (proteksi target 1x steal)", "price": 200, "key": "lock", "value": 1},
    {"id": 4, "name": "💳 Bail Coupon (diskon bail 30% 1x)", "price": 180, "key": "bail_coupon", "value": 1},
]

# ======================

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

def _now():
    return datetime.now(TZ)

def _ts():
    return int(_now().timestamp())

def _fmt_cd(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m}m {s}s" if m else f"{s}s"

def _get_user(db, user_id: int):
    uid = str(user_id)
    if uid not in db["users"]:
        db["users"][uid] = {"uang": 0, "sbr": None}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("sbr", None)
    return u

def _ensure_sbr(u):
    if u.get("sbr") is None:
        u["sbr"] = {
            "steal_last": 0,
            "jail_until": 0,
            "victim_protect_until": 0,  # proteksi diri (korban)
            "wins": 0,
            "fails": 0,
            "streak": 0,
            "stolen_total": 0,
            "stolen_times": 0,
            "hour_window_ts": 0,
            "hour_count": 0,
            "items": {"mask": 0, "shield": 0, "lock": 0, "bail_coupon": 0},
        }
    else:
        s = u["sbr"]
        s.setdefault("steal_last", 0)
        s.setdefault("jail_until", 0)
        s.setdefault("victim_protect_until", 0)
        s.setdefault("wins", 0)
        s.setdefault("fails", 0)
        s.setdefault("streak", 0)
        s.setdefault("stolen_total", 0)
        s.setdefault("stolen_times", 0)
        s.setdefault("hour_window_ts", 0)
        s.setdefault("hour_count", 0)
        s.setdefault("items", {"mask": 0, "shield": 0, "lock": 0, "bail_coupon": 0})
        s["items"].setdefault("mask", 0)
        s["items"].setdefault("shield", 0)
        s["items"].setdefault("lock", 0)
        s["items"].setdefault("bail_coupon", 0)

def _shop_item(item_id: int):
    return next((x for x in SHOP if x["id"] == item_id), None)

async def _extract_target_user(client, message):
    # coba reply dulu
    if getattr(message, "reply_to_message", None) and getattr(message.reply_to_message, "from_user", None):
        return message.reply_to_message.from_user

    # coba parse username/id dari text
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2:
        return None
    raw = parts[1].strip()

    # handle @username / id
    try:
        return await client.get_users(raw)
    except:
        try:
            return await client.get_users(int(raw))
        except:
            return None

def _calc_bail_cost(u):
    # bail cost berdasarkan streak gagal + total
    s = u["sbr"]
    base = 180 + (int(s.get("fails", 0)) * 8)
    return min(520, base)

@PY.UBOT("sbrstart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sbr(u)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ STEAL A BRAINROT AKTIF</b>
{message.from_user.mention}

Cek status: <code>.sbr</code>
Curi: <code>.steal @user</code> (atau reply)
Shop: <code>.sbrshop</code></blockquote>
""")

@PY.UBOT("sbr")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sbr(u)
    s = u["sbr"]

    now = _ts()
    jail_left = max(0, int(s["jail_until"]) - now)
    steal_cd = max(0, int(s["steal_last"]) + STEAL_COOLDOWN - now)
    protect_left = max(0, int(s["victim_protect_until"]) - now)
    items = s["items"]

    _save_db(db)

    await message.reply(f"""
<blockquote><b>🧠 STEAL A BRAINROT — STATUS</b>
{message.from_user.mention}

<b>Uang:</b> <code>{u['uang']}</code>
<b>Win:</b> <code>{s['wins']}</code> | <b>Fail:</b> <code>{s['fails']}</code> | <b>Streak:</b> <code>{s['streak']}</code>
<b>Total dicuri:</b> <code>{s['stolen_total']}</code> | <b>Jumlah aksi sukses:</b> <code>{s['stolen_times']}</code>

<b>Cooldown steal:</b> <code>{_fmt_cd(steal_cd) if steal_cd else "ready ✅"}</code>
<b>Proteksi kamu:</b> <code>{_fmt_cd(protect_left) if protect_left else "—"}</code>
<b>Penjara:</b> <code>{_fmt_cd(jail_left) if jail_left else "bebas ✅"}</code>

<b>Item:</b>
- 🎭 Mask: <code>{items.get('mask',0)}</code>
- 🛡 Shield: <code>{items.get('shield',0)}</code>
- 🔒 Lock: <code>{items.get('lock',0)}</code>
- 💳 Bail Coupon: <code>{items.get('bail_coupon',0)}</code></blockquote>
""")

@PY.UBOT("sbrshop")
async def _(client, message):
    lines = [f"{it['id']}. {it['name']} — <code>{it['price']}</code> uang" for it in SHOP]
    await message.reply(
        "<blockquote><b>🛒 SBR SHOP</b>\n\n"
        + "\n".join(lines)
        + "\n\nBeli: <code>.sbrbuy id qty</code> (qty opsional)</blockquote>"
    )

@PY.UBOT("sbrbuy")
async def _(client, message):
    parts = (message.text or "").split()
    if len(parts) < 2:
        return await message.reply("<blockquote>Format: <code>.sbrbuy id qty</code>\nContoh: <code>.sbrbuy 1 2</code></blockquote>")
    try:
        item_id = int(parts[1])
        qty = int(parts[2]) if len(parts) >= 3 else 1
    except:
        return await message.reply("<blockquote>ID/qty harus angka.</blockquote>")
    if qty <= 0:
        return await message.reply("<blockquote>Qty minimal 1.</blockquote>")

    it = _shop_item(item_id)
    if not it:
        return await message.reply("<blockquote>Item tidak ada. Cek: <code>.sbrshop</code></blockquote>")

    total_price = int(it["price"]) * qty

    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sbr(u)
    s = u["sbr"]

    if int(u["uang"]) < total_price:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang.\nHarga: <code>{total_price}</code> | Saldo: <code>{u['uang']}</code></blockquote>")

    u["uang"] = int(u["uang"]) - total_price
    s["items"][it["key"]] = int(s["items"].get(it["key"], 0)) + (int(it["value"]) * qty)

    _save_db(db)
    await message.reply(f"<blockquote>✅ Beli <b>{it['name']}</b> x<code>{qty}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("sbrbail")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _ensure_sbr(u)
    s = u["sbr"]

    now = _ts()
    if int(s["jail_until"]) <= now:
        _save_db(db)
        return await message.reply("<blockquote>Kamu tidak di penjara.</blockquote>")

    cost = _calc_bail_cost(u)

    # coupon diskon 30% sekali pakai
    if int(s["items"].get("bail_coupon", 0)) > 0:
        cost = int(cost * 0.7)
        s["items"]["bail_coupon"] = int(s["items"]["bail_coupon"]) - 1

    if int(u["uang"]) < cost:
        left = int(s["jail_until"]) - now
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kurang untuk bail.\nBiaya: <code>{cost}</code> | Saldo: <code>{u['uang']}</code>\nSisa penjara: <code>{_fmt_cd(left)}</code></blockquote>")

    u["uang"] = int(u["uang"]) - cost
    s["jail_until"] = 0

    _save_db(db)
    await message.reply(f"<blockquote>✅ Kamu bebas dari penjara!\nBiaya: <code>{cost}</code>\nSaldo: <code>{u['uang']}</code></blockquote>")

@PY.UBOT("steal")
async def _(client, message):
    db = _load_db()
    thief = _get_user(db, message.from_user.id)
    _ensure_sbr(thief)
    ts = _ts()

    s_thief = thief["sbr"]

    # jail check
    if int(s_thief["jail_until"]) > ts:
        left = int(s_thief["jail_until"]) - ts
        _save_db(db)
        return await message.reply(f"<blockquote>🚫 Kamu lagi di penjara.\nSisa: <b>{_fmt_cd(left)}</b>\nBail: <code>.sbrbail</code></blockquote>")

    # rate-limit per hour
    if int(s_thief.get("hour_window_ts", 0)) == 0 or (ts - int(s_thief["hour_window_ts"])) >= 3600:
        s_thief["hour_window_ts"] = ts
        s_thief["hour_count"] = 0
    if int(s_thief["hour_count"]) >= MAX_STEAL_PER_HOUR:
        _save_db(db)
        return await message.reply("<blockquote>⏳ Kamu kebanyakan aksi dalam 1 jam. Istirahat dulu.</blockquote>")

    # cooldown thief
    cd = int(s_thief["steal_last"]) + STEAL_COOLDOWN - ts
    if cd > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>⏳ Cooldown steal: <b>{_fmt_cd(cd)}</b></blockquote>")

    # minimal uang pelaku
    if int(thief["uang"]) < MIN_THIEF_UANG:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kamu terlalu kecil buat “aksi”. Minimal <code>{MIN_THIEF_UANG}</code>.</blockquote>")

    target_user = await _extract_target_user(client, message)
    if not target_user:
        _save_db(db)
        return await message.reply("<blockquote>Format: <code>.steal @user</code> atau reply pesannya.</blockquote>")

    if target_user.is_bot:
        _save_db(db)
        return await message.reply("<blockquote>❌ Tidak bisa target bot.</blockquote>")

    if int(target_user.id) == int(message.from_user.id):
        _save_db(db)
        return await message.reply("<blockquote>❌ Kamu tidak bisa mencuri dari diri sendiri.</blockquote>")

    victim = _get_user(db, int(target_user.id))
    _ensure_sbr(victim)
    s_victim = victim["sbr"]

    # victim protect cd (anti spam)
    vcd = int(s_victim["victim_protect_until"]) - ts
    if vcd > 0:
        _save_db(db)
        return await message.reply(f"<blockquote>🛡 Target lagi “waspada”. Coba lagi <b>{_fmt_cd(vcd)}</b>.</blockquote>")

    # victim minimal uang
    if int(victim["uang"]) < MIN_TARGET_UANG:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Target terlalu miskin 😭 (minimal <code>{MIN_TARGET_UANG}</code> uang).</blockquote>")

    # shield victim blocks 1x
    if int(s_victim["items"].get("shield", 0)) > 0:
        s_victim["items"]["shield"] = int(s_victim["items"]["shield"]) - 1
        s_victim["victim_protect_until"] = ts + VICTIM_PROTECT_CD
        s_thief["steal_last"] = ts
        s_thief["hour_count"] = int(s_thief["hour_count"]) + 1
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>🛡 GAGAL!</b>
Target: {target_user.mention}

Target pakai <b>Shield</b> dan aksi kamu mental 😭
Cooldown kamu aktif. Coba target lain nanti.</blockquote>
""")

    # lock victim blocks 1x (lebih “keras”)
    if int(s_victim["items"].get("lock", 0)) > 0:
        s_victim["items"]["lock"] = int(s_victim["items"]["lock"]) - 1
        s_victim["victim_protect_until"] = ts + (VICTIM_PROTECT_CD + 60)
        # penalty thief kecil
        fine = random.randint(20, 60)
        thief["uang"] = max(0, int(thief["uang"]) - fine)
        s_thief["fails"] = int(s_thief["fails"]) + 1
        s_thief["streak"] = 0
        s_thief["steal_last"] = ts
        s_thief["hour_count"] = int(s_thief["hour_count"]) + 1
        _save_db(db)
        return await message.reply(f"""
<blockquote><b>🔒 KEKUNCI!</b>
Target: {target_user.mention}

Target pakai <b>Lock</b>, kamu kena denda <code>{fine}</code>.
Saldo kamu: <code>{thief['uang']}</code></blockquote>
""")

    # hitung win chance
    # base 52%, dipengaruhi streak + beda saldo (target kaya dikit lebih susah)
    base = 52 + min(12, int(s_thief.get("streak", 0)) * 2)
    if int(victim["uang"]) > int(thief["uang"]) * 3:
        base -= 6

    mask_note = ""
    if int(s_thief["items"].get("mask", 0)) > 0:
        base = min(88, base + 10)
        s_thief["items"]["mask"] = int(s_thief["items"]["mask"]) - 1
        mask_note = f"🎭 Mask aktif (+10% win) (sisa {s_thief['items']['mask']})"

    base = max(15, min(90, base))
    win = random.randint(1, 100) <= base

    # set cooldown/protect
    s_thief["steal_last"] = ts
    s_thief["hour_count"] = int(s_thief["hour_count"]) + 1
    s_victim["victim_protect_until"] = ts + VICTIM_PROTECT_CD

    if win:
        pct = random.randint(STEAL_PERCENT_RANGE[0], STEAL_PERCENT_RANGE[1])
        amount = int(int(victim["uang"]) * (pct / 100.0))
        amount = max(STEAL_MIN_MAX[0], min(STEAL_MIN_MAX[1], amount))
        amount = min(amount, int(victim["uang"]) - 10)  # jangan sampai 0 total
        if amount < 1:
            amount = 1

        victim["uang"] = int(victim["uang"]) - amount
        thief["uang"] = int(thief["uang"]) + amount

        s_thief["wins"] = int(s_thief["wins"]) + 1
        s_thief["streak"] = int(s_thief["streak"]) + 1
        s_thief["stolen_total"] = int(s_thief["stolen_total"]) + amount
        s_thief["stolen_times"] = int(s_thief["stolen_times"]) + 1

        _save_db(db)
        return await message.reply(f"""
<blockquote><b>✅ BERHASIL MENCURI!</b>
Pelaku: {message.from_user.mention}
Target: {target_user.mention}

<b>Dapat:</b> <code>+{amount}</code> uang
<b>Chance:</b> <code>{base}%</code>
{mask_note if mask_note else ""}

Saldo kamu: <code>{thief['uang']}</code></blockquote>
""")
    else:
        fine = random.randint(FINE_RANGE[0], FINE_RANGE[1])
        thief["uang"] = max(0, int(thief["uang"]) - fine)
        s_thief["fails"] = int(s_thief["fails"]) + 1
        s_thief["streak"] = 0

        # kemungkinan masuk penjara
        if random.randint(1, 100) <= 55:
            s_thief["jail_until"] = ts + JAIL_TIME
            jail_note = f"🚔 Kamu ketangkep & masuk penjara <b>{_fmt_cd(JAIL_TIME)}</b>.\nBail: <code>.sbrbail</code>"
        else:
            jail_note = "😮‍💨 Kamu kabur, tapi denda tetap kena."

        _save_db(db)
        return await message.reply(f"""
<blockquote><b>❌ GAGAL MENCURI!</b>
Pelaku: {message.from_user.mention}
Target: {target_user.mention}

<b>Denda:</b> <code>-{fine}</code> uang
<b>Chance:</b> <code>{base}%</code>
{mask_note if mask_note else ""}

{jail_note}
Saldo kamu: <code>{thief['uang']}</code></blockquote>
""")

@PY.UBOT("sbrtop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        s = (data or {}).get("sbr")
        if not s:
            continue
        wins = int(s.get("wins", 0))
        total = int(s.get("stolen_total", 0))
        if wins > 0 or total > 0:
            rank.append((int(uid_str), wins, total))

    rank.sort(key=lambda x: (x[2], x[1]), reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP THIEF</b>\nBelum ada yang bermain.</blockquote>")

    lines = []
    for i, (uid, wins, total) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — win <code>{wins}</code> | total <code>{total}</code>")

    await message.reply("<blockquote><b>🏆 TOP STEAL A BRAINROT</b>\n\n" + "\n".join(lines) + "</blockquote>")
