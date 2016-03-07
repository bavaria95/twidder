import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class PythonOrgSearch(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Firefox()

    def test_title(self):
        '''
        Tests whether page loads and title of it contains "Twidder"
        '''

        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        self.assertIn("Twidder", driver.title)

    def test_login(self):
        '''
        Just tries to login with wrong credentials. Should be 
        "Wrong username or password." in field for errors
        '''

        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        login(driver, "nonexistedmail@gmail.com", "wrong pass")
                
        self.assertIn('Wrong', driver.find_element_by_id('error-log').text)
    
    def test_user_info(self):
        '''
        Logs in with existing email/pass pair, click on Home tab and checks
        whether user information contains it's email.
        '''

        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        login(driver, 'bavaria95@gmail.com', '12345678')
        
        driver.find_element_by_id('home-tab').click()

        self.assertIn('bavaria95@gmail.com', driver.find_element_by_id('home-email').text)

    def test_posting(self):
        '''
        Logs in, navigates to Home tab, enters message in the input field, 
        click Post button and the see whether new message has appeared
        '''

        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        login(driver, 'bavaria95@gmail.com', '12345678')
        
        driver.find_element_by_id('home-tab').click()

        driver.find_element_by_id('status-field-home').send_keys('Uniq message!')
        driver.find_element_by_id('status-send-home').click()
        driver.refresh()

        self.assertIn('Uniq message!', driver.find_element_by_tag_name('li').text)


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