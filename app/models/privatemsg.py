from typing import Dict, List, Union

from pydantic import BaseModel


class Sender(BaseModel):
    user_id: int
    nickname: str
    card: str


class MessageContent(BaseModel):
    type: str
    data: Dict[str, Union[str | int]]


class PrivateMsg(BaseModel):
    self_id: int
    user_id: int
    time: int
    message_id: int
    message_seq: int
    message_type: str
    sender: Sender
    raw_message: str
    font: int
    sub_type: str
    message: List[MessageContent]
    message_format: str
    post_type: str


class GroupMsg(BaseModel):
    self_id: int
    user_id: int
    time: int
    message_id: int
    message_seq: int
    message_type: str
    sender: Sender
    raw_message: str
    font: int
    sub_type: str
    message: List[MessageContent]
    message_format: str
    post_type: str
    group_id: int
