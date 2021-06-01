from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from alexa_new import get_review,cate_crawl,vapp_cralwing
import re
import os
import time
import json
import random

username = "zzh4g523710043@gmail.com"
password = ""

dev_consel_url = "https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.e8108ad1-e266-4194-a2a0-2774ea5e3ddd/development/en_US/"

driver = webdriver.Firefox()
driver.get(dev_consel_url)
driver.find_element_by_id("ap_email").send_keys(username)
driver.find_element_by_id("ap_password").send_keys(password)
driver.find_element_by_id("signInSubmit").click()

#get all sample ulterance

cates = os.listdir("./match_found") 
cates.remove("menual_sort.txt")

for cate in cates:
    skill_dir = "./match_found/" + cate + '/'
    skills = os.listdir(skill_dir)
    for skill in skills:
        print(skill_dir + skill)
        with open(skill_dir + skill,'r') as skill_json:
            skill_detail = json.load(skill_json)
        if '0' not in skill_detail.keys():
            print("no sample utterancec skip")
            continue
        if 'audio_url' not in skill_detail.keys():
            skill_detail['audio_url'] = []
        else:
            print("already crawled skip")
            continue
        if "Flash Briefing" in skill_detail['0']:        
            with open(skill_dir + skill,'w') as skill_json:
                json.dump(skill_detail,skill_json)
            print("flash briefing skip")
            continue
    #strip utterence#
        #exclude first time user audio
        driver.find_element_by_class_name('askt-utterance__input').send_keys(skill_detail['0'])
        driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
        driver.find_element_by_class_name('askt-utterance__input').send_keys("alexa, stop")
        driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
        #return user audio
        driver.find_element_by_class_name('askt-utterance__input').send_keys(skill_detail['0'])
        driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
        time.sleep(10)
        mp3_url = driver.find_element_by_id('asf-player-Dialog').get_attribute('src')
        skill_detail['audio_url'].append(mp3_url)
        #clean up
        driver.find_element_by_class_name('askt-utterance__input').send_keys("alexa, stop")
        driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
        if '1' in skill_detail.keys():
            if "Flash Briefing" in skill_detail['1']:
                with open(skill_dir + skill,'w') as skill_json:
                    json.dump(skill_detail,skill_json)
                print("flash briefing skip")
                continue
            driver.find_element_by_class_name('askt-utterance__input').send_keys(skill_detail['1'])
            driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
            time.sleep(5)
            mp3_url = driver.find_element_by_id('asf-player-Dialog').get_attribute('src')
            skill_detail['audio_url'].append(mp3_url)
            driver.find_element_by_class_name('askt-utterance__input').send_keys("alexa, stop")
            driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
        if '2' in skill_detail.keys():
            if "Flash Briefing" in skill_detail['2']:
                with open(skill_dir + skill,'w') as skill_json:
                    json.dump(skill_detail,skill_json)
                print("flash briefing skip")
                continue
            driver.find_element_by_class_name('askt-utterance__input').send_keys(skill_detail['2'])
            driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
            time.sleep(5)
            mp3_url = driver.find_element_by_id('asf-player-Dialog').get_attribute('src')
            driver.find_element_by_class_name('askt-utterance__input').send_keys("alexa, stop")
            driver.find_element_by_class_name('askt-utterance__input').send_keys(Keys.RETURN)
            skill_detail['audio_url'].append(mp3_url)
        with open(skill_dir + skill,'w') as skill_json:
            json.dump(skill_detail,skill_json)

    #input utterence# done
    #capture audio url# done 
    #record audio url# done
    



