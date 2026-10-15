# Synthetic business stories (developer / tester reference)

These patterns are engineered into the Al Noor Holdings dataset. They are **not** listed as facts on the dashboard. Users should be able to discover them through filters, rankings, and insights.

1. **Technology + GitHub Copilot high ROI** — Software Engineering has high Copilot adoption, strong hours saved, and above-average realization (`UC-001`, `UC-002`, `UC-113`).
2. **Legal over-licensed / low adoption** — Corporate Legal and Contracts have very high license coverage but large Never Activated / Inactive segments and weak use-case evidence (`UC-010`, `UC-011`, `UC-121`).
3. **Finance lifts after training** — FP&A and Accounting show a step-up in adoption and evidence after training campaign months (`UC-021`, `UC-022`, `UC-126`).
4. **Customer Service automation** — Contact center reply assist and routing generate large hours and task volume (`UC-040`, `UC-041`).
5. **Marketing usage without cash** — Copy and content use cases have high demonstrated activity and low realization (~10–16%) (`UC-050`, `UC-051`, `UC-122`).
6. **Procurement modest adoption, excellent ROI** — Bid comparison and clause scans produce cost-avoidance that finance largely validates (`UC-030`, `UC-031`, `UC-123`).
7. **HR inactive licenses** — HR departments are over-licensed relative to usage (`UC-060`–`UC-062`).
8. **Failed expensive agent** — Executive briefing agent (`UC-012`) has high implementation cost, Retired status, and negligible realized value.
9. **Cheap automation, exceptional ROI** — AP invoice exception triage (`UC-020`) is inexpensive and highly realized.
10. **Summer dip** — July–August usage, ramp, and value are scaled down (~14–22%).
11. **Training campaign lift** — Months 8, 18, and 27 increase activation probability enterprise-wide.
12. **Over-licensing** — Legal and HR coverage rates exceed 85% of staff.
13. **Scaling winner** — Pull request review assist (`UC-002`) ramps above 1.0 and is classified Scale.
14. **Token-driven infrastructure growth** — Azure OpenAI token volume and compute cost rise through the history (`UC-005`, `UC-052`, `UC-115`).
15. **Realized trails demonstrated** — Portfolio realization is structurally below demonstrated value; hours are not auto-cashed.
16. **Overlapping tools** — Some Finance, Marketing, Strategy, and Data staff hold both M365 Copilot and ChatGPT Enterprise.
17. **Executive usage pattern** — Executives have fewer sessions and longer average session minutes.
18. **Abandoned experimenters** — A slice of users is active for 1–2 months and then silent.

Seed: `42`. Re-run `python -m generators.generate_all` to regenerate.
