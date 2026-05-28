import random
import asyncio
from PyroUbot import *

__MODULE__ = "ʙᴏʟᴀ"
__HELP__ = """
<blockquote><b>⚽ Game Sepak Bola Pro

Perintah:
<code>{0}latihan</code>
- Latihan untuk menambah pengalaman & trofi (Hemat stamina).

<code>{0}sparing</code>
- Melawan tim lain (Skor acak, butuh stamina banyak).

<code>{0}tendang [kiri/tengah/kanan]</code>
- Penalti shootout melawan kiper.

<code>{0}stats_bola</code>
- Cek rekor Win/Lose & Stamina.

<code>{0}top_bola</code>
- Leaderboard pemain terbaik.</b></blockquote>
"""

# --- DATABASE BOLA ---
async def get_ball(user_id):
    data = await get_vars(user_id, "BALL_DATA")
    if not data:
        # Data awal jika player baru main
        return {"win": 0, "lose": 0, "trofi": 0, "stamina": 100}
    # Pastikan key stamina ada
    if "stamina" not in data:
        data["stamina"] = 100
    return data

async def save_ball(user_id, data, client):
    await set_vars(user_id, "BALL_DATA", data)
    # Simpan ke daftar pemain untuk leaderboard
    players = await get_vars(client.me.id, "BALL_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "BALL_PLAYERS", players)

# --- FUNGSI REGEN STAMINA (Bonus) ---
def regen_stamina(data):
    if data["stamina"] < 100:
        data["stamina"] += 5 # Setiap aksi kasih bonus regen sedikit
        if data["stamina"] > 100:
            data["stamina"] = 100
    return data

# --- COMMANDS ---

@PY.UBOT("latihan")
async def latihan_cmd(client, message):
    user_id = message.from_user.id
    ball = await get_ball(user_id)
    
    if ball["stamina"] < 10:
        return await message.reply("😫 **Stamina habis!**\nKamu butuh minimal `10%` stamina untuk latihan.")

    msg = await message.reply("👟 **Sedang latihan menendang bola...**")
    await asyncio.sleep(2)
    
    # Update data
    ball["stamina"] -= 10
    ball["win"] += 1 # Latihan dihitung win kecil
    ball = regen_stamina(ball)
    
    await save_ball(user_id, ball, client)
    await msg.edit(f"✅ **Latihan Selesai!**\n📈 Pengalaman bertambah.\n⚡ Stamina sisa: `{ball['stamina']}%`")

@PY.UBOT("sparing")
async def sparing_cmd(client, message):
    user_id = message.from_user.id
    ball = await get_ball(user_id)
    
    if ball["stamina"] < 30:
        return await message.reply("😫 **Stamina tidak cukup!**\nButuh minimal `30%` untuk sparing.")
    
    msg = await message.reply("🏟️ **Memasuki lapangan pertandingan...**")
    await asyncio.sleep(3)
    
    skor_kamu = random.randint(0, 5)
    skor_lawan = random.randint(0, 5)
    ball["stamina"] -= 30
    
    if skor_kamu > skor_lawan:
        ball["win"] += 1
        ball["trofi"] += 1
        hasil = f"🏆 **MENANG!** `{skor_kamu}-{skor_lawan}`\nTrofi bertambah!"
    elif skor_kamu == skor_lawan:
        hasil = f"🤝 **SERI!** `{skor_kamu}-{skor_lawan}`"
    else:
        ball["lose"] += 1
        hasil = f"❌ **KALAH!** `{skor_kamu}-{skor_lawan}`"
        
    await save_ball(user_id, ball, client)
    await msg.edit(f"🏁 **Pertandingan Selesai!**\n\n{hasil}\n⚡ Stamina sisa: `{ball['stamina']}%`")

@PY.UBOT("tendang")
async def tendang_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("⚽ Pilih arah: `kiri`, `tengah`, atau `kanan`")
        
    arah = message.command[1].lower()
    if arah not in ["kiri", "tengah", "kanan"]:
        return await message.reply("❌ Pilih: kiri/tengah/kanan")
        
    ball = await get_ball(message.from_user.id)
    kiper = random.choice(["kiri", "tengah", "kanan"])
    
    msg = await message.reply("⚽ **Tendangan penalti...**")
    await asyncio.sleep(1)
    
    if arah == kiper:
        ball["lose"] += 1
        res = f"🧤 **DITEPIS!** Kiper ke arah `{kiper}`."
    else:
        ball["win"] += 1
        res = f"⚽ **GOOLL!!** Bola masuk ke arah `{arah}`."
        
    await save_ball(message.from_user.id, ball, client)
    await msg.edit(res)

@PY.UBOT("stats_bola")
async def ball_stats(client, message):
    user_id = message.from_user.id
    ball = await get_ball(user_id)
    await message.reply(
        f"⚽ **STATISTIK PEMAIN**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🏃 **Stamina:** `{ball['stamina']}%`\n"
        f"✅ **Menang:** `{ball['win']}`\n"
        f"❌ **Kalah:** `{ball['lose']}`\n"
        f"🏆 **Trofi:** `{ball['trofi']}`\n"
        f"━━━━━━━━━━━━━━━"
    )

@PY.UBOT("top_bola")
async def top_bola_cmd(client, message):
    msg = await message.reply("📊 **Menyusun Klasemen...**")
    user_ids = await get_vars(client.me.id, "BALL_PLAYERS") or []
    
    lb = []
    for uid in user_ids:
        data = await get_vars(uid, "BALL_DATA")
        if data:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except:
                name = f"Player-{uid}"
            lb.append({"name": name, "win": data.get("win", 0)})

    if not lb:
        return await msg.edit("📭 Belum ada data pemain.")

    lb.sort(key=lambda x: x["win"], reverse=True)
    
    res = "🏆 **TOP 10 PEMAIN BOLA**\n"
    for i, u in enumerate(lb[:10], 1):
        res += f"{i}. {u['name']} — `{u['win']} Win`\n"
    
    await msg.edit(res)