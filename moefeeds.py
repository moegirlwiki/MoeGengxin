import moeforbidden, feedparser, logging, time, datetime
from google.appengine.ext import db

class feedDataModel(db.Model):
    title = db.StringProperty(required=True)
    link = db.StringProperty(required=True)
    date = db.DateTimeProperty(required=True)

def checkDuplicate(title, date):
	date2 = date-datetime.timedelta(hours=12)
	datas = db.GqlQuery("SELECT * FROM feedDataModel where title=:1 and date > DATETIME(:2)", title, date2.strftime("%Y-%m-%d %H:%M:%S"))
	if(datas.count()==0):
		return True
	return False

def cleanLink(link):
	i=link.find("&diff")
	if(i>=0):
		j=link.find("&",i+1)
		if(j>=0):
			link=link[:i]+link[j:]
		else:
			link=link[:i]
	i=link.find("&oldid")
	if(i>=0):
		j=link.find("&",i+1)
		if(j>=0):
			link=link[:i]+link[j:]
		else:
			link=link[:i]
	i=link.find("index.php?title=")
	if(i>=0):
		link=link[:i]+link[i+16:]
	return link

def force_unicode(string):
    if type(string) == unicode:
        return string
    return string.decode('utf-8')

def checkSummary(s, forbidden):
	s = force_unicode(s)
	for b in forbidden:
		if(s.find(b)>=0):
			return False
	return True

def parseFeed(feed_url):
	feeds = feedparser.parse(feed_url)
	clean_feeds = []
	forbidden = moeforbidden.getForbidden()
	forbidden_utf8 = []
	for f in forbidden:
		forbidden_utf8.append(force_unicode(f))
	for item in feeds["items"]:
		if(checkSummary(item["summary"], forbidden_utf8) and checkSummary(item["title"], forbidden_utf8)):
			clean_feeds.append({"title":item["title"],"link":cleanLink(item["link"]),
				"date":datetime.datetime.fromtimestamp(time.mktime(item.updated_parsed))})
	return clean_feeds

def getFeedFromFile():
	feedDatas = feedDataModel.gql("order by date desc limit 1")
	if(feedDatas.count()==0):
		logging.info("No existing data found")
		return None
	return feedDatas.get()

def writeFeedToFile(feed):
	feedData = feedDataModel(title=feed["title"], link=feed["link"], date=feed["date"])
	feedData.put()
	return feedData

def clearOldFeeds():
	date2 = datetime.datetime.now()-datetime.timedelta(days=1)
	#clear history oldder than one day
	datas = feedDataModel.gbl("where date < DATETIME(:1)", date2.strftime("%Y-%m-%d %H:%M:%S"))
	for d in datas:
		d.delete()

def findLast(feeds, lastFeed):
	last = None
	for feed in feeds:
		if((lastFeed == None) or ((feed["title"] != lastFeed.title) and (feed["date"] > lastFeed.date))):
			if((last == None) or (last["date"] > feed["date"])):
				if(checkDuplicate(feed["title"], feed["date"])):
					last = feed
	return last