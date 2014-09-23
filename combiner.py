#!/bin/bash
import codecs
import os
import sys
import re

# import pudb; pudb.set_trace()

def refine_str(str):
    return str.encode('utf-8').rstrip(os.linesep)

def get_po_object_array(filename):
    f = codecs.open(filename, "r", "utf-8")
    str_block = []
    str_arr = []
    line_number = 0
    while 1:
        line_number += 1
        line = f.readline()
        str_block.append(refine_str(line))
        if line.find(u'\n') == 0:
            str_block.append('##:' + str(line_number))
            str_arr.append(str_block)
            str_block = []
        if not line:
            break
    f.close()
    po_obj_arr = []
    for block in str_arr:
        po_obj = {
            'path': [],
            'msgid': [],
            'msgstr': [],
            'etc': [],
            'line' : []
        }
        regex = r'(.*)'
        item = 'etc'
        for phrase in block:
            if phrase.find('#: ') == 0:
                regex = r'#: (.*)'
                item = 'path'
            elif phrase.find('msgid ') == 0:
                regex = r'msgid "(.*)"'
                item = 'msgid'
            elif phrase.find('msgstr ') == 0:
                regex = r'msgstr "(.*)"'
                item = 'msgstr'
            elif phrase.find('#, ') == 0:
                regex = r'#, (.*)'
                item = 'etc'
            elif phrase.find('##:') ==0:
                regex = r'##:(.*)'
                item = 'line'
            if len(phrase) != 0:
                s = re.sub(r'"(.*)"', r'\1', re.sub(regex, r'\1', phrase))
                po_obj[item].append(s)
        po_obj_arr.append(po_obj)
    return po_obj_arr

def str_po_obj(po_obj):
    string = '\n'
    if len(po_obj['path']) != 0:
        string += '#: ' + '\n#: '.join(po_obj['path']) + '\n'
    if len(po_obj['etc']) != 0:
        string += '#, ' + '\n#, '.join(po_obj['etc']) + '\n'
    string += 'msgid "' + '"\n"'.join(po_obj['msgid']) + '"\n'
    string += 'msgstr "' + '"\n"'.join(po_obj['msgstr']) + '"\n'
    return string

def ismty_msgstr(po_obj):
    if len(po_obj['msgstr']) == 0:
        return True
    else:
        return ''.join(po_obj['msgstr']) == ''

def join_po_arr_by_msgid(source, traget):
    pass

def equals_id(s, t):
    return ''.join(s['msgid']) == ''.join(t['msgid'])

def equals_str(s, t):
    return ''.join(s['msgstr']) == ''.join(t['msgstr'])

def remove_po(po_arr, po):
    return filter(lambda x: not equals_id(x, po), po_arr)

def combination_po_arr(source, target):
    comb_arr = []
    for s_po in source:
        for t_po in target:
            if equals_id(s_po, t_po):
                comb_arr.append(s_po)
    return comb_arr

def subset_po_arr(source, target):
    comb_arr = combination_po_arr(source, target)
    for c_po in comb_arr:
        source = remove_po(source, c_po)
    return source

def union_po_arr(source, target):
    subset_arr = subset_po_arr(source, target)
    return subset_arr + target

def stat_po_arr(po_arr):
    total_po_count = len(po_arr)
    empty_po_count = 0
    empty_po_obj_arr = []
    for po in po_arr:
        if ismty_msgstr(po):
            empty_po_count += 1
            empty_po_obj_arr.append(po)
    print 'total po count : ' + str(total_po_count)
    print 'empty po count : ' + str(empty_po_count)

def stat_diff_po_arr(source, target):
    duplicate_count = 0
    not_duplicate_count = 0
    sameid_emtymsg = 0
    sameid_semtymsg = 0
    sameid_temtymsg = 0
    sameid_diffmsg = 0
    sameid_samemsg = 0

    for s_po in source:
        # print_po_obj(s_po)
        duplicate = False
        for t_po in target:
            if equals_id(s_po, t_po):
                duplicate = True
                if ismty_msgstr(s_po) and ismty_msgstr(t_po):
                    sameid_emtymsg += 1
                elif ismty_msgstr(s_po) and not ismty_msgstr(t_po):
                    sameid_semtymsg += 1
                elif not ismty_msgstr(s_po) and ismty_msgstr(t_po):
                    sameid_temtymsg += 1
                else:
                    if equals_str(s_po, t_po):
                        sameid_diffmsg += 1
                    else:
                        sameid_samemsg += 1
        if duplicate:
            duplicate_count += 1
        else:
            not_duplicate_count += 1
            # print 'not duplicate'

    print 'not duplicate count : ' + str(not_duplicate_count)
    print 'duplicate count : ' + str(duplicate_count)
    print 'same id, same empty msg count : ' + str(sameid_emtymsg)
    print 'same id, source empty msg count : ' + str(sameid_semtymsg)
    print 'same id, target empty msg count : ' + str(sameid_temtymsg)
    print 'same id, different msg count : ' + str(sameid_diffmsg)
    print 'same id, same msg count : ' + str(sameid_samemsg)

if len(sys.argv) != 4:
    print 'usage : python combiner.py [source_po] [target_po] [new_union_po]'
else:
    try:
        source = get_po_object_array(sys.argv[1])
        target = get_po_object_array(sys.argv[2])
        print "# source po stat : " + sys.argv[1]
        stat_po_arr(source)
        print "\n# target po stat : " + sys.argv[2]
        stat_po_arr(target)
        f = open(sys.argv[3], 'w')
        print "\n# po diff stat"
        stat_diff_po_arr(source, target)
        print "\n# union po stat"
        union = union_po_arr(source, target)
        stat_po_arr(union)

        for po in union:
            f.write(str_po_obj(po))
        f.close()
    except Exception as e:
        print e
