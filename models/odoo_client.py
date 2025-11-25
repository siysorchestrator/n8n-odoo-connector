import xmlrpc.client

class OdooClient:
    def __init__(self, url, db, username, password):
        self.url = url
        self.db = db
        self.username = username
        self.password = password
        self.common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        self.uid = self.common.authenticate(db, username, password, {})
        self.models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

    # Generic search_read
    def search_read(self, model, domain=None, fields=None, limit=None):
        domain = domain or []
        fields = fields or []
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'search_read',
            [domain],
            {'fields': fields, 'limit': limit}
        )
    
    # Generic read
    def read(self, model, ids, fields=None):
        fields = fields or []
        return self.models.execute_kw(
            self.db, self.uid, self.password,
            model, 'read',
            [ids],   # list of ids
            {'fields': fields}
        )

    # Generic create
    def create(self, model, values):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'create', [values])

    # Generic write
    def write(self, model, ids, values):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'write', [ids, values])

    # Generic unlink
    def unlink(self, model, ids):
        return self.models.execute_kw(self.db, self.uid, self.password, model, 'unlink', [ids])
