import webapp2
import cgi
import string

class Rot13(webapp2.RequestHandler):
    form = """
    <html>
    <body>
      <h2>Enter some text to ROT13:</h2>
      <form method="post">
	<textarea name="text" rows="10" cols="60">%(text)s</textarea><br/>
        <input type="submit" value="submit">
      </form>
    </body>
    </html>
    """

    def write_form(self, text=""):
        self.response.out.write(self.form % {"text": text})
        
    def get(self):
        self.write_form()

    def post(self):
        text = self.request.get("text")
        encoded_text = text.encode("rot13")
        self.write_form(cgi.escape(encoded_text, quote=True))

