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

username = ""
password = ""

username_2 = ""
password_2 = ""

#print(get_review("https://www.amazon.com/Amazon-Drop-In/product-reviews/B08KRH1Q3Z/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews"))

#os.mkdir("./result/Productivity")
#os.mkdir("./result/metadata")

overwrite = False

#road map

#step 1:
#iterate through all existing categories

category = []
totalapp = 0
total_custom_permission = 0
total_default_permission = 0
logistic = {'totalapp':0,'total_custom_permission':0,'total_default_permission':0}
if os.path.exists('./result/metadata/logistic.json'):
    with open("./result/metadata/logistic.json", "r") as readfile:
        json_data = readfile.read()
        logistic = json.loads(json_data)
        print("./result/metadata/logistic.json, here is a snip")
        print(logistic)
    totalapp = logistic['totalapp']
    total_custom_permission = logistic['total_custom_permission']
    total_default_permission = logistic['total_default_permission']
if (not os.path.exists('cate.json')) or (overwrite):
    driver = webdriver.Firefox()
    driver.get("https://www.amazon.com/alexa-skills/b?ie=UTF8&node=13727921011")
    assert "Alexa" in driver.title
    wait = WebDriverWait(driver, 10)
    #for this portion of xpath filter, look for the class used by category in the index page of alexa skill(key word example: smart home, communication)
    category_raw = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//a[contains(@class, 'a-color-base a-link-normal')]")))
    for cate_raw in category_raw:
        cate_name = re.sub('\ |\?|\.|\!|\/|\;|\:', '', cate_raw.text)
        category.append({'name':cate_name,'url':cate_raw.get_attribute('href'),'completion':False})
        print(cate_raw.text)
        print(cate_raw.get_attribute('href'))
    
    #maybe not 

    with open('cate.json', 'w') as outfile:
        json.dump(category, outfile)
        print("information stored at ./cate.json")

#following part of code kinnnnda make this only runnable at linux system

elif os.path.exists('cate.json') and overwrite == False:
    with open("cate.json", "r") as readfile:
        json_data = readfile.read()
        category = json.loads(json_data)
        print("cate.json loaded, here is a snip")
        print(category[0])

for index in range(len(category)):
    crawl_happened = False
    if (not category[index]["completion"]):
        while not crawl_happened:
            try:
                category[index], totalapp = cate_crawl(category[index], totalapp)
                crawl_happened = True
            except Exception as inst:
                print(inst)
                print("Here we go again~")
        logistic['totalapp'] = totalapp
    if crawl_happened:
        with open('cate.json', 'w') as outfile:
            json.dump(category, outfile)
            print("information stored at ./cate.json after crawling categories")
        with open('./result/metadata/logistic.json', 'w') as outfile:
            json.dump(logistic, outfile)
            print("logistic info stored at ./result/metadata/logistic.json")
        #time.sleep(random.randint(100,200))
#known problem need to tend to
#we know that some category are in the sub category of other category 
#solution: menually deleted for now

#####################################################
#Code above is running at this point. do not touch  #
#for the sake of trouble shooting                   #
#####################################################

#could do: give each app an index?

#next step: to crawel is page by page
#need to complete: vappcrawl
#need to test: vapp crawl

#remember, vapp crawl already have embeded sleeping function

path = "./result/"
path_metadata = "./result/metadata/"

for index in range(len(category)):
    category[index]["all_app_crawled"] = False

crawl_anyway_cate = False
crawl_anyway_app = False

for index in range(len(category)):
    if not category[index]["all_app_crawled"] or crawl_anyway_cate: 
        name = category[index]['name']
        metadata_file_path = path_metadata + name + '_app.json'
        apps = []
        with open(metadata_file_path, "r") as readfile:
            json_data = readfile.read()
            apps = json.loads(json_data)
        if not os.path.exists(path + name):
            os.mkdir(path + name)
        for index in range(len(apps)):
            crawled = False
            if not apps[index]["completion"] or crawl_anyway_app:
                total_custom_permission,total_default_permission = vapp_cralwing(apps[index],name,total_custom_permission, total_default_permission)
                logistic["total_custom_permission"] = total_custom_permission
                logistic["total_default_permission"] = total_default_permission
                crawled = True
            if crawled:
                with open(metadata_file_path, 'w') as outfile:
                    json.dump(apps, outfile)
                with open('./result/metadata/logistic.json', 'w') as outfile:
                    json.dump(logistic, outfile)
                    print("logistic info stored at ./result/metadata/logistic.json")
        category[index]["all_app_crawled"] = True