.. _quickstart

PWD Quickstart Guide
====================

This guide explains how to get started with pwd. It only covers interacting
with the PWD library, integration with uwsgi and nginx are covered in the 
"Hook things up" guide.

If you are familiar with using Flask and to some extent even web.py you will
without doubt see how similar the interaction with PWD is to those frameworks. 
This is very intentional. There are however some small details that differ
so make sure to glance over the basics.

DISCLAIMER: Even though it looks very similar to Flask on the surface this
does not mean that you will be able to expect that the same features are 
availabel to you. Please read the README file for what PWD is and what it is not.


The simplest case
-----------------

Perhaps the most basic thing you can do with PWD is to recive a GET request
and return some text. For this, all you need is five lines of code ::
    
    from pwd.app import App()
    app = App()

    @app.route('/')
    def index(request):
        return 'Hello World'


First we imported the App() object from pwd.app and created a new instance of
it named "app". This app object is what we use to interact with PWD.

After that we used the @app.route() decorator and passed it a route to use
(in this case just '/' for the root path). The function we decorated, called 
"index" in this example will be responsible for whatever we want to do with the
request before we return a response to the server. In this case the only thing it
does is to return the string 'Hello World'.


Basic Routing
-------------

Now let's take a look at routing and the @app.route decorator in a bit more
detail. In the previous example we defined only one route with the '/' URL. Next
we'll declare some more routes with different paths ::

    @app.route('/')
    def index(request):
        return 'This is the start page'


    @app.route('/news')
    def news(request):
        return 'Here are some news'


    @app.route('/user')
    def profile(request):
        return 'This is the users page'
        

So basically we can define as many routes as we like and associate each one
with a function. As you might have noticed in the last example, the name of the
url does not have to be the same as the function name, but it helps to keep
things tidy. 

This far we've only looked at static paths, but you can also use variable paths
to pass specific data from the URL to your view function. This is done by encapsuling
the path in "<" and ">", like so ::
    
    @app.route(/user/<username>)
    def user(request, username):
        return 'Welcome back %s' % username

If you visit the url /user/walter the response will read "Welcome back walter".
You don't need to have the variable at the end of the url and an url can contain
multiple variables ::

    @app.route(/user/<username>/profile/edit/<id>)
    def user(request, username, id):
        do_something(username, id)
        return 'A OK'



The view function
-----------------

The view function is the function you as the user define and the decorate with
the route decorator. The job of this function is to do whatever work you need it
to perform and return something back to the server. It could fetch some data from
a database, do some computation or just return some basic data. 

As you might have seen we pass some arguments to these functions. the first one
is the request argument that is injected by PWF and we'll get back to that one. 
The others are the variables we defined in our url that need to be passed in 
for us to use. 

Example of a view function that does some very basic work before returning
a json object with some very useful data ::
    
    import json    

    @app.route(/user/<fullname>)
    def user(request, fullname):
        names = fullname.split('_')
        capitalized = " ".join([name.capitalize() for name in names])

        return json.dumps({'name': capitalized})



Request methods
---------------

By default a route defined in PWD only supports GET requests. That might feel
a bit too limiting, so lets make it accept POSTs as well. To declare what
methods are supported you add an additional argument to the @app.route decorator
containing a list of methods. Like this ::

    @app.route(/send, methods=['GET', 'POST'])
    def send(request):
        return 'Thanks!'

Now this view supports both GET and POST requests. To handle the different
request types you do the following ::

    @app.route('/send', methods=['GET', 'POST'])
    def send(request):
        if request.method == 'POST':
            return 'Thanks for sending your data!'
        elif request.method == 'GET':
            return 'This endpoint is for sending data'
        else:
            return 'Please use GET or POST requests'



The request object
------------------

In the example above we used the request object through request.method to
check for POST or GET. The request object holds important information about
the request that was made for you to use in your view function.

The request object always needs to be passed into the view function
like this (althoug you can name it whatever you like) ::
    
    @app.route('/page1')
    def page_one(request):
        return 'Hello page 1'


Supported variables are:

    - request.method:
      Return the request method as a string (GET, POST, OPTIONS, PUT etc)

    - request.headers:
      Returns the request headers

    - request.query:
      Returns keys and values from a query string as a dictionary.

    - request.data:
      Returns raw post data as a string or form data as a dictionary.

    - request.environ:
      Returns the raw WSGI environ dict.










