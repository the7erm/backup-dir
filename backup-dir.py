#!/usr/bin/env python2

"""
The MIT License (MIT)

Copyright (c) 2015 Eugene Miller theerm@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import datetime
import shutil
import os
import sys
import subprocess
import glob
import pprint
import re
from time import time, timezone, daylight, altzone
import pytz

ppr = pprint.PrettyPrinter(indent=4)

def pp(arg):
    ppr.pprint(arg)

try:
    SRC_DIR = os.path.realpath(os.path.expanduser(sys.argv[1]))
    BACKUP_DIR = os.path.realpath(os.path.expanduser(sys.argv[2]))
except:
    print """Usage backup-dir.py <src_dir> <backup_dir>"""
    sys.exit()


# all.weekly.12.sql.tar.gz
DIR_TEMPLATE = "{src_basename}/{src_basename}.{label}.{backup_num}"

leave_dump_dir_after_backup = False
remove_astrix_dir = False

def get_time(_time=None):
    local_offset = timezone
    if daylight:
        local_offset = altzone
    if not _time:
        _time = time()
    return _time + local_offset

def get_fullpath(**kwargs):
    src_basename = os.path.basename(SRC_DIR)
    kwargs['src_basename'] = src_basename
    # print "BACKUP_DIR:", BACKUP_DIR
    # print "DIR_TEMPLATE:", DIR_TEMPLATE
    # print "kwargs:", kwargs
    formatted_template = DIR_TEMPLATE.format(**kwargs)
    # print "formatted_template:", formatted_template
    path = os.path.join(BACKUP_DIR, formatted_template)\
           .replace("..",".")
    print "path:", path
    return path

def rename_backups(max_file_number, label):
    for i in range(max_file_number, -1, -1):
        src = get_fullpath(label=label, backup_num="%s" % i)
        dst = get_fullpath(label=label, backup_num="%s" % (i+1))
        if not os.path.exists(src):
            continue

        if os.path.exists(dst):
            print "REMOVE:", dst
            exe(["rm", "-fR", dst])
            
        shutil.move(src, dst)
        print "RENAME: %s => %s" % (src, dst)

def sort_nicely( l ): 
  """ Sort the given list in the way that humans expect. 
  """ 
  convert = lambda text: int(text) if text.isdigit() else text 
  alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
  l.sort( key=alphanum_key ) 

def get_link_dest(path, prepend=None, basename=""):
    files = glob.glob(os.path.join(path, "*"))
    sort_nicely(files)
    pp(files)
    if prepend is not None:
        files.insert(0, os.path.join(prepend, basename))

    links = []
    for i, f in enumerate(files):
        new_path = os.path.join(f, basename)
        if os.path.exists(new_path):
            links.append("--link-dest=%s" % new_path)
    
    links = list(set(links[0:19]))
    sort_nicely(links)
    return links

def exe(cmd):
    pp(cmd)
    process = subprocess.Popen(cmd)
    process.wait()

def cp_al(src, dst):
    src = src.rstrip("/")
    dst = dst.rstrip("/")
    src += "/"
    backup_root = os.path.dirname(dst)
    link_dest = get_link_dest(backup_root)
    cmd = ["rsync", "-aPH", "--one-file-system"] + link_dest + [src] + [dst]
    print "*"*10
    print "cmd:", cmd
    print " ".join(cmd)
    exe(cmd)
    fp = open(os.path.join(dst,"backup-time"), 'w')
    fp.write("%s" % datetime.datetime.now())
    fp.close()

def backup(label, based_on, max_file_number):
    print "--- now ---"
    now = datetime.datetime.fromtimestamp(get_time())
    print "now:", now, based_on
    now = now.strftime(based_on)
    print "now:", now, based_on
    zero_file = get_fullpath(label=label, backup_num="0")
    print "zero_file:", zero_file

    if os.path.exists(zero_file):
         mtime = os.stat(zero_file).st_mtime
         mtime = get_time(mtime)
         zero_file_mtime = datetime.datetime.fromtimestamp(mtime)
         zero_file_mtime = zero_file_mtime.replace()
         print "zero_file_mtime now:", zero_file_mtime
         zf_now = zero_file_mtime.strftime(based_on)
         print "zf_now:", zf_now, based_on
         if zf_now == now:
            print "RETURN zf_now == now"
            return

    rename_backups(max_file_number, label)

    src = CURRENT_BACKUP
    dst = get_fullpath(label=label, backup_num="0")

    print "backup: %s => %s" % (src, dst)
    cp_al(src, dst)
    fp = open(os.path.join(dst, "backup-time"), 'w')
    fp.write("%s" % datetime.datetime.now())
    fp.close()

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR, 0775)
os.chdir(BACKUP_DIR)

rename_backups(23, "")

CURRENT_BACKUP = get_fullpath(label="", backup_num="0")
print "CURRENT_BACKUP:", CURRENT_BACKUP
if not os.path.exists(CURRENT_BACKUP):
    os.makedirs(CURRENT_BACKUP, 0775)

print "SRC_DIR:", SRC_DIR
cp_al(SRC_DIR, CURRENT_BACKUP)

# %H    Hour (24-hour clock) as a decimal number [00,23].
# %j    Day of the year as a decimal number [001,366].
# %W    Week number of the year (Monday as the first day of the week) as a 
#       decimal number [00,53]. All days in a new year preceding the first 
#       Monday are considered to be in week 0.
# %m    Month as a decimal number [01,12].
# %Y    Year with century as a decimal number.

backup("hourly", "%Y%j%H", 23)
backup("daily", "%Y%j", 7)
backup("weekly", "%Y%W", 6)
backup("monthly", "%Y%m", 12)
backup("yearly", "%Y", 5)

