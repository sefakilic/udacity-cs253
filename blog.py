import webapp2
import jinja2
import os
from google.appengine.ext import db
from google.appengine.api import memcache
import logging
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

def age_set(key, val):
    save_time = time.time()
    memcache.set(key, (val, save_time))

def age_get(key):
    r = memcache.get(key)
    if r:
        val, save_time = r
        age = time.time() - save_time
    else:
        val, age = None, 0
    return val, age

class Blog(BasicHandler):
    def get(self):
        blog_posts,age = self.get_blog_posts()
        self.write_html("blog.html", blog_posts=blog_posts, queried=age)

    def get_blog_posts(self):
        """Get blog posts. If they are in cache, don't hit the db"""
        blog_posts,age = age_get("blog_posts")
        if blog_posts:
            return blog_posts, age
        else:
            blog_posts = BlogPost.all().order("-created")
            age_set("blog_posts", blog_posts)
        return age_get("blog_posts")

class BlogJSON(BasicHandler):
    def get(self):
        posts = BlogPost.all().order("-created")
        json_objs = [p.toJSON() for p in posts]
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write('[' + ','.join(json_objs) + ']')
    
class Post(BasicHandler):
    def get(self, post_id):
        post,age = self.get_post(post_id)
        self.write_html("post.html", post=post, queried=age)

    def get_post(self, post_id):
        postkey = "post_%s" % post_id
        post, age = age_get(postkey)
        if post:
            return post, age
        else:
            key = db.Key.from_path("BlogPost", int(post_id))
            post = db.get(key)
            age_set(postkey, post)
            
        return age_get(postkey)

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
            memcache.delete("blog_posts")
            self.redirect("/blog/%s" % b.key().id())
            
class FlushCache(BasicHandler):
    def get(self):
        memcache.flush_all()
        self.redirect("/blog")
