
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os, datetime
from utils import send_discord, send_telegram
from openai import OpenAI
import asyncio

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

async def ask_openai(prompt: str) -> str:
    """
    Llama a la API nueva /responses (clave sk-proj-…).
    Incluye reintentos simples por si hay 429 o fallos transitorios.
    """
    last_err = None
    for attempt in range(3):
        try:
            resp = client.responses.create(
                model=DEFAULT_MODEL,
                input=prompt
            )
            return resp.output_text.strip()
        except Exception as e:
            last_err = e
            # backoff: 1.5s, 3s, 4.5s
            await asyncio.sleep(1.5 * (attempt + 1))
    return f"⚠️ No pude obtener respuesta de OpenAI tras reintentos: {last_err}"
#End

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "").strip()

@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"

@app.post("/webhook")
async def tv_webhook(req: Request):
    try:
        data = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # Autenticación simple por 'secret'
    secret = str(data.get("secret") or "").strip()
    if WEBHOOK_SECRET and secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized (bad secret)")

    ticker  = str(data.get("ticker") or data.get("symbol") or "UNKNOWN")
    tf      = str(data.get("interval") or "?")
    tstamp  = str(data.get("time") or datetime.datetime.utcnow().isoformat())
    price   = data.get("price")
    lo      = data.get("low")
    hi      = data.get("high")
    opn     = data.get("open")
    vol     = data.get("volume")
    note    = str(data.get("note") or "")

    user_msg = (
        f"Ticker: {ticker} | TF: {tf}\n"
        f"Hora: {tstamp} | Precio: {price} (O:{opn}, H:{hi}, L:{lo}, V:{vol})\n"
        f"Señal: {note}\n"
        f"Analiza tendencia actual, soportes/resistencias inmediatos, riesgo y sesgo temporal."
    )

    try:
        answer = await ask_openai(user_msg)
    except Exception as e:
        answer = f"⚠️ Error conversando con OpenAI: {e}"

    text = f"📈 {ticker} [{tf}]\n{answer}"
    await send_discord(text)
    await send_telegram(text)

    return {"ok": True, "analysis": answer}
