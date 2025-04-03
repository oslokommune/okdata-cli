import logging

from okdata.sdk import SDK

log = logging.getLogger()


class PubsClient(SDK):
    def __init__(self, config=None, auth=None, env=None):
        self.__name__ = "pubs"
        super().__init__(config, auth, env)
        self.api_url = "https://api.data{}.oslo.systems/maskinporten".format(
            "-dev" if self.config.config["env"] == "dev" else ""
        )

    def create_maskinporten_client(self, team_id, provider, integration, scopes, env):
        data = {
            "client_type": "maskinporten",
            "team_id": team_id,
            "provider": provider,
            "integration": integration,
            "scopes": scopes,
            "env": env,
        }
        log.info(f"Creating Maskinporten client with payload: {data}")
        return self.post(f"{self.api_url}/clients", data=data).json()

    def create_idporten_client(
        self,
        team_id,
        integration,
        client_uri,
        frontchannel_logout_uri,
        redirect_uris,
        post_logout_redirect_uris,
        env,
    ):
        data = {
            "client_type": "idporten",
            "team_id": team_id,
            "provider": "idporten",
            "integration": integration,
            "client_uri": client_uri,
            "frontchannel_logout_uri": frontchannel_logout_uri,
            "redirect_uris": redirect_uris,
            "post_logout_redirect_uris": post_logout_redirect_uris,
            "env": env,
        }
        log.info(f"Creating ID-porten client with payload: {data}")
        return self.post(f"{self.api_url}/clients", data=data).json()

    def get_clients(self, env):
        url = f"{self.api_url}/clients/{env}"
        log.info(f"Listing clients from: {url}")
        return self.get(url).json()

    def delete_client(self, env, client_id, aws_account, aws_region):
        url = f"{self.api_url}/clients/{env}/{client_id}/delete"
        log.info(f"Deleting client for: {url}")
        return self.post(
            url,
            data={
                "aws_account": aws_account,
                "aws_region": aws_region,
            },
        ).json()

    def create_key(
        self,
        env,
        client_id,
        aws_account,
        aws_region,
        enable_auto_rotate,
    ):
        url = f"{self.api_url}/clients/{env}/{client_id}/keys"
        log.info(f"Creating key for: {url}")
        return self.post(
            url,
            data={
                "destination_aws_account": aws_account,
                "destination_aws_region": aws_region,
                "enable_auto_rotate": enable_auto_rotate,
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

    def get_audit_log(self, env, client_id):
        url = f"{self.api_url}/audit/{env}/{client_id}/log"
        log.info(f"Fetching audit log from: {url}")
        return self.get(url).json()


class ProvidersClient(SDK):
    def __init__(self, config=None, auth=None, env=None):
        self.__name__ = "providers"
        super().__init__(config, auth, env)
        self.api_url = "https://api.data{}.oslo.systems/maskinporten/providers".format(
            "-dev" if self.config.config["env"] == "dev" else ""
        )

    def get_providers(self):
        log.info(f"Listing providers from: {self.api_url}")
        providers = self.get(self.api_url).json()
        return {p["provider_id"]: p["name"] for p in providers}


class ScopesClient(SDK):
    def __init__(self, config=None, auth=None, env=None):
        self.__name__ = "scopes"
        super().__init__(config, auth, env)
        self.api_url = "https://api.data{}.oslo.systems/maskinporten/scopes".format(
            "-dev" if self.config.config["env"] == "dev" else ""
        )

    def get_scopes(self):
        log.info(f"Listing scopes from: {self.api_url}")
        scopes = self.get(self.api_url).json()
        scopes_dict = {}
        for scope in scopes:
            scopes_dict.setdefault(scope["provider_id"], []).append(scope["scope"])
        return scopes_dict
