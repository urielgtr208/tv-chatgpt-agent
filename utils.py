
import os, httpx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5-thinking")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK", "").strip()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "").strip()
RESPONSE_STYLE = os.getenv("RESPONSE_STYLE", "Analiza en 1-2 líneas: dirección, S/R cercanos, riesgo y sesgo temporal. No des consejo de inversión.")

HEADERS_OAI = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

async def ask_openai(user_msg: str) -> str:
    if not OPENAI_API_KEY:
        return "⚠️ Falta OPENAI_API_KEY. Configura la variable de entorno."
    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": f"Eres un analista técnico. {RESPONSE_STYLE}"},
            {"role": "user", "content": user_msg}
        ]
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post("https://api.openai.com/v1/chat/completions", headers=HEADERS_OAI, json=payload)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()

async def send_discord(text: str):
    if not DISCORD_WEBHOOK:
        return
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(DISCORD_WEBHOOK, json={"content": text})

async def send_telegram(text: str):
    if not (TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID):
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient(timeout=15) as client:
        await client.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})
