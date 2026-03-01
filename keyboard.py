from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from model import Forum, Chat


# ── REPLY KEYBOARDS ────────────────────────────────────────────────────────────

admin_choice = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Chat qo'shish"), KeyboardButton(text="Forum qo'shish")],
        [KeyboardButton(text="Chat o'zgartirish"), KeyboardButton(text="Forum o'zgartirish")],
        [KeyboardButton(text="Chat o'chirish"), KeyboardButton(text="Forum o'chirish")],
        [KeyboardButton(text="E'lon yaratish")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

admin_cancel = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Bekor qilish')]],
    resize_keyboard=True,
    one_time_keyboard=True
)

admin_adv_ready = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Tayyor')],
        [KeyboardButton(text='Bekor qilish')]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)


# ── INLINE KEYBOARDS ───────────────────────────────────────────────────────────

def forum_choice_keyboard(forums: list[Forum], selected: list[int] = None) -> InlineKeyboardMarkup:
    """
    Creates inline keyboard with visual indication of selected forums.
    Selected forums are prefixed with ✅.
    """
    if selected is None:
        selected = []
    
    kb = InlineKeyboardBuilder()
    for forum in forums:
        prefix = "✅ " if forum.forum_id in selected else ""
        kb.add(InlineKeyboardButton(
            text=f"{prefix}{forum.forum_name}",
            callback_data=f"forum_{forum.forum_id}"
        ))
    return kb.adjust(2).as_markup()


def preview_keyboard() -> InlineKeyboardMarkup:
    """
    Creates keyboard with Ready and Cancel buttons for advertisement preview.
    """
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="✅ Tayyor", callback_data="ready"))
    kb.add(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return kb.adjust(2).as_markup()


def forum_management_keyboard(forums: list[Forum], action: str) -> InlineKeyboardMarkup:
    """
    Creates inline keyboard for selecting a forum to edit or delete.
    action: 'edit_forum' or 'delete_forum'
    """
    kb = InlineKeyboardBuilder()
    for forum in forums:
        kb.add(InlineKeyboardButton(
            text=forum.forum_name,
            callback_data=f"{action}_{forum.forum_id}"
        ))
    return kb.adjust(2).as_markup()


def chat_management_keyboard(chats: list[Chat], action: str) -> InlineKeyboardMarkup:
    """
    Creates inline keyboard for selecting a chat to edit or delete.
    action: 'edit_chat' or 'delete_chat'
    """
    kb = InlineKeyboardBuilder()
    for chat in chats:
        kb.add(InlineKeyboardButton(
            text=chat.chat_link,
            callback_data=f"{action}_{chat.chat_id}"
        ))
    return kb.adjust(2).as_markup()


def confirmation_keyboard(action: str, entity_id: int) -> InlineKeyboardMarkup:
    """
    Creates confirmation keyboard for delete operations.
    """
    kb = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_{action}_{entity_id}"))
    kb.add(InlineKeyboardButton(text="❌ Yo'q", callback_data="cancel"))
    return kb.adjust(1).as_markup()


def subscribe_keyboard(chats: list[Chat], forum_name: str) -> InlineKeyboardMarkup:
    """Obuna bo'lmagan kanallar + tekshirish tugmasi"""
    kb = InlineKeyboardBuilder()
    for chat in chats:
        kb.add(InlineKeyboardButton(
            text=f"📢 {chat.chat_link}",
            url=f"https://t.me/{chat.chat_link.lstrip('@')}"
        ))
    kb.row(InlineKeyboardButton(
        text="✅ Tekshirish",
        callback_data=f"check_{forum_name}"
    ))
    return kb.adjust(1).as_markup()