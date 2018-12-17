#!/bin/sh

MYSQL_USER=root
MYSQL_PASSWORD=mysqld
DATA_PATH=/backup/mysql_full
DATE=$(date +%Y%m%d)
DATA_FILE=$DATA_PATH/dbfullbak_$DATE.sql.gz
LOG_FILE=$DATA_PATH/dbfullbak_$DATE.log

MYSQL_PATH=/u01/my3306/bin
MYSQL_DUMP="$MYSQL_PATH/mysqldump -u${MYSQL_USER} -p${MYSQL_PASSWORD} -S /u01/my3306/run/mysql.sock -A -R -x --default-character-set=utf8"

echo > $LOG_FILE
echo -e "==== Jobs started at $(date +"%y-%m-%d %H:%M:%S") ===\n" >> $LOG_FILE
echo -e "*** Excuted commend：${MYSQL_DUMP} |gzip > $DATA_FILE" >> $LOG_FILE
${MYSQL_DUMP} |gzip > $DATA_FILE
echo -e "*** Excuted finished：${MYSQL_DUMP} |gzip > $DATA_FILE" >> $LOG_FILE
echo -e "*** Bachkup file size："`du -sh $DATA_FILE`" ===\n" >> $LOG_FILE


echo -e "----Find expired backup and delete those file ----" >> $LOG_FILE
for tfile in $(/usr/bin/find $DATA_PATH/ -mtime +7)
do
      if [-d $tfile ] ; then
	      rmdir $tfile
	  elif [-f $tfile] ; then
	      rm $tfile
	  fi
      echo "----Delete the file $tfile ----" >> $LOG_FILE
done

echo -e "==== Jobs ended at $(date +"%y-%m-%d %H:%M:%S") ===\n" >> $LOG_FILE

