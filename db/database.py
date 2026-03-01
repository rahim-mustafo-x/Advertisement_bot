import sqlite3
from model import (Forum, Chat)
from os import makedirs

makedirs('database', exist_ok=True)
db = sqlite3.connect('database/advertisement.db', check_same_thread=False)
cursor = db.cursor()

#forum
forum_table_name = 'forum_link'
forum_id = 'forum_id'
forum_name = 'forum_name'
forum_link = 'forum_link'

#chat
chat_table_name = 'chat'
chat_id = 'chat_id'
chat_link = 'chat_link'

def create_tables():
    try:
        cursor.execute(f'''
        create table if not exists {forum_table_name}
        (
        {forum_id} integer primary key autoincrement unique,
        {forum_name} text not null,
        {forum_link} text not null unique)
        ''')
        cursor.execute(f'''
        create table if not exists {chat_table_name}
        (
        {chat_id} integer primary key autoincrement unique,
        {chat_link} text not null unique
        )
''')
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in creating tables {error}')

def insert_forum(name:str, link:str):
    try:
        cursor.execute(f'''
        insert into {forum_table_name} ({forum_name}, {forum_link}) values (?,?)''',
        (name,link))
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in insert forum {error}')

def insert_chat(link:str):
    try:
        cursor.execute(f'''
    insert into {chat_table_name} ({chat_link}) values (?)''',
                       (link,))
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in insert chat {error}')

def chats():
    try:
        cursor.execute(f'''select {chat_id}, {chat_link} from {chat_table_name}''')
        rows = cursor.fetchall()
        return [Chat(chats_id, link) for chats_id, link in rows] if rows else []
    except sqlite3.Error as error:
        print(f'there is an error in returning chats {error}')
        return []
def forums():
    try:
        cursor.execute(f'''select {forum_id}, {forum_name}, {forum_link} from {forum_table_name}''')
        rows = cursor.fetchall()
        return [Forum(forums_id, name, link) for forums_id, name, link in rows] if rows else []
    except sqlite3.Error as error:
        print(f'there is an error in returning forums {error}')
        return []


def get_forum_by_id(forum_id_value: int):
    try:
        cursor.execute(f'''select {forum_id}, {forum_name}, {forum_link} from {forum_table_name} where {forum_id}=?''', (forum_id_value,))
        row = cursor.fetchone()
        return Forum(row[0], row[1], row[2]) if row else None
    except sqlite3.Error as error:
        print(f'there is an error in get forum by id {error}')
        return None


def update_forum(forum_id_value: int, name: str, link: str):
    try:
        cursor.execute(f'''update {forum_table_name} set {forum_name}=?, {forum_link}=? where {forum_id}=?''',
                       (name, link, forum_id_value))
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in update forum {error}')


def delete_forum(forum_id_value: int):
    try:
        cursor.execute(f'''delete from {forum_table_name} where {forum_id}=?''', (forum_id_value,))
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in delete forum {error}')


def get_chat_by_id(chat_id_value: int):
    try:
        cursor.execute(f'''select {chat_id}, {chat_link} from {chat_table_name} where {chat_id}=?''', (chat_id_value,))
        row = cursor.fetchone()
        return Chat(row[0], row[1]) if row else None
    except sqlite3.Error as error:
        print(f'there is an error in get chat by id {error}')
        return None


def update_chat(chat_id_value: int, link: str):
    try:
        cursor.execute(f'''update {chat_table_name} set {chat_link}=? where {chat_id}=?''',
                       (link, chat_id_value))
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in update chat {error}')


def delete_chat(chat_id_value: int):
    try:
        cursor.execute(f'''delete from {chat_table_name} where {chat_id}=?''', (chat_id_value,))
        db.commit()
    except sqlite3.Error as error:
        print(f'there is an error in delete chat {error}')
