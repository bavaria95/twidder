import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class TwidderTest(unittest.TestCase):

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

        self.assertIn('Unique message!', driver.find_element_by_tag_name('li').text)

    def test_browse(self):
        '''
        Logs in, navigates to Browse tab, tries to search nonexisted user(expecting to see error)
        then tries to find actual user and checks whether it's his page
        '''

        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        login(driver, 'bavaria95@gmail.com', '12345678')
        
        driver.find_element_by_id('browse-tab').click()

        # try to find nonexistedmail@gmail.com(does not exist)
        driver.find_element_by_id('search-field').send_keys('nonexistedmail@gmail.com')
        driver.find_element_by_id('search-send').click()

        self.assertIn('No such user', driver.find_element_by_id('search-error').text)
        
        # clear search field
        driver.find_element_by_id('search-field').clear()

        # find dima@qwe.com(exists)
        driver.find_element_by_id('search-field').send_keys('dima@qwe.com')
        driver.find_element_by_id('search-send').click()

        # check his email in User info
        self.assertIn('dima@qwe.com', driver.find_element_by_id('browse-email').text)

    
    def test_password_change(self):
        '''
        Logs in, then changes password, checks message and then changes it back
        '''

        driver = self.driver
        driver.get("http://127.0.0.1:5000")

        login(driver, 'bavaria95@gmail.com', '12345678')
        
        driver.find_element_by_id('account-tab').click()

        # changes password from '12345678' to '87654321'
        driver.find_element_by_name('current').send_keys('12345678')
        driver.find_element_by_name('pass1').send_keys('87654321')
        driver.find_element_by_name('pass2').send_keys('87654321')
        driver.find_element_by_id('change-submit').click()

        # clear
        driver.find_element_by_name('current').clear()
        driver.find_element_by_name('pass1').clear()
        driver.find_element_by_name('pass2').clear()

        # changes password from '87654321' back to '12345678'
        driver.find_element_by_name('current').send_keys('87654321')
        driver.find_element_by_name('pass1').send_keys('12345678')
        driver.find_element_by_name('pass2').send_keys('12345678')
        driver.find_element_by_id('change-submit').click()

        # check whether it finished successfully
        self.assertIn('Password changed', driver.find_element_by_id('change-error').text)


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