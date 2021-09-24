import logging

from okdata.sdk import SDK

log = logging.getLogger()


class PubregClient(SDK):
    def __init__(self, config=None, auth=None, env=None):
        self.__name__ = "pubreg"
        super().__init__(config, auth, env)
        self.api_url = "https://api.data{}.oslo.systems/maskinporten".format(
            "-dev" if self.config.config["env"] == "dev" else ""
        )

    def create_client(self, env, name, scopes):
        data = {"env": env, "name": name, "description": name, "scopes": scopes}
        log.info(f"Creating client with payload: {data}")
        return self.post(f"{self.api_url}/clients", data=data).json()

    def get_keys(self, env, client_id):
        url = f"{self.api_url}/clients/{env}/{client_id}/keys"
        log.info(f"Listing keys from: {url}")
        return self.get(url).json()
