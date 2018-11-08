#! /usr/bin/python
# encoding:utf-8
import os
import time
import sys


if __name__ == '__main__':
    ora_home = os.environ.get('ORACLE_HOME')
    today = time.strftime("%Y%m%d")
    username = sys.argv[1]
    password = sys.argv[2]
    directory = sys.argv[3]
    schemas = sys.argv[4]
    comment = sys.argv[5]

    dumpfile = 'expdp_' + comment + '_' + today + '.dmp'
    lopgfile = 'expdp_' + comment + '_' + today + '.log'

    bak_command = ora_home + '/bin/expdp '+ username + '/' + password + ' directory=' + directory + ' dumpfile='+ dumpfile + ' logfile=' + lopgfile + ' schemas=' + schemas
    print bak_command
    os.system(bak_command)
