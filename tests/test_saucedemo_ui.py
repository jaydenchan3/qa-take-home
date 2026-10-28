import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

BASE_URL = "https://www.saucedemo.com"


def css(test_id):
    return (By.CSS_SELECTOR, f'[data-test="{test_id}"]')


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    # Selenium Manager finds or downloads Chrome and a matching chromedriver
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def test_add_backpack_to_cart(driver):
    wait = WebDriverWait(driver, 10)
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located(css("username"))).send_keys("standard_user")
    driver.find_element(*css("password")).send_keys("secret_sauce")
    driver.find_element(*css("login-button")).click()

    # Wait for the full product list so the click doesn't land before the page is ready
    wait.until(EC.visibility_of_element_located(css("inventory-list")))
    wait.until(EC.element_to_be_clickable(css("add-to-cart-sauce-labs-backpack"))).click()
    # The app swaps the button for a new element with a different data-test id
    remove_button = wait.until(EC.visibility_of_element_located(css("remove-sauce-labs-backpack")))
    assert remove_button.text == "Remove"
    assert driver.find_element(*css("shopping-cart-badge")).text == "1"

    driver.find_element(*css("shopping-cart-link")).click()
    cart_list = wait.until(EC.visibility_of_element_located(css("cart-list")))
    items = cart_list.find_elements(*css("inventory-item"))
    assert len(items) == 1
    assert items[0].find_element(*css("inventory-item-name")).text == "Sauce Labs Backpack"
    assert items[0].find_element(*css("inventory-item-price")).text == "$29.99"
