from google.appengine.ext import ndb

from wiki import Wiki


def wikihistory_key(name='default'):
    return ndb.Key('wikis_history', name)


class WikiHistory(ndb.Model):
    """WikiHistory datastore

    A place where recent wiki stores
    all WikiHistory instances has wikis and all wiki.last_modified will be
    same because they are just instances
    """
    url = ndb.StringProperty(required=True)
    history = ndb.StructuredProperty(Wiki, repeated=True)

    @classmethod
    def by_path(cls, path):
        w = WikiHistory.query(Wiki.url == path).get()
        return w

    @classmethod
    def create_wiki_history(cls, wiki):
        return WikiHistory(parent=wikihistory_key(),
                           url=wiki.url,
                           history=[wiki])

    def add_wiki_history(self, wiki):
        self.history.append(wiki)

    def get_wiki(self, index):
        return self.history[index]
