import re
import references
import json
import urllib.request
from dateutil import parser


def frequent_person(people):
    pass


def comp_people(people):
    pass


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
    prox_brk = re.search(r'^(?:https?://)([^/\?]+)(.*)\$\@$', proxy)
    if prox_brk:
        rePRB = re.compile(r'^(https?://)?(?:(.+)\.|)' +
                           re.escape(prox_brk.group(1)) +
                           r'(?:' +
                           re.escape(prox_brk.group(2)) +
                           r'https?://)?(.*)$')
        rePRD = re.compile(re.escape(prox_brk.group(1)))
        for item in items:
            if rePRD.search(item.url):
                item.url = ''.join([m
                                    for m in rePRB.search(item.url).groups()
                                    if m is not None])


def fix_dates(items):
    reODT = re.compile(r'^\d{4}(?:-\d{2}){0,2}$')
    reFDY = re.compile(r'\b(\d{1,2})\b')
    needs_fix = []
    for item in items:
        if not reODT.search(item.date) and item.date != '':
            date_obj = parser.parse(item.date)
            date_days = [int(d) for d in reFDY.findall(item.date)]
            if date_obj.day != date_obj.month and date_obj.day in date_days:
                item.date = date_obj.strftime('%Y-%m-%d')
            else:
                needs_fix.append((item, date_obj, date_days))
