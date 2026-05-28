import asyncio
from datetime import datetime
from PyroUbot import *

__MODULE__ = "ᴅᴏɴᴇ"
__HELP__ = """
<blockquote><b>Bantuan Done</b>

• Perintah :
<code>{0}done</code> nama_barang,harga,pembayaran

• Fungsi :
Konfirmasi transaksi selesai</blockquote>
"""

# ===== SYSTEM TRX ID (FILE BASED) =====
def get_trx_id():
    try:
        with open("trx_id.txt", "r") as f:
            last_id = int(f.read().strip())
    except:
        last_id = 0

    new_id = last_id + 1

    with open("trx_id.txt", "w") as f:
        f.write(str(new_id))

    return f"TRX-{new_id}"


@PY.UBOT("done")
@PY.UBOT("d")
async def done_cmd(client, message):
    proses = await message.reply("<blockquote>⏳ Memproses transaksi...</blockquote>")
    await asyncio.sleep(3)

    try:
        args = message.text.split(" ", 1)
        if len(args) < 2:
            return await proses.edit(
                "<blockquote>❌ Format salah\nContoh:\n<code>.done Seles Ubot Perma,5000,QRIS</code></blockquote>"
            )

        data = args[1].split(",", 2)
        if len(data) < 2:
            return await proses.edit("<blockquote>❌ Data tidak lengkap</blockquote>")

        produk = data[0].strip()
        harga = data[1].strip()
        payment = data[2].strip() if len(data) > 2 else "Lainnya"

        waktu = datetime.now().strftime("%Y-%m-%d %H:%M")
        trx_id = get_trx_id()

        text = f"""
<blockquote>
『 <b>Transaction Successfull </b> 』
━━━━━━━━━━━━━━━
📦 <b>Produk :</b> {produk}
💰 <b>Harga :</b> Rp{harga}
💳 <b>Pembayaran :</b> {payment}
🕒 <b>Waktu :</b> {waktu}
🧾 <b>Nomor TRX :</b> {trx_id}
✅ <b>Status :</b> Tercatat & Selesai!
━━━━━━━━━━━━━━━
👤 <b>Owner :</b> @{client.me.username}
━━━━━━━━━━━━━━━
✨ <b>Terima Kasih Telah Bertransaksi ✨ !</b>
</blockquote>
"""

        await proses.edit(text)

    except Exception as e:
        await proses.edit(f"<blockquote>❌ Error : {e}</blockquote>")