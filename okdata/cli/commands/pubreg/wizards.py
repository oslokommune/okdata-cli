from questionary import prompt

from okdata.cli.commands.pubreg.questions import (
    _providers,
    q_aws_account,
    q_aws_region,
    q_client,
    q_env,
    q_integration,
    q_key,
    q_provider,
    q_scopes,
    q_send_to_aws,
    q_team,
)


def create_client_wizard(team_client):
    choices = prompt(
        [
            q_env(),
            q_team(team_client),
            q_provider(),
            q_scopes(),
            q_integration(),
        ]
    )
    return {
        "env": choices["env"],
        "team_id": choices.get("team_id"),
        "provider_id": choices["provider_id"],
        "provider_name": _providers[choices["provider_id"]],
        "integration": choices["integration"],
        "scopes": choices["scopes"],
    }


def list_clients_wizard():
    choices = prompt([q_env()])
    return {"env": choices["env"]}


def delete_client_wizard(pubreg_client):
    choices = prompt(
        [
            q_env(),
            q_client(pubreg_client),
        ]
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
    }


def create_key_wizard(pubreg_client):
    choices = prompt(
        [
            q_env(),
            q_client(pubreg_client),
            q_send_to_aws(),
            q_aws_account(),
            q_aws_region(),
        ]
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "aws_account": choices.get("aws_account"),
        "aws_region": choices.get("aws_region"),
    }


def list_keys_wizard(pubreg_client):
    choices = prompt(
        [
            q_env(),
            q_client(pubreg_client),
        ]
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
    }


def delete_key_wizard(pubreg_client):
    choices = prompt(
        [
            q_env(),
            q_client(pubreg_client),
            q_key(pubreg_client),
        ]
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "key_id": choices["key_id"],
    }
