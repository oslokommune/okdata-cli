import sys

from questionary import prompt

from okdata.cli.commands.pubreg.questions import (
    _providers,
    q_aws_account,
    q_aws_region,
    q_client,
    q_env,
    q_integration,
    q_key,
    q_key_destination,
    q_provider,
    q_scopes,
    q_team,
)


def _run_questionnaire(*questions):
    choices = prompt(questions)

    if not choices:
        # Questionnaire was interrupted.
        sys.exit()

    return choices


def create_client_wizard(team_client):
    choices = _run_questionnaire(
        q_env(),
        q_team(team_client),
        q_provider(),
        q_scopes(),
        q_integration(),
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
    choices = _run_questionnaire(q_env())
    return {"env": choices["env"]}


def delete_client_wizard(pubreg_client):
    choices = _run_questionnaire(q_env(), q_client(pubreg_client))
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
    }


def create_key_wizard(pubreg_client):
    choices = _run_questionnaire(
        q_env(),
        q_client(pubreg_client),
        q_key_destination(),
        q_aws_account(),
        q_aws_region(),
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "key_destination": choices["key_destination"],
        "aws_account": choices.get("aws_account"),
        "aws_region": choices.get("aws_region"),
    }


def list_keys_wizard(pubreg_client):
    choices = _run_questionnaire(q_env(), q_client(pubreg_client))
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
    }


def delete_key_wizard(pubreg_client):
    choices = _run_questionnaire(
        q_env(),
        q_client(pubreg_client),
        q_key(pubreg_client),
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "key_id": choices["key_id"],
    }
