import requests

from django.conf import settings


class RisApiSession(requests.Session):
    def __init__(self, api):
        super().__init__()

        config = settings.RIS_APIS[api]

        self.base_url = config["url"]
        if self.base_url[-1] != "/":
            self.base_url += "/"

        self.headers = {
            'DB-Client-ID': config["client_id"],
            'DB-Api-Key': config["api_key"],
        }

    def request(self, method, url, *args, **kwargs):
        return super().request(method, self.base_url + url, *args, **kwargs)
