from pydantic import BaseModel


__all__ = ['Config']


class Config(BaseModel):
    mqtt_host: str
    mqtt_port: str
    mqtt_user: str
    mqtt_password: str
    mqtt_topic_modified_repo: str
    mqtt_topic_unmodified_repo: str
    log_level: str = 'INFO'
