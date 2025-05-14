from okdata.cli.commands.pubs.questions import (
    q_aws_account,
    q_aws_region,
    q_client,
    q_client_type,
    q_client_uri,
    q_delete_from_aws,
    q_enable_auto_rotate,
    q_env,
    q_frontchannel_logout_uri,
    q_integration,
    q_key,
    q_key_destination,
    q_post_logout_redirect_uris,
    q_provider,
    q_redirect_uris,
    q_scopes,
)
from okdata.cli.commands.teams.questions import q_team
from okdata.cli.commands.wizard import run_questionnaire


def create_client_wizard(team_client, providers, scopes):
    choices = run_questionnaire(
        q_env(),
        q_team(team_client),
        q_client_type(),
        q_provider(providers),
        q_scopes(scopes),
        q_integration(),
        q_redirect_uris(),
        q_post_logout_redirect_uris(),
        q_frontchannel_logout_uri(),
        q_client_uri(),
    )
    return {
        "env": choices["env"],
        "team_id": choices.get("team_id"),
        "client_type_id": choices["client_type_id"],
        "provider_id": choices.get("provider_id"),
        "integration": choices["integration"],
        "scopes": choices.get("scopes"),
        "redirect_uris": choices.get("redirect_uris"),
        "post_logout_redirect_uris": choices.get("post_logout_redirect_uris"),
        "frontchannel_logout_uri": choices.get("frontchannel_logout_uri"),
        "client_uri": choices.get("client_uri"),
    }


def list_clients_wizard():
    choices = run_questionnaire(q_env())
    return {"env": choices["env"]}


def delete_client_wizard(pubs_client):
    choices = run_questionnaire(
        q_env(),
        q_client(pubs_client),
        q_delete_from_aws(),
        q_aws_account(),
        q_aws_region(),
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "delete_from_aws": choices["delete_from_aws"],
        "aws_account": choices.get("aws_account"),
        "aws_region": choices.get("aws_region"),
    }


def create_key_wizard(pubs_client):
    choices = run_questionnaire(
        q_env(),
        q_client(pubs_client),
        q_key_destination(),
        q_aws_account(),
        q_aws_region(),
        q_enable_auto_rotate(),
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "key_destination": choices["key_destination"],
        "aws_account": choices.get("aws_account"),
        "aws_region": choices.get("aws_region"),
        "enable_auto_rotate": choices.get("enable_auto_rotate"),
    }


def list_keys_wizard(pubs_client):
    choices = run_questionnaire(q_env(), q_client(pubs_client, True))
    return {
        "env": choices["env"],
        **(
            {
                "clients": choices["client"],
            }
            if isinstance(choices["client"], list)
            else {
                "client_id": choices["client"]["id"],
                "client_name": choices["client"]["name"],
            }
        ),
    }


def delete_key_wizard(pubs_client):
    choices = run_questionnaire(
        q_env(),
        q_client(pubs_client),
        q_key(pubs_client),
    )
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
        "key_id": choices["key_id"],
    }


def audit_log_wizard(pubs_client):
    choices = run_questionnaire(q_env(), q_client(pubs_client))
    return {
        "env": choices["env"],
        "client_id": choices["client"]["id"],
        "client_name": choices["client"]["name"],
    }
