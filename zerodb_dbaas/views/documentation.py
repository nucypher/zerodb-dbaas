from pyramid.view import view_config


@view_config(
        route_name='documentation',
        renderer='zerodb_dbaas:templates/documentation.pt',
        effective_principals=[])
def documentation(request):
    """Documentation page"""
    return {}

