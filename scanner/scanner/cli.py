import argparse
import sys

from scanner.checks import indirect_injection
from scanner.harness import TargetClient
from scanner.report import write_html_report, write_json_report


def main():
    parser = argparse.ArgumentParser(description="InjectTrace scanner")
    parser.add_argument("--target", required=True, help="Base URL of the target app, e.g. http://127.0.0.1:8000")
    parser.add_argument("--i-am-authorized", action="store_true", help="Confirm you own or are authorized to test this target")
    parser.add_argument("--out", default="reports", help="Output directory for reports")
    args = parser.parse_args()

    if not args.i_am_authorized:
        print("Refusing to run: pass --i-am-authorized to confirm you own or are authorized to test this target.")
        sys.exit(1)

    client = TargetClient(args.target)
    findings = indirect_injection.run(client)

    json_path = write_json_report(findings, args.out)
    html_path = write_html_report(findings, args.out)

    vulnerable_count = sum(1 for finding in findings if finding.vulnerable)
    print(f"Ran {len(findings)} probes. {vulnerable_count} vulnerable.")
    print(f"Reports written to {json_path} and {html_path}")


if __name__ == "__main__":
    main()