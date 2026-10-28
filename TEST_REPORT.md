# Part 1: Frontend Testing (https://www.saucedemo.com)
Environment: TODO: browser + version. Date: 2026-10-28.

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
| FE-01: Locked-out user cannot log in (Negative) | 1. Open login page 2. Username locked_out_user, password secret_sauce 3. Click Login | Error "Epic sadface: Sorry, this user has been locked out." shown; user stays on login page | P1 / Regression | Pass. Exact error shown. TODO: confirm stayed on login page |
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
TODO: whether typing directly in First Name keeps the full value.
TODO: other differences observed before checkout (images, sort, buttons), or "none observed".

## Assumptions
- Q: Is there a required tax rate? Assumption: 8% inferred from observed totals.
- Q: Does Postal Code require a format? Assumption: any non-empty value; "a" was accepted.
