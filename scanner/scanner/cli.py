import argparse
import sys

from scanner.checks import data_exfiltration, indirect_injection, tool_hijack
from scanner.checks.base import status_of
from scanner.harness import TargetClient
from scanner.report import write_html_report, write_json_report


def main():
    parser = argparse.ArgumentParser(description="InjectTrace scanner")
    parser.add_argument("--target", required=True, help="Base URL of the target app, e.g. http://127.0.0.1:8000")
    parser.add_argument("--i-am-authorized", action="store_true", help="Confirm you own or are authorized to test this target")
    parser.add_argument("--out", default="reports", help="Output directory for reports")
    parser.add_argument("--delay", type=float, default=13.0, help="Seconds to wait between probes, to stay under the target's model rate limit")
    args = parser.parse_args()

    if not args.i_am_authorized:
        print("Refusing to run: pass --i-am-authorized to confirm you own or are authorized to test this target.")
        sys.exit(1)

    client = TargetClient(args.target, delay=args.delay)
    findings = (
        indirect_injection.run(client)
        + tool_hijack.run(client)
        + data_exfiltration.run(client)
    )

    json_path = write_json_report(findings, args.out)
    html_path = write_html_report(findings, args.out)

    statuses = [status_of(finding) for finding in findings]
    print(
        f"Ran {len(findings)} probes. {statuses.count('VULNERABLE')} vulnerable, "
        f"{statuses.count('INCONCLUSIVE')} inconclusive."
    )
    print(f"Reports written to {json_path} and {html_path}")


if __name__ == "__main__":
    main()