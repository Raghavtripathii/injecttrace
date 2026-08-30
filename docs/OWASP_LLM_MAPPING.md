# OWASP LLM Top 10 Mapping

Every check module in InjectTrace maps to a specific OWASP Top 10 for LLM
Applications category. Written down before any check module is coded, so scope
doesn't drift once implementation starts.

| # | Attack class | OWASP LLM category | What it's actually testing | Status |
|---|---|---|---|---|
| 1 | Indirect prompt injection via retrieved content | LLM01: Prompt Injection | A malicious instruction hidden in a retrieved document that the model follows as if it came from the user or system | MVP — build first |
| 2 | Tool-calling hijack | LLM06: Excessive Agency | Whether retrieved content or user input can make the agent invoke a tool it shouldn't, given its actual toolset | Extension |
| 3 | Data exfiltration via tool output / response encoding | LLM02: Insecure Output Handling | Whether the agent can be made to leak system-prompt contents, other users' documents, or secrets — including via encoding tricks | Extension |
| 4 | Jailbreak persistence across retrieval turns | LLM01: Prompt Injection | Whether a jailbreak that fails as a direct prompt succeeds once smuggled in through a retrieved chunk instead | Extension |

Only check module 1 gets built, tested against a real deployment, and written up
before modules 2-4 are started. One fully verified finding is worth more than
four half-tested ones.