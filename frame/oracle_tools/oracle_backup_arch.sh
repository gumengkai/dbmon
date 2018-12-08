#!/bin/bash
export LC_ALL=C

function usage() {
   echo "usage: oraclearchbak.sh -i [oracle_sid] -d [backup directory] -l [log_file] -p [archive log policy]"
   exit 1
}

while getopts ":i:d:c:l:p:" opt; do
    case $opt in
        i) PRI_SID=$OPTARG;;
        d) BACKUP_DIR=$OPTARG;;
        l) LOG_FILE=$OPTARG;;
        p) ARCH_KEEP_DAYS=$OPTARG;;
        \?) usage
    esac
done
shift $(($OPTIND - 1))

if [ -z $PRI_SID ]; then usage; fi
if [ -z $BACKUP_DIR ]; then usage; fi
if [ -z $ARCH_KEEP_DAYS ]; then usage; fi

if test $(id -u) != $(id oracle -u) ; then
    echo "ERROR: OS NOT oracle account!"
    exit
fi

. $(cat /etc/passwd|grep ^oracle|awk -F ':' '{print $6}')/.bash_profile
export ORACLE_SID=$PRI_SID
export NLS_LANG=AMERICAN_AMERICA.UTF8

if [ $? = 1 ];  then
  echo "ERROR: oracle user .bash_profile: Permission denied"
  exit 1
fi

if [ ! -d $BACKUP_DIR ]; then
    echo "make backup dir $BACKUP_DIR"
    mkdir -p $BACKUP_DIR
fi

rman log=$backup_dir/fullbak_${ORACLE_SID}_${d_time}.log append <<EOF
connect target /;
crosscheck archivelog all;
delete noprompt obsolete;
run
{
allocate channel c1 type disk;
backup format '${BACKUP_DIR}/${ORACLE_SID}_db_arch_%d_%T_%s' archivelog all not backed up skip inaccessible;
release channel c1;
}
exit;
EOF


if [ "$ARCH_KEEP_DAYS" -ge 0 ]
then
rman log=$backup_dir/fullbak_${ORACLE_SID}_${d_time}.log append <<EOF
connect target /;
crosscheck archivelog all;
CONFIGURE ARCHIVELOG DELETION POLICY TO BACKED UP 1 times TO DEVICE TYPE DISK SHIPPED TO ALL STANDBY;
delete noprompt archivelog until time 'sysdate-${ARCH_KEEP_DAYS}';
exit;
EOF
fi


