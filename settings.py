from pydantic import BaseSettings, SecretStr
from typing import Union


class Settings(BaseSettings):
    TOKEN: SecretStr
    CHAT_ID: Union[str, int]
    BASE_URL: str
    PREFIX: str
    APIKEY: str

    class Config:
        env_file = '.env_develop'
        env_file_encoding = 'utf-8'


settings = Settings()
