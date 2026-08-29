import re
from playwright.sync_api import Page, expect

def test_add_to_cart_valid_quantity(logged_in_page: Page):
    logged_in_page.goto("/product/1")
    logged_in_page.fill("#quantity-input", "2")
    logged_in_page.click("#add-to-cart-btn")

    expect(logged_in_page).to_have_url("/cart")
    expect(logged_in_page.locator("#cart-table")).to_contain_text("Wireless Earbuds")
    expect(logged_in_page.locator("#cart-total")).to_contain_text("3998.00")  # 1999 x 2
    


def test_add_to_cart_exceeding_stock_blocked_client_side(logged_in_page: Page):
    """Browser's native max= validation should prevent submission entirely."""
    logged_in_page.goto("/product/8")  # Adjustable Dumbbells, stock 15
    logged_in_page.fill("#quantity-input", "999")
    logged_in_page.click("#add-to-cart-btn")

    # Form submission blocked — URL unchanged, still on product page
    expect(logged_in_page).to_have_url(re.compile(r"/product/8"))
    is_valid = logged_in_page.eval_on_selector("#quantity-input", "el => el.checkValidity()")
    assert is_valid is False


def test_add_to_cart_exceeding_stock_blocked_server_side(logged_in_page: Page):
    """Bypass client-side validation to confirm server-side check also rejects it."""
    logged_in_page.goto("/product/8")
    # Remove the max attribute via JS so the browser allows submission through
    logged_in_page.eval_on_selector("#quantity-input", "el => el.removeAttribute('max')")
    logged_in_page.fill("#quantity-input", "999")
    logged_in_page.click("#add-to-cart-btn")

    expect(logged_in_page.locator("#flash-message")).to_contain_text("Only 15 in stock")


def test_add_to_cart_zero_quantity_blocked_client_side(logged_in_page: Page):
    logged_in_page.goto("/product/1")
    logged_in_page.fill("#quantity-input", "0")
    logged_in_page.click("#add-to-cart-btn")

    expect(logged_in_page).to_have_url(re.compile(r"/product/1"))
    is_valid = logged_in_page.eval_on_selector("#quantity-input", "el => el.checkValidity()")
    assert is_valid is False


def test_add_to_cart_zero_quantity_blocked_server_side(logged_in_page: Page):
    logged_in_page.goto("/product/1")
    logged_in_page.eval_on_selector("#quantity-input", "el => el.removeAttribute('min')")
    logged_in_page.fill("#quantity-input", "0")
    logged_in_page.click("#add-to-cart-btn")

    expect(logged_in_page.locator("#flash-message")).to_contain_text("Quantity must be at least 1")


def test_remove_item_from_cart(user_with_item_in_cart: Page):
    page = user_with_item_in_cart
    page.goto("/cart")
    page.click(".remove-item-btn")

    expect(page.locator("#empty-cart-message")).to_be_visible()


def test_checkout_empty_cart(logged_in_page: Page):
    logged_in_page.goto("/checkout")
    expect(logged_in_page).to_have_url("/cart")
    expect(logged_in_page.locator("#flash-message")).to_contain_text("Your cart is empty")


def test_checkout_with_valid_coupon(user_with_item_in_cart: Page):
    page = user_with_item_in_cart
    page.goto("/checkout")
    page.fill("input[name='coupon_code']", "SAVE10")
    page.click("button[type='submit']")

    expect(page).to_have_url("/orders")
    expect(page.locator("body")).to_contain_text("Order placed successfully")


def test_checkout_with_invalid_coupon(user_with_item_in_cart: Page):
    page = user_with_item_in_cart
    page.goto("/checkout")
    page.fill("input[name='coupon_code']", "FAKE99")
    page.click("button[type='submit']")

    expect(page.locator("#flash-message")).to_contain_text("Invalid or expired coupon")