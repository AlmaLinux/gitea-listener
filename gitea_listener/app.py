import json
import logging
import os.path

from fastapi import FastAPI
from paho.mqtt.client import Client
from ruamel.yaml import YAML

from gitea_listener.config import Config
from gitea_listener.encoders import DateTimeEncoder
from gitea_listener.models import PushEvent


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
    mqtt_client.connect(config.mqtt_host, port=int(config.mqtt_port))
    mqtt_client.loop_start()
    logger.info('Connection successful')


@app.on_event('shutdown')
async def shutdown():
    global logger, mqtt_client
    logger.info('Shutting down connection to MQTT...')
    mqtt_client.loop_stop()
    mqtt_client.reconnect()
    logger.info('Connection terminated successfully')


# TODO: Payload could be different for different event types,
#  support all of them in future
@app.post('/process-event')
async def process_event(event_data: PushEvent):
    global mqtt_client, config, logger
    payload_data = event_data.dict()
    logger.debug(f'Publishing event into topic: {payload_data}')
    mqtt_client.publish(config.mqtt_topic, payload=json.dumps(
        payload_data, cls=DateTimeEncoder))
