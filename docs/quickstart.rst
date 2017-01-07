.. _quickstart

PWF Quickstart Guide
====================

This guide explains how to get started with PWF. It only covers interacting
with the PWF library, integration and setup will be covered in another
section.

If you are familiar with Flask and to some extent even Web.py you will
without doubt see many similarities in how you interacti with PWF. 
This is intentional.

BUT, even though it looks very similar to Flask on the surface this
does not mean that you will be able to expect the same features in PWF.
Please read the README for what PWF is and what it is not.


The simplest case
-----------------

The most basic thing you can do with PWF is to recive a GET request
and return some text back to the user. For this, all you need is: ::
    
    from pwf.app import App()
    app = App()

    @app.route('/')
    def index(request):
        return 'Hello World'


First we import the App() object from pwf.app and create a new instance of
it named "app". After that we use the @app.route() decorator and pass it a
route to use (in this case just '/' for the root path). The function we
decorate, called "index" is responsible for generating the data we want
to return back to the user ("Hello World").


Basic Routing
-------------

Now let's take a look at routing and the @app.route decorator in a bit more
detail. In the previous example we defined only one route for '/'. Next
we'll declare some more routes with different paths: ::

    @app.route('/')
    def index(request):
        return 'This is the start page'


    @app.route('/news')
    def news(request):
        return 'Here are some news'


    @app.route('/user')
    def profile(request):
        return 'This is the users page'
        

We can define as many routes as we like and associate each one with a function.
As you might have noticed in the '/user' example, the name of the
path does not have to be the same as the function name.

You can also use variable paths to pass specific data from the URL to your
view function. This is done by encapsuling the variable part of the path
in "<" and ">", like so: ::
    
    @app.route(/user/<username>)
    def user(request, username):
        return 'Welcome back %s' % username

If you visit the path '/user/walter' the response will read "Welcome back walter".
You don't need to have the variable at the end of the path and a path can contain
multiple variable parts: ::

    @app.route(/user/<username>/profile/edit/<id>)
    def user(request, username, id):
        do_something(username, id)
        return 'A OK'



The view function
-----------------

The view function is the function you as the user define for each route. The job
of this function is to do whatever work you need perform and return something
back to the server.

The view function requires you to pass in the request object and any variable
you've defined in your path.

Example of a view function that does some basic work before returning
a JSON object with some very useful data: ::
    
    import json    

    @app.route(/user/<fullname>)
    def user(request, fullname):
        names = fullname.split('_')
        capitalized = " ".join([name.capitalize() for name in names])

        return json.dumps({'name': capitalized})



Request methods
---------------

By default a route defined in PWF only supports GET requests. To declare what
methods are supported you add an additional argument to the @app.route
decorator containing a list of methods: ::

    @app.route(/send, methods=['GET', 'POST'])
    def send(request):
        return 'Thanks!'

Now this view supports both GET and POST requests. To handle them
separately: ::

    @app.route('/send', methods=['GET', 'POST'])
    def send(request):
        if request.method == 'POST':
            return 'Thanks for sending your data!'
        elif request.method == 'GET':
            return 'This endpoint is for sending data'



The Request object
------------------

In the example above we used the request object through request.method to
check for POST or GET. The request object holds information about
the request that you can access in the view function.

The request object always needs to be passed into the view function
(althoug you can name it whatever you like). ::
    
    @app.route('/page1')
    def page_one(request):
        return 'Hello page 1'


Supported methods for the request object are:

``request.method``
    Return the request method as a string ('GET', 'POST', 'OPTIONS' etc)

``request.headers``
    Returns the request headers as a dictionary.

``request.query``
    Returns keys and values from a query string as a dictionary.

``request.data``
    Returns raw post data as a string or form data as a dictionary.

``request.json_data``
    Returns the request data as a dictionary. Requires the data to be
    valid json and the content-type to be application/json, if not it
    return None.

``request.files``
    If files where uploaded they will be stored in the request.files
    dictionary. The key is the name of the file and the value a PWF
    FileWrapper object.

``request.stream``
    Returns a cached version of the wsgi.input stream. 

``request.environ``
    Returns the raw WSGI environ dict.


Some examples: ::
    
    @app.route('/')
    def start(request):
        custom_header = request.headers['X-Custom-Header']
        user_id = request.query['id']

    @app.route('/update', methods=['POST'])
    def update(request):
        user_id = request.data['id']
        name = request.data['name']

    @app.route('/update-json', methods=['POST'])
    def update_json(request):
        data = request.json_data
        user_id = data['id']
        name = data['name']
    
    @app.route('/upload', methods=['POST'])
    def upload_file(request):
        f = request.files['myfile']
        f.save('/path/to/upload' + f.filename)



The Response object
-------------------

Just as there is a Request object PWF also has a Response object.
In all the examples so far the Response object was created for us behind
the scenes after we returned something from the view function. But
sometimes we want to modify it ourselves in the view.

This might be to set some custom headers, change the status code or
set a cookie.

You can create a response object like this: ::

    @app.route('/')
    def index(request):
        data = 'Hello World'
        resp = app.make_response(data)
        return resp

We create the object by calling app.make_response() and passing it our
return data. We then return the object itself from the view. 

To set a custom header, add a cookie and specify the status code: ::
    
    @app.route('/')
    def index(request):
        data = 'Hello World'
        resp = app.make_response(data, code=304) 
        resp['X-Custom-Header'] = 'value'
        resp.set_cookie('session', 'abcd1234')
        return resp

Here we define the response data and status code when we create the
object by passing it to the make_response method, but we can also
add it later. ::

    @app.route('/')
    def index(request):
        resp = app.make_response()
        resp.data = 'Hello Bacon'
        resp.code = 304
        return resp

Supported methods for the response object:

    - ``response.data``

    - ``response.headers``

    - ``response.set_cookie(key, value)``

    - ``response.code``


Using app.first and app.last
----------------------------

The "first" and "last" decorators are used to apply a function before or after
any request. Useful if you want to perform the same operation on all requests.


app.first
---------

Executed before the request reaches the view function. The app.first function
takes the request object as an argument and if the function returns a
not None value the view function is skipped and that value returned to the
server. If nothing is returned the view function will get executed normally.

Example of using @app.first to check the content type of incoming requests and
return 405 for all 'text/plain' requests: ::

    @app.first()
    def check_content_type(request):
        if request.headers['CONTENT_TYPE'] == 'text/plain':
            resp = app.make_response()
            resp.code = 405
            return resp

app.last
--------

Executed after the view function returns and before the response gets
sent back to the server. The app.last function takes the response object
as an argument and also needs to return a response object.

Example of using @app.last to add a content-type header to all requests: ::
    
    @app.last()
    def add_header(response):
        response.headers['Content-Type'] = 'application/json'
        return response


Working with groups
------------------

Sometimes adding rules to all incoming or outgoing requests is too general.
Here you can use groups to define what rules should be applied to what routes.

To define a group you add group="group-name" as an argument to both the routes
that should be included and the @app.last() decorator.

Example: ::
    
    @app.route('/')
    def view_func(request):
        return 'Hello'

    @app.route('/json', group='json_data')
    def view_func(request):
        return json.dumps({'data': 'Hello'})

    @app.last(group='json_data')
    def add_header(response):
        response.headers['Content-Type'] = 'application/json'
        return response


In the example above the add_header function will only be applied to
the '/json' route.


Configuration Handling
----------------------

The configuration is used to both change how PWF behaves and set
your own values to be used throughout the app.

The config is accessed through the app.config object and acts as 
any dictionary

Example: ::

    app = Pwf()
    app.config['DEBUG'] = True
    app.config['DB_USERNAME'] = 'mos_eisley'
    app.config['DB_PASSWORD'] = 'wretchedhiveofscumandvillany'


You can also load the configuration from a json file: ::

    app = Pwf()
    app.config.from_json_file('/path/to/file')


These are the config variables currently supported:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

================================= =========================================
``DEBUG``                         True or False. If set to true exceptions
                                  will not be catched and their traceback
                                  will be available. If set to false Pwf
                                  returns a standard 500 Internal Server
                                  Error response code if the application
                                  failes.
================================= =========================================


Working with files
------------------

The easisest way to upload an access files with Pwf is to use
multipart/form-data. This will make Pwf automatically add any files to
the ``request.files`` dictionary to be accessed in the view function.

The dictionary key is the field name and the value a Pwf FileWrapper object.

Example: ::
    
    @app.route('/file-upload', methods=['POST'])
    def upload(request):
        my_file = request.files['my_file']
        print my_file.filename

        return 'Thanks!'

The FileWrapper is a small wrapper around a wsgi filestream that exposes
standard file operations like save, seek and read. It allows you to access
things like filename, content-type and headers.

To save a file to disk using the FileWrapper object: ::

    @app.route('/file-upload', methods=['POST'])
    def upload(request):
        my_file = request.files['my_file']
        filename = my_file.filename
        path = '/path/to/save/%s' % filename
        my_file.save(path)

        return 'Saved!'

Sometimes you might want to upload a file using raw binary data with for
example an application/octet-stream content-type header. Pwf will not make
any assumptions about this type of data even if the content-disposition is set.
This is by design and according to the IANA specification.

You can use the FileWrapper object to wrap your binary data and then perform
any file-like operations on it.

Example: ::

    from pwf.wrappers import FileWrapper

    @app.route('/binary-upload', methods=['POST'])
    def upload(request):
        binary = request.stream
        filename = 'my_file.png'

        my_file = FileWrapper(binary, filename=filename, content_type='image/png')
        my_file.save('/path/to/file/my_file.png')
        
        return 'Saved'

