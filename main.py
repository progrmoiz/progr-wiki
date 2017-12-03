import os
import json
import time
import urllib
import logging

from abc import ABCMeta, abstractmethod

import webapp2
import jinja2

from model.user import User
from model.wiki import Wiki
from model.wiki_history import WikiHistory

from utils.secure import make_secure_val, check_secure_val
from utils.validate import valid_username, valid_password, valid_email

PATHS = {
    'redirect':  'redirect_to'
}

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
JINJA_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
)


def render_str(template, **params):
    """Render jinja template
    """
    t = JINJA_ENV.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    """This is Base Handler class

    Now our handler will extends this class and gets some additional
    functionality and configuration
    """

    def write(self, *a, **kw):
        """It is simply going to write a response
        """
        self.response.write(*a, **kw)

    def render_str(self, template, extension='.html', **params):
        """Our helper render_str
        """
        # These params is going on every render
        params['title'] = 'Progrwiki'
        params['user'] = self.user
        return render_str(template + extension, **params)

    def render(self, template, **kw):
        """It is going to render a template and
        write it as response
        """
        self.write(self.render_str(template, extension='.html', **kw))

    def render_json(self, d):
        """It is going to write a json response
        """
        json_txt = json.dumps(d)
        self.response.content_type = 'application/json;charset=UTF-8'
        self.write(json_txt)

    def set_secure_cookie(self, name, val):
        """Method for setting private cookie
        """
        cookie_val = make_secure_val(val)
        # max_age=2.628e+6 (30 days)
        self.response.set_cookie(name, cookie_val,
                                 path='/', max_age=3600)

    def read_secure_cookie(self, name):
        """Method for getting private cookie
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        """Set the cookie, so user can keep logged
        """
        self.set_secure_cookie('user_id', str(user.key.id()))

    def logout(self):
        """Remove the cookie, so user will logout
        """
        self.response.set_cookie('user_id', '',
                                 path='/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)

        # set self.user to current user logged in
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))
        # if url ends with .json set selfat to json else html


class MainPage(BaseHandler):

    def get(self):
        self.render('main')


class SignUp(BaseHandler):
    __metaclass__ = ABCMeta

    def get(self):
        if self.user:
            self.redirect('/welcome')
        path = self.request.get('redirect_to')
        self.render('signup', path=path)

    def post(self):
        # currently no errors
        have_error = False

        # getting values
        self.name = self.request.get('name')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')
        self.redirect_to = self.request.get('redirect_to')

        params = dict(name=self.name,
                      email=self.email)

        if not valid_username(self.name):
            params['error_username'] = "This username is invalid"
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That's not a valid password."
            have_error = True
        elif self.password != self.verify:
            params['password'] = self.password
            params['error_verify'] = "Your password didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "This email is invalid."
            have_error = True

        if have_error:
            self.render('signup', **params)
        else:
            self.done()

    @abstractmethod
    def done(self):
        pass


class Register(SignUp):

    def done(self):
        # make sure that user doesn't already exist
        u = User.by_name(self.name)
        if u:
            msg = 'That user already exist'
            self.render('signup', error_username=msg)
        else:
            u = User.register(self.name, self.password, self.email)
            u.put()

            # set cookie
            # and redirect to welcome
            self.login(u)
            self.redirect(self.redirect_to)


class Login(BaseHandler):

    def get(self):
        if self.user:
            self.redirect('/welcome')
        path = self.request.get('redirect_to')
        self.render('login', path=path)

    def post(self):
        self.name = self.request.get('name')
        self.password = self.request.get('password')
        self.redirect_to = self.request.get('redirect_to')

        u = User.login(self.name, self.password)

        if u:
            time.sleep(1)
            self.login(u)
            self.redirect(self.redirect_to)
        else:
            msg = 'Invalid login'
            self.render('login', error=msg)


class Logout(BaseHandler):

    def get(self):
        self.logout()
        path = self.request.get('redirect_to')
        self.redirect('/' + path)


class EditPage(BaseHandler):

    def get(self, url):
        version = self.request.get('v')

        # if user is not logged in redirect to login page
        # if post is already exist add content and subject to template
        if self.user:
            wiki = Wiki.by_path(url)
            if wiki:
                wiki_history = WikiHistory.by_path(wiki.url)

                # ?v=n
                # changing versions
                if version:
                    version = int(version)
                    if version > 0 and version <= len(wiki_history.history):
                        version -= 1
                        wiki = wiki_history.get_wiki(version)
                    else:
                        print('not valid')

                subject = wiki.subject
                content = wiki.content
            else:
                subject = url.replace('_', ' ') if url else ''
                content = None

            btntext = 'Save'

            # if user access _edit page with no path
            # then set path to '' instead of 'None'
            # else normally url
            path = url if url else ''

            params = dict(wiki=wiki,
                          subject=subject,
                          content=content,
                          btntext=btntext,
                          path=path)

            self.render('edit', **params)
        else:
            if url:
                self.redirect('/login?redirect_to=/_edit/' + url)
            else:
                self.redirect('/login?redirect_to=/_edit/')

    def post(self, url):
        content = self.request.get('content')
        subject = self.request.get('subject')
        path = self.request.get('path')

        # if path is empty create path from subject
        if not path:
            path = subject.replace(' ', '_')

        wiki = Wiki.by_path(path)
        print('subject', subject)
        print('path', path)

        if wiki:
            wiki.update_wiki(subject, content, self.user)
            wiki.put()
            wiki_history = WikiHistory.by_path(wiki.url)
            wiki_history.add_wiki_history(wiki)
            wiki_history.put()
            print(wiki_history.url)
            for wiki in wiki_history.history:
                print(wiki.last_contributor)
        else:
            wiki = Wiki.create_wiki(subject, content, self.user)
            wiki.put()
            wiki_history = WikiHistory.create_wiki_history(wiki)
            wiki_history.put()

        time.sleep(1)
        self.redirect('/' + path)


# TODO: IMplemnet _history page
# TODO: /path?v=n history
class HistoryPage(BaseHandler):
    def get(self, url):
        wiki = Wiki.by_path(url)
        if (wiki):
            wiki_history = WikiHistory.by_path(wiki.url)
            history = list(enumerate(wiki_history.history))

            self.render('history', subject=wiki.subject,
                        history=reversed(history))
        else:
            self.redirect('/_edit/' + url)


class WikiPage(BaseHandler):

    def get(self, url):
        version = self.request.get('v')

        wiki = Wiki.by_path(url)
        # the wiki exist
        if wiki:
            wiki_history = WikiHistory.by_path(wiki.url)

            # ?v=n
            # changing versions
            print(len(wiki_history.history))
            print(version)
            if version:
                version = int(version)
                if version >= len(wiki_history.history):
                    version = False
                elif version > 0 and version < len(wiki_history.history):
                    wiki = wiki_history.get_wiki(version-1)
                else:
                    print('not valid')

            redirect = urllib.urlencode({PATHS['redirect']: wiki.url})

            logging.info(redirect)

            params = dict(wiki=wiki,
                          path=wiki.url,
                          redirect=redirect,
                          version=version)

            self.render('wiki-page', **params)
        else:
            self.redirect('/_edit/' + url)


PAGE_RE = r'/([a-zA-Z0-9()_-]+)*'
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/register', Register),
    ('/login', Login),
    ('/logout', Logout),
    ('/_edit' + PAGE_RE, EditPage),
    ('/_history' + PAGE_RE, HistoryPage),
    (PAGE_RE, WikiPage)
], debug=True)
