import webapp2

from google.appengine.ext import ndb

from model import WikiData

# data = []
# for i in range(0, 100):
#     data[i] = WikiData()
#     data[i].subject = 'title ' + str(i)
#     data[i].content = 'body ' + str(i)
#     data[i].history = [data[i].content]
#     data[i].put()

class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.write(*a, **kw)


class MainPage(BaseHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.write('H!ello World!')


class EditPage(BaseHandler):
    pass


class HistoryPage(BaseHandler):
    pass


class WikiPage(BaseHandler):
    def get(self, url):
        self.write(url)


PAGE_RE = r'/([a-zA-Z0-9_-]+)*'
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/_edit/' + PAGE_RE, EditPage),
    ('/_history/' + PAGE_RE, HistoryPage),
    (PAGE_RE, WikiPage)
], debug=True)
