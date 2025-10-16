
# ChatGPT Agent para TradingView (Webhooks → OpenAI → Discord/Telegram)

Proyecto listo para desplegar (Render.com o local con Docker).
Recibe alertas de TradingView por webhook, llama a OpenAI para generar un análisis corto y lo envía a Discord o Telegram.

## 1) Requisitos
- OpenAI API Key — variable `OPENAI_API_KEY`
- Discord Webhook (opcional) — `DISCORD_WEBHOOK`
- Telegram Bot (opcional) — `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`
- Clave del Webhook (secreta) — `WEBHOOK_SECRET`

## 2) Deploy rápido en Render.com (recomendado)
1. Crea una cuenta en https://render.com
2. Sube este proyecto a tu GitHub (o haz fork).
3. En Render: New → Web Service → conecta el repo.
4. Runtime: Docker. Añade variables de entorno:
   - `OPENAI_API_KEY=tu_api_key`
   - `WEBHOOK_SECRET=clave_super_secreta`
   - (Opcional) `DISCORD_WEBHOOK=...`
   - (Opcional) `TELEGRAM_BOT_TOKEN=...`
   - (Opcional) `TELEGRAM_CHAT_ID=...`
   - (Opcional) `OPENAI_MODEL=gpt-5-thinking`
   - (Opcional) `RESPONSE_STYLE=Analiza en 1-2 líneas: dirección, S/R cercanos, riesgo y sesgo temporal. No des consejo de inversión.`
5. Despliega. Usa la URL pública, p. ej. `https://tu-servicio.onrender.com/webhook`

## 3) Ejecutar local con Docker
```bash
docker build -t tv-agent .
docker run -p 8000:8000 --env-file .env tv-agent
```
Con ngrok:
```bash
ngrok http 8000
# Usa: https://xxxx.ngrok-free.app/webhook
```

## 4) Variables de entorno (.env)
Ejemplo:
```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5-thinking
WEBHOOK_SECRET=mi_clave_ultra_segura
DISCORD_WEBHOOK=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
RESPONSE_STYLE=Analiza en 1-2 líneas: dirección, S/R cercanos, riesgo y sesgo temporal. No des consejo de inversión.
```

## 5) Configurar TradingView (Alerta con Webhook)
- Webhook URL: tu endpoint `/webhook`
- Message (JSON):
```
{
  "secret": "mi_clave_ultra_segura",
  "ticker": "{{exchange}}:{{ticker}}",
  "symbol": "{{ticker}}",
  "interval": "{{interval}}",
  "time": "{{timenow}}",
  "price": {{close}},
  "open": {{open}},
  "high": {{high}},
  "low": {{low}},
  "volume": {{volume}},
  "note": "{{strategy.order.action}}"
}
```

## 6) ¿Qué hace el servidor?
- Valida `secret`
- Construye prompt
- Llama a OpenAI
- Envía resultado a Discord y/o Telegram

## 7) Seguridad
- `WEBHOOK_SECRET` fuerte
- Limita IPs si es posible
- Logs mínimos (sin secretos)
- Maneja rate limits

## 8) Archivos
- `main.py`, `utils.py`, `Dockerfile`, `requirements.txt`, `.env.example`, `sample_alert.json`, `render.yaml`
