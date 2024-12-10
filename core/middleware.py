# core/middleware.py

from threading import local


_thread_locals = local()


def get_current_request():
    """
    Returns the request object stored in thread local storage.
    """
    request = getattr(_thread_locals, 'request', None)
    if not request:
        print("ThreadLocals did not capture the request.")
    return getattr(_thread_locals, 'request', None)

class ThreadLocals:
    """
    Middleware that stores the request object in thread local storage.
    This can be used to access the current request from anywhere in your code.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response
