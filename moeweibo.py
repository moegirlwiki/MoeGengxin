import sinaweibo, qqweibo, logging, time, pickle, StringIO
from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache

MyMail=""
MoeWebsite=""
SinaAppKey=""
SinaAppSecret=""
TencentAppKey=""
TencentAppSecret=""

class weiboDataModel(db.Model):
    access_token = db.StringProperty()
    access_token_secret = db.StringProperty()
    expires_in = db.IntegerProperty()
    source = db.StringProperty(required=True)

def sendBySina(title, link, picture):
	client = sinaweibo.APIClient(SinaAppKey, SinaAppSecret, MoeWebsite+"/sinacallback")
	sinaDatas = weiboDataModel.gql("where source='sina'")
	if(sinaDatas.count()==0):
		logging.error("No existing sina data found")
		return False

	flag = True
	for sinaData in sinaDatas:
		client.set_access_token(sinaData.access_token, sinaData.expires_in)
		short_link = client.short_url__shorten(url_long=link)
		short_url = short_link["urls"][0]["url_short"]
		try:
			if(picture==None):
				client.post.statuses__update(status=title+" "+short_url)
			else:
				wrapper = StringIO.StringIO(picture)
				client.upload.statuses__upload(status=title+" "+short_url, pic=wrapper)
				wrapper.close()
		except Exception, e:
			flag = False;
			logging.error(e)
	return flag

def authSinaURL():
	client = sinaweibo.APIClient(SinaAppKey, SinaAppSecret, MoeWebsite+"/sinacallback")
	return client.get_authorize_url()

def authSina(code):
	client = sinaweibo.APIClient(SinaAppKey, SinaAppSecret, MoeWebsite+"/sinacallback")
	r = client.request_access_token(code)
	logging.info('sina token'+r.access_token)
	sinaData = weiboDataModel(access_token=r.access_token, expires_in=r.expires_in, source="sina")
	sinaData.access_token=r.access_token
	sinaData.expires_in=r.expires_in
	sinaData.put()
	return True

def sendByTencent(title, link, picture):
	auth = qqweibo.OAuthHandler(TencentAppKey, TencentAppSecret,
     callback=MoeWebsite+"/tencentcallback")
	tencentDatas = weiboDataModel.gql("where source='tencent'")
	if(tencentDatas.count()==0):
		logging.error("No existing tencent data found")
		return False

	flag = True
	for tencentData in tencentDatas:
		auth.setToken(tencentData.access_token, tencentData.access_token_secret)
		api = qqweibo.API(auth, parser=qqweibo.ModelParser())

		try:
			if(picture==None):
				api.tweet.add(title+" "+link, clientip='127.0.0.1')
			else:
				wrapper = StringIO.StringIO(picture)
				api.tweet.addpic(wrapper, title+" "+link, clientip='127.0.0.1')
				wrapper.close()
		except Exception, e:
			flag = False
			logging.error(e)
	return flag

def authTencentURL():
	auth = qqweibo.OAuthHandler(TencentAppKey, TencentAppSecret,
     callback=MoeWebsite+"/tencentcallback")
	url = auth.get_authorization_url()
	memcache.set(key="tx_rt", value=pickle.dumps(auth.request_token))
	return url

def authTencent(verifier, token):
	auth = qqweibo.OAuthHandler(TencentAppKey, TencentAppSecret,
     callback=MoeWebsite+"/tencentcallback")
	auth.request_token = pickle.loads(memcache.get(key="tx_rt"))
	logging.info(auth.request_token)
	access_token = auth.get_access_token(verifier)

	tencentData = weiboDataModel(source="tencent")
	tencentData.access_token_secret=access_token.secret
	tencentData.access_token=access_token.key
	tencentData.put()
	return True

def clearAuths():
	datas = weiboDataModel.all()
	for d in datas:
		d.delete()