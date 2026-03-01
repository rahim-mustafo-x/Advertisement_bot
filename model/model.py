from dataclasses import dataclass
from aiogram.fsm.state import StatesGroup, State


@dataclass
class Forum:
    forum_id: int
    forum_name: str
    forum_link: str

    def __str__(self) -> str:
        return f'forum_id={self.forum_id}, name={self.forum_name}, link={self.forum_link}'


@dataclass
class Chat:
    chat_id: int
    chat_link: str

    def __str__(self) -> str:
        return f'chat_id={self.chat_id}, chat_link={self.chat_link}'


class CreateAdvertisement(StatesGroup):
    content = State()
    choose_forum = State()


class AddForum(StatesGroup):
    name = State()
    link = State()


class AddChat(StatesGroup):
    link = State()


class EditForum(StatesGroup):
    select_forum = State()
    enter_name = State()
    enter_link = State()


class DeleteForum(StatesGroup):
    select_forum = State()
    confirm = State()


class EditChat(StatesGroup):
    select_chat = State()
    enter_link = State()


class DeleteChat(StatesGroup):
    select_chat = State()
    confirm = State()