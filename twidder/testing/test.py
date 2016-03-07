import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_title(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")
        self.assertIn("Twidder", driver.title)

    def test_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")
        login_mail = driver.find_element_by_name("email")
        login_mail.send_keys("nonexistedmail@gmail.com")

        login_pass = driver.find_element_by_name("pass")
        login_pass.send_keys("wrong pass")

        driver.find_element_by_id('login-button').click()
        
        self.assertIn('Wrong', driver.find_element_by_id('error-log').text)
    
    def test_user_info(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")
        login_mail = driver.find_element_by_name("email")
        login_mail.send_keys("bavaria95@gmail.com")

        login_pass = driver.find_element_by_name("pass")
        login_pass.send_keys("12345678")

        driver.find_element_by_id('login-button').click()
        
        driver.find_element_by_id('home-tab').click()

        print(driver.find_element_by_id('home-email').text)
        self.assertIn('bavaria95@gmail.com', driver.find_element_by_id('home-email').text)


    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()