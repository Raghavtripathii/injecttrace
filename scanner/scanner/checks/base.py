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