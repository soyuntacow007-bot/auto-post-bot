import os
import time
import threading
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# 1. RENDER ÜÇIN WEB SERWER (Uka gitmezligi we öçmezligi üçin)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot janly we islap dur!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    print(f"Web serwer {port} portynda baslady...")
    server.serve_forever()

# 2. TELEGRAM BOTUŇ ESASY IŞLEÝIŞI
def telegram_bot_loop():
    BOT_TOKEN = os.environ.get("8233407402:AAGAnR_P3NwNkfclvoIvz-D_gyVKzQnY4t0")
    CHAT_ID = os.environ.get("@agza_bol_1")
    
    last_message_id = None
    print("Telegram bot aylawy baslady...")
    
    while True:
        try:
            # Öňki hat bar bolsa, ony pozýarys
            if last_message_id:
                delete_url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage"
                requests.post(delete_url, json={"chat_id": CHAT_ID, "message_id": last_message_id})
                print("Onki hat pozuldy.")

            # Täze haty goýýarys
            send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": CHAT_ID,
                "text": "Laýk basyň❤️"  # Isleýän tekstiňizi şu ýerde üýtgedip bilersiňiz
            }
            response = requests.post(send_url, json=payload).json()
            
            if response.get("ok"):
                last_message_id = response["result"]["message_id"]
                print(f"Taze hat goyuldy! Message ID: {last_message_id}")
            
        except Exception as e:
            print(f"Yalnyslyk yuze cykdy: {e}")

        # GÖNI 10 MINUT (600 sekunt) SEKUNDYNA ÇENLI TAKYK GARAŞÝAR
        time.sleep(600)

if __name__ == "__main__":
    bot_thread = threading.Thread(target=telegram_bot_loop)
    bot_thread.daemon = True
    bot_thread.start()
    
    run_web_server()
  
