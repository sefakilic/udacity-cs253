import webapp2
import jinja2
from google.appengine.ext import db
import os
import re
import hashlib
import hmac
import random
import string

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

secret = "nooneknows"

# cookie hash stuff
def make_secure_val(val):
    return "%s|%s" % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    return secure_val == make_secure_val(val)

# user hash stuff
def make_salt(length=10):
    return "".join(random.choice(string.letters) for x in xrange(length))

def make_pw_hash(pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(pw + salt).hexdigest()
    return "%s#%s" % (h, salt)
                               
def valid_pw(pw, h):
    salt = h.split('#')[1]
    return h == make_pw_hash(pw, salt)

def set_cookie(handler, name, value):
    handler.response.headers.add_header("Set-Cookie", "%s=%s; Path=/" %
                                        (str(name), str(value)))

# user model
class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)

def add_user(username, **kw):
    u = User(key_name=username, username=username, **kw)
    u.put()

def get_user(username):
    return User.get_by_key_name(username)

# signup Handler
class Signup(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("signup.html")
        self.response.out.write(template.render())

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        errors = {}
        # verify username
        if not self.valid_username(username):
            errors["invalid_username"] = "That's not a valid username."
            errors["username"] = username
        # verify password
        if not self.valid_password(password):
            errors["invalid_password"] = "That wasn't a valid password."
        elif not self.valid_verify(password, verify):
            # if password is valid, check if password and verify match.
            errors["invalid_verify"] = "Your passwords didn't match."
        # verify  email
        if email and not self.valid_email(email):
            errors["invalid_email"] = "That's not a valid email."

        # check if a user with same username exists?
        if get_user(username):
            errors.clear()
            errors["invalid_username"] = "That user already exists"
            
        if errors:
            template = jinja_environment.get_template("signup.html")
            self.response.out.write(template.render(errors))
        else:
            add_user(username=username, password=make_pw_hash(password))
            set_cookie(self, "username", make_secure_val(username))
            self.redirect("/blog/welcome")
        
    def valid_username(self, username):
        return USER_RE.match(username)

    def valid_password(self, password):
        return PASSWORD_RE.match(password)

    def valid_verify(self, password, verify):
        """Check if password and verify same."""
        return password == verify

    def valid_email(self, email):
        return EMAIL_RE.match(email)

# login handler
class Login(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template("login.html")
        self.response.out.write(template.render())

    def post(self):
        username = self.request.get("username")
        password = self.request.get("password")

        errros = {}
        u = get_user(username)
        if u and valid_pw(password, u.password):
            set_cookie(self, username, make_secure_val(username))
            self.redirect("/blog/welcome")
        else:
            error = "Invalid login"
            template_values = {"error": error}
            template = jinja_environment.get_template("login.html")
            self.response.out.write(template.render(template_values))

class Logout(webapp2.RequestHandler):
    def get(self):
        set_cookie(self, "username", "")  # clear cookie
        self.redirect("/blog/signup")

# welcome page handler
class Welcome(webapp2.RequestHandler):
    def get(self):
        c = self.request.cookies.get("username")
        if check_secure_val(c):
            username = c.split('|')[0]
            template_values = {"username": username}
            template = jinja_environment.get_template("welcome.html")
            self.response.out.write(template.render(template_values))
        else:
            self.redirect("/blog/signup")
        
