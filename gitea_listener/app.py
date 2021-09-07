import json
import logging
import os.path
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from paho.mqtt.client import Client
from ruamel.yaml import YAML

from gitea_listener.config import Config
from gitea_listener.encoders import DateTimeEncoder
from gitea_listener.models import PushEvent, Response


SERVICE_NAME = 'gitea_listener'
app = FastAPI()
mqtt_client: Client = None
logger: logging.Logger = None
config: Config = None


@app.on_event('startup')
async def startup():
    """Starting up Gitea listener app."""

    config_file_path = os.environ.get('GITEA_LISTENER_CONFIG_FILE')
    if not config_file_path:
        raise ValueError('Config not found, please check '
                         '"GITEA_LISTENER_CONFIG_FILE" environment variable '
                         'is set')
    global mqtt_client, logger, config
    config_file_path = os.path.expanduser(os.path.expandvars(config_file_path))
    loader = YAML(typ='safe')
    with open(config_file_path, 'rt') as f:
        config = Config.parse_obj(loader.load(f))

    logging.basicConfig(level=config.log_level)
    logger = logging.getLogger(SERVICE_NAME)
    logger.info('Starting connection to MQTT...')
    mqtt_client = Client(SERVICE_NAME)
    mqtt_client.username_pw_set(config.mqtt_user, config.mqtt_password)
    mqtt_client.connect(config.mqtt_host, port=int(config.mqtt_port))
    mqtt_client.loop_start()
    logger.info('Connection successful')


@app.on_event('shutdown')
async def shutdown():
    global logger, mqtt_client
    logger.info('Shutting down connection to MQTT...')
    mqtt_client.loop_stop()
    logger.info('Connection terminated successfully')


def _push_data_into_topic(topic_name: str, data: PushEvent,
                          retries: int = 5, time_increment: int = 10) -> bool:
    global mqtt_client, config, logger
    try:
        local_retries = retries
        sleep_time = time_increment
        payload_data = data.dict()
        logger.debug(f'Publishing event into topic: {payload_data}')
        success = False
        send_info = None
        while not success and local_retries > 0:
            send_info = mqtt_client.publish(topic_name, payload=json.dumps(
                payload_data, cls=DateTimeEncoder))
            success = send_info.rc == 0
            if not success:
                time.sleep(sleep_time)
                sleep_time += time_increment
        if not success:
            logger.error(f'Cannot publish the message, MQTT info: {send_info}')
            return False
        logger.info('Data pushed successfully')
        return True
    except Exception as e:
        logger.error(f'Error when publishing data into topic: {e}')
        return False


def _respond(topic_name: str, data: PushEvent) -> JSONResponse:
    success = _push_data_into_topic(topic_name, data)
    if not success:
        return JSONResponse({'ok': False}, status_code=400)
    return JSONResponse({'ok': True}, status_code=201)


@app.post('/process-event-unmodified-repo', response_model=Response,
          responses={201: {'model': Response}, 400: {'model': Response}})
async def process_event_unmodified_repo(event_data: PushEvent):
    """
    Pushes event for unmodified repositories into specified topic

    Parameters
    ----------
    event_data: PushEvent

    Returns
    -------
    JSONResponse

    """
    global logger
    logger.info(f'Got new event: ref {event_data.ref} '
                f'commit_id {event_data.after} from repository '
                f'{event_data.repository.name}')
    return _respond(config.mqtt_topic_unmodified_repo, event_data)


# TODO: Payload could be different for different event types,
#  support all of them in future
@app.post('/process-event-modified-repo', response_model=Response,
          responses={201: {'model': Response}, 400: {'model': Response}})
async def process_event_modified_repo(event_data: PushEvent):
    """
    Pushes event for modified repositories into specified topic

    Parameters
    ----------
    event_data: PushEvent

    Returns
    -------
    JSONResponse

    """
    return _respond(config.mqtt_topic_modified_repo, event_data)
