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
        {forum_link} text not null)
        ''')
        cursor.execute(f'''
        create table if not exists {chat_table_name}
        (
        {chat_id} integer primary key autoincrement unique,
        {chat_link} text not null
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
        return [Chat(chats_id, link) for chats_id, link in rows] or None
    except sqlite3.Error as error:
        print(f'there is an error in returning chats {error}')
        return None