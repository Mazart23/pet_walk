from __future__ import annotations
from dataclasses import dataclass

import yaml


@dataclass
class Service:
    http: str
    ip_host: str
    ip: str
    port: str

    @classmethod
    def load(cls, service: str) -> Service:
        with open('/app/config/apps.yaml', 'r') as file:
            config = yaml.safe_load(file)['services'][service]
        return cls(
            http=config['http'],
            ip_host=config['ip_host'],
            ip=config['ip'],
            port=config['port']
        )


class Services:
    CLIENT = Service.load('client')
    CONTROLLER = Service.load('controller')
    REDIRECTER = Service.load('redirecter')
    NOTIFIER = Service.load('notifier')
    

class Url:
    
    @classmethod
    def load_external_url(service: str) -> str:
        with open('/app/config/apps.yaml', 'r') as file:
            url = yaml.safe_load(file)['external'][service]['url']
        return url

    IMGUR = load_external_url.__func__('imgur')
