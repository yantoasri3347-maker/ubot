import random
from PyroUbot import *

# List nama modul yang kelihatan penting banget
legit_names = [
    "Adblock", "Admin", "Afk", "Antigcast", "Antilink", "Antispam", "Antitag",
    "Autochat", "Autojoin", "Autoread", "Backup", "Broadcast", "Cleaner", 
    "Clone", "Control", "Database", "Debugger", "Executor", "Filter", 
    "Gban", "Gcast", "Global", "Profile", "Groups", "Info", "Install", 
    "Invite", "Limit", "Meme", "Notes", "Owner", "Ping", "Pmpermit", 
    "Purge", "Quote", "Sangmata", "Self", "Settings", "Spam", "Staff", 
    "Tagall", "Telegraph", "Translate", "Type", "Vctools", "Zombies"
]

class FakeHelp:
    def __init__(self, name):
        self.__MODULE__ = name
        # Teks bantuan dibikin format ERROR / ENCRYPTED
        error_codes = ["0x00045", "0x8892X", "SYS_FAIL_404", "RESTRICTED_ACCESS", "AUTH_REQUIRED"]
        self.__HELP__ = (
            f"<blockquote><b>⚠️ ERROR_SYSTEM_FAILURE\n"
            f"Code: {random.choice(error_codes)}\n"
            f"Status: Encrypted_Mode_Active\n\n"
            f"Module {name} is locked by root. Please contact the main owner for decryption keys.</b></blockquote>"
        )

def inject_legit_error():
    all_mods = set(legit_names)
    ext_terms = ["Addon", "Pro", "Lite", "Fix", "Module", "Plugin", "Core", "Secure"]
    
    # Tetap suntik sampai 310 biar angka aman
    while len(all_mods) < 310:
        base = random.choice(legit_names)
        ext = random.choice(ext_terms)
        all_mods.add(f"{base}_{ext}")

    for mod_name in all_mods:
        HELP_COMMANDS.update({mod_name.lower(): FakeHelp(mod_name)})

# Jalankan suntikan
inject_legit_error()

@PY.UBOT("cekmod")
@PY.TOP_CMD
async def _(client, message):
    await message.edit(f"<b>📊 Total Modules: {len(HELP_COMMANDS)}</b>")
