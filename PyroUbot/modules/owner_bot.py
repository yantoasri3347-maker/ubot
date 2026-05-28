from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pytz import timezone
from PyroUbot.config import OWNER_ID
from PyroUbot import *

@PY.UBOT("addowner")
async def _(client, message):
    user = message.from_user

    if not await khasjir(user.id):
        return

    msg = await message.reply("𝖨𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗌")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} 𝗎𝗌𝖾𝗋_𝗂𝖽/𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗋𝖾𝗉𝗅𝗒</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    owner_users = await get_list_from_vars(bot.me.id, "OWNER_USERS")

    if target.id in owner_users:
        return await msg.edit(f"""
<blockquote><b>𝖨𝖭𝖥𝖮𝖱𝖬𝖠𝖳𝖨𝖮𝖭</b>
𝖭𝖺𝗆𝖺: {target.mention}
𝖨𝖣: <code>{target.id}</code>
𝖪𝖾𝗍𝖾𝗋𝖺𝗇𝗀𝖺𝗇: 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖡𝖾𝖼𝗈𝗆𝖾 𝖺𝗇 𝖮𝗐𝗇𝖾𝗋</blockquote>
""")

    try:
        await add_to_vars(bot.me.id, "OWNER_USERS", target.id)
    except Exception as error:
        return await msg.edit(str(error))

    await msg.edit(f"""
<blockquote><b>𝖨𝖭𝖥𝖮𝖱𝖬𝖠𝖳𝖨𝖮𝖭</b>
𝖭𝖺𝗆𝖺: {target.mention}
𝖨𝖣: <code>{target.id}</code>
𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖠𝖽𝖽 𝖮𝗐𝗇𝖾𝗋</blockquote>
""")

    await bot.send_message(
        OWNER_ID,
        f"• ɪᴅ-ᴛᴀɴɢᴀɴᴋᴀɴᴀɴ: `{user.id}`\n"
        f"• ɪᴅ-ᴏᴡɴᴇʀ: `{target.id}`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👑 𝚃𝙰𝙽𝙶𝙰𝙽 𝙺𝙰𝙽𝙰𝙽",
                        callback_data=f"profil {user.id}",
                    ),
                    InlineKeyboardButton(
                        "🛡 𝙾𝚆𝙽𝙴𝚁",
                        callback_data=f"profil {target.id}",
                    ),
                ]
            ]
        ),
    )

@PY.UBOT("delowner")
async def _(client, message):
    user = message.from_user
    if not await khasjir(user.id):
        return

    msg = await message.reply("𝖨𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗌")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} 𝗎𝗌𝖾𝗋_𝗂𝖽/𝗎𝗌𝖾𝗋𝗇𝖺𝗆𝖾/𝗋𝖾𝗉𝗅𝗒</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    owner_users = await get_list_from_vars(bot.me.id, "OWNER_USERS")

    if target.id not in owner_users:
        return await msg.edit("𝖴𝗌𝖾𝗋 𝖭𝗈𝗍 𝖮𝗐𝗇𝖾𝗋")

    try:
        await remove_from_vars(bot.me.id, "OWNER_USERS", target.id)
        return await msg.edit(f"""
<blockquote><b>𝖨𝖭𝖥𝖮𝖱𝖬𝖠𝖳𝖨𝖮𝖭</b>
𝖭𝖺𝗆𝖺: {target.mention}
𝖨𝖣: <code>{target.id}</code>
𝖲𝗍𝖺𝗍𝗎𝗌: 𝖲𝗎𝖼𝖼𝖾𝗌𝗌𝖿𝗎𝗅𝗅𝗒 𝖱𝖾𝗆𝗈𝗏𝖾𝖽 𝖥𝗋𝗈𝗆 𝖮𝗐𝗇𝖾𝗋</blockquote>
""")
    except Exception as error:
        return await msg.edit(str(error))
        
@PY.UBOT("getowner")
async def _(client, message):
    user = message.from_user
    if not await khasjir(user.id):
        return
    Sh = await message.reply("𝖨𝗇 𝗉𝗋𝗈𝖼𝖾𝗌𝗌")
    owner_users = await get_list_from_vars(bot.me.id, "OWNER_USERS")

    if not owner_users:
        return await Sh.edit("𝖤𝗆𝗉𝗍𝗒 𝖮𝗐𝗇𝖾𝗋 𝖫𝗂𝗌𝗍")

    owner_list = []
    for user_id in owner_users:
        try:
            user = await client.get_users(int(user_id))
            owner_list.append(
                f"<blockquote>👤 [{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) | `{user.id}`</blockquote>"
            )
        except:
            continue

    if owner_list:
        response = (
            "📋 ᴅᴀꜰᴛᴀʀ ᴏᴡɴᴇʀ:\n\n"
            + "\n".join(owner_list)
            + f"\n\n• ᴛᴏᴛᴀʟ ᴏᴡɴᴇʀ: {len(owner_list)}"
        )
        return await Sh.edit(response)
    else:
        return await Sh.edit("ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀꜰᴛᴀʀ ᴏᴡɴᴇʀ")
        
# FUNC TAMBAHAN

async def is_owner(user_id: int):
    if user_id == OWNER_ID:
        return True
    owner_users = await get_list_from_vars(bot.me.id, "OWNER_USERS")
    return user_id in owner_users
    
async def khasjir(user_id: int):
    if user_id == OWNER_ID:
        return True
    khasjir_users = await get_list_from_vars(bot.me.id, "KHASJIR_USERS")
    return user_id in khasjir_users
    
async def ciogwmah(user_id: int):
    if user_id == OWNER_ID:
        return True
    ciogwmah_users = await get_list_from_vars(bot.me.id, "CIOGWMAH_USERS")
    return user_id in ciogwmah_users
    
async def allrole(user_id: int):
    if user_id == OWNER_ID:
        return True
    allrole_users = await get_list_from_vars(bot.me.id, "ALLROLE_USERS")
    return user_id in allrole_users
    
@PY.UBOT("addtk")
async def _(client, message):
    user = message.from_user

    if not await ciogwmah(user.id):
        return

    msg = await message.reply("Sedang Memproses...")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} user_id/username</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    khasjir_users = await get_list_from_vars(bot.me.id, "KHASJIR_USERS")

    if target.id in khasjir_users:
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Keterangan: </blockquote>
""")

    try:
        await add_to_vars(bot.me.id, "KHASJIR_USERS", target.id)
    except Exception as error:
        return await msg.edit(str(error))

    # PESAN SUKSES
    await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Status: Sukses Add TK</blockquote>
""")

    await bot.send_message(
        OWNER_ID,
        f"• ɪᴅ-ᴄɪᴏ: `{user.id}`\n"
        f"• ɪᴅ-ᴛᴀɴɢᴀɴᴋᴀɴᴀɴ: `{target.id}`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👑 CIO",
                        callback_data=f"profil {user.id}",
                    ),
                    InlineKeyboardButton(
                        "🛡 TANGANKANAN",
                        callback_data=f"profil {target.id}",
                    ),
                ]
            ]
        ),
    )

@PY.UBOT("deltk")
async def _(client, message):
    user = message.from_user
    if not await ciogwmah(user.id):
        return

    msg = await message.reply("Sedang Memproses...")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} user_id/username</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    khasjir_users = await get_list_from_vars(bot.me.id, "KHASJIR_USERS")

    if target.id not in khasjir_users:
        return await msg.edit("User Bukan TK")

    try:
        await remove_from_vars(bot.me.id, "KHASJIR_USERS", target.id)
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Status: Sukses Dihapus Dari TK</blockquote>
""")
    except Exception as error:
        return await msg.edit(str(error))
        
@PY.UBOT("gettk")
async def _(client, message):
    user = message.from_user
    if not await ciogwmah(user.id):
        return
    Sh = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")
    khasjir_users = await get_list_from_vars(bot.me.id, "KHASJIR_USERS")

    if not khasjir_users:
        return await Sh.edit("ᴅᴀꜰᴛᴀʀ ᴛᴀɴɢᴀɴ ᴋᴀɴᴀɴ ᴋᴏꜱᴏɴɢ")

    khasjir_list = []
    for user_id in khasjir_users:
        try:
            user = await client.get_users(int(user_id))
            khasjir_list.append(
                f"<blockquote>👤 [{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) | `{user.id}`</blockquote>"
            )
        except:
            continue

    if khasjir_list:
        response = (
            "📋 ᴅᴀꜰᴛᴀʀ ᴛᴀɴɢᴀɴ ᴋᴀɴᴀɴ:\n\n"
            + "\n".join(khasjir_list)
            + f"\n\n• ᴛᴏᴛᴀʟ ᴛᴀɴɢᴀɴ ᴋᴀɴᴀɴ: {len(khasjir_list)}"
        )
        return await Sh.edit(response)
    else:
        return await Sh.edit("ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀꜰᴛᴀʀ ᴛᴀɴɢᴀɴ ᴋᴀɴᴀɴ")
        
@PY.UBOT("addcio")
async def _(client, message):
    user = message.from_user

    if not await allrole(user.id):
        return

    msg = await message.reply("Sedang Memproses...")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} user_id/username</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    ciogwmah_users = await get_list_from_vars(bot.me.id, "CIOGWMAH_USERS")

    if target.id in ciogwmah_users:
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Keterangan: Sudah Jadi Ceo</blockquote>
""")

    try:
        await add_to_vars(bot.me.id, "CIOGWMAH_USERS", target.id)
    except Exception as error:
        return await msg.edit(str(error))

    # PESAN SUKSES
    await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Status: Sukses Add Ceo</blockquote>
""")

    await bot.send_message(
        OWNER_ID,
        f"• ɪᴅ-ᴀʟʟʀᴏʟᴇ: `{user.id}`\n"
        f"• ɪᴅ-ᴄɪᴏ: `{target.id}`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👑 ALLROLE",
                        callback_data=f"profil {user.id}",
                    ),
                    InlineKeyboardButton(
                        "🛡 CIO",
                        callback_data=f"profil {target.id}",
                    ),
                ]
            ]
        ),
    )

@PY.UBOT("delcio")
async def _(client, message):
    user = message.from_user
    if not await allrole(user.id):
        return

    msg = await message.reply("Sedang Memproses...")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} user_id/username</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    ciogwmah_users = await get_list_from_vars(bot.me.id, "CIOGWMAH_USERS")

    if target.id not in ciogwmah_users:
        return await msg.edit("User Bukan Ceo")

    try:
        await remove_from_vars(bot.me.id, "CIOGWMAH_USERS", target.id)
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Status: Dihapus Dari Ceo</blockquote>
""")
    except Exception as error:
        return await msg.edit(str(error))
        
@PY.UBOT("getcio")
async def _(client, message):
    user = message.from_user
    if not await allrole(user.id):
        return
    Sh = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")
    ciogwmah_users = await get_list_from_vars(bot.me.id, "CIOGWMAH_USERS")

    if not ciogwmah_users:
        return await Sh.edit("ᴅᴀꜰᴛᴀʀ ᴄɪᴏ ᴋᴏsᴏɴɢ")

    ciogwmah_list = []
    for user_id in ciogwmah_users:
        try:
            user = await client.get_users(int(user_id))
            ciogwmah_list.append(
                f"<blockquote>👤 [{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) | `{user.id}`</blockquote>"
            )
        except:
            continue

    if ciogwmah_list:
        response = (
            "📋 ᴅᴀꜰᴛᴀʀ ᴄɪᴏ:\n\n"
            + "\n".join(ciogwmah_list)
            + f"\n\n• ᴛᴏᴛᴀʟ ᴄɪᴏ: {len(ciogwmah_list)}"
        )
        return await Sh.edit(response)
    else:
        return await Sh.edit("ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀꜰᴛᴀʀ ᴄɪᴏ")

@PY.UBOT("allrole")
async def _(client, message):
    user = message.from_user

    if user.id != OWNER_ID:
        return

    msg = await message.reply("Sedang Memproses...")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} user_id/username</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    allrole_users = await get_list_from_vars(bot.me.id, "ALLROLE_USERS")

    if target.id in allrole_users:
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Keterangan: Sudah Jadi Allrole</blockquote>
""")

    try:
        await add_to_vars(bot.me.id, "ALLROLE_USERS", target.id)
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Status: Sukses Add Allrole</blockquote>
""")
    except Exception as error:
        return await msg.edit(str(error))
 
@PY.UBOT("delallrole")
async def _(client, message):
    user = message.from_user
    if user.id != OWNER_ID:
        return

    msg = await message.reply("Sedang Memproses...")
    user_id = await extract_user(message)

    if not user_id:
        return await msg.edit(f"<b>{message.text} user_id/username</b>")

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    allrole_users = await get_list_from_vars(bot.me.id, "ALLROLE_USERS")

    if target.id not in allrole_users:
        return await msg.edit("User Bukan Allrole")

    try:
        await remove_from_vars(bot.me.id, "ALLROLE_USERS", target.id)
        return await msg.edit(f"""
<blockquote><b>INFORMATION</b>
Nama: {target.mention}
ID: <code>{target.id}</code>
Status: Sukses Dihapus Dari Allrole</blockquote>
""")
    except Exception as error:
        return await msg.edit(str(error))
        
@PY.UBOT("getallrole")
async def _(client, message):
    user = message.from_user
    if user.id != OWNER_ID:
        return
    Sh = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")
    allrole_users = await get_list_from_vars(bot.me.id, "ALLROLE_USERS")

    if not allrole_users:
        return await Sh.edit("ᴅᴀꜰᴛᴀʀ ᴀʟʟʀᴏʟᴇ ᴋᴏsᴏɴɢ")

    allrole_list = []
    for user_id in allrole_users:
        try:
            user = await client.get_users(int(user_id))
            allrole_list.append(
                f"<blockquote>👤 [{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) | `{user.id}`</blockquote>"
            )
        except:
            continue

    if allrole_list:
        response = (
            "📋 ᴅᴀꜰᴛᴀʀ ᴀʟʟʀᴏʟᴇ:\n\n"
            + "\n".join(allrole_list)
            + f"\n\n• ᴛᴏᴛᴀʟ ᴀʟʟʀᴏʟᴇ: {len(allrole_list)}"
        )
        return await Sh.edit(response)
    else:
        return await Sh.edit("ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀꜰᴛᴀʀ ᴀʟʟʀᴏʟᴇ")

@PY.UBOT("prem")
async def _(client, message):
    user = message.from_user
    seller_id = await get_list_from_vars(bot.me.id, "SELER_USERS")
    if user.id not in seller_id:
        return
    user_id, get_bulan = await extract_user_and_reason(message)
    msg = await message.reply("memproses...")
    if not user_id:
        return await msg.edit(f"<b>{message.text} ᴜsᴇʀ_ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ - ʙᴜʟᴀɴ</b>")

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(error)
    if not get_bulan:
        get_bulan = 1

    prem_users = await get_list_from_vars(bot.me.id, "PREM_USERS")

    if user.id in prem_users:
        return await msg.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>ɪᴅ: `{user.id}`</b>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ: Sudah Premium</ci></b>
<b>ᴇxᴘɪʀᴇᴅ: {get_bulan} ʙᴜʟᴀɴ</b></blockquote>
"""
        )

    try:
        now = datetime.now(timezone("Asia/Jakarta"))
        expired = now + relativedelta(months=int(get_bulan))
        await set_expired_date(user_id, expired)
        await add_to_vars(bot.me.id, "PREM_USERS", user.id)
        await msg.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>ɪᴅ: `{user.id}`</b>
<b>ᴇxᴘɪʀᴇᴅ: {get_bulan} ʙᴜʟᴀɴ</b>
<b>ꜱɪʟᴀʜᴋᴀɴ ʙᴜᴋᴀ @putraganaubot_bot ᴜɴᴛᴜᴋ ᴍᴇᴍʙᴜᴀᴛ ᴜꜱᴇʀʙᴏᴛ</b></blockquote>

<blockquote>ᴄᴀʀᴀ ʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ :
- sɪʟᴀʜᴋᴀɴ /start ᴅᴜʟᴜ ʙᴏᴛ @putraganaubot_bot 
- ᴋᴀʟᴀᴜ sᴜᴅᴀʜ sᴛᴀʀᴛ ʙᴏᴛ ᴀʙɪsᴛᴜ ᴘᴇɴᴄᴇᴛ ᴛᴏᴍʙᴏʟ ʙᴜᴀᴛ ᴜsᴇʀʙᴏᴛ 
- ɴᴀʜ ɴᴀɴᴛɪ ᴀᴅᴀ ᴀʀᴀʜᴀɴ ᴅᴀʀɪ ʙᴏᴛ ɴʏᴀ ɪᴛᴜ ɪᴋᴜᴛɪɴ</blockquote>
<blockquote><b>ɴᴏᴛᴇ : ᴊᴀɴɢᴀɴ ʟᴜᴘᴀ ʙᴀᴄᴀ ᴀʀᴀʜᴀɴ ᴅᴀʀɪ ʙᴏᴛ ɴʏᴀ</b></blockquote>
"""
        )
        return await bot.send_message(
            OWNER_ID,
            f"• ɪᴅ-ꜱᴇʟʟᴇʀ: `{message.from_user.id}`\n\n• ɪᴅ-ᴄᴜꜱᴛᴏᴍᴇʀ: `{user_id}`",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⁉️ ꜱᴇʟʟᴇʀ",
                            callback_data=f"profil {message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            "ᴄᴜꜱᴛᴏᴍᴇʀ ⁉️", callback_data=f"profil {user_id}"
                        ),
                    ],
                ]
            ),
        )
    except Exception as error:
        return await msg.edit(error)


@PY.UBOT("unprem")
async def _(client, message):
    msg = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"<b>{message.text} ᴜsᴇʀ_ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ</b>"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(error)

    prem_users = await get_list_from_vars(bot.me.id, "PREM_USERS")

    if user.id not in prem_users:
        return await msg.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>ɪᴅ: `{user.id}`</b>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ: ᴛɪᴅᴀᴋ ᴛᴇʀᴅᴀꜰᴛᴀʀ</ci></b></blockquote>
"""
        )
    try:
        await remove_from_vars(bot.me.id, "PREM_USERS", user.id)
        await rem_expired_date(user_id)
        return await msg.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>ɪᴅ: `{user.id}`</b>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ: ᴛᴇʟᴀʜ ᴅɪ ʜᴀᴘᴜꜱ ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀꜱᴇ</ci></b></blockquote>
"""
        )
    except Exception as error:
        return await msg.edit(error)
        

@PY.UBOT("getprem")
async def _(client, message):
    text = ""
    count = 0
    user = message.from_user
    seller_id = await get_list_from_vars(bot.me.id, "SELER_USERS")
    if user.id not in seller_id:
        return
    prem = await get_list_from_vars(bot.me.id, "PREM_USERS")
    prem_users = []

    for user_id in prem:
        try:
            user = await bot.get_users(user_id)
            count += 1
            userlist = f"• {count}: <a href=tg://user?id={user.id}>{user.first_name} {user.last_name or ''}</a> > <code>{user.id}</code>"
        except Exception:
            continue
        text += f"<blockquote><b>{userlist}\n</blockquote></b>"
    if not text:
        await message.reply_text("ᴛɪᴅᴀᴋ ᴀᴅᴀ ᴘᴇɴɢɢᴜɴᴀ ʏᴀɴɢ ᴅɪᴛᴇᴍᴜᴋᴀɴ")
    else:
        await message.reply_text(text)


@PY.UBOT("seles")
async def _(client, message):
    user = message.from_user
    admin_users = await get_list_from_vars(bot.me.id, "ADMIN_USERS")

    if user.id not in admin_users:
        return

    msg = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")

    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"<b>{message.text} ᴜsᴇʀ_ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ</b>"
        )

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    seles_users = await get_list_from_vars(bot.me.id, "SELER_USERS")

    if target.id in seles_users:
        return await msg.edit(
            f"""
<blockquote><b>ɴᴀᴍᴇ:</b> [{target.first_name} {target.last_name or ''}](tg://user?id={target.id})
<b>ɪᴅ:</b> `{target.id}`
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ:</b> ꜱᴜᴅᴀʜ ʀᴇꜱᴇʟʟᴇʀ</blockquote>
"""
        )

    try:
        # TAMBAH KE VARS
        await add_to_vars(bot.me.id, "SELER_USERS", target.id)

        # EDIT PESAN ADMIN
        await msg.edit(
            f"""
<blockquote><b>ɴᴀᴍᴇ:</b> [{target.first_name} {target.last_name or ''}](tg://user?id={target.id})
<b>ɪᴅ:</b> `{target.id}`
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ:</b> ʀᴇꜱᴇʟʟᴇʀ
<b>ꜱɪʟᴀʜᴋᴀɴ ʙᴜᴋᴀ @{bot.me.username}</b></blockquote>
"""
        )

        # KIRIM LOG KE OWNER
        await bot.send_message(
            OWNER_ID,
            f"• ɪᴅ-ᴀᴅᴍɪɴ: `{message.from_user.id}`\n"
            f"• ɪᴅ-sᴇʟᴇs: `{target.id}`",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "⁉️ ᴀᴅᴍɪɴ",
                            callback_data=f"profil {message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            "sᴇʟᴇs ⁉️",
                            callback_data=f"profil {target.id}",
                        ),
                    ]
                ]
            ),
        )

    except Exception as error:
        return await msg.edit(str(error))

@PY.UBOT("unseles")
async def _(client, message):
    user = message.from_user
    admin_users = await get_list_from_vars(bot.me.id, "ADMIN_USERS")
    if user.id not in admin_users:
        return
    msg = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"<b>{message.text} ᴜsᴇʀ_ɪᴅ/ᴜsᴇʀɴᴀᴍᴇ</b>"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(error)

    seles_users = await get_list_from_vars(bot.me.id, "SELER_USERS")

    if user.id not in seles_users:
        return await msg.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>ɪᴅ: `{user.id}`</b>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ: ᴛɪᴅᴀᴋ ᴛᴇʀᴅᴀꜰᴛᴀʀ</ci></b></blockquote>
"""
        )

    try:
        await remove_from_vars(bot.me.id, "SELER_USERS", user.id)
        return await msg.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>ɪᴅ: `{user.id}`</b>
<b>ᴋᴇᴛᴇʀᴀɴɢᴀɴ: ᴛᴇʟᴀʜ ᴅɪ ʜᴀᴘᴜꜱ ᴅᴀʀɪ ᴅᴀᴛᴀʙᴀꜱᴇ</ci></b></blockquote>
"""
        )
    except Exception as error:
        return await msg.edit(error)


@PY.UBOT("getseles")
async def _(client, message):
    user = message.from_user
    admin_users = await get_list_from_vars(bot.me.id, "ADMIN_USERS")
    if user.id not in admin_users:
        return
    Sh = await message.reply("ꜱᴇᴅᴀɴɢ ᴍᴇᴍᴘʀᴏꜱᴇꜱ...")
    seles_users = await get_list_from_vars(bot.me.id, "SELER_USERS")

    if not seles_users:
        return await Sh.edit("ᴅᴀꜰᴛᴀʀ ꜱᴇʟʟᴇʀ ᴋᴏꜱᴏɴɢ")

    seles_list = []
    for user_id in seles_users:
        try:
            user = await client.get_users(int(user_id))
            seles_list.append(
                f"<blockquote>👤 [{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) | `{user.id}`</blockquote>"
            )
        except:
            continue

    if seles_list:
        response = (
            "📋 ᴅᴀꜰᴛᴀʀ ʀᴇꜱᴇʟʟᴇʀ:\n\n"
            + "\n".join(seles_list)
            + f"\n\n• ᴛᴏᴛᴀʟ ʀᴇꜱᴇʟʟᴇʀ: {len(seles_list)}"
        )
        return await Sh.edit(response)
    else:
        return await Sh.edit("ᴛɪᴅᴀᴋ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴍʙɪʟ ᴅᴀꜰᴛᴀʀ ꜱᴇʟʟᴇʀ")


@PY.UBOT("time")
async def _(client, message):
    user = message.from_user
    if user.id != OWNER_ID:
        return
    Tm = await message.reply("processing . . .")
    bajingan = message.command
    if len(bajingan) != 3:
        return await Tm.edit(f"gunakan /set_time user_id hari")
    user_id = int(bajingan[1])
    get_day = int(bajingan[2])
    print(user_id , get_day)
    try:
        get_id = (await client.get_users(user_id)).id
        user = await client.get_users(user_id)
    except Exception as error:
        return await Tm.edit(error)
    if not get_day:
        get_day = 30
    now = datetime.now(timezone("Asia/Jakarta"))
    expire_date = now + timedelta(days=int(get_day))
    await set_expired_date(user_id, expire_date)
    await Tm.edit(f"""
💬 INFORMATION
 Nama: {user.mention}
 Id: {get_id}
 Aktifkan_Selama: {get_day} hari
"""
    )


@PY.UBOT("cek")
async def _(client, message):
    user = message.from_user
    if user.id != OWNER_ID:
        return
    Sh = await message.reply("ᴘʀᴏᴄᴇꜱꜱɪɴɢ . . .")
    user_id = await extract_user(message)
    if not user_id:
        return await Sh.edit("ᴘᴇɴɢɢᴜɴᴀ ᴛɪᴅᴀᴋ ᴛᴇᴍᴜᴋᴀɴ")
    try:
        get_exp = await get_expired_date(user_id)
        sh = await client.get_users(user_id)
    except Exception as error:
        return await Sh.ediit(error)
    if get_exp is None:
        await Sh.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: {sh.mention}</b>
<b>ɪᴅ: `{user_id}`</b>
<b>ᴘʟᴀɴ : ɴᴏɴᴇ</b>
<b>ᴘʀᴇꜰɪx : .</b>
<b>ᴇxᴘɪʀᴇᴅ : ɴᴏɴᴀᴋᴛɪꜰ</b></blockquote>
""")
    else:
        SH = await ubot.get_prefix(user_id)
        exp = get_exp.strftime("%d-%m-%Y")
        if user_id in await get_list_from_vars(bot.me.id, "ULTRA_PREM"):
            status = "SuperUltra"
        else:
            status = "Premium"
        await Sh.edit(f"""
<blockquote><b>ɴᴀᴍᴇ: {sh.mention}</b>
<b>ɪᴅ: `{user_id}`</b>
<b>ᴘʟᴀɴ : {status}</b>
<b>ᴘʀᴇꜰɪx : {' '.join(SH)}</b>
<b>ᴇxᴘɪʀᴇᴅ : {exp}</b></blockquote>
"""
        )


@PY.UBOT("addadmin")
async def _(client, message):
    user = message.from_user
    if not await is_owner(user.id):
        return

    msg = await message.reply("⏳ sedang memproses...")

    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"<b>{message.text} user_id/username</b>"
        )

    try:
        target = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(str(error))

    admin_users = await get_list_from_vars(bot.me.id, "ADMIN_USERS")

    # SUDAH ADMIN
    if target.id in admin_users:
        return await msg.edit(
            f"""
<blockquote><b>💬 INFORMATION</b>
<b>name:</b> [{target.first_name} {target.last_name or ''}](tg://user?id={target.id})
<b>id:</b> <code>{target.id}</code>
<b>keterangan:</b> sudah admin</blockquote>
"""
        )

    # TAMBAH ADMIN
    try:
        await add_to_vars(bot.me.id, "ADMIN_USERS", target.id)
    except Exception as error:
        return await msg.edit(str(error))

    # PESAN SUKSES
    await msg.edit(
        f"""
<blockquote><b>💬 INFORMATION</b>
<b>name:</b> [{target.first_name} {target.last_name or ''}](tg://user?id={target.id})
<b>id:</b> <code>{target.id}</code>
<b>keterangan:</b> admin berhasil ditambahkan</blockquote>
"""
    )

    # LOG KE OWNER
    await bot.send_message(
        OWNER_ID,
        f"• ɪᴅ-ᴏᴡɴᴇʀ: `{user.id}`\n"
        f"• ɪᴅ-ᴀᴅᴍɪɴ: `{target.id}`",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👑 OWNER",
                        callback_data=f"profil {user.id}",
                    ),
                    InlineKeyboardButton(
                        "🛡 ADMIN",
                        callback_data=f"profil {target.id}",
                    ),
                ]
            ]
        ),
    )


@PY.UBOT("unadmin")
async def _(client, message):
    user = message.from_user
    if not await is_owner(user.id):
        return
    msg = await message.reply("sedang memproses...")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"{message.text} user_id/username"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(error)

    admin_users = await get_list_from_vars(bot.me.id, "ADMIN_USERS")

    if user.id not in admin_users:
        return await msg.edit(f"""
<blockquote><b>💬 INFORMATION</b>
<bname: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>id: {user.id}</b>
<b>keterangan: tidak daam daftar</b></blockquote>
"""
        )

    try:
        await remove_from_vars(bot.me.id, "ADMIN_USERS", user.id)
        return await msg.edit(f"""
<blockquote><b>💬 INFORMATION</b>
<b>name: [{user.first_name} {user.last_name or ''}](tg://user?id={user.id})</b>
<b>id: {user.id}</b>
<b>keterangan: unadmin</b></blockquote>
"""
        )
    except Exception as error:
        return await msg.edit(error)


@PY.UBOT("getadmin")
async def _(client, message):
    user = message.from_user
    if not await is_owner(user.id):
        return
    Sh = await message.reply("sedang memproses...")
    admin_users = await get_list_from_vars(bot.me.id, "ADMIN_USERS")

    if not admin_users:
        return await Sh.edit("<s>daftar admin kosong</s>")

    admin_list = []
    for user_id in admin_users:
        try:
            user = await client.get_users(int(user_id))
            admin_list.append(
                f"👤 [{user.first_name} {user.last_name or ''}](tg://user?id={user.id}) | {user.id}"
            )
        except:
            continue

    if admin_list:
        response = (
            "📋 daftar admin:\n\n"
            + "\n".join(admin_list)
            + f"\n\n⚜️ total admin: {len(admin_list)}"
        )
        return await Sh.edit(response)
    else:
        return await Sh.edit("tidak dapat mengambil daftar admin")

@PY.UBOT("addultra")
async def _(client, message):
    prs = await EMO.PROSES(client)
    brhsl = await EMO.BERHASIL(client)
    ggl = await EMO.GAGAL(client)
    user = message.from_user
    if user.id != OWNER_ID:
        return await message.reply_text(f"{ggl}mau ngapain kamu ?")
    msg = await message.reply(f"{prs}sedang memproses...")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"{ggl}{message.text} user_id/username"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(error)

    ultra_users = await get_list_from_vars(bot.me.id, "ULTRA_PREM")

    if user.id in ultra_users:
        return await msg.edit(f"{ggl}sudah menjadi superultra!")

    try:
        await add_to_vars(bot.me.id, "ULTRA_PREM", user.id)
        return await msg.edit(f"{brhsl}berhasil menjadi superultra")
    except Exception as error:
        return await msg.edit(error)

@PY.UBOT("rmultra")
async def _(client, message):
    prs = await EMO.PROSES(client)
    brhsl = await EMO.BERHASIL(client)
    ggl = await EMO.GAGAL(client)
    user = message.from_user
    if user.id != OWNER_ID:
        return await message.reply_text(f"{ggl}mau ngapain kamu ?")
    msg = await message.reply(f"{prs}sedang memproses...")
    user_id = await extract_user(message)
    if not user_id:
        return await msg.edit(
            f"{ggl}{message.text} user_id/username"
        )

    try:
        user = await client.get_users(user_id)
    except Exception as error:
        return await msg.edit(error)

    ultra_users = await get_list_from_vars(bot.me.id, "ULTRA_PREM")

    if user.id not in ultra_users:
        return await msg.edit(f"{ggl}tidak ada di dalam database superultra")

    try:
        await remove_from_vars(bot.me.id, "ULTRA_PREM", user.id)
        return await msg.edit(f"{brhsl}berhasil di hapus dari daftar superultra")
    except Exception as error:
        return await msg.edit(error)
