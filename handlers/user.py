from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, CommandObject

from config import ADMINS
from keyboard import admin_choice, subscribe_keyboard
from service import format_link, forum_list, chat_list

router = Router()


async def check_subscription(bot, user_id: int, chats: list) -> list:
    """
    Verifies user subscription to required channels.
    Returns list of chats user is NOT subscribed to.
    """
    not_subscribed = []
    for chat in chats:
        try:
            # Normalize chat link before API call
            chat_identifier = chat.chat_link
            
            # If it's a number, use as-is (chat_id)
            # Otherwise, ensure it starts with @
            if not chat_identifier.lstrip('-').isdigit():
                if not chat_identifier.startswith('@'):
                    chat_identifier = f"@{chat_identifier}"
            
            member = await bot.get_chat_member(
                chat_id=chat_identifier,
                user_id=user_id
            )
            
            # Check if user is actually subscribed
            if member.status in ('left', 'kicked', 'restricted'):
                not_subscribed.append(chat)
        except Exception as e:
            # If bot is not admin in channel, treat as not subscribed
            error_msg = str(e)
            if "member list is inaccessible" in error_msg.lower():
                print(f"⚠️ Bot {chat.chat_link} kanalida admin emas! Botni admin qiling.")
            else:
                print(f"Error checking subscription for {chat.chat_link}: {e}")
            not_subscribed.append(chat)
    return not_subscribed



@router.message(CommandStart(deep_link=True))
async def start_with_link(message: Message, command: CommandObject):
    from service import find_forum_by_name
    
    # Normalize forum name from deep link
    forum_name = format_link(command.args)
    
    # Case-insensitive forum lookup
    forum = find_forum_by_name(forum_name)
    if not forum:
        await message.answer("❌ Forum topilmadi.")
        return

    # Get required chats and check subscription
    chats = chat_list()
    if not chats:
        # No subscription requirements
        await message.answer(f"✅ Forum linki:\n{forum.forum_link}")
        return
    
    not_subscribed = await check_subscription(message.bot, message.from_user.id, chats)

    if not_subscribed:
        await message.answer(
            "📢 Quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscribe_keyboard(not_subscribed, forum.forum_name)
        )
    else:
        await message.answer(f"✅ Forum linki:\n{forum.forum_link}")



@router.message(CommandStart())
async def start(message: Message):
    name = message.from_user.first_name
    user_id = message.from_user.id
    if user_id in ADMINS:
        await message.answer(f'Assalomu aleykum {name} 👋', reply_markup=admin_choice)
    else:
        await message.answer(f'Assalomu aleykum {name} 👋')


@router.callback_query(F.data.startswith('check_'))
async def check_again(call: CallbackQuery):
    from service import find_forum_by_name
    
    forum_name = call.data.split('_', 1)[1]
    forum = find_forum_by_name(forum_name)
    
    if not forum:
        await call.answer("❌ Forum topilmadi!", show_alert=True)
        return
    
    chats = chat_list()
    not_subscribed = await check_subscription(call.bot, call.from_user.id, chats)

    if not_subscribed:
        await call.answer("❌ Hali obuna bo'lmadingiz!", show_alert=True)
    else:
        await call.message.edit_text(f"✅ Forum linki:\n{forum.forum_link}")
        await call.answer()