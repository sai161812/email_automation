"""Preview an email; delivery requires an explicit --send flag."""
import argparse
import os
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--to", action="append", required=True, help="Recipient; repeat for more than one")
    parser.add_argument("--subject", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--send", action="store_true", help="Send the reviewed message using environment credentials")
    args = parser.parse_args(argv)
    recipients = list(dict.fromkeys(args.to))
    if any("@" not in address or any(char.isspace() for char in address) for address in recipients):
        parser.error("Each recipient must be an email address without whitespace.")
    if not args.send:
        print("Preview only; no email was sent.")
        print("To: " + ", ".join(recipients))
        print("Subject: " + args.subject)
        print(args.body)
        return 0
    sender, password = os.getenv("EMAIL_SENDER"), os.getenv("EMAIL_APP_PASSWORD")
    if not sender or not password:
        print("Set EMAIL_SENDER and EMAIL_APP_PASSWORD before sending.", file=sys.stderr)
        return 2
    try:
        import yagmail
    except ImportError:
        print("Install requirements.txt before sending.", file=sys.stderr)
        return 2
    sent = 0
    try:
        with yagmail.SMTP(sender, password) as client:
            for recipient in recipients:
                client.send(to=recipient, subject=args.subject, contents=args.body)
                sent += 1
    except Exception:
        print(f"Delivery failed after {sent} completed send calls; check delivery before retrying.", file=sys.stderr)
        return 1
    print(f"SMTP send calls completed for {sent} recipient(s). Check the mailbox for delivery.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
