E-Commerce QA Automation Project

A full-stack Flask e-commerce application built as a target for an end-to-end QA automation pipeline — combining manual test case design, Playwright automated testing, and Azure DevOps test management and defect tracking.

Live repo: github.com/Shekhar007284/E-Com-App Azure DevOps project: EcommercePlatform-QA (Test Plans, Boards)

Project overview--------------------------------------------------------------------------------------------------------------------------------------

This project has two halves:
|
|--A working e-commerce application — user auth, product catalog, cart, checkout with coupon codes, order history, and a basic admin panel — built to have  realistic business logic worth testing (stock validation, discount calculation, authorization checks).
|
|--A QA automation pipeline on top of it — 26 manually authored test cases across 4 suites in Azure DevOps Test Plans, 19 of which are automated with Playwright (Python), plus 3 tracked defects moved through a full New → Active → Fixed → Closed lifecycle in Azure Boards.

**The goal was to demonstrate the full QA/DevOps loop end-to-end: requirements → test case design → automation → defect tracking → traceability**

Tech stack----------------------------------------------------------------------------------------------------------------------------------------------

Application
|--Python, Flask, Flask-SQLAlchemy, Flask-Login
|--SQLite (development database)
|--Jinja2 templates, Bootstrap 5

Testing & QA
|--Playwright (Python) — browser automation
|--pytest, pytest-playwright, pytest-html
|--Azure DevOps — Test Plans, Boards (test case management, defect tracking)

Version control
|--Git, GitHub (public repo)

Debugging notes (real issues found and fixed)---------------------------------------------------------------------------------------------------------

Two genuine test-infrastructure bugs came up during development — documenting them here because working through them was part of the actual QA process, not just the passing tests at the end.

1. Playwright glob URL matching produced false failures Using expect(page).to_have_url("**/login") failed even when navigation was correct, because the **/ glob pattern expects a path segment before it — it doesn't match a bare relative path against a base URL cleanly. Fixed by switching to plain relative paths ("/login") or re.compile() for URLs with query strings.

2. A manually created browser context doesn't inherit base_url The pytest-playwright plugin auto-applies --base-url from pytest.ini to its default page fixture, but a second context created manually via browser.new_context() (needed to simulate a second logged-in user) does not inherit it automatically. Fixed by passing base_url explicitly: browser.new_context(base_url=base_url).

3. Client-side validation was masking server-side checks The product detail form uses HTML5 min/max attributes on the quantity input. This meant invalid quantities (0, or values exceeding stock) never reached the Flask backend at all — the browser blocked submission before any request was sent. The server-side validation logic was correct but effectively untested through the UI. Resolved by writing separate tests for each validation layer: one confirming the browser blocks invalid input (checkValidity()), and one that deliberately removes the HTML constraint via JS to confirm the server-side check independently rejects the same input.
4. 
--------Created a Azure DevOps account----------------------------------------------------------------------------------------------------------------

Create a new Organization > Flipkart Clone
|---------------Create a new Project > ECommerce-Platform QA
                |---------------Create a new Test Plan > ECommerce Regression Suite
                                |--------------- : > new suite > static suite
                                                 |-----Authorization
                                                 |-----Products & Cart
                                                 |-----Orders & Authorization
                                                 |-----Checkout & Coupons

------------------------NEXT STEP FOR IMPLEMENTING PLAYWRIGHT FOR AUTOMATED TEST CASES IN A REAL BROWSER-----------------------------------------------

1)Install Playwright and its pytest plugin:
  |-- pip install playwright pytest-playwright pytest-html

2)Install the actual browser binaries (this is the step that's separate from the pip install — Playwright needs real browser engines, not just the Python bindings):
  |-- playwright install
This downloads Chromium, Firefox, and WebKit — might take a minute or two depending on your connection.

3)Verify it worked:
  |-- playwright --version
Running the project locally
bash
git clone https://github.com/Shekhar007284/E-Com-App.git
cd E-Com-App
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
mkdir instance
python seed.py
python app.py

App runs at http://127.0.0.1:5000. Admin login: admin / admin123.

To run the test suite (with the app running in a separate terminal):

bash
pip install playwright pytest-playwright pytest-html
playwright install
pytest tests/ -v
                                                 
