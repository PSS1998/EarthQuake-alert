import urllib.request
from datetime import datetime, timedelta
import time
import json

import schedule
import bs4 as bs
import telegram



TOKEN='put your token here'


def check_lat_long(lat, lng):
	if (float(lng)>50.05 and float(lng)<52.06):
		if (float(lat)>34.70 and float(lat)<36.70):
			return True
	return False

def check_location(location):
	for loc in location:
		if(loc.find("Tehran") != -1):
			return True
	return False 

def send_notification(text):
	global bot
	source = urllib.request.urlopen("https://api.telegram.org/bot"+TOKEN+"/getUpdates").read()
	messages = json.loads(source.decode('utf-8'))
	chat_ids = set()
	for message in messages['result']:
		chat_ids.add(message['message']['from']['id'])
	for chat_id in chat_ids:
		bot.send_message(chat_id=chat_id, text=text)

def get_earthquakes():	
	global last_date
	source = urllib.request.urlopen('http://irsc.ut.ac.ir/events_list.xml').read()
	soup = bs.BeautifulSoup(source,'lxml')

	for item in list(reversed(soup.find_all('item'))):
		header = item.find('licence')
		if header:
			continue
		mag = item.mag.text
		reg1 = item.reg1.text
		reg2 = item.reg2.text
		reg3 = item.reg3.text
		reg = [reg1, reg2, reg3]
		longitude = item.long.text.split()[0]
		latitude = item.lat.text.split()[0]
		date_string = item.date.text
		date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
		if date > last_date:
			if check_lat_long(float(latitude), float(longitude)) or check_location(reg):
				last_date = date
				send_notification("An earthquake with Magnitude of "+mag+" has occurred in "+reg1)


last_date = datetime.utcnow() - timedelta(days=2)
bot = telegram.Bot(token=TOKEN)

#send_notification("test")

get_earthquakes()

schedule.every(10).minutes.do(get_earthquakes)

while True:
	schedule.run_pending()
	time.sleep(1)
