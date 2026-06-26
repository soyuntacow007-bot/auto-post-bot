import telebot
from telebot import types
import time
import threading
import sqlite3
import requests
import os

# Bot token we ID
TOKEN = "8233407402:AAGAnR_P3NwNkfclvoIvz-D_gyVKzQnY4t0"
ADMIN_ID = 6987543325

# Köne database faýlyny poz
try:
    os.remove('posts.db')
    print("Köne database pozuldy")
except:
    pass

# Webhooky poz
try:
    requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook")
    time.sleep(1)
except:
    pass

bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()

# Täze database döret - DOGRY sütünler bilen
conn = sqlite3.connect('posts.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS posts
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT,  -- bu ýerde kanal ady saklanýar
                message_text TEXT,
                interval INTEGER,
                is_active BOOLEAN,
                last_message_id INTEGER)''')
conn.commit()
print("Täze database döredildi!")

active_timers = {}

@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "Siz admin däl!")
        return
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/add_post", "/list_posts", "/stop_post", "/delete_post", "/test")
    bot.send_message(message.chat.id, "🤖 Bot işleýär!\n\nKanal synag: /test\nPost goşmak: /add_post", reply_markup=markup)

@bot.message_handler(commands=['test'])
def test_channel(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    msg = bot.send_message(message.chat.id, "🔍 Test üçin kanal adyny ýazyn:\nMysal: @kanalady")
    bot.register_next_step_handler(msg, test_send)

def test_send(message):
    channel = message.text.strip()
    
    # @ yok bolsa goş
    if not channel.startswith('@'):
        channel = '@' + channel
    
    try:
        # Test habary iber
        sent = bot.send_message(channel, "🧪 Test habary - Bu habar 5 sekuntdan soň pozular")
        bot.send_message(message.chat.id, f"✅ Habar iberildi!\nMessage ID: {sent.message_id}")
        
        # 5 sekunt garaş
        time.sleep(5)
        
        # Habary poz
        bot.delete_message(channel, sent.message_id)
        bot.send_message(message.chat.id, "✅ Test habary pozuldy!\n\nBot kanalda işleýär! ✅")
        
    except Exception as e:
        error_text = str(e)
        bot.send_message(message.chat.id, f"❌ Ýalňyşlyk: {error_text}")
        
        if "chat not found" in error_text:
            bot.send_message(message.chat.id, "❌ Kanal tapylmady!\n\nSebäpleri:\n1. Kanal ady ýalňyş\n2. Siz kanala girmedik\n3. Kanal ýapyk")
        elif "bot was kicked" in error_text:
            bot.send_message(message.chat.id, "❌ Bot kanalda ýok!\n\nBoty kanala goşuň!")
        elif "need administrator rights" in error_text:
            bot.send_message(message.chat.id, "❌ Bot admin däl!\n\nBoty kanala ADMIN edip goşuň!")
        else:
            bot.send_message(message.chat.id, "❌ Bot kanala habar iberip bilmeýär!\n\n1. Boty kanala goşuň\n2. Boty admin ediň\n3. Admin rugsatlaryny beriň")

@bot.message_handler(commands=['add_post'])
def add_post(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    msg = bot.send_message(message.chat.id, "📢 Kanal adyny ýazyn:\nMysal: @kanalady")
    bot.register_next_step_handler(msg, get_channel)

def get_channel(message):
    channel_id = message.text.strip()
    
    # @ yok bolsa goş
    if not channel_id.startswith('@'):
        channel_id = '@' + channel_id
    
    msg = bot.send_message(message.chat.id, "✍️ Habar tekstini ýazyn:")
    bot.register_next_step_handler(msg, get_text, channel_id)

def get_text(message, channel_id):
    text = message.text
    msg = bot.send_message(message.chat.id, "⏱️ Wagt interwalyny ýazyn (sekunt):\n60 = 1 minut\n3600 = 1 sagat\n86400 = 24 sagat")
    bot.register_next_step_handler(msg, get_interval, channel_id, text)

def get_interval(message, channel_id, text):
    try:
        interval = int(message.text)
        if interval < 5:
            interval = 5
            bot.send_message(message.chat.id, "⏱️ 5 sekuntdan kiçi bolup bilmeýär, 5 sekunt edildi.")
        
        # Ilki test iberip gör
        try:
            test_msg = bot.send_message(channel_id, "⚙️ Post goşulýar... Test habary")
            bot.delete_message(channel_id, test_msg.message_id)
            
            # Database goş - channel_id ulanylýar (channel_username däl!)
            cursor.execute("INSERT INTO posts (channel_id, message_text, interval, is_active, last_message_id) VALUES (?, ?, ?, ?, ?)",
                          (channel_id, text, interval, False, 0))
            conn.commit()
            post_id = cursor.lastrowid
            
            # Wagty formatla
            minutes = interval // 60
            seconds = interval % 60
            if minutes > 0:
                time_text = f"{minutes} minut {seconds} sekunt"
            else:
                time_text = f"{interval} sekunt"
            
            bot.send_message(message.chat.id, f"✅ Post goşuldy!\n\n🆔 ID: {post_id}\n📢 Kanal: {channel_id}\n⏱️ Wagt: {time_text}\n\n▶️ Başlatmak: /start_post {post_id}")
            
        except Exception as e:
            error_text = str(e)
            bot.send_message(message.chat.id, f"❌ Kanal bilen baglanyşyk ýalňyşlyk!\n\n{error_text}\n\n1. Bot kanalda adminmi?\n2. Kanal ady dogrymy?\n3. Test etmek üçin /test")
            
    except ValueError:
        bot.send_message(message.chat.id, "❌ Ýalňyş! San ýazyn (mysal: 60)")

@bot.message_handler(commands=['start_post'])
def start_post(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        post_id = int(message.text.split()[1])
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        
        if post:
            cursor.execute("UPDATE posts SET is_active = ? WHERE id = ?", (True, post_id))
            conn.commit()
            bot.send_message(message.chat.id, f"▶️ Post {post_id} aktiwleşdi!")
            
            thread = threading.Thread(target=post_loop, args=(post_id,))
            thread.daemon = True
            thread.start()
            active_timers[post_id] = thread
        else:
            bot.send_message(message.chat.id, "❌ Post tapylmady!")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "ID-ni ýazyn: /start_post 1")

def post_loop(post_id):
    while True:
        try:
            cursor.execute("SELECT * FROM posts WHERE id = ? AND is_active = ?", (post_id, True))
            post = cursor.fetchone()
            
            if not post:
                break
                
            channel = post[1]      # channel_id (kanal ady)
            text = post[2]         # message_text
            interval = post[3]     # interval
            last_msg_id = post[5]  # last_message_id
            
            try:
                # Öňki habary poz
                if last_msg_id and last_msg_id != 0:
                    try:
                        bot.delete_message(channel, last_msg_id)
                        print(f"Post {post_id}: Öňki habar pozuldy")
                    except Exception as e:
                        print(f"Pozmak ýalňyşlygy: {e}")
                
                # Täze habar iber
                sent = bot.send_message(channel, text)
                new_msg_id = sent.message_id
                
                # Täze message_id-ni ýatda sakla
                cursor.execute("UPDATE posts SET last_message_id = ? WHERE id = ?", (new_msg_id, post_id))
                conn.commit()
                
                print(f"✅ Post {post_id}: Täze habar iberildi (ID: {new_msg_id})")
                
            except Exception as e:
                print(f"❌ Post {post_id}: Habar iberilmedi! {e}")
                # 30 sekunt garaşyp gaýtadan synanş
                time.sleep(30)
                continue
            
            # Wagt garaş
            time.sleep(interval)
            
        except Exception as e:
            print(f"Umumy ýalňyşlyk: {e}")
            time.sleep(10)

@bot.message_handler(commands=['list_posts'])
def list_posts(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    
    if posts:
        response = "📋 Postlar:\n\n"
        for post in posts:
            status = "✅ Aktiw" if post[4] else "⭕ Aktiw däl"
            
            # Wagty formatla
            minutes = post[3] // 60
            seconds = post[3] % 60
            if minutes > 0:
                time_text = f"{minutes} minut {seconds} sekunt"
            else:
                time_text = f"{post[3]} sekunt"
            
            response += f"🆔 ID: {post[0]}\n"
            response += f"📢 Kanal: {post[1]}\n"
            response += f"✍️ Habar: {post[2][:30]}...\n"
            response += f"⏱️ Wagt: {time_text}\n"
            response += f"📊 Status: {status}\n"
            response += f"🆔 Soňky hat: {post[5] if post[5] else 'ýok'}\n\n"
            
            # Uzyn bolsa bölek bölek iber
            if len(response) > 3000:
                bot.send_message(message.chat.id, response)
                response = ""
        
        if response:
            bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "📭 Hiç post ýok\n\nTäze post goşmak: /add_post")

@bot.message_handler(commands=['stop_post'])
def stop_post(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        post_id = int(message.text.split()[1])
        cursor.execute("UPDATE posts SET is_active = ? WHERE id = ?", (False, post_id))
        conn.commit()
        bot.send_message(message.chat.id, f"⏹️ Post {post_id} togtadyldy!")
        
        # Soňky haty poz
        cursor.execute("SELECT last_message_id, channel_id FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        if post and post[0] and post[0] != 0:
            try:
                bot.delete_message(post[1], post[0])
                print(f"Post {post_id}: Soňky habar pozuldy")
            except:
                pass
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "ID-ni ýazyn: /stop_post 1")

@bot.message_handler(commands=['delete_post'])
def delete_post(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        post_id = int(message.text.split()[1])
        
        # Soňky haty poz
        cursor.execute("SELECT last_message_id, channel_id FROM posts WHERE id = ?", (post_id,))
        post = cursor.fetchone()
        if post and post[0] and post[0] != 0:
            try:
                bot.delete_message(post[1], post[0])
            except:
                pass
        
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        bot.send_message(message.chat.id, f"🗑️ Post {post_id} pozuldy!")
        
        if post_id in active_timers:
            del active_timers[post_id]
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "ID-ni ýazyn: /delete_post 1")

print("="*50)
print("🤖 Telegram Auto Post Bot")
print("="*50)
print(f"✅ Admin ID: {ADMIN_ID}")
print(f"✅ Token: {TOKEN[:10]}...")
print("✅ Täze database döredildi!")
print("="*50)
print("\n📌 İlki bilen /test komandasy bilen kanaly synap görüň!")
print("📌 Soňra /add_post bilen post goşuň!")
print("="*50)

try:
    bot.polling(none_stop=True, interval=0, timeout=20)
except Exception as e:
    print(f"Polling ýalňyşlygy: {e}")
    bot.remove_webhook()
    bot.polling(none_stop=True, interval=0, timeout=20)
