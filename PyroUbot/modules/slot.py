import asyncio
import random
import os
from motor.motor_asyncio import AsyncIOMotorClient
from PyroUbot import *

# --- DATABASE SETUP ---
MONGO_URL = os.getenv("MONGO_URL") or "mongodb+srv://putragana538_db_user:AH96CWeYDpxCtQV2@cluster0.ktpjbrf.mongodb.net/?appName=Cluster0"
mg_client = AsyncIOMotorClient(MONGO_URL)
db = mg_client['ubot_casino'] 
collection = db['slot_points']

async def get_points(user_id):
    user_data = await collection.find_one({"user_id": int(user_id)})
    return user_data.get("points", 0) if user_data else 0

async def update_points(user_id, amount):
    current = await get_points(user_id)
    new_point = max(0, current + amount)
    await collection.update_one(
        {"user_id": int(user_id)}, {"$set": {"points": new_point}}, upsert=True
    )
    return new_point

# --- HADIAH & SETTING ---
JACKPOT_TITLES = ["🔥 SENSATIONAL", "⚡ MAXWIN", "🏆 MEGA WIN", "💎 SCATTER HITAM"]
JACKPOT_ITEMS = ["Emas Antam 1kg", "Pajero Sport", "Saldo 100jt", "iPhone 16 Pro Max"]
ZONK_ITEMS = ["Sandal Swallow", "Karet Gelang", "Tutup Botol", "Piring Deterjen", "Harapan Kosong", "Es Lilin Cair", "Korek Mati", "Kabel Putus"]

__MODULE__ = "sʟᴏᴛ ɢᴀᴄᴏʀ"
__HELP__ = """
<blockquote><b>Bantuan Untuk Slot Gacor</b>

Perintah:
<code>{0}slot</code> [jumlah] → Main slot (1 spin = 1 poin).
Contoh: <code>.slot 10</code>
<code>{0}mypoint</code> → Cek saldo Cloud.</blockquote></b>
"""

@PY.UBOT("slot")
@PY.TOP_CMD
async def _(client, message):
    user_id = message.from_user.id
    args = message.command
    
    # Berapa kali spin (default 1)
    count = int(args[1]) if len(args) > 1 and args[1].isdigit() else 1
    if count > 20:
        return await message.reply_text("<blockquote><b>❌ MAKSIMAL 20 SPIN!</b></blockquote>")
    
    # Cek Saldo (Biaya 1 poin per spin)
    current_p = await get_points(user_id)
    if current_p < count:
        return await message.reply_text(
            f"<blockquote><b>❌ SALDO TIDAK CUKUP</b>\n\n"
            f"Poinmu kurang, <b>gas deposit biar bisa bet</b> lagi! 🗿\n"
            f"<b>Butuh:</b> <code>{count}</code> | <b>Saldo:</b> <code>{current_p}</code></blockquote>"
        )

    # Potong saldo awal
    await update_points(user_id, -count)
    status = await message.reply_text(f"<blockquote><b>🎰 MEMULAI {count}x SPIN...</b>\n<i>Biaya: {count} Poin</i></blockquote>")
    
    history = []
    total_win = 0

    for i in range(1, count + 1):
        await status.edit(f"<blockquote><b>✨ SPIN KE-{i} DARI {count}...</b>\n<i>Mencari pola scatter... ⚡</i></blockquote>")
        
        slot_msg = await client.send_dice(message.chat.id, emoji="🎰")
        val = slot_msg.dice.value
        await asyncio.sleep(4) # Tunggu animasi
        
        # LOGIKA JP SULIT:
        # 1. Harus dapet emoji kembar (val 1, 22, 43, 64)
        # 2. Harus lolos angka hoki (1 dari 5 chance)
        is_jackpot = val in [1, 22, 43, 64]
        hoki_check = random.randint(1, 5) == 1 # Chance tambahan biar sulit

        if is_jackpot and hoki_check:
            win = 50 # Hadiah JP gede karena sulit
            gift = f"{random.choice(JACKPOT_TITLES)}: {random.choice(JACKPOT_ITEMS)}"
            total_win += win
            history.append(f"<code>[{i}]</code> ✅ {gift} (<code>+{win}</code>)")
        else:
            # Tetap kasih hiburan kecil kalo cuma dapet emoji kembar tapi ga lolos hoki_check
            if is_jackpot:
                win_kecil = 5
                total_win += win_kecil
                history.append(f"<code>[{i}]</code> 💎 <b>BIG WIN:</b> Poin Balik (<code>+{win_kecil}</code>)")
            else:
                history.append(f"<code>[{i}]</code> 💀 ZONK: {random.choice(ZONK_ITEMS)}")
        
        try: await slot_msg.delete()
        except: pass

    # Update saldo akhir
    final_p = await update_points(user_id, total_win)
    
    hasil_teks = "\n".join(history)
    await status.edit(
        f"<blockquote><b>🏁 HASIL SLOT BRUTAL ({count}x)</b>\n\n"
        f"{hasil_teks}\n\n"
        f"<b>💰 SUMMARY:</b>\n"
        f"<b>Total Menang:</b> <code>+{total_win} Poin</code>\n"
        f"<b>Saldo Akhir:</b> <code>{final_p} Poin</code>\n\n"
        f"<i>Analisa: {random.choice(['Bandarnya lagi pelit!', 'Dikit lagi JP itu!', 'Mending kerja bangunan, Cuy.', 'Gacor tipis-tipis.'])}</i></blockquote>"
    )

@PY.UBOT("mypoint")
async def _(client, message):
    p = await get_points(message.from_user.id)
    await message.reply_text(f"<blockquote><b>💰 CLOUD WALLET</b>\n\n<b>User:</b> {message.from_user.mention}\n<b>Saldo:</b> <code>{p} Poin</code></blockquote>")

# --- KUNCI OWNER PUSAT ---
OWNER_PUSAT = 5170517638

@PY.UBOT("addpoint")
@PY.TOP_CMD
async def _(client, message):
    if message.from_user.id != OWNER_PUSAT:
        return await message.reply("<blockquote><b>❌ AKSES DITOLAK!</b></blockquote>")
    
    args = message.command
    target_id = message.reply_to_message.from_user.id if message.reply_to_message else (int(args[1]) if len(args) > 2 else None)
    amount = int(args[1] if message.reply_to_message else args[2]) if (len(args) > 1) else 0

    if not target_id or amount <= 0:
        return await message.reply("<b>Format:</b> <code>.addpoint [jumlah]</code> (reply) atau <code>.addpoint [id] [jumlah]</code>")

    new_p = await update_points(target_id, amount)
    await message.reply(f"<blockquote><b>✅ BERHASIL TAMBAH</b>\n<b>User:</b> <code>{target_id}</code>\n<b>Suntik:</b> <code>+{amount}</code>\n<b>Total:</b> <code>{new_p}</code></blockquote>")

@PY.UBOT("delpoint")
@PY.TOP_CMD
async def _(client, message):
    # Cek apakah yang ngetik itu lu (Owner Pusat)
    if message.from_user.id != OWNER_PUSAT:
        return await message.reply("<blockquote><b>❌ Akses Ditolak Khusus Bandar!</b></blockquote>")

    # Wajib reply orang yang mau dikuras poinnya
    if not message.reply_to_message:
        return await message.reply("<b>Cara Pakai:</b> Reply orangnya terus ketik <code>.delpoint</code> untuk hapus semua poinnya.")

    target_id = message.reply_to_message.from_user.id
    
    # Setel poin ke 0 di MongoDB
    await collection.update_one(
        {"user_id": target_id}, 
        {"$set": {"points": 0}}, 
        upsert=True
    )
    
    await message.reply(
        f"<blockquote><b>💀 SALDO DIKURAS HABIS!</b>\n\n"
        f"<b>User:</b> <code>{target_id}</code>\n"
        f"<b>Status:</b> Berhasil dihapus semua.\n"
        f"<b>Sisa Saldo:</b> <code>0</code></blockquote>"
    )