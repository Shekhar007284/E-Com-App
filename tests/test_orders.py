import re
from playwright.sync_api import Page, expect

def test_view_own_order_history(user_with_item_in_cart: Page):
    page = user_with_item_in_cart
    page.goto("/checkout")
    page.click("#place-order-btn")

    expect(page).to_have_url("/orders")
    expect(page.locator("#orders-list")).to_contain_text("Placed")


def test_unauthorized_access_to_others_order(browser, logged_in_page: Page, unique_user, base_url):
    # User A places an order
    page_a = logged_in_page
    page_a.goto("/product/1")
    page_a.fill("#quantity-input", "1")
    page_a.click("#add-to-cart-btn")
    page_a.goto("/checkout")
    page_a.click("#place-order-btn")
    expect(page_a).to_have_url("/orders")

    order_card = page_a.locator("[data-order-id]").first
    order_id = order_card.get_attribute("data-order-id")

    # User B: fresh browser context WITH base_url passed explicitly
    context_b = browser.new_context(base_url=base_url)
    page_b = context_b.new_page()
    import time
    ts = str(int(time.time() * 1000))
    page_b.goto("/register")
    page_b.fill("#username", f"userb_{ts}")
    page_b.fill("#email", f"userb_{ts}@example.com")
    page_b.fill("#password", "testpass123")
    page_b.click("#register-submit")

    page_b.goto("/login")
    page_b.fill("#username", f"userb_{ts}")
    page_b.fill("#password", "testpass123")
    page_b.click("#login-submit")

    page_b.goto(f"/order/{order_id}")

    expect(page_b).to_have_url("/orders")
    expect(page_b.locator("#flash-message")).to_contain_text("Unauthorized access to this order")

    context_b.close()


def test_admin_can_view_any_order(page: Page, user_with_item_in_cart: Page):
    # Place an order as regular user first
    reg_page = user_with_item_in_cart
    reg_page.goto("/checkout")
    reg_page.click("#place-order-btn")
    order_card = reg_page.locator("[data-order-id]").first
    order_id = order_card.get_attribute("data-order-id")

    # Log in as admin in the same page object (fresh page, separate session)
    page.goto("/login")
    page.fill("#username", "admin")
    page.fill("#password", "admin123")
    page.click("#login-submit")

    page.goto(f"/order/{order_id}")
    expect(page.locator("body")).not_to_contain_text("Unauthorized")