from asyncio import run
from aiogram import Bot, Dispatcher


from db import (create_tables, insert_chat, chats)
from config import BOT_TOKEN

dispatcher = Dispatcher()
bot = Bot(token=BOT_TOKEN)

async def main():
    await dispatcher.start_polling(bot)


if __name__=='__main__':
    create_tables()
    # insert_chat('https://t.me/rahim_mustafo')
    print(chats())
    run(main())
