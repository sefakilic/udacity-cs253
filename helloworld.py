import webapp2
import rot13
import signup
import blog

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write("Hello, Udacity!")

app = webapp2.WSGIApplication([("/?", MainPage),
                               ("/rot13/?", rot13.Rot13),
                               ("/blog/signup/?", signup.Signup),
                               ("/blog/login/?", signup.Login),
                               ("/blog/logout/?", signup.Logout),
                               ("/blog/welcome/?", signup.Welcome),
                               ("/blog/?", blog.Blog),
                               ("/blog/([0-9]+)/?", blog.Post),
                               ("/blog/newpost/?", blog.NewPost),
                              #json
                               (("/blog/.json"), blog.BlogJSON),
                               (("/blog/([0-9]+).json"), blog.PostJSON)],
                              debug=True)

