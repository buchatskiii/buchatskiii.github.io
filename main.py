"""
English Tutor API — принимает заявки с сайта и отправляет в Telegram
"""
import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import httpx
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="English Tutor API")

# Разрешаем запросы с любых источников (для формы на сайте)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Telegram config
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    logger.warning("BOT_TOKEN or CHAT_ID not set in .env file!")


class Lead(BaseModel):
    name: str
    phone: str
    email: str
    goal: str = ""
    message: str = ""
    privacy: bool = False


GOAL_NAMES = {
    "ege": "ЕГЭ",
    "oge": "ОГЭ",
    "ielts": "IELTS/TOEFL",
    "general": "Общий английский",
    "business": "Бизнес английский",
    "other": "Другое",
}


def format_lead_message(lead: Lead) -> str:
    """Форматирует заявку в сообщение для Telegram"""
    from datetime import datetime

    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    goal_name = GOAL_NAMES.get(lead.goal, lead.goal or "Не указана")

    msg = (
        f"<b>📩 Новая заявка с сайта!</b>\n\n"
        f"👤 <b>Имя:</b> {lead.name}\n"
        f"📞 <b>Телефон:</b> {lead.phone}\n"
        f"📧 <b>Email:</b> {lead.email}\n"
        f"🎯 <b>Цель:</b> {goal_name}\n"
        f"💬 <b>Комментарий:</b> {lead.message or '—'}\n\n"
        f"🕐 {now}"
    )
    return msg


@app.get("/health")
async def health():
    """Проверка здоровья API"""
    return {
        "status": "healthy",
        "bot_configured": bool(BOT_TOKEN and CHAT_ID),
    }


@app.post("/api/lead")
async def send_lead(lead: Lead):
    """Принимает заявку с сайта и отправляет в Telegram"""
    if not lead.privacy:
        raise HTTPException(status_code=400, detail="Необходимо согласие на обработку данных")

    if not lead.name or not lead.phone or not lead.email:
        raise HTTPException(status_code=400, detail="Заполните имя, телефон и email")

    if not BOT_TOKEN or not CHAT_ID:
        logger.error("Telegram not configured: BOT_TOKEN or CHAT_ID missing")
        raise HTTPException(status_code=500, detail="Сервер не настроен")

    message = format_lead_message(lead)

    try:
        # Используем прямой IP Telegram API для обхода DNS блокировок
        TELEGRAM_API_IP = "149.154.167.220"  # api.telegram.org
        # verify=False т.к. сертификат Telegram не валиден для IP-адреса
        async with httpx.AsyncClient(timeout=15, verify=False) as client:
            url = f"https://{TELEGRAM_API_IP}/bot{BOT_TOKEN}/sendMessage"
            headers = {"Host": "api.telegram.org"}
            payload = {
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML",
            }
            response = await client.post(url, json=payload, headers=headers)
            result = response.json()

            if result.get("ok"):
                logger.info(f"Lead sent to Telegram: {lead.name} / {lead.phone}")
                return {"status": "success", "message": "Заявка отправлена"}
            else:
                logger.error(f"Telegram API error: {result}")
                raise HTTPException(status_code=502, detail="Ошибка отправки в Telegram")

    except httpx.TimeoutException:
        logger.error("Telegram API timeout")
        raise HTTPException(status_code=504, detail="Таймаут при отправке")
    except Exception as e:
        logger.error(f"Error sending lead: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
