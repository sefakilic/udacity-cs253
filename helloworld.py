import webapp2
import rot13

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-Type"] = "text/plain"
        self.response.write("Hello, Udacity!")

app = webapp2.WSGIApplication([("/", MainPage),
                               ("/rot13", rot13.Rot13)],
                              debug=True)
