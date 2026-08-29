import re
from playwright.sync_api import Page, expect

def test_register_with_valid_details(page: Page, unique_user):
    page.goto("/register")
    page.fill("#username", unique_user["username"])
    page.fill("#email", unique_user["email"])
    page.fill("#password", unique_user["password"])
    page.click("#register-submit")

    expect(page).to_have_url("/login")
    expect(page.locator("#flash-message")).to_contain_text("Registration successful")


def test_register_with_duplicate_username(page: Page, registered_user):
    page.goto("/register")
    page.fill("#username", registered_user["username"])
    page.fill("#email", "different_email@example.com")
    page.fill("#password", "somepassword")
    page.click("#register-submit")

    expect(page).to_have_url("/register")
    expect(page.locator("#flash-message")).to_contain_text("already exists")


def test_login_with_valid_credentials(page: Page, registered_user):
    page.goto("/login")
    page.fill("#username", registered_user["username"])
    page.fill("#password", registered_user["password"])
    page.click("#login-submit")

    expect(page).to_have_url("/products")
    expect(page.locator(f"text=Hi, {registered_user['username']}")).to_be_visible()


def test_login_with_invalid_password(page: Page, registered_user):
    page.goto("/login")
    page.fill("#username", registered_user["username"])
    page.fill("#password", "wrongpassword")
    page.click("#login-submit")

    expect(page).to_have_url("/login")
    expect(page.locator("#flash-message")).to_contain_text("Invalid username or password")


def test_access_cart_while_logged_out(page: Page):
    page.goto("/cart")
    expect(page).to_have_url(re.compile(r"/login"))


def test_logout_clears_session(logged_in_page: Page):
    logged_in_page.click("#logout-link")
    expect(logged_in_page).to_have_url("/login")

    logged_in_page.goto("/cart")
    expect(logged_in_page).to_have_url(re.compile(r"/login"))