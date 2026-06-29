"""
Backend для сайта репетитора по английскому языку.
Принимает заявки из формы и отправляет уведомления в Telegram.
"""
import os
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from dotenv import load_dotenv
import telegram

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID_STR = os.getenv("CHAT_ID")

if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
    logger.warning("BOT_TOKEN не настроен! Отправка в Telegram работать не будет.")

if not CHAT_ID_STR:
    logger.warning("CHAT_ID не настроен!")
    CHAT_ID_STR = "745673632"

# Преобразуем CHAT_ID в число (Telegram API требует int)
try:
    CHAT_ID = int(CHAT_ID_STR)
except ValueError:
    logger.warning(f"CHAT_ID '{CHAT_ID_STR}' не является числом! Используем значение по умолчанию.")
    CHAT_ID = 745673632

# Создаём приложение
app = FastAPI(
    title="English Tutor API",
    description="API для приёма заявок с сайта репетитора",
    version="1.0.0",
)

# CORS — разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://beklox.ru", "https://www.beklox.ru"],
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
)


# Модель данных формы
class LeadForm(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Имя")
    phone: str = Field(..., min_length=5, max_length=30, description="Телефон")
    email: str = Field(..., max_length=100, description="Email")
    goal: str = Field(default="", max_length=100, description="Цель")
    message: str = Field(default="", max_length=1000, description="Комментарий")
    privacy: bool = Field(..., description="Согласие с политикой конфиденциальности")


async def send_telegram_notification(lead: LeadForm) -> bool:
    """
    Отправляет уведомление о новой заявке в Telegram.
    """
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        logger.info("Telegram не настроен. Пропускаем отправку.")
        return False

    try:
        bot = telegram.Bot(token=BOT_TOKEN)

        # Форматируем сообщение
        goal_text = {
            "ege": "Подготовка к ЕГЭ",
            "oge": "Подготовка к ОГЭ",
            "ielts": "IELTS / TOEFL",
            "general": "Общий английский",
            "other": "Другое",
        }.get(lead.goal, lead.goal or "Не указана")

        message = (
            f"📩 <b>Новая заявка с сайта!</b>\n\n"
            f"👤 <b>Имя:</b> {lead.name}\n"
            f"📞 <b>Телефон:</b> {lead.phone}\n"
            f"📧 <b>Email:</b> {lead.email}\n"
            f"🎯 <b>Цель:</b> {goal_text}\n"
        )

        if lead.message:
            message += f"💬 <b>Комментарий:</b> {lead.message}\n"

        message += (
            f"\n✅ Согласие на обработку данных: Да\n"
            f"🕐 <b>Время заявки:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

        logger.info(f"Уведомление отправлено в Telegram. Имя: {lead.name}")
        return True

    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")
        # Пробуем получить update, чтобы узнать ID чата
        try:
            updates = await bot.get_updates()
            if updates:
                logger.info(f"Доступные чаты: {[(u.message.chat.id, u.message.chat.type, u.message.from_user.id) for u in updates if u.message]}")
            else:
                logger.info("Нет обновлений. Напишите боту любое сообщение в Telegram, чтобы он мог определить ваш ID.")
        except Exception as e2:
            logger.error(f"Не удалось получить обновления: {e2}")
        return False


@app.get("/")
async def root():
    """Проверка работоспособности API."""
    return {
        "status": "ok",
        "message": "English Tutor API работает",
        "version": "1.0.0",
    }


@app.post("/api/lead")
async def submit_lead(lead: LeadForm):
    """
    Принимает заявку с сайта и отправляет уведомление в Telegram.
    """
    logger.info(f"Получена заявка от {lead.name} ({lead.phone})")

    # Проверяем согласие с политикой конфиденциальности
    if not lead.privacy:
        raise HTTPException(
            status_code=400,
            detail="Необходимо согласиться с политикой конфиденциальности",
        )

    # Отправляем в Telegram
    telegram_sent = await send_telegram_notification(lead)

    return {
        "status": "success",
        "message": "Спасибо! Ваша заявка принята. Я свяжусь с вами в течение 2 часов.",
        "telegram_notified": telegram_sent,
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса."""
    return {
        "status": "healthy",
        "telegram_configured": BOT_TOKEN != "your_bot_token_here" and bool(BOT_TOKEN),
    }


@app.get("/api/get-chat-id")
async def get_chat_id():
    """
    Получает ID последнего чата, который написал боту.
    Нужно сначала написать боту любое сообщение в Telegram.
    """
    if not BOT_TOKEN or BOT_TOKEN == "your_bot_token_here":
        return {"status": "error", "message": "BOT_TOKEN не настроен"}
    
    try:
        bot = telegram.Bot(token=BOT_TOKEN)
        updates = await bot.get_updates()
        
        if not updates:
            return {
                "status": "error",
                "message": "Нет обновлений. Напишите боту любое сообщение в Telegram!",
            }
        
        # Берём последнее обновление
        last_update = updates[-1]
        if last_update.message:
            chat = last_update.message.chat
            return {
                "status": "success",
                "chat_id": chat.id,
                "chat_type": chat.type,
                "chat_title": chat.title or chat.first_name or "Неизвестно",
                "message": f"Ваш ID: {chat.id}. Скопируйте его в .env файл как CHAT_ID={chat.id}",
            }
        
        return {"status": "error", "message": "Нет сообщений в обновлениях"}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
