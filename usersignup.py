import webapp2
import jinja2
import os
import re

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

class UserSignup(webapp2.RequestHandler):    
    def get(self, template_values = {}):
        template = jinja_environment.get_template("signup.html")
        self.response.out.write(template.render(template_values))

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
        # verify email
        if email and not self.valid_email(email):
            errors["invalid_email"] = "That's not a valid email."

        if errors:
            template = jinja_environment.get_template("signup.html")
            self.response.out.write(template.render(errors))
        else:
            self.redirect("/welcome?username=%s" % username)
            
 
    def valid_username(self, username):
        return USER_RE.match(username)

    def valid_password(self, password):
        return PASSWORD_RE.match(password)

    def valid_verify(self, password, verify):
        """Check if password and verify same."""
        return password == verify

    def valid_email(self, email):
        return EMAIL_RE.match(email)
        
class Welcome(webapp2.RequestHandler):
    def get(self):
        username = self.request.get("username")
        template_values = {"username": username}
        template = jinja_environment.get_template("welcome.html")
        self.response.out.write(template.render(template_values))
        
