from asyncio import run
from aiogram import Bot, Dispatcher
from service import create_db
from config import BOT_TOKEN
from handlers import (router_admin, router_user)
from flask import Flask
from os import environ
import threading

dispatcher = Dispatcher()
bot = Bot(token=BOT_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running'

def run_flask():
    port = int(environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

async def main():
    dispatcher.include_router(router_user)
    dispatcher.include_router(router_admin)
    await dispatcher.start_polling(bot)

if __name__=='__main__':
    try:
        create_db()
        threading.Thread(target=run_flask).start()
        run(main())
    except Exception as exc:
        print('error ',exc)
    except KeyboardInterrupt as error:
        print('error ', error)
