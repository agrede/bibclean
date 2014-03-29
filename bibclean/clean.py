import regex
import references
import json
import urllib.request
import exceptions as bexc
from warnings import warn


def remove_ezproxies(items, *args, **kwargs):
    proxy_list_url = kwargs.get('proxy_list_url', None)
    proxy_list = kwargs.get('proxy_list', {})
    proxy_names = kwargs.get('proxy_name', None)
    proxy = kwargs.get('proxy', None)
    if proxy is not None:
        return remove_ezproxy(items, proxy)
    if proxy_list is None or len(proxy_list) < 1:
        proxy_list = {}
        try:
            proxy_list = get_proxy_list(proxy_list_url)
        except:
            raise
    if proxy_names is None:
        proxy_names = list(proxy_list.keys())
    for pn in proxy_names:
        if pn in proxy_list:
            remove_ezproxy(items, proxy_list[pn])
        else:
            warn('Proxy \'%s\' not found' % pn, bexc.ProxyNameNotFound)


def get_proxy_list(
        proxy_list_url='http://ezproxy-db.appspot.com/proxies.json'):
    proxy_list = {}
    try:
        rqst = urllib.request.urlopen(proxy_list_url)
        data = json.loads(rqst.read().decode())
    except Exception as exc:
        raise bexc.RemoteProxyListError(
            'Could not connect to: %s' %
            str(proxy_list_url)).with_traceback(
            exc.__traceback__)
    else:
        try:
            for p in data:
                proxy_list[p['name']] = p['url']
        except Exception as exc:
            raise bexc.RemoteProxyListFormatError(
                'Improper proxy list format').with_traceback(exc.__traceback__)


def remove_ezproxy(items, proxy):
    prox_brk = regex.search(r'^(?:https?://)([^/\?]+)(.*)\$\@$', proxy)
    if prox_brk:
        rePRB = regex.compile(
            r'^(https?://)?(?:(.+)\.|)' +
            regex.escape(prox_brk.group(1)) +
            r'(?:' +
            regex.escape(prox_brk.group(2)) +
            r'https?://)?(.*)$')
        rePRD = regex.compile(regex.escape(prox_brk.group(1)))
        for item in items:
            if rePRD.search(item.url):
                item.url = ''.join([m
                                    for m in rePRB.search(item.url).groups()
                                    if m is not None])
    else:
        raise bexc.ProxyFormatError('Wrong format for proxy: %s' % proxy)


def dates_to_fix(items):
    return [item for item in items
            if item.date is not None or item.date is not item.formated_date()]


def fix_dates(items, datestrs=None):
    """
    Sets items[idx].date to items[idx].formatted_date() or op. datestrs[idx]

    Optional param datestrs:
       Must be same length as items
       datestrs[idx] = None uses items[idx].formatted_date() for that idx
    """
    if datestrs is not None and len(datestrs) is not len(items):
        return None

    for idx, item in enumerate(items):
        if datestrs is None or datestrs[idx] is None:
            item.date = item.formatted_date()
        else:
            item.date = datestrs[idx]
