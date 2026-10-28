# QA Engineer Take-Home: Sirona Medical
Test cases, results, bug report and prioritization are in TEST_REPORT.md.
Evidence (screenshots, raw API output) is in evidence/.

## Running the automated test
Requires Python 3 (tested on WSL Ubuntu).
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q
```
Expected: 1 passed. Needs internet access; hits the live restful-booker API.

## What it tests and why
tests/test_booking_api.py automates the Part 2 Smoke scenario: POST /booking, then
immediately GET /booking/{id}, asserting both return 200 and the retrieved booking equals
the sent payload exactly. API chosen over frontend: it is the Part 2 Smoke test, has no
browser setup risk, and every line maps to a request I ran by hand with curl.
Repeatable: each run creates its own booking, so it never depends on existing data. It
does not delete the booking; the sandbox resets periodically.

## Fail-to-pass check
Changed the expected additionalneeds to "Lunch". The test failed at the final assertion
with diff {'additionalneeds': 'Breakfast'} != {'additionalneeds': 'Lunch'}. Restored with
git checkout; passed again. Confirms the assertion actually checks the saved data.

## Result
1 passed (2026-10-28). Known risk: the API's periodic data reset could delete the
booking between POST and GET; mitigated by reading back immediately; failures print the
response body.

## Next steps
Automate next: the negative scenario (PUT without auth, then re-GET unchanged), cheap and
covers authorization; then FE-04 end-to-end checkout in a browser (Playwright).
Keep manual: exploratory testing, visual/content checks (copy, images, layout), and
account-specific quirks like problem_user, where human judgment finds more than scripts.
