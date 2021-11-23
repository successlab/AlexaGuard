import time


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import speech_recognition as sr
import requests
from pydub import AudioSegment

from determine_question_type import *
from generate_answer import *

import asyncio
from api_helper import async_chat

import json

#pip3 install SpeechRecognition pydub

# To-do import "Your model"

# if_abusive(skill_output) --> True/False
# if sexual(skill_output) --> True/False

class ChatWithAlexa:
    def __init__(self, test_url, usrname, passwd, parser):
        self.url = test_url
        self.usrname = usrname
        self.passwd = passwd
        self.audio_url = ""
        self.parser = parser #CoreNLPParser()
        with open('profiles.json') as profiles_file:
            self.profiles = json.load(profiles_file)


    def start_browser(self):
        self.browser = webdriver.Firefox()
        self.browser.get(self.url) # You have to replace the url with your own skills' testing page url
        time.sleep(1)
        self.browser.find_element_by_id("ap_email").send_keys(self.usrname)
        self.browser.find_element_by_id("ap_password").send_keys(self.passwd)
        time.sleep(1)
        self.browser.find_element_by_id("signInSubmit").click()

    def sent_request(self, request):
        time.sleep(1)
        self.browser.find_element_by_css_selector('input.askt-utterance__input').send_keys(request)
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.RETURN)
        time.sleep(10)

    def skill_chat(self, invocation):
        """
        We initialize the skill with this
        """
        self.sent_request(invocation)
        #time.sleep(15) #<- this wait is too long. we could missed entire response's url

        #serch for new audio url every 0.5 second
        #if found new audio url is different then new, reset wait to 15
        #change this to dynamic?

        #legacy code saved for future usage.
        """
        i = 0
        urls = []
        while i < 30: # check audio_url for 30 times in 15 second
            new_audio_url = self.get_audio_url()
            if self.audio_url != new_audio_url:
                i = 0
                urls.append(new_audio_url)
                self.audio_url = new_audio_url 
            time.sleep(0.5)
            i += 1

        self.get_text()

        self.urls = urls

        print("\n\n\n")
        print(self.new)
        print("\n\n\n")
        print(self.urls)
        print("\n\n\n")
        print(self.get_newest_text())
        
        self.urls = urls
        """
        for i in range(4):
            self.get_text()
            reply = self.conversational_engine(self.get_newest_response())
            self.sent_request(reply)


        #for xx in self.browser.find_elements_by_css_selector("p.askt-dialog__message"):
        #    print(xx.text)
        #    print(xx.get_attribute("class"))

    def conversational_engine(self, skill_output):
        """
        what and how to respond
        """
        #if self.if_qeustion(skill_output):
        q_t = determine_qeustion_type(skill_output,self.parser)
        if q_t == 'selection_CC':
            return (answer_selection_CC(skill_output,self.parser))
        elif q_t == 'selection_SC':
            return (answer_selection_SC(skill_output))
        elif q_t == 'Y/N':
            return (answer_YN_question())
        elif q_t == 'instruction':
            return (answer_instruction_question(skill_output))
        elif q_t == 'WH':
            return (answer_WH(skill_output,self.profiles[0]))
        else:
            #print("wait man what happened? q_t = ",q_t)
            return (asyncio.run(async_chat(skill_output)))
        #https://www.usenix.org/system/files/sec20-guo.pdf



    def chat_input(self, input_to_skill):
        """
        input to the test portal
        """
        time.sleep(1)
        self.browser.find_element_by_css_selector('input.askt-utterance__input').send_keys(input_to_skill)
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.RETURN)
        time.sleep(15)

        #for xx in self.browser.find_elements_by_css_selector("p.askt-dialog__message"):
        #    print(xx.text)
        #    print(xx.get_attribute("class"))

    def get_audio_url(self):
        """
        if this skill is use recorded url, get it from the test portal

        we call this skill as a one line
        """

        audio_url = self.browser.find_element_by_id('asf-player-Dialog').get_attribute('src')

        return audio_url

    def get_text(self):
        
        text = []
        
        for xx in self.browser.find_elements_by_css_selector("p.askt-dialog__message"):

            #print(xx.get_attribute("class"))
            #print(xx.get_attribute("class").split(" "))
            xx_attribute = xx.get_attribute("class").split(" ")[1]

            if xx_attribute == "askt-dialog__message--request":
                xx_attribute = 'request'
                text.append([xx.text,xx_attribute])
            elif xx_attribute == "askt-dialog__message--active-response" or xx_attribute == "askt-dialog__message--response" :
                xx_attribute = 'response'
                text.append([xx.text,xx_attribute])
            #else:
            #    raise "askt-dialog__message have unexpected attribute"
            # NOTE: the last played msg have different class
            # NOTE: therefore we need to look for both(last one is at last anyway)
            
            #new_temp.append([xx.text,xx_attribute])

        #recall that xx.get_attribute("class") will return a string that can seperate by space
        #askt-dialog__message--request and askt-dialog__bubble--response

        self.text = text

        # ok i doubt this will become too long(unless we keep using the same window without closing it.)
        # so optimization can wait a little bit
        # we automatically assume the last "request" is the last commend we uttered
        # and then the rest are response
        
    def get_newest_request(self):
        #this function assume that self.get_text() is already runned
        for t in self.text[::-1]:
            if t[1] == 'request':
                return t[0]
            else:
                continue
        print(self.text)
        raise "no request found"
    
    def get_newest_response(self):
        #this function assume that self.get_text() is already runned
        for t in self.text[::-1]:
            if t[1] == 'response':
                return t[0]
            else:
                continue
        print(self.text)
        raise "no response found"
        

    def transcribe_audio_url(self,audio_url):
        #download ffmpeg
        #add ffmpeg to environment var
        req = requests.get(audio_url, allow_redirects=True)

        open('audio.mp3', 'wb').write(req.content)

        sound = AudioSegment.from_mp3("audio.mp3")
        sound.export("audio.wav", format="wav")

        #r.content
        with sr.AudioFile('audio.wav') as source:
            r = sr.Recognizer()
            audio_data = r.record(source)
            # recognize (convert from speech to text)
            text = r.recognize_google(audio_data)
            return text


    def analysis_audio_url(self,audio_url):

        return ""
        #To-do: tiny url? cloud front? 
        #To-do: ...

    def quit(self):

        quit_text = "alexa quit"
        
        self.browser.find_element_by_css_selector('input.askt-utterance__input').send_keys(quit_text)
        time.sleep(1)
        self.browser.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.RETURN)

        # checking for situation where skill stuck in a loop because simulation is weird
        # (plenty of skill will stuck in a loop in simulation while working properly in normal alexa)

        # if stuck
        newest_text = self.get_newest_text()
        if len(newest_text) != 1: # <- the latest actually have response 
            self.browser.close()
            self.start_browser()
    
with open("credential.json") as credential_file:
    credential = json.load(credential_file)
    username = credential['email']
    password = credential['password']
urlin = 'https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.e8108ad1-e266-4194-a2a0-2774ea5e3ddd/development/en_US/'


with CoreNLPServer(*jars):
    parser = CoreNLPParser()
    xchat = ChatWithAlexa(urlin, username, password, parser)
    xchat.start_browser()
    xchat.skill_chat("Alexa, enable lab rule")
    print(xchat.get_text())
    xchat.browser.close()

#restart browser for every new skill tested? highly in-efficient
#