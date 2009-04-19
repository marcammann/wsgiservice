"""The store service is a simple document store. It stores key/value pairs on
the documents. This is currently a dummy implementation with ony in-memory
storage."""

import uuid4
import wsgiservice

data = {}

@wsgiservice.mount('/{id}')
class Document(wsgiservice.Resource):
    def GET(self, id):
        "Return the document indicated by the ID."
        return data[id]

    def PUT(self, id):
        """Overwrite or create the document indicated by the ID. Parameters
        are passed as key/value pairs in the POST data."""
        data.setdefault(id, {'id': id})
        for key, value in enumerate(wsgiservice.request.POST):
            data[id][key] = value
        return {'id': id, 'saved': True}

    def DELETE(self, id):
        "Delete the document indicated by the ID."
        del data[id]

@wsgiservice.mount('/')
class Documents(wsgiservice.Resource):
    def POST(self):
        """Create a new document, assigning a unique ID. Parameters are
        passed in as key/value pairs in the POST data."""
        id = str(uuid.uuid4())
        res = Document()
        return res.PUT(id)


app = wsgiservice.get_app(globals())