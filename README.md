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
The UI test needs Chrome: Selenium Manager (built into Selenium) automatically downloaded
Chrome for Testing and chromedriver into ~/.cache/selenium on first run. No manual driver
install. Needs internet.

Expected: 2 passed (the UI test is intermittently flaky; see Known issues). Needs internet
access; hits the live restful-booker API and saucedemo.com.

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
UI test: changed the expected price to "$19.99". The test failed at the price assertion
('$29.99' == '$19.99'), with every earlier step passing; restored with git checkout; full
suite passed again.

## Result
API test: 1 passed (2026-10-28). UI test: passes on most runs, intermittently flaky
(see Known issues). Full suite: 2 passed on the final run. Known risk: the API's periodic data reset could delete the
booking between POST and GET; mitigated by reading back immediately; failures print the
response body.

## Bonus: frontend test (Selenium)
tests/test_saucedemo_ui.py automates FE-02 (a Part 1 Smoke test): log in as
standard_user, add Sauce Labs Backpack, assert the button changes to "Remove" and
the cart badge shows "1", then open the cart and assert exactly one item, "Sauce Labs
Backpack", "$29.99". Why Selenium: I've used it before, so I can explain and modify
it. Repeatable: each run starts a fresh browser session with an empty cart.

## Known issues
The UI test is intermittently flaky. Initial runs: 3 failures in 8. In a separate
diagnostic loop (2 failures in 8), each failure showed the click raised no error but had
no effect: still on /inventory.html, button unchanged, no badge, no console errors, so
the wait for "Remove" timed out. The pytest failures gave only the timeout traceback. The test
already used an explicit wait for the button to be clickable; I added a wait for the
full product list before clicking, after which it passed 9 of 10 runs. Too few runs
to prove that helped. Root cause not confirmed: most likely the click lands before
the page's JavaScript is ready, but an intermittent app defect (a click that does
nothing) can't be ruled out.
I deliberately did not add click retries: a retry would make the test green by
hiding exactly the kind of bug it should catch.
Next step: capture a screenshot and page state on failure, run it many times, and
manually try rapid clicks right after login to see if the defect reproduces by hand.
Also investigate whether the 'Dynamic Catalog' feature re-renders the product list
after load.

## Next steps
Automate next: the negative scenario (PUT without auth, then re-GET unchanged), cheap and
covers authorization; then FE-04 end-to-end checkout in Selenium, extending
the bonus test.
Keep manual: exploratory testing, visual/content checks (copy, images, layout), and
account-specific quirks like problem_user, where human judgment finds more than scripts.
