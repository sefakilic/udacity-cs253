import webapp2
import rot13
import signup
import blog

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write("Hello, Udacity!")

app = webapp2.WSGIApplication([("/", MainPage),
                               ("/rot13", rot13.Rot13),
                               ("/signup", signup.Signup),
                               ("/login", signup.Login),
                               ("/logout", signup.Logout),
                               ("/welcome", signup.Welcome),
                               ("/blog", blog.Blog),
                               ("/blog/newpost", blog.NewPost)],
                              debug=True)

