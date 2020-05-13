import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class Speaker():
    def __init__(self):
        self.driver = webdriver.Chrome('/Users/AKHIL/Development/telugu_google_assistant/chromedriver')
        self.driver.get('http://tdil-dc.in/tts1/')
    def speak(self, text_to_say):
        text_to_say = text_to_say.split("---")[0]
        self.driver.find_element_by_xpath("//*[@id='Language']/option[4]").click()
        self.driver.find_element_by_xpath('//*[@id="ip"]').clear()
        self.driver.find_element_by_xpath('//*[@id="ip"]').send_keys(text_to_say)
        self.driver.implicitly_wait(0.25)
        self.driver.find_element_by_xpath('//*[@id="AutoNumber1"]/tbody/tr[4]/td[2]/input[2]').click()
    def quit(self):
        self.driver.quit()
