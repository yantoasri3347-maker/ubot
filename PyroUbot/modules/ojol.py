import random
import asyncio
from PyroUbot import *

__MODULE__ = "ᴏᴊᴏʟ"
__HELP__ = """
<blockquote><b>Bantuan Game Ojol (V3 - Extreme)

Perintah:
<code>{0}narik</code>
- Narik Motor (Resiko sedang).

<code>{0}narik_mobil</code>
- Narik Mobil (Resiko kecil, hasil besar).

<code>{0}dompet</code>
- Cek kekayaan dan kendaraan.

<code>{0}ojol_shop</code>
- Beli kendaraan baru.

<code>{0}top_ojol</code>
- Ranking driver terkaya.</b></blockquote>
"""

# Katalog Kendaraan
MOTOR_SHOP = {
    "beat": {"nama": "Honda Beat", "harga": 500000},
    "nmax": {"nama": "Yamaha NMAX", "harga": 1500000},
    "zx25r": {"nama": "Kawasaki ZX25R", "harga": 5000000},
}

MOBIL_SHOP = {
    "avanza": {"nama": "Toyota Avanza", "harga": 10000000},
    "pajero": {"nama": "Mitsubishi Pajero", "harga": 25000000},
    "tesla": {"nama": "Tesla Model 3", "harga": 50000000},
}

async def get_ojol_data(user_id):
    data = await get_vars(user_id, "OJOL_DATA")
    if not data:
        return {"saldo": 0, "orderan": 0, "motor": "Sepeda Onthel", "mobil": None}
    return data

async def save_ojol_data(user_id, data, client):
    await set_vars(user_id, "OJOL_DATA", data)
    players = await get_vars(client.me.id, "OJOL_PLAYERS") or []
    if user_id not in players:
        players.append(user_id)
        await set_vars(client.me.id, "OJOL_PLAYERS", players)

@PY.UBOT("narik")
async def narik_motor_cmd(client, message):
    user_id = message.from_user.id
    stats = await get_ojol_data(user_id)
    
    msg = await message.reply("🛵 **Mencari orderan motor...**")
    await asyncio.sleep(2)
    
    # --- SISTEM RESIKO ---
    kejadian = random.randint(1, 100)
    if kejadian <= 5: # 5% Peluang Begal
        rugi = random.randint(5000, 20000)
        stats["saldo"] = max(0, stats["saldo"] - rugi)
        await save_ojol_data(user_id, stats, client)
        return await msg.edit(f"💀 **APES!** Kamu dibegal di gang gelap. Saldo berkurang `Rp{rugi:,}`")
    
    elif kejadian <= 15: # 10% Peluang Ban Bocor
        rugi = 10000
        stats["saldo"] = max(0, stats["saldo"] - rugi)
        await save_ojol_data(user_id, stats, client)
        return await msg.edit(f"🛠️ **BAN BOCOR!** Kamu harus tambal ban. Biaya: `Rp{rugi:,}`")
    # ----------------------

    ongkos = random.randint(10000, 25000)
    stats["saldo"] += ongkos
    stats["orderan"] += 1
    await save_ojol_data(user_id, stats, client)
    await msg.edit(f"✅ **Selesai!** Narik pakai `{stats['motor']}` dapat `Rp{ongkos:,}`")

@PY.UBOT("narik_mobil")
async def narik_mobil_cmd(client, message):
    user_id = message.from_user.id
    stats = await get_ojol_data(user_id)
    
    if not stats.get("mobil"):
        return await message.reply("❌ Kamu belum punya mobil!")
    
    msg = await message.reply("🚗 **Mencari orderan Gocar...**")
    await asyncio.sleep(3)
    
    # --- SISTEM RESIKO MOBIL ---
    kejadian = random.randint(1, 100)
    if kejadian <= 8: # 8% Peluang Ditabrak/Lakalantas
        rugi = random.randint(50000, 150000)
        stats["saldo"] = max(0, stats["saldo"] - rugi)
        await save_ojol_data(user_id, stats, client)
        return await msg.edit(f"💥 **KECELAKAAN!** Mobilmu nabrak trotoar. Biaya perbaikan: `Rp{rugi:,}`")
    # ----------------------------

    ongkos = random.randint(40000, 120000)
    stats["saldo"] += ongkos
    stats["orderan"] += 1
    await save_ojol_data(user_id, stats, client)
    await msg.edit(f"✅ **Gocar Selesai!** Pakai `{stats['mobil']}` dapat `Rp{ongkos:,}`")

@PY.UBOT("ojol_shop")
async def shop_cmd(client, message):
    teks = "🛒 **OJOL SHOWROOM**\n\n"
    teks += "🏍️ **MOTOR:**\n"
    for k, v in MOTOR_SHOP.items():
        teks += f"• `{k}` : {v['nama']} (`Rp{v['harga']:,}`)\n"
    teks += "\n🚗 **MOBIL:**\n"
    for k, v in MOBIL_SHOP.items():
        teks += f"• `{k}` : {v['nama']} (`Rp{v['harga']:,}`)\n"
    teks += f"\n**Cara Beli:** `.beli [kode]`"
    await message.reply(teks)

@PY.UBOT("beli")
async def beli_cmd(client, message):
    if len(message.command) < 2: return
    kode = message.command[1].lower()
    user_id = message.from_user.id
    stats = await get_ojol_data(user_id)
    item = MOTOR_SHOP.get(kode) or MOBIL_SHOP.get(kode)
    
    if not item: return await message.reply("❌ Kode salah.")
    if stats["saldo"] < item["harga"]:
        return await message.reply(f"❌ Saldo kurang `Rp{item['harga'] - stats['saldo']:,}`")
    
    stats["saldo"] -= item["harga"]
    if kode in MOTOR_SHOP: stats["motor"] = item["nama"]
    else: stats["mobil"] = item["nama"]
        
    await save_ojol_data(user_id, stats, client)
    await message.reply(f"🎉 Berhasil membeli **{item['nama']}**!")

@PY.UBOT("dompet")
async def dompet_cmd(client, message):
    user_id = message.from_user.id
    stats = await get_ojol_data(user_id)
    await message.reply(
        f"💳 **DOMPET DRIVER**\n"
        f"💰 **Saldo:** `Rp{stats['saldo']:,}`\n"
        f"📦 **Order:** `{stats['orderan']}`\n"
        f"🏍️ **Motor:** `{stats['motor']}`\n"
        f"🚗 **Mobil:** `{stats.get('mobil') or '-'}`"
    )
    
# Ganti dengan User ID kamu (bisa cek lewat .id atau @userinfobot)
OWNER_ID = 5170517638 

@PY.UBOT("addsaldo")
async def add_saldo_cmd(client, message):
    user_id = message.from_user.id
    
    # Pengecekan apakah yang ngetik adalah Owner
    if user_id != OWNER_ID:
        return await message.reply("❌ Perintah ini hanya untuk Owner Bot!")

    # Cek format perintah: .addsaldo [jumlah] (sambil mereply target)
    if len(message.command) < 2:
        return await message.reply("❌ Format: Reply user lalu ketik `.addsaldo 100000` atau `.addsaldo [id_user] 100000`")

    # Ambil Target User ID dan Jumlah Saldo
    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        try:
            nominal = int(message.command[1])
        except ValueError:
            return await message.reply("❌ Nominal harus berupa angka!")
    else:
        if len(message.command) < 3:
            return await message.reply("❌ Masukkan ID User dan Nominal jika tidak me-reply pesan.")
        try:
            target_id = int(message.command[1])
            nominal = int(message.command[2])
        except ValueError:
            return await message.reply("❌ ID User dan Nominal harus berupa angka!")

    # Update Database
    stats = await get_ojol_data(target_id)
    stats["saldo"] += nominal
    await save_ojol_data(target_id, stats, client)

    # Ambil info target untuk konfirmasi
    try:
        target_user = await client.get_users(target_id)
        target_name = target_user.first_name
    except:
        target_name = f"User({target_id})"

    await message.reply(
        f"✅ **BERHASIL ADD SALDO**\n"
        f"──────────────────\n"
        f"👤 **Target:** {target_name}\n"
        f"💰 **Nominal:** `Rp{nominal:,}`\n"
        f"💵 **Saldo Baru:** `Rp{stats['saldo']:,}`\n"
        f"──────────────────\n"
        f"✍️ *Oleh Owner Bot*"
    )

@PY.UBOT("top_ojol")
async def top_ojol_cmd(client, message):
    msg = await message.reply("📊 **Menghitung Ranking...**")
    user_ids = await get_vars(client.me.id, "OJOL_PLAYERS") or []
    lb = []
    for uid in user_ids:
        data = await get_vars(uid, "OJOL_DATA")
        if data:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except: name = f"User-{uid}"
            lb.append({"name": name, "saldo": data.get("saldo", 0)})
    lb.sort(key=lambda x: x["saldo"], reverse=True)
    res = "🏆 **TOP 10 DRIVER TERKAYA**\n"
    for i, u in enumerate(lb[:10], 1):
        res += f"{i}. {u['name']} — `Rp{u['saldo']:,}`\n"
    await msg.edit(res)