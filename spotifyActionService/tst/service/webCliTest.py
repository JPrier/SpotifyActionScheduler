import pytest
import service.web_cli as under_test
from click.testing import CliRunner


def test_web_cli_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    runner = CliRunner()
    calls: list[tuple[str, int]] = []

    class DummyApp:
        def run(self, host: str, port: int) -> None:
            calls.append((host, port))

    monkeypatch.setattr(under_test, "create_app", lambda: DummyApp())

    result = runner.invoke(under_test.run, ["--host", "0.0.0.0", "--port", "1234"])
    assert result.exit_code == 0
    assert calls == [("0.0.0.0", 1234)]
