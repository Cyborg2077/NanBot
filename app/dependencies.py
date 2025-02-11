from typing import Dict, Any
from app.utils.msgcache import MsgCache
from app.config import Config
from openai import OpenAI


class GlobalDependencies:
    config: Dict[str, Any] = None
    llm_client: OpenAI = None
    msg_cache: MsgCache = None

    @classmethod
    def initialize(cls):
        if not cls.config:
            cls.config = Config.load_config()

        if not cls.llm_client:
            cls.llm_client = OpenAI(
                api_key=cls.config['openai']['api_key'],
                base_url=cls.config['openai']['base_url'],
            )

        if not cls.msg_cache:
            cls.msg_cache = MsgCache()


deps = GlobalDependencies()
