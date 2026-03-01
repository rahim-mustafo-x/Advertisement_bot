from dataclasses import dataclass

@dataclass
class Forum:
    forum_id:int
    forum_name:str
    forum_link:str

    def __str__(self)->str:
        return f'forum_id={self.forum_id}, name={self.forum_name}, link={self.forum_link}'

@dataclass
class Chat:
    chat_id:int
    chat_link:str
    def __str__(self)->str:
        return f'chat_id={self.chat_id}, chat_link={self.chat_link}'