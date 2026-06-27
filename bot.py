import telebot
import os

# Bot token we Kanal maglumatlary
TOKEN = "8233407402:AAGAnR_P3NwNkfclvoIvz-D_gyVKzQnY4t0"
CHANNEL_ID = "@nexus_vpn_tm"  # <-- Şu ýere öz kanal adyňy ýaz (mysal: @kanal_ady)

# Kanala iberiljek hemişelik tekst (Şu ýere öz reklama tekstiňi ýaz)
POST_TEXT = """🔥 NEXUS | VPN Türkmenistan 🇹🇲

🚀 Çalt we durnukly VPN hyzmatlary!
🔓 Ähli sosial ulgamlar açyk.

Habarlaşmak üçin: @admin"""

bot = telebot.TeleBot(TOKEN)

# Öňki iberilen hatyň ID-sini faýldan oka
ID_FILE = "last_msg_id.txt"
last_msg_id = None

if os.path.exists(ID_FILE):
    with open(ID_FILE, "r") as f:
        content = f.read().strip()
        if content.isdigit():
            last_msg_id = int(content)

# 1. Öňki haty kanaldan poz
if last_msg_id:
    try:
        bot.delete_message(CHANNEL_ID, last_msg_id)
        print(f"✅ Köne hat pozuldy (ID: {last_msg_id})")
    except Exception as e:
        print(f"⚠️ Köne haty pozup bolmady (Mümkin el bilen pozulgandyr): {e}")

# 2. Täze haty kanala iber
try:
    sent_msg = bot.send_message(CHANNEL_ID, POST_TEXT)
    new_msg_id = sent_msg.message_id
    print(f"✅ Täze hat iberildi (ID: {new_msg_id})")
    
    # Täze ID-ni ýatda saklamak üçin faýla ýaz
    with open(ID_FILE, "w") as f:
        f.write(str(new_msg_id))
        
except Exception as e:
    print(f"❌ Täze hat iberilende ýalňyşlyk ýüze çykdy: {e}")

print("🤖 Bot işini durnukly tamamlady we ýapyldy.")
