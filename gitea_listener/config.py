from pydantic import BaseModel


__all__ = ['Config']


class Config(BaseModel):
    mqtt_host: str
    mqtt_port: str
    mqtt_topic: str
    log_level: str = 'INFO'
