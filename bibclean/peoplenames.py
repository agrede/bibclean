from unidecode import unidecode
import regex


reBRK = regex.compile(r"\b((\p{Ll})\p{Ll}*)\b|" +
                      r"\b((Ó)\s?\p{Lu}\p{Ll}*)|" +
                      r"((\p{Lu})('\p{Lu})?\p{Ll}*)")


def break_name(name):
    """Breaks name tuple arrays with tuples of the form ('Name', 'N')."""
    parts = [[], []]
    for idx, nm in enumerate(name):
        for p in reBRK.findall(nm):
            if p[0] != '':
                parts[idx].append(p[:2])
            elif p[2] != '':
                parts[idx].append((p[2], p[3]))
            else:
                parts[idx].append((p[4], p[5]))
    return parts


def part_comp(parts, comp):
    """Uses parts with nested arrays or tuples to return parts[:][comp]."""
    return [p[comp] for p in parts]


def inv_idx(idxs, N):
    """ Returns list of numbers in range(0, N) that are not in list idxs."""
    return [idx for idx in range(0, N) if idx not in idxs]


def name_comp(a, b):
    """
    Calculate comparison score between two Unicode name tuples.

    a and b have the form (last, first) and must have a full part of the last
    name in common: e.g. ('Smith Doe', 'John') and ('Doe', 'John') will return
    a non-zero result, but ('Smith D.', 'John') and ('Doe', 'John') will
    return 0.

    Unicode and ASCII equivalents are compared, Unicode matches score higher.
    """
    # Break names into parts --------------------------------------------------
    # Name a
    ap = break_name(a)           # Unicode parts
    aa = name_to_ascii(a)        # ASCII name
    aap = break_name(aa)         # ASCII parts
    lnap = part_comp(aap[0], 0)  # Full ASCII last name parts
    # Name b
    bp = break_name(b)
    ba = name_to_ascii(b)
    bap = break_name(ba)
    lnbp = part_comp(bap[0], 0)
    # Score Last Name ---------------------------------------------------------
    # Get array of tuples [(ai,bi)] where lnap[ai] == lnbp[bi]
    lnm = [(idx, lnbp.index(n)) for idx, n in enumerate(lnap) if n in lnbp]
    if not lnm:  # No matches for last name
        return 0
    score = 0.0
    if a[0] == b[0]:                               # Last name Uni full match
        score += 2
    elif aa[0] == ba[0]:                           # Last name ASCII full match
        score += 1.75
    elif len(lnm) == max([len(lnap), len(lnbp)]):  # Out of order ASCII match
        for idx in lnm:
            if ap[0][idx[0]][0] == bp[0][idx[1]][0]:
                score += 0.75
            else:
                score += 0.5
    else:  # Partial match, add non-matching parts to first name parts
        for idx in lnm:
            if ap[0][idx[0]][0] == bp[0][idx[1]][0]:
                score += 0.75
            else:
                score += 0.5
        aiidx = inv_idx(part_comp(lnm, 0), len(ap[0]))
        biidx = inv_idx(part_comp(lnm, 1), len(bp[0]))
        ap[1] += [ap[0][idx] for idx in aiidx]
        aap[1] += [aap[0][idx] for idx in aiidx]
        bp[1] += [bp[0][idx] for idx in biidx]
        bap[1] += [bap[0][idx] for idx in biidx]
    # Insure that more first name parts are in  a than b
    if len(ap[1]) < len(bp[1]):
        tmp = ap
        ap = bp
        bp = tmp
        tmp = aap
        aap = bap
        bap = aap
    # Build arrays needed for scoring first names
    # Arrays for a
    afns = part_comp(ap[1], 0)    # Full Uni first name parts
    ains = part_comp(ap[1], 1)    # First name Uni initials
    aafns = part_comp(aap[1], 0)  # Full ASCII fist name parts
    aains = part_comp(aap[1], 1)  # First name ASCII initials
    # Arrays for b
    bfns = part_comp(bp[1], 0)
    bins = part_comp(bp[1], 1)
    bafns = part_comp(bap[1], 0)
    bains = part_comp(bap[1], 1)
    # Score First Name --------------------------------------------------------
    for idx in range(0, len(afns)):
        if afns[idx] in bfns:      # Full Uni
            tidx = bfns.index(afns[idx])
            score += 2/(idx+tidx+2)
        elif aafns[idx] in bafns:  # Full ASCII
            tidx = bafns.index(aafns[idx])
            score += 1.75/(idx+tidx+2)
        elif ains[idx] in bins:    # Uni Initials
            tidx = bins.index(ains[idx])
            score += 1/(idx+tidx+2)
        elif aains[idx] in bains:  # ASCII Initials
            tidx = bains.index(aains[idx])
            score += 1/(idx+tidx+2)
    return score


reRepeatBlock = regex.compile(r'^(.*?)\1*$')


def name_repeat_block_length(parts):
    """
    Gets the length of the repeating sequence of names

    e.g. 'S.R.A. Stephen Robert Andrew' has the repetition 'SRASRA' -> 3
    """
    initials = ''.join([p[1].capitalize() for p in parts])
    initials_repeat_block = reRepeatBlock.search(initials).group(1)
    if initials_repeat_block != initials:
        li = len(initials)
        lirb = len(initials_repeat_block)
        for fidx in range(0, lirb):
            if len(set(
                    [p[0] for p in parts[fidx:li:lirb] if p[0] != p[1]])) > 1:
                return li
        return lirb
    return len(initials)


def name_redundancy(parts):
    """True if name appears to have redundancies"""
    return len(parts) != name_repeat_block_length(parts)


def remove_redundancies(parts):
    """
    Removes redundancies in name parts

    e.g. 'Robert James R.J.' -> 'Robert James'
    """
    final_parts = []
    nrbl = name_repeat_block_length(parts)
    pl = len(parts)
    if pl == nrbl:
        return parts
    for fidx in range(0, nrbl):
        final_parts.append(max(parts[fidx:pl:nrbl], key=lambda x: len(x[0])))
    return final_parts


def name_part_in_parts(part, parts):
    """Returns index of name parts location in parts or None"""
    if part[0] in part_comp(parts, 0):
        return part_comp(parts, 0).index(part[0])
    elif name_to_ascii(part[0]) in name_to_ascii(part_comp(parts, 0)):
        return name_to_ascii(part_comp(parts, 0)).index(name_to_ascii(part[0]))
    elif part[1] in part_comp(parts, 1):
        return part_comp(parts, 1).index(part[1])
    elif name_to_ascii(part[1])[0] in part_comp(
            name_to_ascii(part_comp(parts, 1)), 0):
        return name_to_ascii(
            part_comp(parts, 1)).index(name_to_ascii(part[1])[0])
    else:
        return None


def fullest_name(a, b):
    """Using two equivalent names, tries to return full name"""
    name = ['', '']
    ap = break_name(a)
    bp = break_name(b)
    ap[1] = remove_redundancies(ap[1])
    bp[1] = remove_redundancies(bp[1])
    if len(ap[0]) < len(bp[0]):
        tmp = ap[0]
        ap[0] = bp[0]
        bp[0] = tmp
    if len(ap[1]) < len(bp[1]):
        tmp = ap[1]
        ap[1] = bp[1]
        bp[1] = tmp
    for idx in range(0, 2):
        nps = []
        anps = ap[idx]
        bnps = bp[idx]
        for anp in anps:
            bidx = name_part_in_parts(anp, bnps)
            if bidx is not None:
                nps.append(get_unicode_name(anp, bnps[bidx]))
            else:
                nps.append(anp)
            if nps[-1][0] == nps[-1][1]:
                nps[-1] = (''.join([nps[-1][0], '.']), nps[-1][1])
        name[idx] = ' '.join(part_comp(nps, 0))
    return tuple(name)


def get_unicode_name(a, b):
    """Of two seemingly equal name parts, returns the best one"""
    if (a == b):
        return a
    a_ascii = a == name_to_ascii(a)
    b_ascii = b == name_to_ascii(b)
    a_init = a[0] == a[1]
    b_init = b[0] == b[1]
    if a_init and b_init:
        if not b_ascii:
            return b
        else:
            return a
    elif a_init or b_init:
        if not b_init:
            return b
        else:
            return a
    elif a_ascii:
        return b
    else:
        return a


def name_to_ascii(name):
    """
    Changes lists of names to pseudo-ASCII equivilent keeping structure.

    e.g. ('Ó Súilleabháin', 'Jörg Tanjō') -> ("O'Suilleabhain", 'Jorg Tanjo')
    """
    return rec_apply(single_name_to_ascii, name)


def single_name_to_ascii(name):
    """
    Changes names to pseudo-ASCII equivilent.

    e.g. 'Ó Súilleabháin' -> "O'Suilleabhain"
    """
    name = regex.sub(r'\bÓ\s?(\p{Lu})', 'O\'\g<1>', name)
    name = regex.sub(r'`', '\'', unidecode(name))
    return name


def rec_apply(function, item):
    """Recursively apply function to list types keeping structure"""
    itype = type(item)
    if itype is set:
        return set([rec_apply(function, itm) for itm in item])
    elif itype is tuple:
        return tuple([rec_apply(function, itm) for itm in item])
    elif itype is dict:
        ndict = {}
        for key, value in item.items():
            ndict[key] = rec_apply(function, value)
        return ndict
    elif itype is list:
        return [rec_apply(function, itm) for itm in item]
    else:
        return function(item)


def is_name(name):
    try:
        if not (type(name) is tuple or type(name) is list):
            return False
        if len(name) is not 2:
            return False
        for idx in range(0, 2):
            if type(name[idx]) is not str and len(name[idx]) < 1:
                return False
    except:
        return False
    else:
        return True


reSLN = regex.compile(r'^[A-Z](?:\'[A-Z])?[a-z]+$')


def is_odd_last_name(last_name):
    if reSLN.search(last_name):
        return False
    else:
        return True


def odd_last_names(last_names):
    olns = []
    for ln in last_names:
        if is_odd_last_name(ln):
            olns.append(ln)
    return olns


reSFN = regex.compile(r'^[A-Z](?:[a-z]+|\.)?(?:\s?[A-Z](?:[a-z]+|\.)?)?$')


def is_odd_first_name(first_name):
    if reSFN.search(first_name):
        return False
    else:
        return True
