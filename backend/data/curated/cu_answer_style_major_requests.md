---
title: "Answer Style Rules for Major Requests (Product Output)"
source_title: "Internal product rules (offline assistant)"
source_url: "offline"
collected_at: "2026-02-07"
topic: "answer_rules"
---

## Summary
When users ask about majors or course planning, the assistant must return links + step-by-step actions and avoid guessing requirements.

## Required output blocks (for your MVP)
1) Checklist (step-by-step)
2) Recommendations (courses or next actions)
3) Risks (common pitfalls)
4) Official Links (major page + registration help)

## Rules
- Always include the majors index link:
  https://bulletin.columbia.edu/general-studies/majors-concentrations/
- Always include the specific major page link if the major is named
- If user asks "What should I take this semester?"
  - recommend 3–5 items max
  - label any assumptions (first semester, math background unknown, etc.)
- Do NOT claim a course is required unless it is stated on the official major page
- If info is not in docs: say "Not covered in provided docs" and suggest what to check next

## Example snippet (CS as example only)
"I recommend starting with a gateway course first (example: an intro programming course like COMS W1004 for CS). Confirm requirements on the CS major page."
