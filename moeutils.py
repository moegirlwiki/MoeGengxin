import logging
import moefeeds, moeweibo
from google.appengine.api import urlfetch
from google.appengine.api import images
from BeautifulSoup import BeautifulSoup 

def getImage(feed_url):
	# Save IMG
	page = urlfetch.fetch(feed_url)
	if(page.status_code != 200):
		return None
	soup = BeautifulSoup(page.content)
	content = soup.find("div",{"id":"bodyContent"})
	img = None
	for tag in content.findAll("img"):
		if(tag["width"]!=None and ((int(tag["width"])<100) or (int(tag["width"])>800))):
			continue
		if(tag["height"]!=None and ((int(tag["height"])<100) or (int(tag["height"])>800))):
			continue
		img = tag
		break
	image_content = None
	if(img != None):
		image_remote=urlfetch.fetch(img["src"] )
		if(image_remote.status_code!=200):
			return None
		image_content = image_remote.content
		if(img["width"]!=None and img["height"]!=None):
			image_content = images.resize(image_content, int(img["width"]), int(img["height"]))
	return image_content

def schedule():
	feeds = moefeeds.parseFeed("http://zh.moegirl.org/index.php?title=Special:%E6%9C%80%E8%BF%91%E6%9B%B4%E6%94%B9&feed=atom&namespace=0")
	lastFeed = moefeeds.getFeedFromFile() #Maybe None
	# Find the last unsend feed
	feed = moefeeds.findLast(feeds, lastFeed)
	if(feed == None):
		return "No feeds need to be sent"
	feed = moefeeds.writeFeedToFile(feed)
	msg = "Feed to be sent "+feed.title+"<br/>"

	image = getImage(feed.link)
	
	if(moeweibo.sendBySina(feed.title, feed.link, image)):
		msg += "Sina: Success<br/>"
	else:
		msg += "Sina: Failure<br/>"

	if(moeweibo.sendByTencent(feed.title, feed.link, image)):
		msg += "Tencent: Success<br/>"
	else:
		msg += "Tencent: Failure<br/>"
	return msg