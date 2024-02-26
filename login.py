from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from lxml import etree
import requests
import json
import time
import os
import shutil
#import dropbox

#dropbox_token = ''
accountText = "帳號"
passwdText = "密碼"
accountName = "帳號名"
authorID = '作者的ID'
illu_url_list = []
json_keys={'manga', 'illusts'}
#dbx = dropbox.Dropbox(dropbox_token)
#print(dbx.users_get_current_account())

url = 'https://www.pixiv.net/ajax/user/'+ authorID +'/profile/all?lang=zh_tw'
brower_options = webdriver.FirefoxOptions()
brower_profile = webdriver.FirefoxProfile()
# brower_options.add_argument('--headless')
brower_profile.set_preference('devtools.jsonview.enabled', False)
brower_options.profile = brower_profile


with  webdriver.Firefox(options=brower_options) as driver:
	
	print('login...')
	driver.get("https://accounts.pixiv.net/login")
	account = driver.find_element(By.XPATH,"//input[@autocomplete = 'username']")
	passwd = driver.find_element(By.XPATH,"//input[@autocomplete = 'current-password']")
	account.send_keys(accountText)
	passwd.send_keys(passwdText)
	passwd.send_keys(Keys.RETURN)
	WebDriverWait(driver, 15).until(lambda driver: driver.find_element(By.XPATH,"//div[@title='"+accountName+"']"))
	
	print('finish')
	cookies = driver.get_cookies()
	
	requests.packages.urllib3.disable_warnings()
	session = requests.Session()
	headers = {
		'Users-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86 64; rv:91.0) Gecko/20100101 Firefox/91.0',
		'Referer': 'https://www.pixiv.net/artworks/92424316'
	}
	for cookie in cookies:
		session.cookies.set(cookie['name'], cookie['value'])

	driver.get(url)	
	tree = etree.HTML(driver.page_source)
	illu_json = json.loads(str(tree.xpath('/html/body/pre/text()'))[2:-2])

	os.makedirs(authorID, exist_ok=True)
	print(illu_json)
	for x in json_keys:
		for i in illu_json['body'][x]:
			print('crawering illu_ID : '+i)
			url = 'https://www.pixiv.net/artworks/' + i
			driver.get(url)
			try:
				WebDriverWait(driver, 15).until(lambda driver: driver.find_element(By.CLASS_NAME,"sc-1qpw8k9-1"))
			except:
				print('Error')
				with open('Error.txt','a') as E:
					E.write(url)
				continue
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			illu_html = soup.find(class_="sc-1qpw8k9-1")
			illu_url = str(illu_html['src'])
			illu_url = illu_url.replace('pximg.net', 'pixiv.cat')
			illu_url = illu_url.replace('img-master', 'img-original')
			illu_url = illu_url[:illu_url.find('p0')+2] + illu_url[-4:]
			illu_url_list.append(illu_url)
			k = 0
			p_loc = illu_url.find('p0')
			while(True):
				p_num = 'p' + str(k)
				illu_url = illu_url[:p_loc] + p_num + illu_url[-4:]
				try:
					r = session.get(illu_url)
					r.raise_for_status()
					illu_url_list.append(illu_url)
					with open(authorID+'/'+illu_url[illu_url.rfind('/')+1:], 'wb') as q:
						q.write(r.content)
				except Exception as err:
					try:
						illu_url = illu_url[:-3] + 'png'
						r = session.get(illu_url)
						r.raise_for_status()
						illu_url_list.append(illu_url)
						with open(authorID+'/'+illu_url[illu_url.rfind('/')+1:], 'wb') as q:
							q.write(r.content)
					except Exception as err:
						print(str(k) + ' illutions')
						break
				k+=1
print('finish')
print('conpressing file')
shutil.make_archive(authorID, 'zip', authorID)

"""
with open(authorID + '.zip', 'rb') as f:
	print('uploading...')
	dbx.files_upload(f.read(), '/pixiv/'+authorID+'.zip')

print('finish')
'''
for i in illu_url_list:
	print(i)
'''
"""
