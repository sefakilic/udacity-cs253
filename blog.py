import webapp2
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
        
class BasicHandler(webapp2.RequestHandler):
    def write_html(self, template_file, **kwargs):
        template = jinja_environment.get_template(template_file)
        self.response.out.write(template.render(**kwargs))
        
class Blog(BasicHandler):
    def get(self):
        # if &id=xx on URL, fetch and display corresponding blog post
        post_id = self.request.get("id")
        if post_id:
            key = db.Key.from_path("BlogPost", int(post_id))
            post = db.get(key)
            blog_posts = [post]
        # otherwise, display all blog posts
        else:
            blog_posts = BlogPost.all().order("-created")
        self.write_html("blog.html", blog_posts=blog_posts)


class NewPost(BasicHandler):
    def get(self):
        self.write_html("newpost.html")

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")
        if not (subject and content):
            error_msg = "subject and content, please."
            self.write_html("newpost.html", error=error_msg)
        else:
            b = BlogPost(subject=subject, content=content)
            b.put()
            self.redirect("/blog?id=%s" % b.key().id())
        
