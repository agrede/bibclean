#!/usr/bin/env python

from unidecode import unidecode
from pyzotero import zotero
import re
from datetime import datetime
from dateutil import parser as dup
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("library_id", help="Zotero API user ID", type=str)
parser.add_argument("api_key", help="Zotero API user key", type=str)
args = parser.parse_args()

zot = zotero.Zotero(args.library_id, 'user', args.api_key)

itms = zot.everything(zot.top())

auths = {}
itm_key = {}
itm_auths = {}
odd_names = []
odd_fnames_idx = {}
odd_dates_idx = {}

reOLN = re.compile(r'[^a-zA-Z]')
reOFN = re.compile(r'(^[a-z])|([^a-zA-Z -\.])')
reODT = re.compile(r'^\d{4}(?:-\d{2}){0,2}$')
reFDY = re.compile(r'\b(\d{1,2})\b')
for idx, itm in enumerate(itms):
    key = itm['key']
    itm_key[key] = idx
    if 'date' in itm:
        if not reODT.search(itm['date']) and itm['date'] != '':
            dts = itm['date']
            dto = dup.parse(dts)
            dys = [int(d) for d in reFDY.findall(dts)]
            odd_dates_idx[key] = (dto, dts, dys)
    if 'creators' in itm:
        itm_auths[itm['key']] = []
        for crtr in itm['creators']:
            if 'firstName' in crtr and 'lastName' in crtr:
                name_last = unidecode(crtr['lastName'])
                name_first = unidecode(crtr['firstName'])
                if not name_last in auths:
                    auths[name_last] = {}
                    if reOLN.search(name_last):
                        odd_names.append(name_last)
                if not name_first in auths[name_last]:
                    auths[name_last][name_first] = []
                if reOFN.search(name_first):
                    if not name_first in odd_fnames_idx:
                        odd_fnames_idx[name_first] = set()
                    odd_fnames_idx[name_first].add(key)
                auths[name_last][name_first].append(key)
                itm_auths[key].append((name_last, name_first))
odd_names.sort()
odd_fnames = list(odd_fnames_idx.keys())
odd_fnames.sort()

auth_counts = {}
for lastn, tmp in auths.items():
    auth_counts[lastn] = len(tmp)
auth_order = sorted(auth_counts, key=auth_counts.get, reverse=True)


def print_items(kys):
    for itm in kys:
        idx = itm_key[itm]
        print(itms[idx]['date'],
              itms[idx]['publicationTitle'],
              itms[idx]['title'])


def has_initials(name, initials):
    name_inits = re.findall('([A-Z])', name)
    for init in name_inits:
        if init in initials:
            return True
    return False


match_name = re.compile('\(?(([A-Z])[a-zA-Z]*)\)?')
name_inits = re.compile('([A-Z])')
for nm in odd_names:
    ms = match_name.findall(nm)
    ofi = []
    for ofnm in list(auths[nm].keys()):
        ofi += name_inits.findall(ofnm)
    for idm, m in enumerate(ms):
        if m[0] in auths:
            oms = [seq[1] for seq in (ms[:idm] + ms[(idm+1):])] + ofi
            for fnm in list(auths[m[0]].keys()):
                if has_initials(fnm, oms):
                    print(nm, '; ', ', '.join(list(auths[nm].keys())),
                          ': ', m[0], ', ', fnm, sep='')


def name_comp_score(name1, name2):
    score = 0.0
    if name1[0] != name2[0]:
        return 0
    brkname = re.compile(r'(([A-Z])[a-z]*)')
    fna1 = brkname.findall(name1[1])
    fna2 = brkname.findall(name2[1])
    if len(fna2) < len(fna1):
        tmp = fna1
        fna1 = fna2
        fna2 = tmp

    for idx, fnm in enumerate(fna1):
        if fnm[0] == fna2[idx][0]:
            score += 1/(idx+1)
        elif fnm[1] == fna2[idx][1]:
            score += 0.5/(idx+1)
    return score


def name_list_scores(names):
    name_scores = []
    for i in range(0, len(names)-2):
        score = name_comp_score(names[i], names[i+1])
        if score > 0:
            name_scores.append((score, names[i], names[i+1]))
    return name_scores


def name_occrs(names):
    if len(names) < 1:
        return []
    tstname = names[0]
    count = 1
    i = 1
    res = []
    while (i < len(names)):
        score = name_comp_score(tstname, names[i])
        if score < 0.5:
            res.append((count, tstname))
            tstname = names[i]
            count = 0
        elif len(tstname[1]) < len(names[i][1]):
            tstname = names[i]
        count += 1
        i += 1
    res.append((count, tstname))
    return res


def name_list_comp(names1, names2):
    comp_list = []
    nmslst = {}
    for nm1 in names1:
        if not nm1[1][0] in nmslst:
            nmslst[nm1[1][0]] = []
        nmslst[nm1[1][0]].append(nm1)
    for nm2 in names2:
        if nm2[1][0] in nmslst:
            for nm1 in nmslst[nm2[1][0]]:
                score = name_comp_score(nm1[1], nm2[1])
                if score >= 0.25:
                    cmbscore = score*(nm1[0]+nm2[0])
                    comp_list.append((cmbscore, score, nm1, nm2))
    return comp_list


def list_coauths(keys, ign_list):
    coauths = []
    for key in keys:
        coauths += [itm for itm in itm_auths[key] if itm not in ign_list]
    coauths.sort()
    return coauths


def comp_fnames(lname, fname1, fname2):
    ca1 = name_occrs(list_coauths(auths[lname][fname1], [(lname, fname1)]))
    ca2 = name_occrs(list_coauths(auths[lname][fname2], [(lname, fname2)]))
    return name_list_comp(ca1, ca2)


def fix_dates():
    for key, val in odd_dates_idx.items():
        if val[0].day != val[0].month and val[0].day in val[2]:
            itms[itm_key[key]]['date'] = val[0].strftime('%Y-%m-%d')
            if zot.check_items([itms[itm_key[key]]]):
                itms[itm_key[key]] = zot.update_item(itms[itm_key[key]])
                print(itms[itm_key[key]]['key'], key,
                      itms[itm_key[key]]['date'], val[0].strftime('%Y-%m-%d'))


prox = 'http://ezproxy.rit.edu/login?url=$@'


def fix_proxy(proxy):
    prox_brk = re.search(r'^(?:https?://)([^/\?]+)(.*)\$\@$', prox)
    if prox_brk:
        rePRB = re.compile(r'^(https?://)?(?:(.+)\.|)' +
                           re.escape(prox_brk.group(1)) +
                           r'(?:' +
                           re.escape(prox_brk.group(2)) +
                           r'https?://)?(.*)$')
        rePRD = re.compile(re.escape(prox_brk.group(1)))
        for idx, itm in enumerate(itms):
            url = itm['url']
            key = itm['key']
            if rePRD.search(url):
                nurl = ''.join([m
                                for m in rePRB.search(url).groups()
                                if m is not None])
                itms[idx]['url'] = nurl
                if zot.check_items([itms[idx]]):
                    itms[idx] = zot.update_item(itms[idx])


def brk_name(name):
    parts = []
    for nm in re.findall(r'\b(([a-z])[a-z]*)\b|(([A-Z])[a-z]*)', name):
        if nm[0] == '':
            parts.append(nm[2:])
        else:
            parts.append(nm[:2])
    return parts


def name_rpts(parts):
    inits = ''.join([p[1].capitalize() for p in parts])
    norep_inits = re.search(r'^(.*?)\1*$', inits).group(1)
    if norep_inits != inits:
        nms = grp_names([p[0].capitalize() for p in parts], len(norep_inits))
        new_full = [beg_str_equal(nm) for nm in nms]
        if None not in new_full:
            brkname = re.compile(r'(([A-Z])[a-z]*)')
            parts = []
            for nm in new_full:
                parts += brkname.findall(nm)
    return parts


def beg_str_equal(strs):
    strs.sort(key=len, reverse=True)
    for k in range(1, len(strs)):
        if strs[k-1][:len(strs[k])] != strs[k]:
            return None
    return strs[0]


def grp_names(names, n):
    rtn = []
    for k in range(0, n):
        rtn.append([names[i] for i in range(k, len(names), n)])
    return rtn


def fnd_rep(names, thresh):
    rtn = []
    for idx, name in enumerate(names):
        parts = brk_name(name)
        if len(parts) >= thresh:
            rmr_parts = name_rpts(parts)
            if len(parts) != len(rmr_parts) and len(rmr_parts) >= thresh:
                rtn.append((idx, name, parts, rmr_parts))
    return rtn


try:
    zot = zotero.Zotero('', 'user', '')
except:
    print('Could not connect')


class Person(object):
    """
    Author Info
    """
    def __init__(self, name_first, name_last):
        self._name = [name_last, name_first]
        self._ascii_name = [re.sub(r'`', '\'', unidecode(n))
                            for n in self._name]

    def name(self, idx, uni):
        if uni:
            return self._name[idx]
        else:
            return self._ascii_name[idx]

    def name_last(self, *args, **kwargs):
        uni = kwargs.get('uni', False)
        return self.name(0, uni)

    def name_first(self, *args, **kwargs):
        uni = kwargs.get('uni', True)
        return self.name(1, uni)

    def update(self):
        pass

ppl = []
for x in itms[239]['creators']:
    if 'firstName' in x and 'lastName' in x:
        ppl.append(Person(x['firstName'], x['lastName']))

for idi, itm in enumerate(ref.items):
    if itm is None:
        print('Item:', str(idi))
    else:
        for idc, con in enumerate(itm.contributors):
            if con is None:
                print('Item', str(idi), 'Con:', str(idc))

for ln, fns in ref.people.items():
    if fns is None:
        print('No FNS:', ln)
    else:
        for fn, per in fns.items():
            if per is None:
                print('No Person:', ln, fn)
            else:
                for idx, con in enumerate(per.contributions):
                    if con is None:
                        print('No Contrib:', ln, fn, '; id:', idx)


def myapp(function, arg):
    return function(arg)

def addtwo(value):
    return value+2


class myparser(dateutil.parser.parser):
    def myparse(self, timestr, default=None,
                ignoretz=False, tzinfos=None,
                **kwargs):
        if not default:
            default = datetime.datetime.now().replace(hour=0, minute=0,
                                                      second=0, microsecond=0)

        return self._parse(timestr, **kwargs)


b = [mwe.Box(x) for x in ['A', 'B', 'C']]
o = [mwe.Owner(x) for x in ['Bob', 'John', 'Steve']]
ic = [[1, 2, 0], [2, 1, 0], [1, 1, 1]]

for idb, bi in enumerate(b):
    for ido, oi in enumerate(o):
        for c in range(0, ic[idb][ido]):
            bi.add_item(oi, ''.join([oi.name, bi.name, str(c+1)]))


y = {'A', 'B', 'C'}
yc = y.copy()


def ln_change_scores():
    lnsc = {}
    for ln, fns in ref.people.items():
        lnsc[ln] = 0
        comp = max(fns.items(), key=lambda x: len(x[1].contributions))[1]
        for fn, p in fns.items():
            if p is not comp:
                lnsc[ln] += comp.compare(p)*len(p.contributions)
        lnsc[ln] = lnsc[ln]*len(comp.contributions)
    return sorted(lnsc.items(), key=lambda x: x[1], reverse=True)


sfn = ''
ln = ''
def change_all(ln, sfn):
    sp = ref.people[ln][sfn]
    ps = list(ref.people[ln].values())
    for p in ps:
        if sp != p:
            tmp = p.contributions.copy()
            for c in tmp:
                c.person = sp
def parse:
    pass


def name_date_range():
    ndr = {}
    for ln, fns in ref.people.items():
        for p in fns.values():
            try:
                if ln in ndr:
                    ndr[ln][0] = min(list(p.contributions) + [ndr[ln][0]],
                                     key=lambda x: parse(x.item.date))
                    ndr[ln][1] = max(list(p.contributions) + [ndr[ln][1]],
                                     key=lambda x: parse(x.item.date))
                else:
                    ndr[ln] = [
                        min(list(p.contributions),
                            key=lambda x: parse(x.item.date)),
                        max(list(p.contributions),
                            key=lambda x: parse(x.item.date))]
            except:
                continue
    return ndr
