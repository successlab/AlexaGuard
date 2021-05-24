from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import os
import time
import json
import random

username = ""
password = ""

username_2 = ""
password_2 = ""

#file structure
#new file structure will be
#./result_new/[category]/[name_of_skill].json

#structure of skill json file
#{'1':"invocation utterance #1",'2':"invocation utterance #2",cusper'(customer permission): 'N', 'defper'(default permission): 'N', 'publ': 'by Raj', 'url': 'https://www.amazon.com/Raj-Convert-Fahrenheit-to-Celsius/dp/B072MJRBSG/ref=sr_1_9?dchild=1&qid=1610528405&s=digital-skills&sr=1-9', 'name': 'ConvertFahrenheittoCelsius', 'reviewnum': '8', 'des': 'Description\nThis skill converts a Fahrenheit value to its corresponding Celsius value.\nWhen prompted for the Fahrenheit say the Fahrenheit value. This can be any positive number.\nThe skill will respond with the corresponding Celsius value.', 'apprate': '0','review':[{},{},{}...]}

#structre of review
#{'rate': '1.0 ', 'content': "\n\n  Alexa can do this without this skill. It's worthless to buy this.\n\n"}

def get_review(url):

	#this fcintion will return an array packed of many json file
	#each json file stand for a single review

	review_count = 0 
	HasNext = True
	reviewdriver = webdriver.Firefox()
	result = []
	try:
		reviewdriver.get(url)
	except:
		reviewdriver.quit()
		return result
	while HasNext == True:
		wait = WebDriverWait(reviewdriver, 5)
		try:
			token = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[contains(@class, 'a-section review aok-relative')]")))
		except:
			reviewdriver.quit()
			return result
		soup=BeautifulSoup(reviewdriver.page_source, 'lxml')
		reviewboxes = soup.findAll("div", {"class": "a-section review aok-relative"})
		for reviewbox in reviewboxes:
			data = {}
			print((">>> review number : " + str(review_count)))
			reviewrate = reviewbox.find("span", {"class" : "a-icon-alt"})
			data["rate"] = reviewrate.get_text().split("out",1)[0] 
			reviewcontent = reviewbox.find("span", {"data-hook" : "review-body"})
			data["content"] = reviewcontent.get_text()
			try:
				reviewscore = reviewbox.find("span", {"data-hook" : "helpful-vote-statement"})
				data["helpness"] = reviewscore.get_text().split("people",1)[0] 
			except:
				data["helpness"] = str(0)
			result.append(data)
			review_count += 1
			time.sleep(0.2)
		try:
			#go to next page
			clicknext = reviewdriver.find_element_by_xpath("//li[@class='a-last']")
			clicknext.click()
			print("try clicking")
		except:
			HasNext = False
	reviewdriver.quit()
	return result

def failed_vapp_cralwing(name, url, path):
	#save to a saperate file with link and cate info for later check
	try:
		print("empty vapp page")
		data = {}
		data['url'] = str(url)
		data['name'] = name
		data['info'] = "Crawling of this application is likely crushed"
		file_path = path+ str(name) +".json"
		aff= open(file_path,"w+")
		aff.write(str(data))
		aff.close()
	except:
		print("opps")

def vapp_cralwing(vapp, cate, total_custom_permission, total_default_permission):
	#assume directory ./result/[category] is already created
	
	#subdriver: firefox driver class, have to be login already
	#total_customer_permission,total_default_permission,totalapp are for logistic
	
	#maybe pass the path in as a variable to make life easier??
	
	name = vapp["name"]
	url = vapp["url"]

	subdriver = webdriver.Firefox()
	subdriver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Falexa-skills%2Fb%3Fie%3DUTF8%26node%3D13727921011%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&")
	subdriver.find_element_by_id("ap_email").send_keys(username)
	subdriver.find_element_by_id("continue").click()
	subdriver.find_element_by_id("ap_password").send_keys(password)
	subdriver.find_element_by_id("signInSubmit").click()

	path = "./result/"
	path = path + str(cate) + '/'
	time.sleep(0.1 * random.randint(1,10))
	subdriver.get(url)
	try:
		#collect information for screen print out and json file
		#detail_name is the name of the app
		detail_name = subdriver.find_element_by_xpath("//h1[contains(@class, 'a2s-title-content')]").text
		detail_name = re.sub('\ |\?|\.|\!|\/|\;|\:', '', detail_name)
		detail_publisher = subdriver.find_element_by_xpath("//span[contains(@class, 'a-size-base a-color-secondary')]").text
		file_path = path+ str(detail_name) +".json"
		#need utility for check path existence
		if os.path.exists(file_path):
			subdriver.quit()
			vapp["completion"] = True
			raise Exception(file_path + ' already exist')
		if not os.path.exists(path):
			raise Exception(path + ' (directory)does not exist')
	except Exception as inst:
	#find out what's triggering this
		print(inst)
		return total_custom_permission, total_default_permission
	try:
		appdata = {}
		appdata["url"] =  url
		print("now crawling " + detail_name)
		print(detail_publisher)
		appdata["publ"] = detail_publisher
		appdata["name"] = detail_name
		# find three voice commands
		utter_count = 0
		wait = WebDriverWait(subdriver, 5)
		utterbox = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@id, 'a2s-product-utterances')]")))
		for utterel in utterbox:
			utter_text = utterel.find_elements_by_class_name("a2s-utterance-text")
			for eltext in utter_text:
				print(('voice command: ' + str(utter_count)))
				print(eltext.text)#utter_text
				appdata[str(utter_count)] = eltext.text
				utter_count += 1
		# find rate
		try:
			wait = WebDriverWait(subdriver, 5)
			rate_text = wait.until(EC.presence_of_element_located((By.XPATH,  "//span[contains(@class,'a-size-medium a-color-base')]")))
			appdata["apprate"] = rate_text.text
			print(rate_text.text)
		except:
			print("NO rating")
			appdata["apprate"] = str(0)
		# find skill detail
		try:
			wait = WebDriverWait(subdriver, 5)
			skill_detail = wait.until(EC.presence_of_element_located((By.XPATH,  "//div[contains(@id,'a2s-skill-details')]")))
			appdata["skdetail"] = skill_detail.text
			print(skill_detail.text)
		except:
			print("NO rating")
			appdata["skdetail"] = ""
		# reviewers number
		try:
			wait = WebDriverWait(subdriver, 5)
			review_num = wait.until(EC.presence_of_element_located((By.XPATH,  "//span[contains(@class,'a-size-small a-color-link a2s-review-star-count')]")))
			appdata["reviewnum"] = review_num.text
			print(review_num.text)
		except:
			print("no review number")
			appdata["reviewnum"] = str(0)
		# find description
		try:
			wait = WebDriverWait(subdriver, 5)
			desbox = wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@id, 'a2s-description')]")))
			#~ print desbox.text
			appdata["des"] = desbox.text
		except:
			print("[no] description")
			appdata["des"] = "N"
		# find custom permission account linking
		try:
			wait = WebDriverWait(subdriver, 5)
			cusper = wait.until(EC.presence_of_element_located((By.XPATH,  "//span[contains(@id,'a2s-skill-account-link-msg')]")))
			#~ print cusper.text
			appdata["cusper"] = "Y"
			total_custom_permission += 1
		except:
			print("[no] custom permission")
			appdata["cusper"] = "N"
		# find default permission
		try:
			wait = WebDriverWait(subdriver, 5)
			defper = wait.until(EC.presence_of_all_elements_located((By.XPATH,  "//li[contains(@class,'a2s-permissions-list-item')]")))
			appdata["defper"] = []
			for dp in defper:
				print(dp.text)
				appdata["defper"].append(dp.text)
				total_default_permission += 1
		except:
			print("no default permission")
	except:
		failed_vapp_cralwing(name,url,path)
		vapp["completion"] = True
		subdriver.quit()
		return total_custom_permission, total_default_permission
	# review
	try:
		review_page_url = review_num.find_element_by_xpath("//a[contains(@class,'a-link-normal a2s-link')]").get_attribute('href')
		review_data = get_review(review_page_url)
		appdata['review'] = review_data
	except:
		print("{error}\n no review")
	with open(file_path, 'w') as outfile:
		json.dump(appdata, outfile)
	subdriver.quit()
	vapp["completion"] = True
	return total_custom_permission, total_default_permission

def cate_crawl(cate, totalapp):
	
	#road map:
	#this fucntion will
	#1. crawl entire category
	#2. store all app under said category in a json file
	#3. store said json file
	#4. input other argument so we can control over write<-NOT WORKED YETT

	#recall
	#cate : {'name':cate_name,'url':"www.xxx.xxx",'completion':False}

	#assume directory /result/metadata already exist
	#login is necessary for stupid reason...
	#assume subdriver that was passed in is already loged in

	
	subdriver = webdriver.Firefox()
	subdriver.get("https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Falexa-skills%2Fb%3Fie%3DUTF8%26node%3D13727921011%26ref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&")
	subdriver.find_element_by_id("ap_email").send_keys(username)
	subdriver.find_element_by_id("continue").click()
	subdriver.find_element_by_id("ap_password").send_keys(password)
	subdriver.find_element_by_id("signInSubmit").click()

	name = cate['name']
	url = cate['url']
	apps = []
	cate_page_count = 1
	print("now crawling category: " + name)
	subdriver.get(url)

	#jump to "all result" page
	see_all_result = subdriver.find_element_by_xpath("//div[contains(@class, 'a-box a-text-center apb-browse-searchresults-footer')]")
	see_all_result.click()

	path = "./result/metadata/" 
	file_path = path + name + '_app.json'
	#following codes extract the last page
	last_page = 1
	tempel = subdriver.find_elements_by_xpath("//li[contains(@class, 'a-disabled')]")
	for tem in tempel:
		if tem.text.isnumeric():
			last_page = int(tem.text)
			break
	while cate_page_count <= last_page:
		#retain token to make sure we got all our stuff
		wait = WebDriverWait(subdriver, 5)
		token = wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[contains(@class, 's-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col sg-col-12-of-16')]")))
		soup = BeautifulSoup(subdriver.page_source, 'lxml')
		subelement = soup.find_all("div", class_="s-result-item s-asin sg-col-0-of-12 sg-col-16-of-20 sg-col sg-col-12-of-16")
		#noted, at this point subelement contain entire div box
		for subel in subelement: 
			# initialize the checklist for each page
			app_name = subel.find("span",class_ = 'a-size-medium a-color-base a-text-normal').text
			app_url = "https://www.amazon.com" + subel.find("a",class_ = 'a-link-normal a-text-normal').get('href')
			apps.append({"name":app_name,"url":app_url,"completion":False})
			totalapp += 1
		print(("total number of app crawled: " + str(len(apps))))
		try:
			nextButton = subdriver.find_element_by_xpath("//li[contains(@class, 'a-last')]")
			print(nextButton.text)
			nextButton.click()
			#subdriver.get(nextlink)
			cate_page_count += 1
		except:
			print("<< no next page >>")
			print("finish crawling following category:" + name)
	#aff= open(file_path,"w+")
	#aff.write(str(apps))
	with open(file_path, 'w') as outfile:
		json.dump(apps, outfile)
		print("information stored at " + file_path)
	subdriver.quit()
	cate["completion"] = True
	subdriver.quit()
	return cate, totalapp
