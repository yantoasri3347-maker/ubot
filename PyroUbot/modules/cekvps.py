import psutil
import platform
from datetime import datetime
from PyroUbot import *

__MODULE__ = "ᴠᴘꜱ ɪɴꜰᴏ"
__HELP__ = """
<blockquote><b>Bantuan Untuk VPS Info</b>

Perintah:
<code>{0}vpsinfo</code> → Cek spesifikasi dan penggunaan server.</blockquote></b>
"""

def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

@PY.UBOT("vpsinfo")
@PY.TOP_CMD
async def _(client, message):
    # Pesan loading
    status_msg = await message.reply_text("<blockquote><b>🔍 Sedang mengambil data server...</b></blockquote>")
    
    # Logika mengambil data sistem
    uname = platform.uname()
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    
    # Info CPU & RAM
    cpufreq = psutil.cpu_freq()
    svmem = psutil.virtual_memory()
    
    # Info Disk
    partitions = psutil.disk_partitions()
    disk_info = ""
    for partition in partitions:
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            disk_info += f"<b>Disk {partition.mountpoint}:</b> <code>{get_size(partition_usage.used)} / {get_size(partition_usage.total)}</code>\n"
        except:
            continue

    hasil = (
        f"<blockquote><b>🖥️ SPESIFIKASI VPS</b>\n\n"
        f"<b>⚙️ OS:</b> <code>{uname.system} {uname.release}</code>\n"
        f"<b>⏰ Uptime:</b> <code>{bt.day}/{bt.month}/{bt.year}</code>\n\n"
        f"<b>🧠 CPU:</b> <code>{psutil.cpu_count(logical=True)} Core ({psutil.cpu_percentage()}%)</code>\n"
        f"<b>💾 RAM:</b> <code>{get_size(svmem.used)} / {get_size(svmem.total)} ({svmem.percent}%)</code>\n"
        f"{disk_info}\n"
        f"<b>💡 ARAHAN:</b>\n"
        f"<i>Jika RAM di atas 90%, segera restart bot atau bersihkan cache server agar tidak terjadi error.</i></blockquote>"
    )
    
    await status_msg.edit(hasil)
    