from pyramid.security import Allow, Everyone


class Root(object):
    __acl__ = [(Allow, Everyone, 'view'),
               (Allow, 'group:customers', 'use')]

    def __init__(self, request):
        pass
