from db import forums, insert_forum, insert_chat, chats, create_tables


def create_db():
    create_tables()


def add_chat(link: str):
    insert_chat(format_link(link))


def add_forum(name: str, link: str):
    insert_forum(name, link)


def forum_list():
    return forums()


def chat_list():
    return chats()


def format_link(link: str) -> str:
    """
    Normalizes link/username to standard format.
    
    Handles formats:
    - "https://t.me/username" -> "username"
    - "t.me/username" -> "username"
    - "@username" -> "username"
    - "username" -> "username"
    - "t.me/username/123" -> "username"
    
    Returns lowercase for consistent comparison.
    """
    link = link.strip()
    for prefix in ['https://t.me/', 't.me/', '@']:
        if link.startswith(prefix):
            link = link[len(prefix):]
            break
    return link.split('/')[0].lower()


def find_forum_by_name(name: str):
    """
    Finds forum by name with case-insensitive matching.
    
    Returns Forum object or None.
    """
    all_forums = forums()
    if not all_forums:
        return None
    
    normalized_name = format_link(name)
    for forum in all_forums:
        if format_link(forum.forum_name) == normalized_name:
            return forum
    return None


def get_forum(forum_id: int):
    from db import get_forum_by_id
    return get_forum_by_id(forum_id)


def update_forum_data(forum_id: int, name: str, link: str):
    from db import update_forum
    update_forum(forum_id, name, format_link(link))


def remove_forum(forum_id: int):
    from db import delete_forum
    delete_forum(forum_id)


def get_chat(chat_id: int):
    from db import get_chat_by_id
    return get_chat_by_id(chat_id)


def update_chat_data(chat_id: int, link: str):
    from db import update_chat
    update_chat(chat_id, format_link(link))


def remove_chat(chat_id: int):
    from db import delete_chat
    delete_chat(chat_id)
