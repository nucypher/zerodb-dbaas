from pyramid.view import view_config

from zerodb_dbaas.models import Counter


@view_config(route_name='count', renderer='zerodb_dbaas:templates/count.pt')
@view_config(route_name='count_json', renderer='json')
def my_view(request):
    db = request.dbsession
    count = 0

    counters = db[Counter].query(name='root')
    for counter in counters:
        counter.inc()
        count = counter.count
        break

    return {'project': 'zerodb-dbaas', 'count': count}
