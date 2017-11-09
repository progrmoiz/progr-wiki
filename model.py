from google.appengine.ext import ndb

class WikiData(ndb.Model):
    subject = ndb.StringProperty()
    content = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)
    history = ndb.PickleProperty(compressed=True)