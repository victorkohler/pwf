# -*- coding: utf-8 -*-
"""
@author: Victor Kohler
@since: date 17/12/2016
@version: 0.1
"""

import re
from request import Request
from response import Response
from functools import wraps


class Pwf(object):
    """The Pwf objects handles the interactions between the view functions and
    the WSGI application. It is instanciated once and you then interact with that
    instance to define routes, change configurations and more.

    Example usage to define a view:
    
        app = Pwf()

        app.routes('/')
        def index(request):
                return 'Hello world'


    The above example instantiates the Pwf obhects, defines a route to '/'
    through the app.routes decorater and returns 'Hello World' from the
    view function.
    """
    
    def __init__(self):
        self.routes = []

    def build_route_pattern(self, url):
        route_regex = re.sub(r'(<\w+>)', r'(?P\1.+)', url)
        return re.compile("^{}$".format(route_regex))

    def get_route_match(self, path):
        for route_pattern, methods, view_function in self.routes:
            m = route_pattern.match(path)
            if m:
                return m.groupdict(), methods, view_function
            
        return None

    def route(self, url, methods=['GET']):
        """This function is used as a decorator for each view function
        to define the route/url associated with that view.
        
        Example:
            @app.route('/profile')
            def profile(request):
                return 'This is the profile page'

        It adds the url along with the function itself in the self.routes
        dictionary for the path_dispatcher to user.
        """

        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)
        
            route_pattern = self.build_route_pattern(url) 
            self.routes.append((route_pattern, methods, f))
            return wrapper

        return decorate

    def path_dispatch(self, request, make_response):
        """Gets the requested url path from the headers and
        matches it to a url, function and method stored in self.routes.

        The view funtion itself then gets executed to generate the
        response-data and we build a Response object from it.

        If the requested path is not found in self.routes or the
        request method used in not supported by the view we return
        an error Response object. 
        """

        path = request.headers['PATH_INFO']
        method = request.headers['REQUEST_METHOD']

        route_match = self.get_route_match(path)
        
        if route_match:
            kwargs, methods, view_function = route_match
            if method not in methods:
                response = Response(make_response, 405)
            else:
                data = view_function(request, **kwargs)

                # If the response object is already created,
                # we return it, of not we create it
                if isinstance(data, Response):
                    response = data
                    # Attach the WSGI make_response object
                    response.make_response = make_response
                else:
                    response = Response(make_response, data=data)
        else:
            response = Response(make_response, 404)

        return response

    def dispatch_request(self, environ, make_response):
        """Instantiate a new Request object based on environ,
        pass it to the path dispatcher to get the response instance
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

    def __call__(self, environ, make_response):
        """Gets executed every time an instance of the class
        gets called. 
        
        Calls dispatch_request with the standard WSGI varables
        environ and make_request to get back a response.

        It then calls render() on the response to render it 
        back to the server.
        """

        resp = self.dispatch_request(environ, make_response)
        return resp.render()

    def __repr__(self):
        return '%s()' % self.__class__.__name__



