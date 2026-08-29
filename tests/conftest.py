import pytest
from playwright.sync_api import Page

@pytest.fixture
def unique_user():
    """Generates a unique username/email per test run to avoid collisions."""
    import time
    ts = str(int(time.time() * 1000))
    return {
        "username": f"testuser_{ts}",
        "email": f"testuser_{ts}@example.com",
        "password": "testpass123"
    }

@pytest.fixture
def registered_user(page: Page, unique_user):
    """Registers a fresh user and returns their credentials, ready to log in."""
    page.goto("/register")
    page.fill("#username", unique_user["username"])
    page.fill("#email", unique_user["email"])
    page.fill("#password", unique_user["password"])
    page.click("#register-submit")
    return unique_user

@pytest.fixture
def logged_in_page(page: Page, registered_user):
    """Returns a page with an authenticated session already established."""
    page.goto("/login")
    page.fill("#username", registered_user["username"])
    page.fill("#password", registered_user["password"])
    page.click("#login-submit")
    page.wait_for_url("**/products")
    return page

@pytest.fixture
def user_with_item_in_cart(logged_in_page: Page):
    """Logged in user with one product already added to cart."""
    logged_in_page.goto("/product/1")  # Wireless Earbuds, ₹1999, stock 50
    logged_in_page.fill("#quantity-input", "2")
    logged_in_page.click("#add-to-cart-btn")
    return logged_in_page