# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""

import re
from wrappers import Config
from request import Request
from response import Response
from functools import wraps
from stack import _app_stack
from exceptions import HTTPException, MethodNotAllowed, NotFound, InternalError
from utils import log
import wsgiref.simple_server


class Pwf(object):
    """This is the central object you instantiate and interact with in your
    program. Once created it can be used in the view to access things
    like cookies, headers, response codes etc.

    Example usage to define a view:
    
        app = Pwf()

        app.routes('/')
        def index(request):
                return 'Hello world'


    The above example instantiates the Pwf object, defines a route to '/'
    through the app.routes decorator and returns 'Hello World' from the
    view function.
    """
    
    def __init__(self):
        self.routes = []
        self.config = Config()
        self.first_funcs = {}
        self.last_funcs = {}
        self.errorhandlers = {}
        _app_stack.push(self)
    
    def run(self, host='127.0.0.1', port=5000):
        """Serves the PWF app using the wsgiref simple server. Use this
        only for quick testing in development.
        """
        httpd = wsgiref.simple_server.make_server('', port, self)
        log("PWF now running on http://%s:%s/" % (host, port,))
        httpd.serve_forever()

    def build_route_pattern(self, url):
        """Regex to find path variables in path"""
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', url)
        return re.compile("^{}$".format(route_regex))

    def get_route_match(self, path):
        """Match a path to an entry in self.routes and return variables,
        supported methods and view function
        """
        for route_pattern, methods, group, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), methods, group, view_function
            
        return None

    def route(self, url, methods=['GET'], group=None):
        """This function is used as a decorator for each view function
        to define the route associated with that view.
        
        Example:
            @app.route('/profile')
            def profile(request):
                return 'This is the profile page'

        It adds the path along with the view function itself, the request
        method and any route variables to self.routes for the path_dispatcher
        to user.
        """
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
        
            route_pattern = self.build_route_pattern(url) 
            self.routes.append((route_pattern, methods, group, f))
            return wrapper

        return decorate

    def path_dispatch(self, request, make_response):
        """Dispatches the request, does pre and post processing and
        dispatches any exceptions to the exception handler.
        """
        try:
            rv = self.preprocess_request(request)
            if rv is None:
                rv = self.process_request(request)
        except Exception as e:
            rv = self.handle_exception(e, make_response)

        return self.postprocess_request(rv, make_response)

    def dispatch_request(self, environ, make_response):
        """Instantiate a new Request object based on environ,
        pass it to the path dispatcher to get the response instance.
        """
        request = Request(environ)
        response = self.path_dispatch(request, make_response)
        return response

    def make_response(self, data=None):
        """Called from the view function to create and return
        a response object. This can then be used to add cookies,
        headers and more.
        """
        response = Response(data=data)
        return response

    def first(self, group=None):
        """Decorator used to specify functions to be executed
        before a request. If these functions return a value
        that will be used in the response rather than that of
        the view.
        
        Example usage to return "405 Method Not Allowed" for all
        request with content type text/plain:
        
        @app.first()
        def check_content_type(request):
            if request.headers['CONTENT_TYPE'] == 'text/plain':
                resp = app.make_response()
                resp.code = 405
                return resp
        """
        def wrapper(f):
            self.first_funcs.setdefault(group, []).append(f)
            return f
        return wrapper

    def last(self, group=None):
        """Decorator used to specify functions to be executed
        after each request. If these functions return a value
        that will be used in the response.
        
        Example usage to add a header to all responses:

        @app.last()
        def add_header(response):
            response.headers['Content-Type'] = 'application/json'
            return response
        """
        def wrapper(f):
            self.last_funcs.setdefault(group, []).append(f)
            return f
        return wrapper

    def error(self, code):
        """
        Define an error handler function to return custom data
        for different error codes.
        
        Example:
            
            @app.error(405)
            def handle_forbidden():
                return "I'm sorry Dave, I'm afraid i can't do that"
        """
        def wrapper(f):
            self.errorhandlers[code] = f
        return wrapper

    def preprocess_request(self, request):
        """The first step of the request to response cycle.
        Here we execute any general @app.first functions and
        if a return value is given return it to the server.
        """
        #: Execute any general "first" functions
        rv = self.__execute_first(request)
        if rv is not None:
            return rv

    def process_request(self, request):
        """Gets the requested path from the headers and
        matches it to a route, function, group and method stored in
        self.routes. The view funtion itself then gets executed to generate
        the response-data.

        If the requested path is not found in self.routes or the
        request method used is not supported by the view we return
        an error Response object.

        We also execute any "first" and "last" functions.
        """
        path = request.headers['PATH_INFO']
        method = request.headers['REQUEST_METHOD']

        #: Match to a route
        route_match = self.get_route_match(path)

        if route_match:
            kwargs, methods, group, view_function = route_match

            #: Execute any first functions for route group
            first_group_rv = self.__execute_first_groups(request, group)
            if first_group_rv is not None:
                return first_group_rv
            
            if method not in methods:
                raise MethodNotAllowed()
            else:
                rv = view_function(request, **kwargs)

            #: Execute any last functions for a route group. If we don't want
            #: functions without a group to be executed on top of the ones with
            #: a group, we should build and return the response here.
            last_group_rv = self.__execute_last_groups(rv, group)      
            if last_group_rv is not None:
                return last_group_rv
            
        else:
            raise NotFound()
            
        return rv

    def postprocess_request(self, rv, make_response):
        """The last step of the request to response cycle.
        Here we execute any general @app.last functions and
        return a valid response object.
        """
        response = self.__build_response(rv, make_response)
        
        try:
            last_rv = self.__execute_last(response)
        except Exception as e:
            last_rv = self.handle_exception(e, make_response)

        if last_rv is not None:
            return last_rv

        return response
    
    def handle_exception(self, e, make_response):
        """Builds the appropriate response object
        based on what exception was raised.
        
        If debug is true we don't handle the exception
        but just re-raise it again.
        """
        if self.config.get('DEBUG', None):
            raise e

        if isinstance(e, (NotFound, MethodNotAllowed)):
            rv = self.__error_return(make_response, e.respcode)
        elif isinstance(e, Exception):
            rv = self.__error_return(make_response, 500)
        
        return rv

    def __build_response(self, data, make_response, code=200):
        """Generaes the final response object.

        If the view function returns a Response object (The Response
        object was created in the view) we attach the make_response
        to it. If the view function return is standard data (and headers)
        we create the Response object here.
        """
        if isinstance(data, Response):
            response = data
            response.make_response = make_response # Attach the WSGI make_response object
        else:
            response = Response(make_response, code, data=data)
        
        return response

    def __execute_first_groups(self, request, group):
        """Execute only the first functions attached to a group."""
        if group is not None:
            rv = self.__execute_first(request, group)
            return rv

    def __execute_last_groups(self, response, group):
        """Execute only the last functions attached to a group-"""
        if group is not None:
            rv = self.__execute_last(response, group)
            return rv

    def __execute_first(self, request, group=None):
        """Runs through and executes any functions
        in the self.first_funcs dictionary.
        """
        funcs = self.first_funcs.get(group, ())
        for func in funcs:
            rv = func(request)
            if rv is not None: 
                return rv

    def __execute_last(self, response, group=None):
        """Runs throug and executes any functions
        in the self.last_funcs dictionary.
        """
        if not isinstance(response, Response):
            response = Response(data=response)

        funcs = self.last_funcs.get(group, ())
        for func in funcs:
            rv = func(response)
            if rv is not None:
                return rv

    def __error_return(self, make_response, code=404):
        """Checks if an error handler was defined by the
        user and in that case returns that as the response.
        If no handler was defined we return an empty response.
        """
        errorhandler = self.errorhandlers.get(code, None)

        if callable(errorhandler):
            rv = errorhandler()
        else:
            rv = None
        
        if rv is not None:
            response = self.__build_response(rv, make_response, code=code)
        else:
            response = Response(make_response, code)
        return response
        
    def __call__(self, environ, make_response):
        """Gets executed every time an instance of the class
        gets called. 
        
        Calls dispatch_request with the standard WSGI objects
        environ and make_request to get back a response.

        It then calls render() on the response to render it 
        back to the server.
        """
        resp = self.dispatch_request(environ, make_response)
        return resp.render()

    def __repr__(self):
        return '%s()' % self.__class__.__name__
