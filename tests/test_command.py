from mock import MagicMock
from nose.tools import assert_equals

from remotespark.livyclientlib.command import Command
from remotespark.utils.constants import SESSION_KIND_SPARK
import remotespark.utils.configuration as conf
from . import test_livysession as tls


def test_execute():
    kind = SESSION_KIND_SPARK
    http_client = MagicMock()
    http_client.post_session.return_value = tls.TestLivySession.session_create_json
    http_client.post_statement.return_value = tls.TestLivySession.post_statement_json
    http_client.get_session.return_value = tls.TestLivySession.ready_sessions_json
    http_client.get_statement.return_value = tls.TestLivySession.ready_statement_json
    conf.override_all({
        "status_sleep_seconds": 0.01,
        "statement_sleep_seconds": 0.01
    })
    session = tls.TestLivySession._create_session(kind=kind, http_client=http_client)
    conf.load()
    session.start(create_sql_context=False)
    command = Command("command")

    result = command.execute(session)

    http_client.post_statement.assert_called_with(0, {"code": command.code})
    http_client.get_statement.assert_called_with(0, 0)
    assert result[0]
    assert_equals(tls.TestLivySession.pi_result, result[1])