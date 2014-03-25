import regex
import references
import json
import urllib.request


def remove_ezproxies(items, *args, **kwargs):
    proxy_list_url = kwargs.get('proxy_list_url',
                                'http://ezproxy-db.appspot.com/proxies.json')
    proxy_list = kwargs.get('proxy_list', None)
    proxy_names = kwargs.get('proxy_name', None)
    proxy = kwargs.get('proxy', None)
    if proxy is not None:
        return remove_ezproxy(items, proxy)
    if proxy_list is None:
        proxy_list = {}
        site = urllib.request.urlopen(proxy_list_url)
        proxies = json.loads(site.read().decode())
        for p in proxies:
            proxy_list[p['name']] = p['url']
    if proxy_names is None:
        proxy_names = list(proxy_list.keys())
    for pn in proxy_names:
        if pn in proxies:
            remove_ezproxy(items, proxy_list[pn])


def remove_ezproxy(items, proxy):
    prox_brk = regex.search(r'^(?:https?://)([^/\?]+)(.*)\$\@$', proxy)
    if prox_brk:
        rePRB = regex.compile(r'^(https?://)?(?:(.+)\.|)' +
                           re.escape(prox_brk.group(1)) +
                           r'(?:' +
                           re.escape(prox_brk.group(2)) +
                           r'https?://)?(.*)$')
        rePRD = regex.compile(re.escape(prox_brk.group(1)))
        for item in items:
            if rePRD.search(item.url):
                item.url = ''.join([m
                                    for m in rePRB.search(item.url).groups()
                                    if m is not None])


def dates_to_fix(items):
    return [item for item in items if item.date is not item.formated_date()]


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
