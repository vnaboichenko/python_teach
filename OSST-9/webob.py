import paste.fileapp
import paste.httpserver
import routes
import webob
import webob.dec
import webob.exc
from kr_8 import libvirt_wrapper

HOST = '0.0.0.0'
PORT = 8080

class ExampleApp(object):
    '''
    A WSGI "application."

    See: http://pythonpaste.org/do-it-yourself-framework.html#writing-a-wsgi-application
    '''

    # Our routes map URIs to methods of this app, and define how to extract args from requests
    # Complaint: in order to make this RESTful, you have to plan routes yourself
    map = routes.Mapper()
    map.connect('index', '/', method='index')
    map.connect('action', '/{name}/{action}', method='action_metod')

    @webob.dec.wsgify
    def __call__(self, req):
        '''
        Glue.  A WSGI app is a callable; thus in order to make this object an application, 
        we define __call__ to make it callable.  We then ask our Mapper to do some routing,
        and dispatch to the appropriate method.  That method must return a webob.Response.
        '''
        results = self.map.routematch(environ=req.environ)
        if not results:
            return webob.exc.HTTPNotFound()
        match, route = results
        link = routes.URLGenerator(self.map, req.environ)
        req.urlvars = ((), match)
        kwargs = match.copy()
        method = kwargs.pop('method')
        req.link = link
        return getattr(self, method)(req, **kwargs)


    def action_metod(sefl, req, name = None, action=None):

        wrapper = libvirt_wrapper(name)

        action_hash = {
        "create": wrapper.create,
        "start": wrapper.start,
        "stop": wrapper.stop,
        "restart": wrapper.restart,
        "delete": wrapper.delete,
        "list": wrapper.list_vm,
        "status": wrapper.status}

        action = action_hash.get(action)
        return webob.Response(
            body='''<html><body>
                  <p>%s</p> 
                </body></html>''' % action()
        )


    def index(self, req):
        '''
        Controller #1: a landing page.
        '''
        wrapper = libvirt_wrapper()
        return webob.Response(
            body='''<html><body>
                  <p>VM list is %s</p> 
                  <p>Action list is create, start, stop, restart, delete, list, status</p> 
                </body></html>''' % wrapper.list_vm()
        )

def main():
    '''
    CLI entry point.
    '''
    paste.httpserver.serve(ExampleApp(), host=HOST, port=PORT)

if __name__ == '__main__':
    main()
