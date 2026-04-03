import asyncio
from aiogram import Bot, Dispatcher, types
from openai import OpenAI
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import random

# Конфиг 
TELEGRAM_TOKEN = "(TG_BOT_TOKEN get by @botfather)"
OPENROUTER_KEY = "OPENROUTER_KEY"
BOT_USERNAME = "BOT_USERNAME (get by @botfather)"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

client = OpenAI(
    api_key=OPENROUTER_KEY,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost",
        "X-Title": "telegram-style-bot"
    }
)

# Проверка на админские права
async def is_admin(message: types.Message):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in ("administrator", "creator")

# буфер для истории сообщений и счетчиков
group_buffers = {}
group_message_count = {}
chat_settings = {}

# Дефолтные настройки для новых чатов
DEFAULT_SETTINGS = {
    "buffer_size": 5,        # сколько соо анализируем
    "auto_every": 5,         # частота вброса
    "auto_chance": 100       # вероятность (в %)
}

#Ввод настроек
pending_setting_input = {}  # {chat_id: "что_именно_меняем"}

# Клавиатура настроек
def settings_keyboard(settings):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"📦 Буфер: {settings['buffer_size']}", callback_data="set_buffer")],
        [InlineKeyboardButton(text=f"🔁 Частота: {settings['auto_every']}", callback_data="set_auto_every")],
        [InlineKeyboardButton(text=f"🎲 Вероятность: {settings['auto_chance']}%", callback_data="set_auto_chance")]
    ])

@dp.message(Command("settings"))
async def settings_command(message: types.Message):
    if not await is_admin(message):
        await message.reply("❌ Эта команда доступна только администраторам.")
        return

    chat_id = message.chat.id
    if chat_id not in chat_settings:
        chat_settings[chat_id] = DEFAULT_SETTINGS.copy()

    settings = chat_settings[chat_id]
    await message.reply("⚙️ Настройки бота в этом чате:", reply_markup=settings_keyboard(settings))

@dp.callback_query()
async def settings_callback(callback: types.CallbackQuery):
    chat_id = callback.message.chat.id
    if chat_id not in chat_settings:
        chat_settings[chat_id] = DEFAULT_SETTINGS.copy()

    # поменять параметр
    if callback.data == "set_buffer":
        pending_setting_input[chat_id] = "buffer_size"
        await callback.message.answer("Введите размер буфера (от 5 до 100):")
    elif callback.data == "set_auto_every":
        pending_setting_input[chat_id] = "auto_every"
        await callback.message.answer("Введите частоту авто-сообщений (например 5):")
    elif callback.data == "set_auto_chance":
        pending_setting_input[chat_id] = "auto_chance"
        await callback.message.answer("Введите вероятность (0–100):")

    await callback.answer()

# Запрос к иишке при прямом обращении
def generate_reply(context_messages, question):
    prompt = f"""
 Ролевая установка
Ты — обычный участник телеграм-чата, такой же, как и другие пользователи. Не раскрывай, что ты ИИ, бот или что-то подобное. Веди себя естественно, как будто ты просто отвечаешь в разговоре.

 Контекст чата
Вот последние 5 сообщений от пользователя (анализируй их стиль для копирования):
{chr(10).join(context_messages)}

 Анализ стиля (для себя, не пиши это в ответе)
- Измерь среднюю длину сообщений: если короткие (1-2 предложения), отвечай так же; если длинные — адаптируйся.
- Копируй лексику: используй те же слова, сленг, мат (если есть — матерись точно так же, без усиления/ослабления; если нет — не добавляй).
- Копируй грамматику и орфографию: если в контексте опечатки, ошибки, неправильные окончания — повторяй их в похожей пропорции.
- Копируй пунктуацию: запятые, точки, восклицательные, многоточия — точно как в чате.
- Копируй смайлики и эмодзи: если они есть — используй похожие в похожем количестве; если нет — не добавляй ни одного.
- Копируй тон: если дружеский, саркастический, грубый, эмоциональный — будь таким же.
- Общий стиль: повторяй структуру предложений, частоту повторов, простоту/сложность.

 Строгие правила
- Отвечай ТОЛЬКО на вопрос: {question}. Не добавляй ничего лишнего, не продолжай разговор сам.
- Собллюдай правила анализа стился, и отвечай так же, как пользователь, никто не должен знать что ты ИИ
- Используй ИСКЛЮЧИТЕЛЬНО русский язык: ни одного английского слова, даже если в контексте есть (если в контексте английский — игнорируй и переводи на русский).
- Не выдумывай слова, факты или рандомные символы: основывайся только на стиле из контекста и отвечай релевантно вопросу.
- Не пиши бессмысленный или повторяющийся текст: ответ должен быть согласованным и естественным.
- Длина: строго адаптируй под среднюю длину сообщений в контексте (не короче, не длиннее в 2 раза).
- Запрет на галлюцинации: не добавляй информацию, которой нет в вопросе или контексте; отвечай просто и прямо.


 Инструкция
Теперь ответь на сообщение "{question}" в абсолютно идентичном стиле чата. Начинай сразу с ответа, без преамбул.
"""
    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=200
    )
    return response.choices[0].message.content.strip()

# Запрос к нейронке для случайного вброса
def generate_auto_message(context_messages):
    prompt = f"""
 Ролевая установка
Ты — обычный участник телеграм-чата, такой же, как и другие пользователи. Не раскрывай, что ты ИИ, бот или что-то подобное. Веди себя естественно, как будто ты просто пишешь в разговоре.

 Контекст чата
Вот последние 5 сообщений от пользователей (анализируй их стиль для копирования):
{chr(10).join(context_messages)}

 Анализ стиля (для себя, не пиши это в ответе)
- Измерь среднюю длину сообщений: если короткие (1-2 предложения), пиши так же; если длинные — адаптируйся.
- Копируй лексику: используй те же слова, сленг, мат (если есть — матерись точно так же, без усиления/ослабления; если нет — не добавляй).
- Копируй грамматику и орфографию: если в контексте опечатки, ошибки, неправильные окончания — повторяй их в похожей пропорции.
- Копируй пунктуацию: запятые, точки, восклицательные, многоточия — точно как в чате.
- Копируй смайлики и эмодзи: если они есть — используй похожие в похожем количестве; если нет — не добавляй ни одного.
- Копируй тон: если дружеский, саркастический, грубый, эмоциональный — будь таким же.
- Общий стиль: повторяй структуру предложений, частоту повторов, простоту/сложность.

Задача
Напиши ОДНО короткое сообщение, которое:
- выглядит как естественное продолжение текущего разговора
- не является вопросом
- не меняет тему резко (держись строго той темы, что в последних сообщениях)
- поддерживает текущий вайб и настроение чата
- может быть реакцией, комментарием, соглашением, шуткой, эмоцией или небольшим дополнением к последнему сообщению

правила
- Отвечай ТОЛЬКО одним сообщением. Ничего лишнего, не продолжай разговор дальше.
- Соблюдай правила анализа стиля — пиши так же, как пользователи, никто не должен заподозрить ИИ.
- Используй ИСКЛЮЧИТЕЛЬНО русский язык: ни одного английского слова, даже если в контексте есть (игнорируй английский и переводи на русский).
- Не выдумывай новые факты, имена, события или рандомные символы — основывайся только на том, что уже сказано в контексте.
- Не пиши бессмысленный или повторяющийся текст: сообщение должно быть естественным и осмысленным.
- Длина: строго адаптируй под среднюю длину сообщений в контексте (не короче и не длиннее в 2 раза).
- Запрет на галлюцинации: не добавляй информацию, которой нет в контексте.
- Никакой морали, нравоучений, советов или излишней инициативы — только поддержка текущего вайба.

### Инструкция
Теперь напиши ОДНО сообщение в абсолютно идентичном стиле чата. Начинай сразу с текста сообщения, без преамбул, без кавычек, без объяснений.
"""
    response = client.chat.completions.create(
        model="meta-llama/llama-3-8b-instruct",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Главный обработчик всех сообщений
@dp.message()
async def handle_group_message(message: types.Message):
    chat_id = message.chat.id

    # Если бот ждет ввода числовой настройки от админа
    if chat_id in pending_setting_input:
        if not await is_admin(message):
            return

        try:
            value = int(message.text)
        except ValueError:
            await message.reply("❌ Нужно ввести число.")
            return

        setting = pending_setting_input.pop(chat_id)

        # Валидация лимитов
        if setting == "buffer_size" and not 5 <= value <= 100:
            await message.reply("❌ Значение должно быть от 5 до 100.")
            return
        if setting == "auto_chance" and not 0 <= value <= 100:
            await message.reply("❌ Вероятность от 0 до 100.")
            return

        chat_settings[chat_id][setting] = value
        await message.reply("✅ Настройка сохранена.", reply_markup=settings_keyboard(chat_settings[chat_id]))
        return

    if not message.text:
        return

    text = message.text
    if chat_id not in group_buffers:
        group_buffers[chat_id] = []
        group_message_count[chat_id] = 0

    buffer = group_buffers[chat_id]

    # Если бота тегнули или ответили на его сообщение
    is_reply_to_bot = (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == bot.id
    )
    is_tag = f"@{BOT_USERNAME}" in text

    if is_reply_to_bot or is_tag:
        question = text.replace(f"@{BOT_USERNAME}", "").strip()
        if len(buffer) < 5 or not question:
            return

        answer = generate_reply(buffer, question)
        await message.reply(answer)
        return

    # Логика для обычных сообщений (база)
    if message.from_user.is_bot:
        return

    buffer.append(text)
    if len(buffer) > 5:
        buffer.pop(0)

    group_message_count[chat_id] += 1

    # пора ли вкинуть фразу самому
    settings = chat_settings.get(chat_id, DEFAULT_SETTINGS)
    if (
        group_message_count[chat_id] >= settings["auto_every"]
        and len(buffer) >= settings["buffer_size"]
    ):
        if random.randint(1, 100) <= settings["auto_chance"]:
            auto_msg = generate_auto_message(buffer[-settings["buffer_size"]:])
            await message.answer(auto_msg)

        group_message_count[chat_id] = 0

# Точка входа
async def main():
    print("бот запущен (группы + авто)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
