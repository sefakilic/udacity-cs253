import webapp2
import jinja2
import os
from google.appengine.ext import db
import time
import json

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True)

class BlogPost(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def toJSON(self):
        d = dict(subject=self.subject, content=self.content,
                 created=self.created.strftime("%b %d, %Y"))
        return json.dumps(d)
        
class BasicHandler(webapp2.RequestHandler):
    def write_html(self, template_file, **kwargs):
        template = jinja_environment.get_template(template_file)
        self.response.out.write(template.render(**kwargs))
        
class Blog(BasicHandler):
    def get(self):
        blog_posts = BlogPost.all().order("-created")
        self.write_html("blog.html", blog_posts=blog_posts)

class BlogJSON(BasicHandler):
    def get(self):
        posts = BlogPost.all().order("-created")
        json_objs = [p.toJSON() for p in posts]
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write('[' + ','.join(json_objs) + ']')
    
class Post(BasicHandler):
    def get(self, post_id):
        key = db.Key.from_path("BlogPost", int(post_id))
        post = db.get(key)
        self.write_html("post.html", post=post)

class PostJSON(BasicHandler):
    def get(self, post_id):
        key = db.Key.from_path("BlogPost", int(post_id))
        post = db.get(key)
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(post.toJSON())
        
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
            self.redirect("/blog/%s" % b.key().id())
            
