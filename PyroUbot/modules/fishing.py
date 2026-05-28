import json, os, random, time as t
from PyroUbot import *

__MODULE__ = "ꜰɪꜱʜɪɴɢ ᴘʀᴏ"
__HELP__ = """
<blockquote><b>🎣 Fishing Pro</b>

<b>Perintah Utama</b>
• <code>{0}mancing</code> — mancing ikan
• <code>{0}ikan</code> — lihat ikan
• <code>{0}jualikan</code> — jual semua ikan
• <code>{0}profil</code> — profil mancing
• <code>{0}topmancing</code> — leaderboard

<b>Rod</b>
• <code>{0}rod</code> — lihat rod
• <code>{0}upgraderod</code> — upgrade rod

<b>Lomba mancing</b>
• <code>{0}skorlomba</code> — melihat skor lomba
• <code>{0}lombamancing</code> — memulai lomba
• <code>{0}stoplomba</code> — hentikan lomba</blockquote>
"""

DB = "PyroUbot/database/fishing.json"
COOLDOWN = 5

# ================= EVENT =================
EVENT = {"on": False}

# ================= ROD CONFIG =================
ROD_INFO = {
    "Kayu": {"base_bonus": 0},
    "Besi": {"base_bonus": 5},
    "Emas": {"base_bonus": 10},
    "Legend": {"base_bonus": 20},
}

# ================= FISH =================
FISHES = {
    "Common": [("Lele", 5), ("Nila", 6)],
    "Rare": [("Salmon", 15)],
    "Epic": [("Hiu", 40)],
    "Secret utama": [
        ("Megalodon", 120),
        ("El maja", 150),
        ("Dino", 170),
        ("Megawati wkwk", 200),
        ("Buaya", 130),
    ]
}

RATE = {
    "Common": 70,
    "Rare": 30,
    "Epic": 15,
    "Secret utama": 5,
}

# ================= DATABASE =================
def load():
    if not os.path.exists(DB):
        with open(DB, "w") as f:
            f.write("{}")
    try:
        return json.load(open(DB))
    except:
        return {}

def save(data):
    json.dump(data, open(DB, "w"), indent=2)

def get_user(uid):
    data = load()
    uid = str(uid)

    if uid not in data:
        data[uid] = {
            "level": 1,
            "exp": 0,
            "coin": 0,
            "rod": {"name": "Kayu", "level": 1},
            "fish": {},
            "last": 0,
            "lomba": 0
        }

    # migrasi rod lama
    if isinstance(data[uid]["rod"], str):
        data[uid]["rod"] = {"name": data[uid]["rod"], "level": 1}

    save(data)
    return data, data[uid]

# ================= LOGIC =================
def exp_need(lv):
    return lv * 50

def pick_rarity(bonus):
    roll = random.randint(1, 100 + bonus)
    total = 0
    for r, v in RATE.items():
        total += v
        if roll <= total + bonus:
            return r
    return "Common"

def fish_price(name):
    for fishes in FISHES.values():
        for f, p in fishes:
            if f.lower() == name.lower():
                return p
    return 0

# ================= COMMAND =================
@PY.UBOT("mancing")
async def mancing(_, m):
    data, u = get_user(m.from_user.id)

    if t.time() - u["last"] < COOLDOWN:
        return await m.reply("⏳ Tunggu cooldown")

    rod = u["rod"]
    base = ROD_INFO[rod["name"]]["base_bonus"]
    bonus = base + (rod["level"] * 3)

    rarity = pick_rarity(bonus)
    fish, price = random.choice(FISHES[rarity])

    u["fish"][fish] = u["fish"].get(fish, 0) + 1
    u["exp"] += price
    u["last"] = t.time()
    
    while u["exp"] >= exp_need(u["level"]):
        u["exp"] -= exp_need(u["level"])
        u["level"] += 1

    if EVENT["on"]:
        u["lomba"] += price

    save(data)

    await m.reply(
        f"🎣 <b>Hasil Mancing</b>\n\n"
        f"🐟 {fish}\n"
        f"✨ {rarity}\n"
        f"💰 {price} coin\n"
        f"🎯 Bonus Rod: +{bonus}%"
    )

@PY.UBOT("lombamancing")
async def lomba(_, m):
    EVENT["on"] = True
    data = load()
    for u in data.values():
        u["lomba"] = 0
    save(data)
    await m.reply("🏁 <b>Lomba mancing dimulai!</b>")

@PY.UBOT("stoplomba")
async def stop(_, m):
    EVENT["on"] = False
    data = load()

    rank = sorted(data.items(), key=lambda x: x[1]["lomba"], reverse=True)
    txt = "🏆 <b>Hasil Lomba</b>\n\n"

    for i, (uid, u) in enumerate(rank[:5], 1):
        txt += f"{i}. <code>{uid}</code> — {u['lomba']} pts\n"
        u["coin"] += 200

    save(data)
    await m.reply(txt)

@PY.UBOT("skorlomba")
async def skor(_, m):
    _, u = get_user(m.from_user.id)
    await m.reply(f"🎯 Skor lomba kamu: {u['lomba']}")

@PY.UBOT("rod")
async def rod(_, m):
    _, u = get_user(m.from_user.id)
    r = u["rod"]
    bonus = ROD_INFO[r["name"]]["base_bonus"] + (r["level"] * 3)

    await m.reply(
        f"🎣 <b>Rod Kamu</b>\n\n"
        f"🔹 Nama: {r['name']}\n"
        f"🔺 Level: {r['level']}\n"
        f"🎯 Bonus: +{bonus}%"
    )

@PY.UBOT("upgraderod")
async def upgraderod(_, m):
    data, u = get_user(m.from_user.id)
    r = u["rod"]
    cost = r["level"] * 100

    if u["coin"] < cost:
        return await m.reply("❌ Coin tidak cukup")

    u["coin"] -= cost
    r["level"] += 1
    save(data)

    await m.reply(
        f"⬆️ <b>Rod Upgrade</b>\n\n"
        f"🎣 {r['name']} Lv {r['level']}\n"
        f"💰 -{cost} coin"
    )

@PY.UBOT("ikan")
async def ikan(_, m):
    u = load().get(str(m.from_user.id))
    if not u or not u["fish"]:
        return await m.reply("❌ Tidak ada ikan")

    txt = "🎒 <b>Koleksi Ikan</b>\n\n"
    for f, j in u["fish"].items():
        txt += f"• {f} × {j}\n"
    await m.reply(txt)

@PY.UBOT("jualikan")
async def jual(_, m):
    data, u = get_user(m.from_user.id)
    total = sum(fish_price(f) * j for f, j in u["fish"].items())

    u["fish"] = {}
    u["coin"] += total
    save(data)

    await m.reply(f"💰 Semua ikan terjual\nCoin +{total}")

@PY.UBOT("profil")
async def profil(_, m):
    u = load().get(str(m.from_user.id))
    await m.reply(
        f"👤 <b>Profil Mancing</b>\n\n"
        f"🎚 Level: {u['level']}\n"
        f"🎣 Rod: {u['rod']['name']} Lv {u['rod']['level']}\n"
        f"💰 Coin: {u['coin']}\n"
        f"📈 EXP: {u['exp']}/{exp_need(u['level'])}"
    )

@PY.UBOT("topmancing")
async def top(_, m):
    data = load()
    rank = sorted(data.items(), key=lambda x: x[1]["level"], reverse=True)[:10]

    txt = "🏆 <b>Top Mancing</b>\n\n"
    for i, (uid, u) in enumerate(rank, 1):
        txt += f"{i}. <code>{uid}</code> — Lv {u['level']}\n"
    await m.reply(txt)