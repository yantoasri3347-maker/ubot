import os
import json
import random
from datetime import datetime
from pytz import timezone

from PyroUbot import *

__MODULE__ = "ludoking"
__HELP__ = """
<blockquote><b>Game Ludo King</b>

<b>Solo</b>
- <code>.ludostart</code> → aktifkan
- <code>.ludoplay</code> → main cepat vs bot

<b>Duel</b>
- <code>.ludo @user bet</code> / reply + bet → tantang duel
- <code>.ludoaccept</code> → terima duel
- <code>.ludoroll</code> → lempar dadu (giliran)
- <code>.ludostatus</code> → status duel
- <code>.ludocancel</code> → batal duel (pembuat)

<b>Leaderboard</b>
- <code>.ludotop</code> → top win</blockquote>
"""

TZ = timezone("Asia/Jakarta")
DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "gacha.json")
os.makedirs(DATA_DIR, exist_ok=True)

LUDO_FILE = os.path.join(DATA_DIR, "ludo_duel.json")

BOARD_LEN = 30              # panjang lintasan
CAPTURE_BONUS = 4           # bonus langkah kalau "nangkep"
DEFAULT_BET = 120
MIN_BET = 50
MAX_BET = 5000

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
        db["users"][uid] = {"uang": 0, "ludo": {"win": 0, "lose": 0}}
    u = db["users"][uid]
    u.setdefault("uang", 0)
    u.setdefault("ludo", {"win": 0, "lose": 0})
    u["ludo"].setdefault("win", 0)
    u["ludo"].setdefault("lose", 0)
    return u

def _ts():
    return int(datetime.now(TZ).timestamp())

def _progress_bar(pos: int) -> str:
    # bar sederhana
    pos = max(0, min(BOARD_LEN, pos))
    left = "─" * (pos)
    right = "─" * (BOARD_LEN - pos)
    return f"{left}🔴{right}"

def _progress_bar2(p1: int, p2: int) -> str:
    # represent 2 token di track
    p1 = max(0, min(BOARD_LEN, p1))
    p2 = max(0, min(BOARD_LEN, p2))
    s = []
    for i in range(BOARD_LEN + 1):
        if i == p1 and i == p2:
            s.append("🟣")   # tabrakan
        elif i == p1:
            s.append("🔴")
        elif i == p2:
            s.append("🔵")
        else:
            s.append("─")
    return "".join(s)

def _dice():
    return random.randint(1, 6)

async def _extract_target(client, message):
    if getattr(message, "reply_to_message", None) and getattr(message.reply_to_message, "from_user", None):
        return message.reply_to_message.from_user
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2:
        return None
    raw = parts[1].strip()
    try:
        return await client.get_users(raw)
    except:
        try:
            return await client.get_users(int(raw))
        except:
            return None

def _find_active_duel(duels, user_id: int):
    uid = str(user_id)
    for did, d in duels.items():
        if d.get("p1") == uid or d.get("p2") == uid:
            return did, d
    return None, None

@PY.UBOT("ludostart")
async def _(client, message):
    db = _load_db()
    u = _get_user(db, message.from_user.id)
    _save_db(db)
    await message.reply(f"""
<blockquote><b>✅ LUDO KING AKTIF</b>
{message.from_user.mention}

Solo: <code>.ludoplay</code>
Duel: <code>.ludo @user 200</code></blockquote>
""")

@PY.UBOT("ludoplay")
async def _(client, message):
    # solo vs bot, game cepat 6 turn masing-masing, lalu siapa lebih jauh menang
    db = _load_db()
    u = _get_user(db, message.from_user.id)

    bet = DEFAULT_BET
    if u["uang"] < bet:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kamu kurang untuk solo bet <code>{bet}</code>.\nSaldo: <code>{u['uang']}</code></blockquote>")

    # potong bet dulu
    u["uang"] -= bet

    p = 0
    b = 0
    log = []
    for turn in range(1, 7):
        d1 = _dice()
        d2 = _dice()
        p = min(BOARD_LEN, p + d1)
        b = min(BOARD_LEN, b + d2)

        # capture rule simple: kalau posisi sama & bukan finish, player dapat bonus
        if p == b and p < BOARD_LEN:
            p = min(BOARD_LEN, p + CAPTURE_BONUS)
            log.append(f"Turn {turn}: kamu {d1}, bot {d2} → 🟣 tabrakan! kamu +{CAPTURE_BONUS}")
        else:
            log.append(f"Turn {turn}: kamu {d1}, bot {d2}")

    if p > b:
        win = True
    elif b > p:
        win = False
    else:
        win = None

    if win is True:
        reward = int(bet * 2.0)
        u["uang"] += reward
        u["ludo"]["win"] += 1
        result = f"✅ Kamu menang! +<code>{reward}</code> uang"
    elif win is False:
        u["ludo"]["lose"] += 1
        result = f"❌ Kamu kalah! -<code>{bet}</code> uang"
    else:
        # draw: balikin bet
        u["uang"] += bet
        result = f"🤝 Seri! bet dikembalikan <code>{bet}</code>"

    _save_db(db)

    await message.reply(f"""
<blockquote><b>🎲 LUDO SOLO vs BOT</b>
{message.from_user.mention}

<b>Track:</b>
{_progress_bar2(p, b)}
<b>Pos kamu:</b> <code>{p}/{BOARD_LEN}</code>
<b>Pos bot:</b> <code>{b}/{BOARD_LEN}</code>

<b>Log:</b>
{chr(10).join(["- "+x for x in log])}

<b>Hasil:</b> {result}
<b>Saldo:</b> <code>{u['uang']}</code></blockquote>
""")

@PY.UBOT("ludo")
async def _(client, message):
    # create duel
    parts = (message.text or "").split(maxsplit=2)
    db = _load_db()
    u = _get_user(db, message.from_user.id)

    duel_db = _load_json(LUDO_FILE, {"duels": {}})
    duels = duel_db.get("duels", {})

    # cek apakah user sudah ada duel
    did, _ = _find_active_duel(duels, message.from_user.id)
    if did:
        return await message.reply("<blockquote>❌ Kamu masih punya duel aktif. Cek: <code>.ludostatus</code></blockquote>")

    target = await _extract_target(client, message)
    if not target:
        return await message.reply("<blockquote>Format: <code>.ludo @user 200</code> atau reply target + tulis <code>.ludo 200</code></blockquote>")
    if target.is_bot or target.id == message.from_user.id:
        return await message.reply("<blockquote>❌ Target tidak valid.</blockquote>")

    # bet parsing
    bet = DEFAULT_BET
    if len(parts) >= 3:
        try:
            bet = int(parts[2].strip())
        except:
            bet = DEFAULT_BET
    else:
        # kalau reply: .ludo 200
        if getattr(message, "reply_to_message", None) and len(parts) >= 2:
            try:
                bet = int(parts[1].strip())
            except:
                bet = DEFAULT_BET

    bet = max(MIN_BET, min(MAX_BET, bet))

    # cek saldo
    if int(u["uang"]) < bet:
        _save_db(db)
        return await message.reply(f"<blockquote>❌ Uang kamu kurang untuk bet <code>{bet}</code>.\nSaldo: <code>{u['uang']}</code></blockquote>")

    # cek saldo target (optional, tapi lebih fair)
    db2 = _load_db()
    ut = _get_user(db2, target.id)
    if int(ut["uang"]) < bet:
        _save_db(db2)
        return await message.reply(f"<blockquote>❌ Target belum cukup uang untuk bet <code>{bet}</code>.</blockquote>")

    duel_id = str(_ts()) + str(random.randint(100, 999))
    duels[duel_id] = {
        "p1": str(message.from_user.id),
        "p2": str(target.id),
        "bet": bet,
        "state": "pending",
        "turn": "p1",   # p1 mulai
        "p1pos": 0,
        "p2pos": 0,
        "created": _ts(),
        "last_roll": 0,
    }
    duel_db["duels"] = duels
    _save_json(LUDO_FILE, duel_db)

    await message.reply(f"""
<blockquote><b>🎲 Tantangan Ludo!</b>
Dari: {message.from_user.mention}
Ke: {target.mention}

<b>Bet:</b> <code>{bet}</code> uang
Target ketik: <code>.ludoaccept</code></blockquote>
""")

@PY.UBOT("ludoaccept")
async def _(client, message):
    duel_db = _load_json(LUDO_FILE, {"duels": {}})
    duels = duel_db.get("duels", {})
    did, d = _find_active_duel(duels, message.from_user.id)

    if not did:
        return await message.reply("<blockquote>❌ Kamu tidak punya duel pending.</blockquote>")

    if d.get("state") != "pending":
        return await message.reply("<blockquote>❌ Duel ini bukan pending.</blockquote>")

    if d.get("p2") != str(message.from_user.id):
        return await message.reply("<blockquote>❌ Kamu bukan target duel ini.</blockquote>")

    # potong uang kedua pihak
    bet = int(d["bet"])
    db = _load_db()
    u1 = _get_user(db, int(d["p1"]))
    u2 = _get_user(db, int(d["p2"]))

    if int(u1["uang"]) < bet or int(u2["uang"]) < bet:
        return await message.reply("<blockquote>❌ Salah satu pemain uangnya kurang. Duel dibatalkan.</blockquote>")

    u1["uang"] -= bet
    u2["uang"] -= bet

    d["state"] = "active"
    d["last_roll"] = _ts()
    duels[did] = d
    duel_db["duels"] = duels
    _save_json(LUDO_FILE, duel_db)
    _save_db(db)

    p1 = await client.get_users(int(d["p1"]))
    await message.reply(f"""
<blockquote><b>✅ Duel dimulai!</b>
P1: {p1.mention}
P2: {message.from_user.mention}

Giliran: <b>P1</b>
Ketik: <code>.ludoroll</code></blockquote>
""")

@PY.UBOT("ludostatus")
async def _(client, message):
    duel_db = _load_json(LUDO_FILE, {"duels": {}})
    did, d = _find_active_duel(duel_db.get("duels", {}), message.from_user.id)
    if not did:
        return await message.reply("<blockquote>❌ Kamu tidak punya duel aktif.</blockquote>")

    p1 = d["p1"]
    p2 = d["p2"]
    bet = d["bet"]
    st = d["state"]

    try:
        u1 = await client.get_users(int(p1))
        u2 = await client.get_users(int(p2))
        n1, n2 = u1.first_name, u2.first_name
    except:
        n1, n2 = "P1", "P2"

    bar = _progress_bar2(int(d["p1pos"]), int(d["p2pos"]))
    turn_name = n1 if d["turn"] == "p1" else n2

    await message.reply(f"""
<blockquote><b>🎲 LUDO STATUS</b>
<b>Status:</b> <code>{st}</code>
<b>Bet:</b> <code>{bet}</code>

<b>Track:</b>
{bar}
<b>{n1}:</b> <code>{d['p1pos']}/{BOARD_LEN}</code>
<b>{n2}:</b> <code>{d['p2pos']}/{BOARD_LEN}</code>

<b>Giliran:</b> <b>{turn_name}</b></blockquote>
""")

@PY.UBOT("ludocancel")
async def _(client, message):
    duel_db = _load_json(LUDO_FILE, {"duels": {}})
    duels = duel_db.get("duels", {})
    did, d = _find_active_duel(duels, message.from_user.id)

    if not did:
        return await message.reply("<blockquote>❌ Tidak ada duel untuk dibatalkan.</blockquote>")

    if d.get("p1") != str(message.from_user.id):
        return await message.reply("<blockquote>❌ Hanya pembuat duel (P1) yang bisa cancel.</blockquote>")

    # kalau sudah active, tidak bisa cancel biar fair
    if d.get("state") == "active":
        return await message.reply("<blockquote>❌ Duel sudah aktif, tidak bisa cancel.</blockquote>")

    del duels[did]
    duel_db["duels"] = duels
    _save_json(LUDO_FILE, duel_db)
    await message.reply("<blockquote>✅ Duel dibatalkan.</blockquote>")

@PY.UBOT("ludoroll")
async def _(client, message):
    duel_db = _load_json(LUDO_FILE, {"duels": {}})
    duels = duel_db.get("duels", {})
    did, d = _find_active_duel(duels, message.from_user.id)

    if not did:
        return await message.reply("<blockquote>❌ Kamu tidak punya duel aktif.</blockquote>")
    if d.get("state") != "active":
        return await message.reply("<blockquote>❌ Duel belum aktif. Ketik <code>.ludoaccept</code> jika pending.</blockquote>")

    uid = str(message.from_user.id)
    is_p1 = (uid == d["p1"])
    is_p2 = (uid == d["p2"])
    if not (is_p1 or is_p2):
        return await message.reply("<blockquote>❌ Kamu bukan pemain duel ini.</blockquote>")

    turn = d["turn"]
    if (turn == "p1" and not is_p1) or (turn == "p2" and not is_p2):
        return await message.reply("<blockquote>⏳ Bukan giliran kamu.</blockquote>")

    roll = _dice()

    # gerak
    if turn == "p1":
        d["p1pos"] = min(BOARD_LEN, int(d["p1pos"]) + roll)
    else:
        d["p2pos"] = min(BOARD_LEN, int(d["p2pos"]) + roll)

    event = ""
    # capture: kalau posisi sama & belum finish, yang jalan dapat bonus
    if int(d["p1pos"]) == int(d["p2pos"]) and int(d["p1pos"]) < BOARD_LEN:
        if turn == "p1":
            d["p1pos"] = min(BOARD_LEN, int(d["p1pos"]) + CAPTURE_BONUS)
        else:
            d["p2pos"] = min(BOARD_LEN, int(d["p2pos"]) + CAPTURE_BONUS)
        event = f"🟣 Nangkep! bonus +{CAPTURE_BONUS} langkah"

    # cek menang
    winner = None
    if int(d["p1pos"]) >= BOARD_LEN:
        winner = "p1"
    elif int(d["p2pos"]) >= BOARD_LEN:
        winner = "p2"

    # ganti giliran (kalau belum selesai)
    if not winner:
        d["turn"] = "p2" if turn == "p1" else "p1"

    duels[did] = d
    duel_db["duels"] = duels
    _save_json(LUDO_FILE, duel_db)

    # tampil status ringkas
    try:
        u1 = await client.get_users(int(d["p1"]))
        u2 = await client.get_users(int(d["p2"]))
        n1, n2 = u1.first_name, u2.first_name
        m1, m2 = u1.mention, u2.mention
    except:
        n1, n2 = "P1", "P2"
        m1, m2 = "P1", "P2"

    bar = _progress_bar2(int(d["p1pos"]), int(d["p2pos"]))
    msg_roll = f"""
<blockquote><b>🎲 LUDO ROLL</b>
Giliran: <b>{n1 if turn=='p1' else n2}</b>
Dadu: <code>{roll}</code>
{event if event else ""}

<b>Track:</b>
{bar}
<b>{n1}:</b> <code>{d['p1pos']}/{BOARD_LEN}</code>
<b>{n2}:</b> <code>{d['p2pos']}/{BOARD_LEN}</code>
</blockquote>
"""

    if not winner:
        next_name = n1 if d["turn"] == "p1" else n2
        return await message.reply(msg_roll + f"<blockquote>Giliran selanjutnya: <b>{next_name}</b> → <code>.ludoroll</code></blockquote>")

    # finalize duel
    bet = int(d["bet"])
    pot = bet * 2

    db = _load_db()
    p1u = _get_user(db, int(d["p1"]))
    p2u = _get_user(db, int(d["p2"]))

    if winner == "p1":
        p1u["uang"] += pot
        p1u["ludo"]["win"] += 1
        p2u["ludo"]["lose"] += 1
        win_text = f"🏆 Pemenang: {m1}\nHadiah: <code>+{pot}</code> uang"
    else:
        p2u["uang"] += pot
        p2u["ludo"]["win"] += 1
        p1u["ludo"]["lose"] += 1
        win_text = f"🏆 Pemenang: {m2}\nHadiah: <code>+{pot}</code> uang"

    _save_db(db)

    # hapus duel
    duel_db = _load_json(LUDO_FILE, {"duels": {}})
    duels = duel_db.get("duels", {})
    if did in duels:
        del duels[did]
        duel_db["duels"] = duels
        _save_json(LUDO_FILE, duel_db)

    await message.reply(msg_roll + f"<blockquote><b>✅ DUEL SELESAI</b>\n{win_text}</blockquote>")

@PY.UBOT("ludotop")
async def _(client, message):
    db = _load_db()
    users = db.get("users", {})

    rank = []
    for uid_str, data in users.items():
        l = (data or {}).get("ludo")
        if not l:
            continue
        w = int(l.get("win", 0))
        if w > 0:
            rank.append((int(uid_str), w))

    rank.sort(key=lambda x: x[1], reverse=True)
    rank = rank[:10]

    if not rank:
        return await message.reply("<blockquote><b>🏆 TOP LUDO</b>\nBelum ada yang menang.</blockquote>")

    lines = []
    for i, (uid, w) in enumerate(rank, start=1):
        try:
            us = await client.get_users(uid)
            name = us.first_name or "Unknown"
        except:
            name = "Unknown"
        lines.append(f"{i}. <b>{name}</b> — win <code>{w}</code>")

    await message.reply("<blockquote><b>🏆 TOP LUDO KING</b>\n\n" + "\n".join(lines) + "</blockquote>")
