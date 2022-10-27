from typing import Union
from httpx import AsyncClient
from aiogram import Bot, Dispatcher
from settings import settings
import docker

DOCKER_CLIENT = docker.DockerClient(base_url='unix://var/run/docker.sock')
RUNNING = 'running'

bot = Bot(token=settings.TOKEN.get_secret_value())
dp = Dispatcher(bot=bot)


class MonitoringService:

    @staticmethod
    async def get_requeest(url: str, params: dict, prefix: str):
        async with AsyncClient() as cliient:
            return await cliient.get(f'{url}{prefix}', params=params)
    
    @staticmethod
    async def get_message_web(status_code: int) -> str:
        return f'status code is {status_code}, check service'

    @staticmethod
    async def send_message(chat_id: Union[str, int], message: str):
        await bot.send_message(chat_id, message)
    
    @staticmethod
    async def get_container_message(container_name: str, status: bool) -> str:
        return f'{container_name} work status {status}'

    @staticmethod
    def get_stay_container(container_name: str = None) ->bool:
        container = DOCKER_CLIENT.containers.get(container_name)
        container_state = container.attrs['State']
        container_is_running = container_state['Status'] == RUNNING
        return container_is_running