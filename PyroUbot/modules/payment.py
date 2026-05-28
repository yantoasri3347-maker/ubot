# ============================================================
# 📄 ᴍᴏᴅᴜʟ ᴘᴀʏᴍᴇɴᴛ ᴏᴛᴏᴍᴀᴛɪꜱ ᴘᴀᴋᴀꜱɪʀ ꜰᴜʟʟ ꜱᴍᴀʀᴛ ᴍᴀᴛʜ
# ============================================================
# ᴅᴇꜱᴋʀɪᴘꜱɪ: ᴏᴛᴏᴍᴀᴛɪꜱ ʜɪᴛᴜɴɢ ꜱᴇʟɪꜱɪʜ, ʟᴏɢ ᴄʜ ᴘʜᴏᴛᴏ, ᴘᴍ ᴏᴡɴᴇʀ
# ============================================================

import asyncio
import aiohttp
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PyroUbot import *

PakasirApiData = {
    "ApiKey": "2lWMGe9pu0EFNBKdcGqolbvepdDD4Otr",
    "ProjectSlug": "putranavila"
}

IdChannelLogTransaksi = -1003768411962 

# --- ᴅᴀᴛᴀʙᴀꜱᴇ ʜᴀʀɢᴀ ᴘᴀᴛᴏᴋᴀɴ ---
HargaAsli = {
    "member": {"1": 1000, "0": 2000},
    "seles": {"1": 3000, "0": 5000},
    "admin": {"1": 7000, "0": 10000},
    "owner": {"1": 13000, "0": 15000},
    "tk": {"1": 17000, "0": 20000},
    "ceo": {"1": 22000, "0": 25000},
    "founder": {"1": 32000, "0": 35000}
}

async def CekStatusBayarPakasir(IdPesanan, JumlahBayar=None):
    UrlApiPakasir = "https://app.pakasir.com/api/transactiondetail"
    ParameterRequest = {
        "project": PakasirApiData["ProjectSlug"],
        "api_key": PakasirApiData["ApiKey"],
        "order_id": IdPesanan
    }
    if JumlahBayar:
        ParameterRequest["amount"] = JumlahBayar

    async with aiohttp.ClientSession() as SesiClient:
        try:
            async with SesiClient.get(UrlApiPakasir, params=ParameterRequest) as ResponApi:
                DataJson = await ResponApi.json()
                DetailTransaksi = DataJson.get("transaction") or DataJson or {}
                StatusTransaksi = str(DetailTransaksi.get("status", "")).upper()
                ListStatusLunas = ["PAID", "SUCCESS", "BERHASIL", "COMPLETED"]
                return any(StatusValid in StatusTransaksi for StatusValid in ListStatusLunas)
        except Exception as e:
            print("PAKASIR ERROR:", e)
            return False

@bot.on_callback_query(filters.regex("^pilih_durasi"))
async def ProsesKonfirmasiBayar(client, callback_query):
    DataQuery = callback_query.data.split()
    RoleDipesan = DataQuery[1]
    DurasiDipesan = DataQuery[2]
    UserId = callback_query.from_user.id
    
    # 1. ʜɪᴛᴜɴɢ ᴘᴏᴛᴏɴɢᴀɴ ʀᴏʟᴇ ʟᴀᴍᴀ ꜱᴇʙᴇʟᴜᴍ ʙᴜᴀᴛ ǫʀɪꜱ
    Potongan = 0
    if await is_vars(client.me.id, "ALLROLE_USERS", UserId): Potongan = HargaAsli["founder"][DurasiDipesan]
    elif await is_vars(client.me.id, "CIOGWMAH_USERS", UserId): Potongan = HargaAsli["ceo"][DurasiDipesan]
    elif await is_vars(client.me.id, "KHASJIR_USERS", UserId): Potongan = HargaAsli["tk"][DurasiDipesan]
    elif await is_vars(client.me.id, "OWNER_USERS", UserId): Potongan = HargaAsli["owner"][DurasiDipesan]
    elif await is_vars(client.me.id, "ADMIN_USERS", UserId): Potongan = HargaAsli["admin"][DurasiDipesan]
    elif await is_vars(client.me.id, "SELER_USERS", UserId): Potongan = HargaAsli["seles"][DurasiDipesan]
    elif await is_vars(client.me.id, "PREM_USERS", UserId): Potongan = HargaAsli["member"][DurasiDipesan]

    HargaTarget = HargaAsli.get(RoleDipesan, {}).get(DurasiDipesan, 0)
    NominalHarusDibayar = HargaTarget - Potongan

    if NominalHarusDibayar <= 0:
        return await callback_query.answer("⚠️ ᴀɴᴅᴀ ꜱᴜᴅᴀʜ ᴍᴇᴍɪʟɪᴋɪ ʀᴏʟᴇ ɪɴɪ ᴀᴛᴀᴜ ʏᴀɴɢ ʟᴇʙɪʜ ᴛɪɴɢɢɪ!", show_alert=True)

    IdPesanan = f"IQB-{UserId}-{datetime.now().strftime('%H%M%S')}"
    UrlBuatQris = f"https://app.pakasir.com/api/create-transaction"
    Payload = {
        "project": PakasirApiData["ProjectSlug"],
        "api_key": PakasirApiData["ApiKey"],
        "order_id": IdPesanan,
        "amount": NominalHarusDibayar,
        "payment_method": "qris"
    }

    await callback_query.edit_message_text("<blockquote><b>🔄 ꜱᴇᴅᴀɴɢ ᴍᴇɴɢɢᴇɴᴇʀᴀᴛᴇ ǫʀɪꜱ ᴘᴇᴍʙᴀʏᴀʀᴀɴ...</b></blockquote>")

    async with aiohttp.ClientSession() as Sesi:
        async with Sesi.post(UrlBuatQris, data=Payload) as Respon:
            DataQris = await Respon.json()
            LinkQris = DataQris.get("data", {}).get("qr_image")
            if not LinkQris:
                return await callback_query.edit_message_text("<blockquote><b>❌ ɢᴀɢᴀʟ ᴍᴇɴɢᴀᴍʙɪʟ ǫʀɪꜱ. ᴄᴏʙᴀ ʟᴀɢɪ ɴᴀɴᴛɪ!</b></blockquote>")

    TeksBayar = (
        f"<blockquote><b>💳 ɪɴꜰᴏʀᴍᴀꜱɪ ᴘᴇᴍʙᴀʏᴀʀᴀɴ\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🛒 ᴘʀᴏᴅᴜᴋ: {RoleDipesan.upper()}\n"
        f"🗓️ ᴅᴜʀᴀꜱɪ: {'1 ʙᴜʟᴀɴ' if DurasiDipesan == '1' else 'ᴘᴇʀᴍᴀɴᴇɴ'}\n"
        f"💰 ᴛᴏᴛᴀʟ ʙᴀʏᴀʀ: ʀᴘ {NominalHarusDibayar:,}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💡 ꜱɪʟᴀʜᴋᴀɴ ꜱᴄᴀɴ ǫʀɪꜱ ᴅɪ ᴀᴛᴀꜱ. ꜱᴇᴛᴇʟᴀʜ ʙᴀʏᴀʀ, ᴛᴜɴɢɢᴜ 30 ᴅᴇᴛɪᴋ ʟᴀʟᴜ ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ.</b></blockquote>"
    )
    
    Tombol = [[InlineKeyboardButton("✅ ᴄᴇᴋ ᴘᴇᴍʙᴀʏᴀʀᴀɴ", callback_data=f"cek_bayar {IdPesanan} {RoleDipesan} {DurasiDipesan}")]]
    await bot.send_photo(UserId, photo=LinkQris, caption=TeksBayar, reply_markup=InlineKeyboardMarkup(Tombol))

@bot.on_callback_query(filters.regex("^cek_bayar"))
async def ProsesVerifikasiPembayaran(client, callback_query):
    DataQuery = callback_query.data.split()
    UserId = callback_query.from_user.id
    NamaUser = callback_query.from_user.first_name

    IdPesanan = DataQuery[1]
    RoleDipesan = DataQuery[2]
    DurasiDipesan = DataQuery[3]

    # 1. ʜɪᴛᴜɴɢ ᴜʟᴀɴɢ ꜱᴇʟɪꜱɪʜ ᴜɴᴛᴜᴋ ᴠᴇʀɪꜰɪᴋᴀꜱɪ
    Potongan = 0
    if await is_vars(client.me.id, "ALLROLE_USERS", UserId): Potongan = HargaAsli["founder"][DurasiDipesan]
    elif await is_vars(client.me.id, "CIOGWMAH_USERS", UserId): Potongan = HargaAsli["ceo"][DurasiDipesan]
    elif await is_vars(client.me.id, "KHASJIR_USERS", UserId): Potongan = HargaAsli["tk"][DurasiDipesan]
    elif await is_vars(client.me.id, "OWNER_USERS", UserId): Potongan = HargaAsli["owner"][DurasiDipesan]
    elif await is_vars(client.me.id, "ADMIN_USERS", UserId): Potongan = HargaAsli["admin"][DurasiDipesan]
    elif await is_vars(client.me.id, "SELER_USERS", UserId): Potongan = HargaAsli["seles"][DurasiDipesan]
    elif await is_vars(client.me.id, "PREM_USERS", UserId): Potongan = HargaAsli["member"][DurasiDipesan]

    HargaTarget = HargaAsli.get(RoleDipesan, {}).get(DurasiDipesan, 0)
    NominalHarusDibayar = HargaTarget - Potongan

    # 2. ᴄᴇᴋ ᴋᴇ ᴘᴀᴋᴀꜱɪʀ
    ApakahLunas = await CekStatusBayarPakasir(IdPesanan, NominalHarusDibayar)

    if not ApakahLunas:
        return await callback_query.answer("❌ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʟᴜᴍ ᴛᴇʀᴅᴇᴛᴇᴋꜱɪ!", show_alert=True)

    # 3. ᴘʀᴏꜱᴇꜱ ɪɴᴘᴜᴛ ᴅᴀᴛᴀʙᴀꜱᴇ
    ListRoleSistem = ["PREM_USERS", "SELER_USERS", "ADMIN_USERS", "OWNER_USERS", "KHASJIR_USERS", "CIOGWMAH_USERS", "ALLROLE_USERS"]
    HierarkiRank = {"member": 1, "seles": 2, "admin": 3, "owner": 4, "tk": 5, "ceo": 6, "founder": 7}
    TargetLevel = HierarkiRank.get(RoleDipesan, 1)

    for i in range(TargetLevel):
        try: await add_to_vars(client.me.id, ListRoleSistem[i], UserId)
        except: continue

    ZonaWaktu = timezone("Asia/Jakarta")
    WaktuSekarang = datetime.now(ZonaWaktu)
    TeksMasaAktif = "1 ʙᴜʟᴀɴ" if DurasiDipesan == "1" else "ᴘᴇʀᴍᴀɴᴇɴ"
    TanggalExpired = WaktuSekarang + (relativedelta(months=1) if DurasiDipesan == "1" else relativedelta(years=100))
    await set_expired_date(UserId, TanggalExpired)

    # 4. ɴᴏᴛɪꜰɪᴋᴀꜱɪ ꜱᴜᴋꜱᴇꜱ ᴜꜱᴇʀ (ꜱᴍᴀʟʟᴄᴀᴘꜱ & ʙʟᴏᴄᴋǫᴜᴏᴛᴇ)
    TeksSuksesUser = (
        f"<blockquote><b>✅ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʀʜᴀꜱɪʟ!\n\n"
        f"💎 ʀᴏʟᴇ: {RoleDipesan.upper()}\n"
        f"🗓️ ᴍᴀꜱᴀ ᴀᴋᴛɪғ: {TeksMasaAktif.upper()}\n\n"
        f"ꜱᴇᴋᴀʀᴀɴɢ ᴀɴᴅᴀ ʙɪꜱᴀ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ ᴅᴇɴɢᴀɴ ᴍᴇɴᴇᴋᴀɴ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ!</b>"
    )
    if not (RoleDipesan.lower() == "member" and DurasiDipesan == "1"):
        TeksSuksesUser += (
            f"\n\n<b>🔗 ꜱɪʟᴀʜᴋᴀɴ ᴍᴀꜱᴜᴋ ɢʀᴜᴘ ʙᴇʀɪᴋᴜᴛ: https://t.me/+OeAeHyyFyAw2MjRl</b>\n"
            f"<b>💬 ᴅɪᴍᴏʜᴏɴ ᴜɴᴛᴜᴋ ᴀᴅᴅʙʟ ᴅᴀɴ ꜱᴇʙᴜᴛ ʀᴏʟᴇ ᴅᴀɴ ᴛᴀɢ ᴀᴅᴍɪɴ ᴜᴛᴀᴍᴀ!</b>"
        )
    TeksSuksesUser += "</blockquote>"
    await bot.send_message(UserId, TeksSuksesUser, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 ʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ ꜱᴇᴋᴀʀᴀɴɢ", callback_data="add_ubot")]]))

    # 5. ʟᴏɢ ᴄʜᴀɴɴᴇʟ & ᴘᴍ ᴏᴡɴᴇʀ
    WaktuFormatStruk = WaktuSekarang.strftime("%A, %d %B %Y %H:%M WIB")
    for Eng, Indo in {'Monday':'𝗦𝗲𝗻𝗶𝗻','Tuesday':'𝗦𝗲𝗹𝗮𝘀𝗮','Wednesday':'𝗥𝗮𝗯𝘂','Thursday':'𝗞𝗮𝗺𝗶𝘀','Friday':'𝗝𝘂𝗺𝗮𝘁','Saturday':'𝗦𝗮𝗯𝘁𝘂','Sunday':'𝗠𝗶𝗻𝗴𝗴𝘂'}.items():
        WaktuFormatStruk = WaktuFormatStruk.replace(Eng, Indo)

    TeksCaptionLog = (
        f"<blockquote>"
        f"📜 <b>𝗦𝗧𝗥𝗨𝗞 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 𝗣𝗥𝗢𝗗𝗨𝗞</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━❍\n"
        f"🪪 <b>𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗔𝗦 𝗣𝗘𝗠𝗕𝗘𝗟𝗜</b>\n"
        f"├⌑ 👤 <b>𝗡𝗮𝗺𝗮 : {NamaUser}</b>\n"
        f"╰⌑ 🆔 <b>𝗜𝗗 : <code>{UserId}</code></b>\n\n"
        f"🎀 <b>𝗗𝗔𝗧𝗔 𝗣𝗥𝗢𝗗𝗨𝗞</b>\n"
        f"├⌑ 🛒 <b>𝗣𝗿𝗼𝗱𝘂𝗸 : {RoleDipesan.upper()} ({TeksMasaAktif.upper()})</b>\n"
        f"├⌑ 💰 <b>𝗛𝗮𝗿𝗴𝗮 : 𝗥𝗽 {NominalHarusDibayar:,}</b>\n"
        f"╰⌑ ⏰ <b>𝗪𝗮𝗸𝘁𝘂 : {WaktuFormatStruk}</b>\n\n"
        f"📨 <b>𝗧𝗲𝗿𝗶𝗺𝗮𝗸𝗮𝘀𝗶𝗵 𝗦𝘂𝗱𝗮𝗵 𝗕𝗲𝗹𝗮𝗻𝗷𝗮</b>\n"
        f"</blockquote>"
    )
    try: await bot.send_photo(chat_id=IdChannelLogTransaksi, photo="https://files.catbox.moe/wrnyvx.jpg", caption=TeksCaptionLog)
    except: pass

    TeksCaptionOwner = (
        f"<blockquote>"
        f"<b>🔔 ʟᴀᴘᴏʀᴀɴ ᴘᴇɴᴊᴜᴀʟᴀɴ (ᴘᴍ)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>ᴘᴇᴍʙᴇʟɪ: {NamaUser}</b>\n"
        f"🆔 <b>ɪᴅ: <code>{UserId}</code></b>\n"
        f"🛒 <b>ᴘʀᴏᴅᴜᴋ: {RoleDipesan.upper()} - {TeksMasaAktif.upper()}</b>\n"
        f"💰 <b>ɴᴏᴍɪɴᴀʟ: ʀᴘ {NominalHarusDibayar:,}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <i>ꜱᴜᴅᴀʜ ᴏᴛᴏᴍᴀᴛɪꜱ ᴛᴇʀ-ɪɴᴘᴜᴛ ᴋᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.</i>"
        f"</blockquote>"
    )
    try: await bot.send_message(chat_id=5170517638, text=TeksCaptionOwner)
    except: pass
    