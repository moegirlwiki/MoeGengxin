import webapp2, moeweibo, moeutils, moefeeds, moeforbidden, logging
from google.appengine.api import mail

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("""
            <html><head><title>MoeWeibo</title></head>
            <body>BiuBiu<br/>
        	<!--a href='authredirect?code=sina'>Sina Auth</a><br/>
            <a href='authredirect?code=tencent'>Tencent Auth</a><br/>
        	<a href='send'>Send</a-->
            </body></html>""")

class AuthCallbackHandler(webapp2.RequestHandler):
    def get(self):
        if(self.request.get("code")=="sina"):
            self.redirect(moeweibo.authSinaURL())
        elif(self.request.get("code")=="tencent"):
            self.redirect(moeweibo.authTencentURL())

class SinaCallbackHandler(webapp2.RequestHandler):
    def get(self):
        if(moeweibo.authSina(self.request.get("code"))):
            self.response.write("<html><head><title>MoeWeibo</title></head><body>Your account has been saved</body></html>")
        else:
            self.response.write("<html><head><title>MoeWeibo</title></head><body>Something wrong happened</body></html>")

class TencentCallbackHandler(webapp2.RequestHandler):
    def get(self):
        if(moeweibo.authTencent(self.request.get("oauth_verifier"), self.request.get("oauth_token"))):
            self.response.write("<html><head><title>MoeWeibo</title></head><body>Your account has been saved</body></html>")
        else:
            self.response.write("<html><head><title>MoeWeibo</title></head><body>Something wrong happened</body></html>")

class SendCallbackHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write(moeutils.schedule())

class SendmailCallbackHandler(webapp2.RequestHandler):
    def get(self):
        mail.send_mail(sender=moeweibo.MyMail,
              to="admin@moegirl.org",
              subject="Time to Refresh Weibo Auth!",
              body="Click me!\n"+
              moeweibo.MoeWebsite+"/clearauth\n"+
              moeweibo.MoeWebsite+"/authredirect?code=sina\n"+
              moeweibo.MoeWebsite+"/authredirect?code=tencent\n")
        self.response.write("OK")

class ClearCallbackHandler(webapp2.RequestHandler):
    def get(self):
        moefeeds.clearOldFeeds()
        self.response.write("<html><head><title>MoeWeibo</title></head><body>Clear History Success</body></html>")

class ClearAuthCallbackHandler(webapp2.RequestHandler):
    def get(self):
        moeweibo.clearAuths()
        self.response.write("<html><head><title>MoeWeibo</title></head><body>Clear Auth Success</body></html>")

class ForbiddenCallbackHandler(webapp2.RequestHandler):
    def get(self):
        html = "<html><head><title>MoeWeibo</title></head><body>"

        c = self.request.get("add")
        if(len(c)>0):
            if(moeforbidden.addForbidden(c)):
                html += "Add success<br/>"
            else:
                html += "Add fail<br/>"
        c = self.request.get("remove")
        if(len(c)>0):
            if(moeforbidden.removeForbidden(c)):
                html += "Remove success<br/>"
            else:
                html += "Remove fail<br/>"
        
        html += "<ul>"
        l = moeforbidden.getForbidden()
        for d in l:
            html += "<li>"+d+"</li>"
        html += "</ul><br/>"
        html += """
        Add:<form method="get">
        <input name="add" />
        <input type="submit" />
        </form><br/>"""
        html += """
        Remove:<form method="get">
        <input name="remove" />
        <input type="submit" />
        </form><br/>"""
        html += "PS.All characters are lowered</br>"
        html += "</body></html>"
        self.response.write(html)

class TestCallbackHandler(webapp2.RequestHandler):
    def get(self):
        feeds = moefeeds.parseFeed("http://zh.moegirl.org/index.php?title=Special:%E6%9C%80%E8%BF%91%E6%9B%B4%E6%94%B9&feed=atom&namespace=0")
        #self.response.write(feeds)
        self.response.write("Click me!\n"+
              moeweibo.MoeWebsite+"/clearauth\n"+
              moeweibo.MoeWebsite+"/authredirect?code=sina\n"+
              moeweibo.MoeWebsite+"/authredirect?code=tencent")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/authredirect', AuthCallbackHandler),
    ('/sinacallback', SinaCallbackHandler),
    ('/tencentcallback', TencentCallbackHandler),
    ('/send', SendCallbackHandler),
    ('/sendmail', SendmailCallbackHandler),
    ('/clear', ClearCallbackHandler),
    ('/clearauth', ClearAuthCallbackHandler),
    ('/forbidden', ForbiddenCallbackHandler),
    ('/test', TestCallbackHandler)
], debug=True)
