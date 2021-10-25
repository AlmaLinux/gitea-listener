System overview 
---

Git-listener is a flow that is called from the webhook of the git-service for AlmaLinux. This call records data from the webhook into the MQTT queue. The data from the MQTT queue can be read by any service that is signed up to this queue. And any service can do everything that is needed by service's logic. 

Mentioned tools and libraries are required for gitea-listener to run in the current state:
- PostgreSQL == 13
- Mosquitto
- Docker
- Docker-compose


Running docker-compose 
---

You can start the system using the Docker Compose tool.

Pre-requisites:
- `docker` and `docker-compose` tools are installed and set up;

To start the system, run the following command: `docker-compose up -d`. To rebuild images after your local changes, just run `docker-compose up -d --build`.


Configs
---

Gitea-listener has 2 endpoints. Each of them can be added to the webhook. Any event can be recorded to a queue that depends on the endpoint. 

Mosquitto has its config file for the MQTT queue service:
```
{
per_listener_settings true

persistence true
persistence_location /mosquitto/data/

listener 1883
allow_anonymous false
password_file /mosquitto/config/passwd_file
}
```

Gitea-listener has one more config file that contains data for connection to MQTT: 
```
{
mqtt_host: mosquitto
mqtt_port: 1883
mqtt_user:
mqtt_password:
mqtt_topic_modified_repo: gitea-webhooks-modified
mqtt_topic_unmodified_repo: gitea-webhooks-unmodified
}
```

Both of the config files are included in the gitea-listener repository.


Scheduling tasks
---

There are 2 endpoints for the gitea-listener:
```ruby
/process-event-modified-repo #  is used for the repository that contains differences between AlmaLinux and CentOS creation. The message goes to gitea-webhooks-modified queue.
```

```ruby
/process-event-unmodified-repo # is used for unmodified repositories. The message goes to gitea-webhooks-unmodified queue. 
```

Reporting issues 
---

All issues should be reported to the [Build System project](https://github.com/AlmaLinux/build-system).