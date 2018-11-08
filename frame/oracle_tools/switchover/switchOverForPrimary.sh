num1=`ps -ef|grep LOCAL=NO|grep -v grep| wc -l`
if [ $num1 -ne 0 ]
then
ps -ef|grep LOCAL=NO|grep -v grep|awk {'print $2'}|xargs kill -9
else
echo "the process num is zero"
fi

i=0
while [ ${i} -lt 5 ]
do
num2=`ps -ef|grep LOCAL=NO|grep -v grep| wc -l`
if [ $num2 -ne 0 ]
then
ps -ef|grep LOCAL=NO|grep -v grep|awk {'print $2'}|xargs kill -9
else
break
fi
i=`expr $i + 1`
done

su - oracle <<EOF
sqlplus '/ as sysdba'
alter system switch logfile;
alter system switch logfile;
alter system switch logfile;
alter database commit to switchover to physical standby with session shutdown;
shutdown immediate;
exit;
EOF
