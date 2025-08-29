+++
type = "post"
title = "Introducing Motor, an asynchronous MongoDB driver for Python and Tornado"
date = "2012-07-06T14:37:29"
description = ""
category = ["MongoDB", "Motor", "Programming", "Python"]
tag = []
enable_lightbox = false
thumbnail = "dampfmaschinen2-brockhaus.jpg"
draft = false
+++

<p><img alt="Dampfmaschinen2 brockhaus" border="0" src="dampfmaschinen2-brockhaus.jpg" style="display:block; margin-left:auto; margin-right:auto;" title="Dampfmaschinen2_brockhaus.jpg"/></p>
<p>Tornado is a popular asynchronous Python web server, and MongoDB a widely used non-relational database. Alas, to connect to MongoDB from a Tornado app requires a tradeoff: You can either use <a href="http://pypi.python.org/pypi/pymongo/">PyMongo</a> and give up the advantages of an async web server, or use <a href="http://pypi.python.org/pypi/asyncmongo/1.2.1">AsyncMongo</a>, which is non-blocking but lacks key features.</p>
<p>I decided to fill the gap by writing a new async driver called Motor (for "MOngo + TORnado"), and it's reached the public alpha stage. Please try it out and tell me what you think. I'll maintain a homepage for it <a href="http://motor.readthedocs.org/">here</a>.</p>
<h1 id="status">Status</h1>
<p><strong>Update</strong>: /motor-progress-report/.</p>
<p>Motor is alpha. It is certainly buggy. Its implementation and possibly its API will change in the coming months. I hope you'll help me by reporting bugs, requesting features, and pointing out how it could be better.</p>
<h1 id="advantages">Advantages</h1>
<p>Two good projects, AsyncMongo and <a href="https://github.com/yamins81/apymongo/">APyMongo</a>, took the straightforward approach to implementing an async MongoDB driver: they forked PyMongo and rewrote it to use callbacks. But this approach creates a maintenance headache: now every improvement to PyMongo must be manually ported over. Motor sidesteps the problem. It uses a Gevent-like technique to wrap PyMongo and run it asynchronously, while presenting a classic callback interface to Tornado applications. This wrapping means Motor reuses all of PyMongo's code and, aside from GridFS support, Motor is already feature-complete. Motor can easily keep up with PyMongo development in the future.</p>
<h1 id="installation">Installation</h1>
<p>Motor depends on <a href="http://pypi.python.org/pypi/greenlet">greenlet</a> and, of course, Tornado. It's been tested only with Python 2.7. You can get the code from my fork of the PyMongo repo, on the <code>motor</code> branch:</p>

{{<highlight plain>}}
pip install tornado greenlet    
pip install git+https://github.com/ajdavis/mongo-python-driver.git@motor
{{< / highlight >}}

<p>To keep up with development, <a href="https://github.com/ajdavis/mongo-python-driver/tree/motor">watch my repo</a> and do </p>

{{<highlight plain>}}
pip install -U git+https://github.com/ajdavis/mongo-python-driver.git@motor
{{< / highlight >}}

<p>when you want to upgrade.</p>
<p><strong>Note</strong>: Do not install the official PyMongo. If you have it installed, uninstall it before installing my fork.</p>
<h1 id="example">Example</h1>
<p>Here's an example of an application that can create and display short messages.</p>
<p><strong>Updated Jan 11, 2013</strong>: <a href="/motorconnection-has-been-renamed-motorclient/">MotorConnection has been renamed MotorClient</a>.</p>

{{<highlight python3>}}
import tornado.web, tornado.ioloop
import motor

class NewMessageHandler(tornado.web.RequestHandler):
    def get(self):
        """Show a 'compose message' form"""
        self.write('''
        <form method="post">
            <input type="text" name="msg">
            <input type="submit">
        </form>''')

    # Method exits before the HTTP request completes, thus "asynchronous"
    @tornado.web.asynchronous
    def post(self):
        """Insert a message
        """
        msg = self.get_argument('msg')

        # Async insert; callback is executed when insert completes
        self.settings['db'].messages.insert(
            {'msg': msg},
            callback=self._on_response)

    def _on_response(self, result, error):
        if error:
            raise tornado.web.HTTPError(500, error)
        else:
            self.redirect('/')

class MessagesHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        """Display all messages
        """
        self.write('<a href="/compose">Compose a message</a><br>')
        self.write('<ul>')
        db = self.settings['db']
        db.messages.find().sort([('_id', -1)]).each(self._got_message)

    def _got_message(self, message, error):
        if error:
            raise tornado.web.HTTPError(500, error)
        elif message:
            self.write('<li>%s</li>' % message['msg'])
        else:
            # Iteration complete
            self.write('</ul>')
            self.finish()

db = motor.MotorClient().open_sync().test

application = tornado.web.Application([
        (r'/compose', NewMessageHandler),
        (r'/', MessagesHandler)
    ], db=db
)

print 'Listening on http://localhost:8888'
application.listen(8888)
tornado.ioloop.IOLoop.instance().start()
{{< / highlight >}}

<p>A full example is <a href="https://github.com/ajdavis/motor-blog">Motor-Blog</a>, a basic blog engine.</p>
<h1 id="support">Support</h1>
<p>For now, you can ask for help in the comments, or email me directly at <a href="mailto:jesse@10gen.com">jesse@10gen.com</a> if you have any questions or feedback. I'm going on Zencation July 25th through August 13; aside from that time I'll do my best to respond immediately.</p>
<h1 id="roadmap">Roadmap</h1>
<p>In the next few months I'll implement the PyMongo feature I'm missing, <a href="https://pymongo.readthedocs.io/en/stable/api/gridfs/index.html">GridFS</a>, and make Motor work with all the Python versions Tornado does: Python 2.5, 2.6, 2.7, 3.2, and PyPy. (Only Python 2.7 is tested now.) Once the public alpha and beta stages have shaken out the bugs and revealed missing features, I hope Motor will be included as a module in the official PyMongo distribution.</p>
