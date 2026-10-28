# Summary
- Part 1 (Frontend, saucedemo): 4 test cases executed manually as standard_user: 4 Pass
  (2 positive, 2 negative). 1 re-run as problem_user (FE-04): Fail, Last Name input is
  redirected into First Name, checkout blocked.
- Part 2 (API, restful-booker): 2 scenarios / 4 requests via curl: all Pass.
- Part 3: BUG-01, checkout overview shows unrounded item total ($59.980000000000004), Low severity.
- Part 4: Ranked C > B > F > E > D > A. Release blockers: C and B.
- Part 5: 1 automated API test (pytest + requests): Pass. Fail-to-pass check performed.
- Key findings: BUG-01 (display-only float artifact; PDF receipt correct); problem_user
  checkout blocker; API returns 403 (not 401) without credentials; several API doc
  inconsistencies; one unexplained booking disappearance, likely the documented reset.
- Not completed: Bonus: 1 frontend test (Selenium, FE-02): passes on most runs but is intermittently
  flaky (see README). Frontend tests run in Chrome only. Automated test does not
  delete the booking it creates (sandbox resets periodically).

# Part 1: Frontend Testing (https://www.saucedemo.com)
Environment: Chrome 155.0.8059.86 (64-bit). Date: 2026-10-28.

## Observations
1. Item total shows a floating-point artifact. standard_user, Sauce Labs Bike Light ($9.99)
   + Sauce Labs Fleece Jacket ($49.99): checkout overview shows "Item total:
   $59.980000000000004" (expected $59.98). Tax $4.80 and Total $64.78 are correct, so the
   display is wrong, not the charge. Reproduced twice. Control: Backpack ($29.99) + Bolt
   T-Shirt ($15.99) shows $45.98 / $3.68 / $49.66 correctly. Likely cause: unrounded JS
   float addition (suspected, not confirmed). Evidence: evidence/part3.png.
2. Product copy contains code-like text: "carry.allTheThings()" in the Backpack
   description and the product name "Test.allTheThings() T-Shirt (Red)". Possibly
   intentional for a demo store; would raise as a question, not a bug.
3. Checkout overview shows pre-filled "Payment Information: SauceCard #31337" and "Free
   Pony Express Delivery!" without the user entering payment details. Assumed demo
   behavior.
4. With all checkout fields blank, only "Error: First Name is required" is shown; the form
   reports one missing field at a time. Minor usability note.

## Test cases
| ID / Title | Steps | Expected Result | Priority / Suite | Status / Actual |
|---|---|---|---|---|
| FE-01: Locked-out user cannot log in (Negative) | 1. Open login page 2. Username locked_out_user, password secret_sauce 3. Click Login | Error "Epic sadface: Sorry, this user has been locked out." shown; user stays on login page | P1 / Regression | Pass. Exact error shown; user stays on login page. |
| FE-02: Add item to cart (Positive) | 1. Log in as standard_user 2. Click "Add to cart" on Sauce Labs Backpack 3. Open cart | Cart badge shows 1; button changes to "Remove"; cart lists Sauce Labs Backpack, qty 1, $29.99 | P0 / Both | Pass. Cart badge shows 1; Backpack button changed to "Remove" on the products page (other items still "Add to cart"); cart lists Sauce Labs Backpack, qty 1, $29.99. Evidence: evidence/fe02_products.png, evidence/fe02_cart.png |
| FE-03: Checkout blocked when First Name blank (Negative) | 1. Log in, add an item 2. Cart > Checkout 3. Leave First Name blank, fill Last Name and Postal Code 4. Click Continue | Error "Error: First Name is required"; stays on Checkout: Your Information | P1 / Regression | Pass. With Last Name and Postal Code filled and First Name blank, "Error: First Name is required" shown; stays on Checkout: Your Information. |
| FE-04: End-to-end checkout (Positive) | 1. Log in as standard_user 2. Add item(s) 3. Cart > Checkout 4. Enter First Name, Last Name, Postal Code > Continue 5. Verify overview totals 6. Click Finish | Item total = sum of item prices; tax and total correct; "Thank you for your order!" shown | P0 / Both | Pass. Sauce Labs Fleece Jacket only: Item total $49.99 / Tax $4.00 / Total $53.99 (matches expected: 8% of 49.99 = 3.9992, rounded to $4.00); "Thank you for your order!" shown after Finish. |

Priority scale: P0 = core flow broken, no workaround. P1 = important behavior wrong,
narrower impact or workaround exists. P2 = minor/cosmetic.

## Smoke selection
Smoke: FE-02 and FE-04. Smoke answers "is this build usable at all": the fast happy
path through the purchase flow. If either fails, deeper testing isn't worthwhile.
FE-04 partly overlaps FE-02; accepted. "Both" = runs in Smoke and is also part of
Regression.

## Execution summary
4 executed, 4 passed, 0 failed (2 positive, 2 negative), standard_user.
Plus 1 re-run as problem_user (FE-04): Fail (see below).

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
- Q: Are problem_user's defects intentional? Assumption: yes, it is a deliberately faulty
  test account, so its Last Name defect is documented as a difference rather than chosen
  as the Part 3 bug, which was reproduced on standard_user.

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

# Part 3: Bug Report

## BUG-01: Checkout overview shows unrounded item total ($59.980000000000004)

**Severity:** Low. Display only: tax and total are calculated correctly, so the
customer is charged the right amount, but a malformed price is shown at the point of purchase.
**Priority suggestion:** P2.
**Environment:** https://www.saucedemo.com, Chrome 155.0.8059.86 (64-bit), WSL/Windows, 2026-10-28.
**User:** standard_user / secret_sauce

### Steps to reproduce
1. Go to https://www.saucedemo.com and log in as standard_user / secret_sauce.
2. Ensure the cart is empty (Menu > Reset App State if needed).
3. Click "Add to cart" on "Sauce Labs Bike Light" ($9.99).
4. Click "Add to cart" on "Sauce Labs Fleece Jacket" ($49.99).
5. Click the cart icon, then "Checkout".
6. Enter any First Name, Last Name and Postal Code, then click "Continue".
7. Look at "Price Total" on the Checkout: Overview page.

### Expected
Item total: $59.98 (9.99 + 49.99), shown to 2 decimal places.

### Actual
Item total: $59.980000000000004
Tax: $4.80 (correct: 8% of 59.98 = 4.7984, rounded)
Total: $64.78 (correct)

### Reproducibility
2/2 attempts with this item combination.
Control: Sauce Labs Backpack ($29.99) + Sauce Labs Bolt T-Shirt ($15.99) displays
correctly as $45.98 / $3.68 / $49.66, so the issue depends on the item combination.

### Related observation
The "Generate PDF order" receipt for the same order (Fleece Jacket + Bike Light) shows
Item total $59.98, Tax $4.80, Total $64.78, correctly rounded. The defect is confined
to the Checkout: Overview page display; the order data itself is correct.
Evidence: evidence/part3.pdf (PDF receipt)

### Evidence
Screenshot: evidence/part3.png (checkout overview showing $59.980000000000004)

### Suspected cause (not confirmed)
The item total appears to be summed as binary floating-point numbers and displayed
without rounding to 2 decimals: in JavaScript, 9.99 + 49.99 evaluates to 59.980000000000004.
Fix would be to format the displayed value to 2 decimals or compute money in integer cents.
The PDF receipt formats the same value correctly, which suggests the overview page is
missing a 2-decimal formatting step that the PDF path has.

### Impact
No incorrect charge, but a visibly wrong price on the final confirmation screen undermines
customer trust and may cause abandoned checkouts. Could affect any price combination
whose float sum isn't exactly representable.

# Part 4: Bug Prioritization

## Ranking
| Rank | Bug | Blocks release? | Reasoning |
|---|---|---|---|
| 1 | C: User can view another user's order (name, address) by changing the order number in the URL | Yes | Security/privacy breach. Exposure of customer data can't be undone, destroys customer trust, and in healthcare may carry legal reporting obligations. Silent: the app looks fine while it leaks. |
| 2 | B: Place Order does nothing for any user | Yes | Core functionality broken for everyone, no workaround: zero orders, zero revenue. Severe but recoverable: once fixed and deployed, orders resume. |
| 3 | F: Expired token returns HTTP 200 with an error message instead of 401 | No | Clients that treat 200 as success may show stale or empty data or never redirect to login. Correctness issue with a security flavor across every API consumer; fix soon after release. |
| 4 | E: Exports over 1,000 items take ~40s | No | Works, just slowly, and only for large exports. Performance issue; impact depends on who exports at that size. |
| 5 | D: Cart count stays at 0 until refresh; item is in the cart | No | Display out of sync with real state. Workaround exists (refresh). Can confuse users into adding items twice. |
| 6 | A: Footer typo "Privcay Policy" | No | Cosmetic, lowest severity. A one-line fix, so worth including if it's free, but it doesn't drive the decision (low severity, near-zero cost). |

## Release blockers
B and C. C exposes customer data; B means the release can't do its basic job. I would not ship with either.

## Questions before a final decision
- C: Is this new in the release build, or already live in production? If already live,
  it's an active incident: check access logs for exploitation, assess breach-notification
  obligations (e.g. HIPAA), and fix immediately regardless of the release. If new in this
  build, it's a release blocker only. Also: can any logged-in user exploit it, or only certain roles?
- B: Is there any workaround (phone orders, previous build, feature flag rollback)? Is it all browsers/platforms?
- C and B: How long would each fix take, and how firm is the release date?
- F: Which clients consume this API, and do any rely on the status code to detect session expiry?
- E: Who exports over 1,000 items, and how often? Does the export time out anywhere?
- D: Does it cause duplicate items or abandoned carts in analytics?
