from ast import While
from math import pi
from  services import MonitoringService
from settings import settings
import asyncio
from httpx import ConnectTimeout, ConnectError
from logger import logger
from docker.errors import NotFound

hash_status_containers = {
    'garnet_decider_container': False,
    'garnet_core_container': False,
    'garnet_adminka_mock_container': False,
    'garnet_scraper_container': False,
    'garnet_gui_container': False,
    'garnet_db_container': False,
    'garnet_rabbit_container': False
}

TIMEOUT = 1
DELAY = 30
containers_list = [
    'garnet_decider_container', 'garnet_core_container', 'garnet_adminka_mock_container',
    'garnet_scraper_container', 'garnet_gui_container', 'garnet_db_container', 'garnet_rabbit_container'
]

async def docker_container_checker(hash_status_containers: dict, services: MonitoringService):
    for name_con in containers_list:
        try:
            status = services.get_stay_container(name_con)
            if not status:
                cont_msg_err = await services.get_container_message(container_name=name_con, status=status)
                logger.error(cont_msg_err)
                hash_status_containers[name_con] = False
                await services.send_message(chat_id=settings.CHAT_ID, message=cont_msg_err)
            elif not hash_status_containers[name_con]:
                msg_successful = f'{name_con} connect successful'
                logger.info(msg_successful)
                hash_status_containers[name_con] = True
                await services.send_message(chat_id=settings.CHAT_ID, message=msg_successful)
        except NotFound:
            logger.error(f'container {name_con} not found, you need build container')
    await asyncio.sleep(TIMEOUT)


async def ping_service(services: MonitoringService):
    try:
        response = await services.get_requeest(
            url=settings.BASE_URL,
            prefix=settings.PREFIX,
            params={'api_key': settings.APIKEY}
        )
    except ConnectTimeout:
        connect_time_msg = 'host or internet problem, connect timeout error, will try in 30 sec'
        logger.error(connect_time_msg)
        await services.send_message(chat_id=settings.CHAT_ID, message=connect_time_msg)
    except ConnectError:
        connect_msg = 'garnet core is not work, will try in 30 sec'
        logger.error(connect_msg)
        await services.send_message(chat_id=settings.CHAT_ID, message=connect_msg)
    try:
        if response.status_code != 200:
            web_msg = await services.get_message_web(status_code=response.status_code)
            await services.send_message(chat_id=settings.CHAT_ID, messge=web_msg)
            logger.error(web_msg)
    except UnboundLocalError:
        logger.error('the request cannot be made, there is no connection to the service')
    await asyncio.sleep(TIMEOUT)


async def bot_starting():
    services: MonitoringService = MonitoringService()
    while True:
        await docker_container_checker(services=services, hash_status_containers=hash_status_containers)
        await ping_service(services=services)
        await asyncio.sleep(DELAY)


if __name__ == "__main__":
    try:
        asyncio.run(bot_starting())
    except KeyboardInterrupt:
        logger.info('you stopped the scan')
    except Exception as err:
        logger.warning(err)