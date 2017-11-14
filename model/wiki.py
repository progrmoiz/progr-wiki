from datetime import datetime
from google.appengine.ext import ndb

from user import User


def wiki_key(name='default'):
    return ndb.Key('wikis', name)


class Wiki(ndb.Model):
    """Wiki datastore

    subject vs url:
    subject has a seperator of space while url has underscore (_)
    """
    subject = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    content = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

    # update last_modified value manually
    last_modified = ndb.DateTimeProperty(auto_now_add=True)
    last_contributor = ndb.StructuredProperty(User)

    @classmethod
    def by_id(cls, id):
        return Wiki.get_by_id(id, parent=wiki_key())

    @classmethod
    def by_path(cls, path):
        w = Wiki.query(Wiki.url == path).get()
        return w

    @classmethod
    def create_wiki(cls, subject, content, contributor):
        url = subject.replace(' ', '_')
        return Wiki(parent=wiki_key(),
                    subject=subject,
                    url=url,
                    content=content,
                    last_contributor=contributor)

    def update_wiki(self, subject, content, contributor):
        url = subject.replace(' ', '_')
        self.url = url
        self.subject = subject
        self.content = content
        self.last_contributor = contributor
        self.last_modified = datetime.now()
