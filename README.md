# Email automation demo

A small Python command-line example. Importing the module does nothing. Running it previews the message unless `--send` is explicitly supplied.

```sh
python main.py --to fiction@example.test --subject "Demo" --body "Preview content"
```

Repeat `--to` for multiple recipients. Review the preview before delivery. The example address above is fictional.

For actual delivery, install `python -m pip install -r requirements.txt`, set `EMAIL_SENDER` and `EMAIL_APP_PASSWORD` in your environment, then repeat the reviewed command with `--send`. Use your provider's supported SMTP credential; do not put a password in source code. The script does not store credentials.

A successful SMTP call does not prove inbox delivery. Partial failures exit with status 1 and report how many send calls completed; check the mailbox before retrying to avoid duplicates. Missing credentials or dependencies exit with status 2. There is no queue, retry mechanism, delivery tracking, or deduplication across runs.

Verify without sending mail:

```sh
python -m unittest discover -s tests -v
```

Tests cover preview, missing credentials, and import behavior. Real SMTP delivery has not been exercised by these tests.
