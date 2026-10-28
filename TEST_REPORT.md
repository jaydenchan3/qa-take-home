# Part 1: Frontend Testing (https://www.saucedemo.com)
Environment: Chrome 155.0.8059.86 (64-bit). Date: 2026-10-28.

## Observations
1. Item total shows a floating-point artifact. standard_user, Sauce Labs Bike Light ($9.99)
   + Sauce Labs Fleece Jacket ($49.99): checkout overview shows "Item total:
   $59.980000000000004" (expected $59.98). Tax $4.80 and Total $64.78 are correct, so the
   display is wrong, not the charge. Reproduced twice. Control: Backpack ($29.99) + Bolt
   T-Shirt ($15.99) shows $45.98 / $3.68 / $49.66 correctly. Likely cause: unrounded JS
   float addition (suspected, not confirmed). Evidence: screenshots/TODO-filename.
2. Product copy contains code-like text: "carry.allTheThings()" in the Backpack
   description and the product name "Test.allTheThings() T-Shirt (Red)". Possibly
   intentional for a demo store; would raise as a question, not a bug.
3. Checkout overview shows pre-filled "Payment Information: SauceCard #31337" and "Free
   Pony Express Delivery!" without the user entering payment details. Assumed demo
   behavior.

## Test cases
| ID / Title | Steps | Expected Result | Priority / Suite | Status / Actual |
|---|---|---|---|---|
| FE-01: Locked-out user cannot log in (Negative) | 1. Open login page 2. Username locked_out_user, password secret_sauce 3. Click Login | Error "Epic sadface: Sorry, this user has been locked out." shown; user stays on login page | P1 / Regression | Pass. Exact error shown; user stays on login page. |
| FE-02: Add item to cart (Positive) | 1. Log in as standard_user 2. Click "Add to cart" on Sauce Labs Backpack 3. Open cart | Cart badge shows 1; button changes to "Remove"; cart lists Sauce Labs Backpack, qty 1, $29.99 | P0 / Both | Pass. Cart lists Backpack, qty 1, $29.99. TODO: badge/Remove observed but not captured |
| FE-03: Checkout blocked when First Name blank (Negative) | 1. Log in, add an item 2. Cart > Checkout 3. Leave First Name blank, fill Last Name and Postal Code 4. Click Continue | Error "Error: First Name is required"; stays on Checkout: Your Information | P1 / Regression | Pass. Exact error shown |
| FE-04: End-to-end checkout (Positive) | 1. Log in as standard_user 2. Add item(s) 3. Cart > Checkout 4. Enter First Name, Last Name, Postal Code > Continue 5. Verify overview totals 6. Click Finish | Item total = sum of item prices; tax and total correct; "Thank you for your order!" shown | P0 / Both | Pass. TODO: confirm items: Backpack only: $29.99 / Tax $2.40 / Total $32.39; confirmation shown |

Priority scale: P0 = core flow broken, no workaround. P1 = important behavior wrong,
narrower impact or workaround exists. P2 = minor/cosmetic.

## Smoke selection
Smoke: FE-02 and FE-04. Smoke answers "is this build usable at all": the fast happy
path through the purchase flow. If either fails, deeper testing isn't worthwhile.
FE-04 partly overlaps FE-02; accepted. "Both" = runs in Smoke and is also part of
Regression.

## Execution summary
4 executed, 4 passed, 0 failed (2 positive, 2 negative), standard_user.

## problem_user re-run (FE-04)
Status: Fail. On "Checkout: Your Information", typing in Last Name overwrites the First
Name field, and First Name only ever holds the last character typed. Last Name stays
empty, so Continue shows "Error: Last Name is required" and checkout cannot be
completed. Steps 5-6 not executed. Same steps pass with standard_user.
First Name accepts direct input normally ("John" stays "John"). The defect is in the
Last Name field: its input is redirected into First Name (one character at a time),
so Last Name can never be filled and checkout cannot proceed.
No other differences observed during the FE-04 steps before checkout (login,
inventory, add to cart, cart page).

## Assumptions
- Q: Is there a required tax rate? Assumption: 8% inferred from observed totals.
- Q: Does Postal Code require a format? Assumption: any non-empty value; "a" was accepted.

# Part 2: API Testing
API: https://restful-booker.herokuapp.com. Tool: curl -i, WSL Ubuntu. Date: 2026-10-28.
Raw request/response output: evidence/part2_curl.txt

## Scenario 1 (Positive): create a booking, retrieve it, verify saved data
| # | Method / Endpoint | Request | Expected | Actual | Result |
|---|---|---|---|---|---|
| 1 | POST /booking | Headers Content-Type & Accept: application/json. Body: firstname Testy, lastname McTest, totalprice 123, depositpaid true, checkin 2026-11-01, checkout 2026-11-05, additionalneeds Breakfast | 200; bookingid returned; booking echoed | 200; bookingid 666; booking echoed identically | Pass |
| 2 | GET /booking/666 | Accept: application/json | 200; all 7 fields equal the request | 200; all 7 fields identical | Pass |

## Scenario 2 (Negative): update without authorization
| # | Method / Endpoint | Request | Expected | Actual | Result |
|---|---|---|---|---|---|
| 1 | PUT /booking/666 | No Cookie or Authorization header. Body changes firstname to "Hacked", totalprice 1, depositpaid false | Rejected with 401 or 403 | 403 Forbidden (body "Forbidden") | Pass |
| 2 | GET /booking/666 | Accept: application/json | 200; booking unchanged | 200; unchanged (Testy / 123 / true); same etag as before the PUT | Pass |

Assumption: the API docs define no error responses for any endpoint. Expected status is
therefore taken from HTTP convention (401 or 403 = rejected), and the decisive check is
that the booking is unchanged on re-read. The re-GET proves the rejection was real, not
just a status code.

## Smoke selection
Scenario 1 (Positive). It's the happy path: it proves the API's core function (save a
booking and read it back) works at the simplest level. If it fails, nothing else is worth testing.

## Execution summary
2 scenarios, 4 requests, all Pass.

## Unexpected behavior
1. Booking disappeared, not reproduced. Booking 5062 was created at 17:50:08 UTC and
   returned 404 at 17:51:02 (54s later). The next booking received ID 666 (the ID counter
   apparently restarted) and stayed retrievable for 6+ minutes, polled every ~15s
   (evidence/reset_watch.log). Most likely the documented periodic data reset.
   Not considered a bug. Implication: tests must create their own data and read it back
   immediately.
2. 403 instead of 401 for missing credentials. By convention 401 = not authenticated,
   403 = authenticated but not permitted. No credentials were sent, so 401 is arguably
   more accurate. Docs are silent. Question for the team, not a confirmed bug.
3. POST /booking returns 200; convention for resource creation is 201 Created.
   Functionally fine. Question, not a bug.
4. Documentation inconsistencies (from the apidoc page, not runtime behavior):
   - DELETE and Ping list "Success 200" but their examples show "201 Created"
     (Ping actually returned 201 in testing)
   - The PartialUpdateBooking (PATCH) example uses curl -X PUT
   - No error responses documented for any endpoint
   - id is typed String on GET but Number on PUT, PATCH and DELETE
   Documentation bugs: would mislead developers; API behavior itself unaffected.
