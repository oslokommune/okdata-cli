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

    def create_client(self, team_id, provider, integration, scopes, env):
        data = {
            "team_id": team_id,
            "provider": provider,
            "integration": integration,
            "scopes": scopes,
            "env": env,
        }
        log.info(f"Creating client with payload: {data}")
        return self.post(f"{self.api_url}/clients", data=data).json()

    def get_clients(self, env):
        url = f"{self.api_url}/clients/{env}"
        log.info(f"Listing clients from: {url}")
        return self.get(url).json()

    def delete_client(self, env, client_id):
        url = f"{self.api_url}/clients/{env}/{client_id}"
        log.info(f"Deleting client for: {url}")
        return self.delete(url).json()

    def create_key(self, env, client_id, aws_account=None, aws_region=None):
        url = f"{self.api_url}/clients/{env}/{client_id}/keys"
        log.info(f"Creating key for: {url}")
        return self.post(
            url,
            data={
                "destination_aws_account": aws_account,
                "destination_aws_region": aws_region,
            },
        ).json()

    def delete_key(self, env, client_id, key_id):
        url = f"{self.api_url}/clients/{env}/{client_id}/keys/{key_id}"
        log.info(f"Deleting key: {url}")
        return self.delete(url)

    def get_keys(self, env, client_id):
        url = f"{self.api_url}/clients/{env}/{client_id}/keys"
        log.info(f"Listing keys from: {url}")
        return self.get(url).json()
