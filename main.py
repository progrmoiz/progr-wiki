import webapp2


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
    pass


PAGE_RE = r'/([a-zA-Z0-9_-]+)*'
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/_edit/' + PAGE_RE, EditPage),
    ('/_history/' + PAGE_RE, HistoryPage),
    (PAGE_RE, WikiPage)
], debug=True)
