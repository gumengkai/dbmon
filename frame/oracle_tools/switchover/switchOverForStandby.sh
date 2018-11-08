su - grid <<EOF
srvctl stop listener
EOF

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

echo "CastielEchoIt"

su - oracle <<EOF
sqlplus '/ as sysdba'
alter database recover managed standby database cancel;
alter database commit to switchover to primary with session shutdown;
alter database open;
exit;
EOF
