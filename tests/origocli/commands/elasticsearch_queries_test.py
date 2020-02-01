from conftest import set_argv

from origocli.commands.elasticsearch_queries import ElasticsearchQueryCommand


def test_event_stat(mocker):
    set_argv("esq", "eventstat", "some-dataset-id")
    cmd = ElasticsearchQueryCommand()
    mocker.spy(cmd.sdk, "event_stat")
    cmd.handler()
    cmd.sdk.event_stat.assert_called_once_with("some-dataset-id")
