from dataclasses import dataclass
from typing import Optional


@dataclass
class Finding:
    check_id: str
    owasp_category: str
    severity: str
    query: str
    target_response: str
    vulnerable: bool
    evidence: Optional[str] = None
    notes: Optional[str] = None
    payload_reached: Optional[bool] = None


def was_retrieved(result: dict, source_doc: str) -> bool:
    return source_doc in result.get("sources", [])


def status_of(finding: Finding) -> str:
    if finding.vulnerable:
        return "VULNERABLE"
    if finding.payload_reached is False:
        return "INCONCLUSIVE"
    return "NOT REPRODUCED"