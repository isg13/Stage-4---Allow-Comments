import time
import os
import webapp2
import jinja2
from google.appengine.ext import ndb

template_dir=os.path.join(os.path.dirname(__file__), 'template')
jinja_env=jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
								autoescape = True)
DEFAULT_WALL = "Public"

def wall_key(wall_name = DEFAULT_WALL):
	return ndb.Key('Wall', wall_name)

class CommentsArea(ndb.Model):
	name = ndb.StringProperty(indexed=False)
	content = ndb.StringProperty(indexed=False)
	date = ndb.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):
		wall_name = self.request.get('wall_name', DEFAULT_WALL)
		if wall_name == DEFAULT_WALL.lower(): wall_name = DEFAULT_WALL
		comments_query = CommentsArea.query(ancestor = wall_key(wall_name)).order(-CommentsArea.date)
		comments = comments_query.fetch()
		self.render("page.html", comments=comments)

class Post(Handler):
	def post(self):
		wall_name = self.request.get('wall_name',DEFAULT_WALL)
		comments_area = CommentsArea(parent = wall_key(wall_name))
		comments_area.name = self.request.get('name')
		comments_area.content = self.request.get('comments')
		if not comments_area.content:
			error = "Please try again as comments without content are not allowed";
			self.render("page.html", notification=error)
		else:
			comments_area.put()
			self.redirect('/')
		
app=webapp2.WSGIApplication([('/', MainPage), ("/comments", Post)], debug=True)