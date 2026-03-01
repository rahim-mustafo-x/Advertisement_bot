from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from keyboard import (admin_choice, admin_cancel, admin_adv_ready, forum_choice_keyboard, 
                      subscribe_keyboard, preview_keyboard, forum_management_keyboard, 
                      chat_management_keyboard, confirmation_keyboard)
from model import CreateAdvertisement, AddForum, AddChat, EditForum, DeleteForum, EditChat, DeleteChat
from service import forum_list, add_forum, add_chat, format_link

router = Router()


# ── BEKOR QILISH ───────────────────────────────────────────────────────────────

@router.message(
    StateFilter(
        CreateAdvertisement.content, CreateAdvertisement.choose_forum,
        AddForum.name, AddForum.link,
        AddChat.link,
        EditForum.enter_name, EditForum.enter_link,
        DeleteForum.select_forum, DeleteForum.confirm,
        EditChat.enter_link,
        DeleteChat.select_chat, DeleteChat.confirm
    ),
    F.text == 'Bekor qilish'
)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Bekor qilindi', reply_markup=admin_choice)


# ── CHAT QO'SHISH ──────────────────────────────────────────────────────────────

@router.message(F.text == "Chat qo'shish")
async def ask_chat_link(message: Message, state: FSMContext):
    await message.answer(
        "Kanal yoki guruh username ini yuboring\n"
        "Masalan: @mychannel yoki t.me/mychannel",
        reply_markup=admin_cancel
    )
    await state.set_state(AddChat.link)


@router.message(AddChat.link, F.text)
async def save_chat(message: Message, state: FSMContext):
    add_chat(message.text)
    await state.clear()
    await message.answer("✅ Chat qo'shildi", reply_markup=admin_choice)


# ── FORUM QO'SHISH ─────────────────────────────────────────────────────────────

@router.message(F.text == "Forum qo'shish")
async def ask_forum_name(message: Message, state: FSMContext):
    await message.answer("Forum nomini kiriting", reply_markup=admin_cancel)
    await state.set_state(AddForum.name)


@router.message(AddForum.name, F.text)
async def ask_forum_link(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Forum linkini kiriting\nMasalan: t.me/myforum", reply_markup=admin_cancel)
    await state.set_state(AddForum.link)


@router.message(AddForum.link, F.text)
async def save_forum(message: Message, state: FSMContext):
    data = await state.get_data()
    add_forum(data['name'], message.text)
    await state.clear()
    await message.answer("✅ Forum qo'shildi", reply_markup=admin_choice)


# ── E'LON YARATISH ─────────────────────────────────────────────────────────────

@router.message(F.text == "E'lon yaratish")
async def ask_content(message: Message, state: FSMContext):
    await message.answer(
        "Matn va rasmni bitta xabarda yuboring",
        reply_markup=admin_cancel
    )
    await state.set_state(CreateAdvertisement.content)


@router.message(CreateAdvertisement.content)
async def show_forums(message: Message, state: FSMContext):
    # Validate message contains photo
    if not message.photo:
        await message.answer(
            "❌ Iltimos, rasm va matn yuboring!\n"
            "Rasmga caption qo'shib yuboring.",
            reply_markup=admin_cancel
        )
        return
    
    forums = forum_list()
    if not forums:
        await message.answer("❌ Hech qanday forum yo'q. Avval forum qo'shing.", reply_markup=admin_choice)
        await state.clear()
        return

    # Store complete message object and initialize selected_forums list
    await state.update_data(content=message, selected_forums=[])
    await message.answer(
        "Qaysi forumlarga yuborish kerak? (Bir nechta tanlash mumkin)",
        reply_markup=forum_choice_keyboard(forums, [])
    )
    await state.set_state(CreateAdvertisement.choose_forum)


@router.callback_query(CreateAdvertisement.choose_forum, F.data.startswith('forum_'))
async def forum_chosen(call: CallbackQuery, state: FSMContext):
    forum_id = int(call.data.split('_')[1])
    data = await state.get_data()
    selected_forums = data.get('selected_forums', [])
    
    # Toggle logic: if forum_id in list, remove it; otherwise add it
    if forum_id in selected_forums:
        selected_forums.remove(forum_id)
    else:
        selected_forums.append(forum_id)
    
    await state.update_data(selected_forums=selected_forums)
    
    # Get all forums and selected forum objects
    all_forums = forum_list()
    selected_forum_objects = [f for f in all_forums if f.forum_id in selected_forums]
    
    # Build preview message
    if selected_forums:
        forum_names = "\n".join([f"• {f.forum_name}" for f in selected_forum_objects])
        preview_text = f"📋 Tanlangan forumlar ({len(selected_forums)}):\n{forum_names}\n\n👇 E'lon preview:"
    else:
        preview_text = "❌ Hech qanday forum tanlanmagan.\n\nForumlarni tanlang:"
    
    # Update keyboard with visual indicators
    await call.message.edit_text(
        preview_text,
        reply_markup=forum_choice_keyboard(all_forums, selected_forums)
    )
    
    # Show preview if forums are selected
    if selected_forums:
        content: Message = data.get('content')
        # Send preview with "Tayyor" button
        await content.copy_to(
            chat_id=call.message.chat.id,
            reply_markup=preview_keyboard()
        )
    
    await call.answer()



@router.callback_query(CreateAdvertisement.choose_forum, F.data == 'ready')
async def send_advertisement(call: CallbackQuery, state: FSMContext):
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    
    data = await state.get_data()
    selected_forums = data.get('selected_forums', [])
    
    # Validate selected_forums is not empty
    if not selected_forums:
        await call.answer("❌ Hech qanday forum tanlanmagan!", show_alert=True)
        return
    
    content: Message = data.get('content')
    all_forums = forum_list()
    selected_forum_objects = [f for f in all_forums if f.forum_id in selected_forums]
    
    # Build inline keyboard with forum buttons
    kb = InlineKeyboardBuilder()
    bot_username = (await call.bot.me()).username
    
    for forum in selected_forum_objects:
        # Create deep link: t.me/botusername?start=forum_name
        deep_link = f"https://t.me/{bot_username}?start={format_link(forum.forum_name)}"
        kb.add(InlineKeyboardButton(
            text=forum.forum_name,
            url=deep_link
        ))
    
    kb.adjust(1)  # One button per row
    
    # Send advertisement with forum buttons
    await content.copy_to(
        chat_id=call.message.chat.id,
        reply_markup=kb.as_markup()
    )
    
    await call.message.answer(
        "✅ E'lon tayyor! Yuqoridagi xabarni forumlarga joylashtiring.",
        reply_markup=admin_choice
    )
    await state.clear()
    await call.answer()


@router.callback_query(CreateAdvertisement.choose_forum, F.data == 'cancel')
async def cancel_advertisement(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Bekor qilindi', reply_markup=admin_choice)
    await call.answer()


# ── FORUM O'ZGARTIRISH ─────────────────────────────────────────────────────────

@router.message(F.text == "Forum o'zgartirish")
async def edit_forum_start(message: Message, state: FSMContext):
    from model import EditForum
    from keyboard import forum_management_keyboard
    
    forums = forum_list()
    if not forums:
        await message.answer("❌ Hech qanday forum yo'q.", reply_markup=admin_choice)
        return
    
    await message.answer(
        "Qaysi forumni o'zgartirmoqchisiz?",
        reply_markup=forum_management_keyboard(forums, 'edit_forum')
    )
    await state.set_state(EditForum.select_forum)


@router.callback_query(EditForum.select_forum, F.data.startswith('edit_forum_'))
async def edit_forum_selected(call: CallbackQuery, state: FSMContext):
    from model import EditForum
    from service import get_forum
    
    forum_id = int(call.data.split('_')[2])
    forum = get_forum(forum_id)
    
    if not forum:
        await call.answer("❌ Forum topilmadi!", show_alert=True)
        return
    
    await state.update_data(forum_id=forum_id)
    await call.message.answer(
        f"📝 Joriy ma'lumotlar:\n"
        f"Nom: {forum.forum_name}\n"
        f"Link: {forum.forum_link}\n\n"
        f"Yangi forum nomini kiriting:",
        reply_markup=admin_cancel
    )
    await state.set_state(EditForum.enter_name)
    await call.answer()


@router.message(EditForum.enter_name, F.text)
async def edit_forum_name(message: Message, state: FSMContext):
    from model import EditForum
    
    if not message.text.strip():
        await message.answer("❌ Forum nomi bo'sh bo'lishi mumkin emas!")
        return
    
    await state.update_data(new_name=message.text.strip())
    await message.answer("Yangi forum linkini kiriting:", reply_markup=admin_cancel)
    await state.set_state(EditForum.enter_link)


@router.message(EditForum.enter_link, F.text)
async def edit_forum_link(message: Message, state: FSMContext):
    from service import update_forum_data
    
    data = await state.get_data()
    forum_id = data['forum_id']
    new_name = data['new_name']
    new_link = message.text.strip()
    
    try:
        update_forum_data(forum_id, new_name, new_link)
        await message.answer(
            f"✅ Forum yangilandi!\n"
            f"Nom: {new_name}\n"
            f"Link: {new_link}",
            reply_markup=admin_choice
        )
    except Exception as e:
        await message.answer(f"❌ Xato: {e}", reply_markup=admin_choice)
    
    await state.clear()


# ── FORUM O'CHIRISH ────────────────────────────────────────────────────────────

@router.message(F.text == "Forum o'chirish")
async def delete_forum_start(message: Message, state: FSMContext):
    from model import DeleteForum
    from keyboard import forum_management_keyboard
    
    forums = forum_list()
    if not forums:
        await message.answer("❌ Hech qanday forum yo'q.", reply_markup=admin_choice)
        return
    
    await message.answer(
        "Qaysi forumni o'chirmoqchisiz?",
        reply_markup=forum_management_keyboard(forums, 'delete_forum')
    )
    await state.set_state(DeleteForum.select_forum)


@router.callback_query(DeleteForum.select_forum, F.data.startswith('delete_forum_'))
async def delete_forum_selected(call: CallbackQuery, state: FSMContext):
    from model import DeleteForum
    from service import get_forum
    from keyboard import confirmation_keyboard
    
    forum_id = int(call.data.split('_')[2])
    forum = get_forum(forum_id)
    
    if not forum:
        await call.answer("❌ Forum topilmadi!", show_alert=True)
        return
    
    await state.update_data(forum_id=forum_id)
    await call.message.answer(
        f"⚠️ Rostdan ham o'chirmoqchimisiz?\n\n"
        f"Forum: {forum.forum_name}\n"
        f"Link: {forum.forum_link}",
        reply_markup=confirmation_keyboard('delete_forum', forum_id)
    )
    await state.set_state(DeleteForum.confirm)
    await call.answer()


@router.callback_query(DeleteForum.confirm, F.data.startswith('confirm_delete_forum_'))
async def delete_forum_confirmed(call: CallbackQuery, state: FSMContext):
    from service import remove_forum
    
    data = await state.get_data()
    forum_id = data['forum_id']
    
    try:
        remove_forum(forum_id)
        await call.message.answer("✅ Forum o'chirildi!", reply_markup=admin_choice)
    except Exception as e:
        await call.message.answer(f"❌ Xato: {e}", reply_markup=admin_choice)
    
    await state.clear()
    await call.answer()


# ── CHAT O'ZGARTIRISH ──────────────────────────────────────────────────────────

@router.message(F.text == "Chat o'zgartirish")
async def edit_chat_start(message: Message, state: FSMContext):
    from model import EditChat
    from keyboard import chat_management_keyboard
    from service import chat_list
    
    chats = chat_list()
    if not chats:
        await message.answer("❌ Hech qanday chat yo'q.", reply_markup=admin_choice)
        return
    
    await message.answer(
        "Qaysi chatni o'zgartirmoqchisiz?",
        reply_markup=chat_management_keyboard(chats, 'edit_chat')
    )
    await state.set_state(EditChat.select_chat)


@router.callback_query(EditChat.select_chat, F.data.startswith('edit_chat_'))
async def edit_chat_selected(call: CallbackQuery, state: FSMContext):
    from model import EditChat
    from service import get_chat
    
    chat_id = int(call.data.split('_')[2])
    chat = get_chat(chat_id)
    
    if not chat:
        await call.answer("❌ Chat topilmadi!", show_alert=True)
        return
    
    await state.update_data(chat_id=chat_id)
    await call.message.answer(
        f"📝 Joriy link: {chat.chat_link}\n\n"
        f"Yangi chat linkini kiriting:",
        reply_markup=admin_cancel
    )
    await state.set_state(EditChat.enter_link)
    await call.answer()


@router.message(EditChat.enter_link, F.text)
async def edit_chat_link(message: Message, state: FSMContext):
    from service import update_chat_data
    
    data = await state.get_data()
    chat_id = data['chat_id']
    new_link = message.text.strip()
    
    try:
        update_chat_data(chat_id, new_link)
        await message.answer(
            f"✅ Chat yangilandi!\n"
            f"Link: {new_link}",
            reply_markup=admin_choice
        )
    except Exception as e:
        await message.answer(f"❌ Xato: {e}", reply_markup=admin_choice)
    
    await state.clear()


# ── CHAT O'CHIRISH ─────────────────────────────────────────────────────────────

@router.message(F.text == "Chat o'chirish")
async def delete_chat_start(message: Message, state: FSMContext):
    from model import DeleteChat
    from keyboard import chat_management_keyboard
    from service import chat_list
    
    chats = chat_list()
    if not chats:
        await message.answer("❌ Hech qanday chat yo'q.", reply_markup=admin_choice)
        return
    
    await message.answer(
        "Qaysi chatni o'chirmoqchisiz?",
        reply_markup=chat_management_keyboard(chats, 'delete_chat')
    )
    await state.set_state(DeleteChat.select_chat)


@router.callback_query(DeleteChat.select_chat, F.data.startswith('delete_chat_'))
async def delete_chat_selected(call: CallbackQuery, state: FSMContext):
    from model import DeleteChat
    from service import get_chat
    from keyboard import confirmation_keyboard
    
    chat_id = int(call.data.split('_')[2])
    chat = get_chat(chat_id)
    
    if not chat:
        await call.answer("❌ Chat topilmadi!", show_alert=True)
        return
    
    await state.update_data(chat_id=chat_id)
    await call.message.answer(
        f"⚠️ Rostdan ham o'chirmoqchimisiz?\n\n"
        f"Chat: {chat.chat_link}",
        reply_markup=confirmation_keyboard('delete_chat', chat_id)
    )
    await state.set_state(DeleteChat.confirm)
    await call.answer()


@router.callback_query(DeleteChat.confirm, F.data.startswith('confirm_delete_chat_'))
async def delete_chat_confirmed(call: CallbackQuery, state: FSMContext):
    from service import remove_chat
    
    data = await state.get_data()
    chat_id = data['chat_id']
    
    try:
        remove_chat(chat_id)
        await call.message.answer("✅ Chat o'chirildi!", reply_markup=admin_choice)
    except Exception as e:
        await call.message.answer(f"❌ Xato: {e}", reply_markup=admin_choice)
    
    await state.clear()
    await call.answer()
