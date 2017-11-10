from google.appengine.ext import ndb


def wiki_key(name='default'):
    return ndb.Key('wikis', name)


class Wiki(ndb.Model):
    subject = ndb.StringProperty()
    content = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    last_modified = ndb.DateTimeProperty(auto_now=True)

    @classmethod
    def by_id(cls, id):
        return Wiki.get_by_id(id, parent=wiki_key())

    @classmethod
    def by_subject(cls, subject):
        w = Wiki.query(Wiki.subject == subject).get()
        return w
