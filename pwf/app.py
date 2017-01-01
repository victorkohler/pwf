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
        """Gets the requested path from the headers and
        matches it to a route, function and method stored in self.routes.
        The view funtion itself then gets executed to generate the
        response-data.

        If the requested path is not found in self.routes or the
        request method used is not supported by the view we return
        an error Response object.

        We also execute any "before" and "after" functions.
        """

        # Execute any general "before" functions
        rv = self.__execute_before(request)
        if rv:
            response = self.__build_response(rv, make_response)
            return response
       
        # Match to a route
        path = request.headers['PATH_INFO']
        method = request.headers['REQUEST_METHOD']
        route_match = self.get_route_match(path)

        if route_match:
            kwargs, methods, group, view_function = route_match
            
            #Execute any before functions for route group
            before_rv = self.__execute_groups(request, group)

            if before_rv:
                response = self.__build_response(before_rv, make_response)
                return response

            if method not in methods:
                response = Response(make_response, 405)
            else:
                data = view_function(request, **kwargs)
                response = self.__build_response(data, make_response)
            
            # Execute any after functions for route group.
            # If we don't want functions without a group to be executed
            # on top of the group one we should just return the 'after_rv'
            # here.
            after_rv = self.__execute_after(response, group)
            if after_rv is not None:
                response = after_rv

        else:
            response = Response(make_response, 404)
        
        # Execute general 'after' functions
        after_rv = self.__execute_after(response)
        if after_rv is not None:
            return after_rv

        return response

    def dispatch_request(self, environ, make_response):
        """Instantiate a new Request object based on environ,
        pass it to the path dispatcher to get the response instance.
        """
        request = Request(environ)
        response = self.path_dispatch(request, make_response)
        return response

    def __build_response(self, data, make_response):
        """Generaes the final response object.

        If the view function returns a Response object (The Response
        object was created in the view) we attach the make_response
        to it. If the view function return is standard data (and headers)
        we create the Response object here.
        """
        if isinstance(data, Response):
            response = data
            # Attach the WSGI make_response object
            response.make_response = make_response
        else:
            response = Response(make_response, data=data)
        
        return response

    def __execute_groups(self, request, group):
        if group is not None:
            rv = self.__execute_before(request, group)
            return rv

    def __execute_before(self, request, group=None):
        """Runs through and executes any functions
        in the self.first_funcs dictionary.
        """
        funcs = self.first_funcs.get(group, ())
        for func in funcs:
            rv = func(request)
            if rv is not None: 
                return rv

    def __execute_after(self, response, group=None):
        funcs = self.last_funcs.get(group, ())
        for func in funcs:
            rv = func(response)
            if rv is not None:
                return rv
        
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
        
        @app.before()
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

        @app.after()
        def add_header(response):
            response.headers['Content-Type'] = 'application/json'
            return response
        """
        def wrapper(f):
            self.last_funcs.setdefault(group, []).append(f)
            return f
        return wrapper


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



