import cgi
from functools import wraps
import httplib
import urlparse

import cgitb
cgitb.enable()


class Request(object):
    """ Creates a request object given the environ
    object from the server.
    
    parse headers, query strings and post data

    """

    def __init__(self, environ):
        
        """
            Set Reguest object variables that will then 
            be accessible in the view function.
        """

        self.environ = environ
        self.headers = self.__parse_headers(environ)
        self.query = self.__parse_query(environ)
        self.data = self.__parse_data(environ)


    def __parse_headers(self, environ):
        length = environ.get('CONTENT_LENGTH', 0)
        headers = { 'CONTENT_LENGTH': 0 if not length else int(length) }

        # The headers we're interested in. 
        wanted_headers = ['REQUEST_METHOD', 'PATH_INFO', 'REMOTE_ADDR', 
                'REMOTE_HOST', 'CONTENT_TYPE']

        # Get header name and value from environ
        for k, v in environ.items():
            # Grab the headers we want and add them to the headers list.
            # We also want all the HTTP headers
            # TODO: Add support for cusom headers here?
            if k in wanted_headers or k.startswith('HTTP'):
                headers[k] = v
        
        return headers


    def __parse_query(self, environ):
        
        # Parse a query string into a dictionary with keys are query variable
        # names dict values is a list with query values.

        # query = cgi.parse_qs(environ['QUERY_STRING']) #NOTE: cgi.parse_qs is deprecated
        query = urlparse.parse_qs(environ['QUERY_STRING'])

        # Only select the first value for any give query variable.
        # Perhaps support multiple values in the future 
        unique_variables = {k: v[0] for k, v in query.items()}
        return unique_variables


    def __parse_data(self, environ):
        # parse the request body data

        # Get the content type of request body
        content_type = environ['CONTENT_TYPE'].lower()
        data = {}

        # If we're dealing with form data.
        if 'form' in content_type:
            print 'INSIDE FORM CONTENT TYPE'

            # cgi.FieldStorage reads form data and returns a FieldStorage object
            # that can be accessed like a standard dict
            env_data = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
            
            for k in env_data.list:
                # check that the request is not "application/x-www-form-urlencoded"
                # NOTE Perhaps add support for x-www-form in the futuere 
                if not isinstance(k, cgi.MiniFieldStorage):
                    if k.filename:
                         data[k.name] = k.file
                    else:
                        data[k.name] = k.value
            return data
        else:

            # If not form content (json, xml, javascript etc)
            # we just read and return the raw data from the environ object
            length = self.headers['CONTENT_LENGTH']
            return environ['wsgi.input'].read(length)

                


class Response(object):
    """ Response object is responsible for iterating the make_response and
    returning the view data

    :params code, the status code
    :params data, the raw data rendered from the view
    """

    def __init__(self, make_response, code=200, data=''):

        # Currently supporting a tuple of data-str and
        # header-dict. Or only data-str and empty headers

        if isinstance(data, tuple):
            self.data = data[0]
            headers = data[1]
        else:
            self.data = data
            headers = {}

        print map(lambda x:x.lower(), headers)

        # If the content type is not specified, we set
        # it to text/html as the default
        if 'content-type' not in map(lambda x:x.lower(), headers):
            headers['Content-Type'] = 'text/html'

        print [(k, v) for k,v in headers.items()]

        # Set headers as list of tuples
        self.headers = [(k, v) for k, v in headers.items()]

        # set the status code
        self.code = code

        # set the make response object to global
        self.make_response = make_response



    def render(self):
        # The final step. Render the response back to the server.

        # httplib.responses maps the HTTP 1.1 status codes to the W3C names
        # Output example: '200 OK' or '404 Not Found'
        resp_code = '{} {}'.format(self.code, httplib.responses[self.code])

        # If response code is 4XX or 5XX we return only the code as text
        if str(self.code)[0] in ['4', '5']:
            self.make_response(resp_code, self.headers)
            return resp_code.encode('utf-8')

       
        # NOTE: Do we need bytes if we're running python 2.x?
        try:
            data = bytes(self.data)
            print data
        except Exception:
            data = str(self.data).encode('utf-8')

        # Execute the WSGI make response function
        self.make_response(resp_code, self.headers)

        # Return the view data
        return data


class App(object):

    def __init__(self):
        self.routes = {}

    def route(self, url, methods=['GET']):
        """ This function gets called as a decorator for
        each view function. It adds the function itself, the
        specified url and the request methods to self.routes
        """
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            self.routes[url] = {'methods': methods, 'func': wrapper}
            return wrapper
        return decorate



    def path_dispatch(self, request, make_response):

        #Check the current path
        path = request.headers['PATH_INFO']

        #Check the current method
        method = request.headers['REQUEST_METHOD']

        view = self.routes.get(path) # Get the route function and method

        if not view:
            response = Response(make_response, 404) # If non-existent route, return 404
        elif method not in view['methods']:
            response = Response(make_response, 405) # If wrong method, return 405
        else:
            data = view['func'](request) # Execute view function to create response data
            response = Response(make_response, data=data) #Create a response object with view data

        return response



    def dispatch_request(self, environ, make_response):
        request = Request(environ) # Create a new Request object from environ

        # Generate a response from the request object we created
        response = self.path_dispatch(request, make_response)
        return response


    def __call__(self, environ, make_response):
        """ Gets executed when an instance of the
        class is called.

        environ and make_response are the
        standard wsgi objects
        """

        # The actual wsgi application
        resp = self.dispatch_request(environ, make_response)
        return resp.render()











