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

        login(driver, "nonexistedmail@gmail.com", "wrong pass")
                
        self.assertIn('Wrong', driver.find_element_by_id('error-log').text)
    
    def test_user_info(self):
        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        login(driver, 'bavaria95@gmail.com', '12345678')
        
        driver.find_element_by_id('home-tab').click()

        self.assertIn('bavaria95@gmail.com', driver.find_element_by_id('home-email').text)


    def tearDown(self):
        self.driver.close()

def login(driver, email, passwd):
    login_mail = driver.find_element_by_name("email")
    login_mail.send_keys(email)

    login_pass = driver.find_element_by_name("pass")
    login_pass.send_keys(passwd)

    driver.find_element_by_id('login-button').click()


if __name__ == "__main__":
    unittest.main()