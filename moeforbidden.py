import logging
from google.appengine.ext import db

class forbiddenModel(db.Model):
    content = db.StringProperty(required=True)


def addForbidden(content):
	content = content.lower()
	datas = db.GqlQuery("SELECT * FROM forbiddenModel where content=:1", content)
	if(datas.count()==0):
		d = forbiddenModel(content=content)
		d.put()
		return True
	return False

def removeForbidden(content):
	content = content.lower()
	datas = db.GqlQuery("SELECT * FROM forbiddenModel where content=:1", content)
	if(datas.count()==0):
		return False
	for d in datas:
		d.delete()
	return True

def getForbidden():
	d = []
	datas = db.GqlQuery("SELECT * FROM forbiddenModel")
	for d2 in datas:
		d.append(d2.content) 
	return d
	