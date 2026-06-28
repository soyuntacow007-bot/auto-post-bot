import telebot
import os


# Bot token (Seniň tokeniň)
TOKEN = "8233407402:AAGAnR_P3NwNkfclvoIvz-D_gyVKzQnY4t0"

# ⚠️ ÜNS BERIŇ: Şu aşakdaky ýere öz hakyky kanal adyňy ýaz (Mysal: @kanal_ady)
CHANNEL_ID = "@agza_bol_1"  

# 📝 Kanala goýuljak reklama teksti
POST_TEXT = """

 Laýk basyň❤️"""

bot = telebot.TeleBot(TOKEN)

# Öňki goýlan hatyň ID-sini faýldan okaýar
ID_FILE = "last_msg_id.txt"
last_msg_id = None

if os.path.exists(ID_FILE):
    with open(ID_FILE, "r") as f:
        content = f.read().strip()
        if content.isdigit():
            last_msg_id = int(content)

# 1. Öňki haty kanaldan pozýar
if last_msg_id:
    try:
        bot.delete_message(CHANNEL_ID, last_msg_id)
        print(f"✅ Köne hat pozuldy (ID: {last_msg_id})")
    except Exception as e:
        print(f"⚠️ Köne hat tapylmady ýa-da eýýäm pozulgy: {e}")

# 2. Täze haty kanala goýýar
try:
    sent_msg = bot.send_message(CHANNEL_ID, POST_TEXT)
    new_msg_id = sent_msg.message_id
    print(f"✅ Täze hat iberildi (ID: {new_msg_id})")
    
    # Täze ID-ni ýatda saklamak üçin faýla ýazýar
    with open(ID_FILE, "w") as f:
        f.write(str(new_msg_id))
        
except Exception as e:
    print(f"❌ Kanala hat ugradylanda ýalňyşlyk boldy: {e}")

print("🤖 Bot işini durnukly tamamlady.")
