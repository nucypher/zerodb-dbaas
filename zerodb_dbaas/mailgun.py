import requests
from threading import Thread


def send(request, **kw):
    """
    Standard keywords are from, to, subject, text, html
    """
    api_key = request.registry.settings['mailgun.key']
    api_url = request.registry.settings['mailgun.url']

    return requests.post(
            api_url + '/messages',
            auth=('api', api_key),
            data=kw)


def send_async(request, **kw):
    thread = Thread(target=send, args=(request,), kwargs=kw)
    thread.start()
