from  services import MonitoringService
from settings import settings
import asyncio
from httpx import ConnectTimeout, ConnectError
import logging

file_log = logging.FileHandler('Log.log')
console_out = logging.StreamHandler()

logging.basicConfig(handlers=(file_log, console_out), 
                    format='[%(asctime)s | %(levelname)s]: %(message)s', 
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.INFO)


servisces: MonitoringService = MonitoringService()
TIMEOUT = 30
containers_list = [
    'garnet_decider_container', 'garnet_core_container', 'garnet_adminka_mock_container',
    'garnet_scraper_container', 'garnet_gui_container', 'garnet_db_container', 'garnet_rabbit_container',
    # 'garnet_clean_service_container'
]

async def main():
    while True:
        for name_con in containers_list:
            status = servisces.get_stay_container(name_con)
            if not status:
                cont_msg = await servisces.get_container_message(container_name=name_con, status=status)
                logging.error(cont_msg)
                await servisces.send_message(chat_id=settings.CHAT_ID, message=cont_msg)
        try:
            response = await servisces.get_requeest(
                url=settings.BASE_URL,
                prefix=settings.PREFIX,
                params={'api_key': settings.APIKEY}
            )
        except ConnectTimeout:
            msg_timeout = 'host or internet problem, connect timeout error, will try after 30 sec'
            logging.error(msg_timeout)
            await asyncio.sleep(TIMEOUT)
            continue
        except ConnectError:
            msg_connect_err = 'garnet core is not work, will try after 30 sec'
            logging.error(msg_connect_err)
            await asyncio.sleep(TIMEOUT)
            continue
        if response.status_code != 200:
            web_msg = await servisces.get_message_web(status_code=response.status_code)
            await servisces.send_message(chat_id=settings.CHAT_ID, messge=web_msg)
            logging.error(f'status_code web {response.status_code}')
        await asyncio.sleep(TIMEOUT)

if __name__ == "__main__":
    asyncio.run(main())
