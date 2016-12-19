import json

def application(environ, start_response):
    
    # This is the content of the response
    response_body = json.dumps({
        'success': True
        })

    status = '200 OK'

    response_headers = [
        ('Content-Type', 'application/json'),
        ('Content-Length', str(len(response_body)))
        ]

    # Send the response back to the server
    start_response(status, response_headers)

    return [response_body]








