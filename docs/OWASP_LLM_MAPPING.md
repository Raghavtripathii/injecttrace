# OWASP LLM Top 10 Mapping

Every check module in InjectTrace maps to a specific category of the OWASP Top 10
for LLM Applications (2025 edition). Written down before the modules were coded,
so scope didn't drift once implementation started.

| # | Attack class | OWASP LLM category | What it's actually testing | Status |
|---|---|---|---|---|
| 1 | Indirect prompt injection via retrieved content | LLM01: Prompt Injection | A malicious instruction hidden in a retrieved document that the model follows as if it came from the user or system | Built |
| 2 | Tool-calling hijack | LLM06: Excessive Agency | Whether retrieved content or user input can make the agent invoke a tool it shouldn't, given its actual toolset | Built |
| 3 | Data exfiltration via response content and encoding | LLM07: System Prompt Leakage, LLM02: Sensitive Information Disclosure | Whether the agent can be made to reveal its own instructions or a confidential document, in plain text or hidden behind an encoding like base64 | Built |
| 4 | Jailbreak persistence across retrieval turns | LLM01: Prompt Injection | Whether a jailbreak that fails as a direct prompt succeeds once smuggled in through a retrieved chunk instead | Planned |

Categories follow the 2025 numbering. The earlier 2023 list called LLM02 "Insecure
Output Handling"; that category is now LLM05 (Improper Output Handling) and is not
covered by any module here.