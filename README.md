---  ENGLISH  ---

Chameleon (Telegram Style Mimic Bot)

A bot for Telegram groups based on aiogram 3 and Llama 3. The concept is simple: it reads the chat history and tries to respond in the same style as the participants (sentence length, slang, profanity, punctuation).
What it can do: Style adaptation: Analyzes the last 5–10 messages and copies the communication style. Automatic replies: Every few messages (configurable), it automatically sends phrases to keep the conversation going. Replies to tags: Responds if it’s mentioned in a message or a reply. Settings: Using /settings, admins can change the response frequency, trigger probability, and memory buffer size.

How it works:

Messages from the chat are saved to a local buffer (memory).
When a trigger (counter or tag) is activated, the bot sends the context to Llama 3 via OpenRouter.
The neural network generates a response, adhering to the “role” of a regular participant.

Setup:

Install dependencies with `pip install aiogram openai`.
In the code, set `TELEGRAM_TOKEN`, `BOT_USERNAME`, and `OPENROUTER_KEY`.
Run the bot
Note: For the bot to work correctly in groups, you need to disable Privacy Mode in BotFather.

---   RUSSIAN  ---

Chameleon (Telegram Style Mimic Bot)

Бот для Telegram-групп на aiogram 3 и Llama 3. Суть простая: он читает историю чата и пытается отвечать в том же стиле, что и участники (длина фраз, сленг, маты, пунктуация).

Что умеет:
Подстройка под стиль: Анализирует последние 5-10 сообщений и копирует манеру общения.
Автоматические ответы: Раз в несколько сообщений (настраивается) сам вбрасывает фразы, чтобы поддержать диалог.
Ответы на теги: Отвечает, если его упомянули в сообщении или реплаем.
Настройки: Через `/settings` админы могут менять частоту ответов, шанс срабатывания и размер буфера памяти.

 Как работает:
1. Сообщения из чата сохраняются в локальный буфер (память).
2. При срабатывании триггера (счетчик или тег) бот отправляет контекст в Llama 3 через OpenRouter.
3. Нейронка генерирует ответ, соблюдая «ролевую установку» обычного участника.

 Запуск:
1. Ставим зависимости pip install aiogram openai.
2. В коде прописываем TELEGRAM_TOKEN, BOT_USERNAME и OPENROUTER_KEY.
3. Запускаем

Примечание: Для корректной работы в группах боту нужно выключить Privacy Mode в BotFather
