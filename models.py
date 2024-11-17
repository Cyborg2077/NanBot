from typing import List, Dict

from pydantic import BaseModel


class Sender(BaseModel):
    user_id: int
    nickname: str
    card: str


class MessageContent(BaseModel):
    type: str
    data: Dict[str, str]


class Msg(BaseModel):
    self_id: int
    user_id: int
    time: int
    message_id: int
    real_id: int
    message_seq: int
    message_type: str
    sender: Sender
    raw_message: str
    font: int
    sub_type: str
    message: List[MessageContent]
    message_format: str
    post_type: str
