import time


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# To-do import "Your model"

# if_abusive(skill_output) --> True/False
# if sexual(skill_output) --> True/False

class ChatWithAlexa:
    def __init__(self, test_url, usrname, passwd):
        self.url = test_url
        self.usrname = usrname
        self.passwd = passwd



    def start_browser(self):
        self.browser = webdriver.Firefox()
        self.browser.get(self.url) # You have to replace the url with your own skills' testing page url
        time.sleep(1)
        self.browser.find_element_by_id("ap_email").send_keys(self.usrname)
        self.browser.find_element_by_id("ap_password").send_keys(self.passwd)
        time.sleep(1)
        self.browser.find_element_by_id("signInSubmit").click()

    def skill_chat(self, invocation_name):
        start_skill_command = "Alexa, enable " + invocation_name
        time.sleep(1)
        self.browser.find_element_by_css_selector('input.askt-utterance__input').send_keys(start_skill_command)
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.RETURN)
        time.sleep(15)

        for xx in self.browser.find_elements_by_css_selector("p.askt-dialog__message"):
        	print(xx.text)

    def conversational_engine(self, skill_output):
        """
        what and how to respond
        """
        if if_question(skill_output):
            return

    def chat_input(self, input_to_skill):
        """
        input to the test portal
        """
        time.sleep(1)
        self.browser.find_element_by_css_selector('input.askt-utterance__input').send_keys(input_to_skill)
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.RETURN)
        time.sleep(15)

        for xx in self.browser.find_elements_by_css_selector("p.askt-dialog__message"):
        	print(xx.text)

    def if_qeustion(self, skill_output):
        """
        decide if this is a uqestion, and decide what to answer
        """
        res = False
        return res

    def get_audio_url(self):
        """
        if this skill is use recorded url, get it from the test portal
        """

        return ""

urlin = 'https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.e3ba10bf-381e-4efe-b30f-58ca79d41737/development/en_US/'
username = 'yangyong@tamu.edu'
password = ''

xchat = ChatWithAlexa(urlin, username, password)
xchat.start_browser()
xchat.skill_chat("lab rule")
