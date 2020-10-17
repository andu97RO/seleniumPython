from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException

import time
import logging
import pytest

email = "bogdan.andrei450@gmail.com"
passw = "Georgiana14@"

logging.basicConfig(level=logging.DEBUG)
mylogger = logging.getLogger()


def initDriver():
    """
    Function used to instantiate chrome driver
    :return: driverChrome object
    """
    driverChrome = webdriver.Chrome(executable_path="/Users/Andu/Desktop/Munca/chromedriver.exe")
    driverChrome.get("http://automationpractice.com/")
    driverChrome.maximize_window()
    driverChrome.implicitly_wait(10)
    return driverChrome


def login(driverChrome):
    driverChrome.find_element(By.XPATH, "//a[@title='Log in to your customer account']").click()
    driverChrome.implicitly_wait(5)

    driverChrome.find_element(By.ID, "email").send_keys(email)
    driverChrome.find_element(By.ID, "passwd").send_keys(passw)
    driverChrome.find_element(By.ID, "SubmitLogin").click()
    driverChrome.implicitly_wait(5)

    with pytest.raises(NoSuchElementException):
        driverChrome.find_element(By.XPATH, "//li[contains(text(),'Authentication failed.')]")
        pytest.fail("Authentication failed")


def search(driverChrome, searchText):
    # Write in the search box
    searchinput = driverChrome.find_element_by_id("search_query_top")
    searchinput.send_keys(searchText)

    # Click on search
    driverChrome.find_element_by_name("submit_search").click()
    driverChrome.implicitly_wait(2)

    # Clear field
    driverChrome.execute_script("document.getElementById('search_query_top').value=''")


def mouseOverWebElement(driverChrome, xpath):
    element_to_hover = driverChrome.find_element_by_xpath(xpath)
    hover = ActionChains(driverChrome).move_to_element(element_to_hover)
    hover.perform()


def add_to_cart_button(driverChrome, text):
    driverChrome.find_element_by_xpath(
        "//a[@title='" + text + "']//parent::*//parent::*//parent::*//ancestor::a[@title='Add to cart']").click()


def verify_cart_product(driverChrome, name_of_product):
    product = driverChrome.find_element_by_xpath("//p//a[text()='" + name_of_product + "']")
    return product


def isElementPresent(element):
    try:
        if element is not None:
            print("Element Found")
            return True
        else:
            print("Element not found")
            return False
    except:
        print("Element not found")
        return False


def test_scenario1():
    """
    1. Visit http://automationpractice.com and log in
    2. Search by a keyword e.g. printed
    3. Validate the search results are correct
    """
    searchText = "printed"
    driverChrome = initDriver()

    mylogger.info("Step 1: Visit the url and login")
    login(driverChrome)

    mylogger.info("Step 2: Search by a keyword e.g. printed")
    search(driverChrome, searchText)

    mylogger.info("Step 3: Validate the search results are correct")
    searchAssert = driverChrome.find_element(By.XPATH, "//span[contains(text(),'printed')]").text
    print(searchAssert)
    assert eval(searchAssert) == "PRINTED"


def test_scenario2():
    """
    1. Add several products to the shopping cart
    2. Validate the cart contains the ordered products
    3. Delete one of the products and do any necessary checks
    4. Increase the quantity for one of the products and do any necessary checks
    5. Validate the total costs
    6. Submit the order
    7. Check the Order history details
    """
    searchText1 = "Printed Chiffon Dress"
    searchText2 = "Faded Short Sleeve T-shirts"
    searchTexts = [searchText1, searchText2]

    driverChrome = initDriver()
    login(driverChrome)

    mylogger.info("Step 1: Add several products to the shopping cart")
    for text in searchTexts:
        # Search for the first Product
        search(driverChrome, text)
        driverChrome.implicitly_wait(5)

        # Click on List
        driverChrome.find_element_by_xpath("//i[@class='icon-th-list']").click()
        driverChrome.implicitly_wait(5)

        # click on add to cart
        add_to_cart_button(driverChrome, text)
        driverChrome.implicitly_wait(5)

        # Click on continue shopping
        driverChrome.find_element_by_xpath("//span[@title='Continue shopping']").click()
        driverChrome.implicitly_wait(5)

    mylogger.info("Step 2. Validate the cart contains the ordered products")
    # Go to checkout
    mouseOverWebElement(driverChrome, "//a[@title='View my shopping cart']")
    driverChrome.find_element_by_id("button_order_cart").click()
    driverChrome.implicitly_wait(5)

    # Validate the number of products
    products = driverChrome.find_element_by_id("summary_products_quantity").text
    assert products == "2 Products", "There are more or less 2 products"

    for text in searchTexts:
        assert isElementPresent(verify_cart_product(driverChrome, text)), "Element is not present"

    mylogger.info("Step 3: Delete one of the products and do any necessary checks")
    delete_product = driverChrome.find_elements_by_xpath("//a[@title='Delete']")
    delete_product[0].click()
    driverChrome.implicitly_wait(5)
    time.sleep(5)

    assert isElementPresent(verify_cart_product(driverChrome, searchText2)), "Element 2 is present"
    newproducts = driverChrome.find_element_by_id("summary_products_quantity").text
    assert newproducts == "1 Product", "There are more or less than 1 product"
    time.sleep(5)

    mylogger.info("Step 4: Increase the quantity for one of the products and do any necessary checks")
    # Click on +
    plusicon = driverChrome.find_element_by_xpath("//a[@title='Add']")
    plusicon.click()
    plusicon.click()
    time.sleep(5)
    verifynew = driverChrome.find_element_by_id("summary_products_quantity").text
    assert verifynew == "3 Products", "There are 3 ore more products"

    mylogger.info("Step 5: Validate the total costs")
    totalcost = driverChrome.find_element_by_id("total_price").text
    assert totalcost == "$51.53", "Total cost are not the same, as we expected"

    mylogger.info("Step 6: Submit the order")
    checkout = driverChrome.find_element_by_xpath("//a[@title='Proceed to checkout'][@class='button btn btn-default standard-checkout button-medium']")

    #click on the first checkout
    checkout.click()
    driverChrome.implicitly_wait(5)

    #click on the second checkout (Adress)
    driverChrome.find_element_by_name("processAddress").click()
    driverChrome.implicitly_wait(5)

    #click on the third checkout (Shipping)
    driverChrome.find_element_by_id("cgv").click()
    driverChrome.find_element_by_name("processCarrier").click()
    driverChrome.implicitly_wait(5)

    #Payment check
    driverChrome.find_element_by_xpath("//a[@title='Pay by bank wire']").click()
    driverChrome.implicitly_wait(5)

    #Confirm order
    driverChrome.find_element_by_xpath("//button[@class='button btn btn-default button-medium']").click()
    driverChrome.implicitly_wait(5)

    mylogger.info("Step 7: Check the Order history details")
    driverChrome.find_element_by_xpath("//a[@title='Back to orders']").click()
    driverChrome.implicitly_wait(5)

    #Click on pdf document
    pdf = driverChrome.find_elements_by_xpath("//a[@title='Invoice']//i")
    pdf[0].click()







