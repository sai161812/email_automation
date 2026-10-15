import contextlib
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("email_demo", Path(__file__).resolve().parents[1] / "main.py")
APP = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(APP)


class EmailTests(unittest.TestCase):
    args = ["--to", "fiction@example.test", "--subject", "Demo", "--body", "Fictional content"]

    def test_preview_does_not_load_smtp_library(self):
        with patch.dict(sys.modules, {"yagmail": None}), contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(APP.main(self.args), 0)
        self.assertIn("no email was sent", output.getvalue())

    def test_send_without_credentials_fails_before_smtp(self):
        with patch.dict(APP.os.environ, {}, clear=True), patch.dict(sys.modules, {"yagmail": None}), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(APP.main(self.args + ["--send"]), 2)

    def test_import_has_no_delivery_side_effect(self):
        with patch.dict(sys.modules, {"yagmail": None}):
            SPEC.loader.exec_module(importlib.util.module_from_spec(SPEC))

    def test_send_deduplicates_recipients_with_mocked_smtp(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        smtp = Mock()
        library = SimpleNamespace(SMTP=Mock())
        library.SMTP.return_value.__enter__ = Mock(return_value=smtp)
        library.SMTP.return_value.__exit__ = Mock(return_value=False)
        with patch.dict(APP.os.environ, {"EMAIL_SENDER":"sender@example.test","EMAIL_APP_PASSWORD":"synthetic"}), patch.dict(sys.modules,{"yagmail":library}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(APP.main(self.args + ["--to","fiction@example.test","--send"]),0)
        smtp.send.assert_called_once_with(to="fiction@example.test",subject="Demo",contents="Fictional content")

    def test_partial_delivery_reports_failure_without_leaking_error(self):
        from types import SimpleNamespace
        from unittest.mock import Mock
        smtp = Mock()
        smtp.send.side_effect = [None, RuntimeError("private credential details")]
        manager = Mock()
        manager.__enter__ = Mock(return_value=smtp)
        manager.__exit__ = Mock(return_value=False)
        library = SimpleNamespace(SMTP=Mock(return_value=manager))
        with patch.dict(APP.os.environ, {"EMAIL_SENDER":"sender@example.test","EMAIL_APP_PASSWORD":"synthetic"}), patch.dict(sys.modules,{"yagmail":library}), contextlib.redirect_stderr(io.StringIO()) as errors:
            self.assertEqual(APP.main(self.args + ["--to","second@example.test","--send"]),1)
        self.assertIn("after 1 completed send calls",errors.getvalue())
        self.assertNotIn("private credential",errors.getvalue())
