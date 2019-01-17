#!/bin/bash
export LC_ALL=C

function usage() {
   echo "usage: oraclefullbak.sh -i [oracle_sid] -d [backup directory] -l [logfile] -r [retention days]"
   exit 1
}

while getopts ":i:d:r:c:l:" opt; do
    case $opt in
        i  ) PRI_SID=$OPTARG;;
        d  ) BACK_DIR=$OPTARG;;
        r  ) RE_DAYS=$OPTARG;;
        l  ) LOG_FILE=$OPTARG;;
        \? ) usage
    esac
done
shift $(($OPTIND - 1))

if [ -z $PRI_SID ]; then usage; fi
if [ -z $BACK_DIR ]; then usage; fi
if [ -z $RE_DAYS ]; then usage; fi

if test $(id -u) != $(id oracle -u) ; then
    echo "ERROR: OS NOT oracle account!"
    exit 1
fi

. $(cat /etc/passwd|grep ^oracle|awk -F ':' '{print $6}')/.bash_profile
export ORACLE_SID=$PRI_SID
export NLS_LANG=AMERICAN_AMERICA.UTF8

if [ $? = 1 ];  then
  echo "ERROR: oracle user .bash_profile: Permission denied"
  exit 1
fi

if [ -d $BACK_DIR ];then
        echo "The database backup dir has existed."
else
        mkdir -p $BACK_DIR
        echo "mkdir database backup dir."
fi

d_date=`date +%y%m%d`
d_time=`date +%y%m%d%H%M`
backup_dir=${BACK_DIR}
control_dir=${BACK_DIR}


if [ ! -d $backup_dir ]; then
    echo "make temp dir $backup_dir"
    mkdir -p $backup_dir
fi


if [ ! -d $control_dir ]; then
    echo "make control dir $control_dir"
    mkdir -p $control_dir
fi

#####check bak dir free space <90% #####
# usedrate=`df -h $BACK_DIR | grep -E "[0-9]%" | awk '{if ($4~/%/) print $4; else print $5}' |sed s/%//g`

# if [ $usedrate -ge 90 ]; then
#     echo -e "backup dir $BACK_DIR used $usedrate % >  90% Threshold space,please check $TMPDIR,backup exit!"
#     exit
# else
#     echo -e "backup dir $BACK_DIR used $usedrate % <  90% Threshold space !"
# fi
#

rman log=$backup_dir/fullbak_${ORACLE_SID}_${d_time}.log append <<EOF
connect target /;
#connect catalog rman/rman_123@rman;
configure retention policy to recovery window of ${RE_DAYS} days;
configure controlfile autobackup on;
configure controlfile autobackup format for device type disk to '${control_dir}/${ORACLE_SID}_control_%F';
run
{
allocate channel c1 type disk;
backup  database format '${backup_dir}/${ORACLE_SID}_db_full_%T_%U' tag='full_bk';
sql 'alter system archive log current';
backup archivelog all format '${backup_dir}/${ORACLE_SID}_db_arch_%T_%U' not backed up skip inaccessible;
release channel c1;
}
crosscheck backup;
delete noprompt expired backup;
delete noprompt obsolete;
exit;
EOF
exit
