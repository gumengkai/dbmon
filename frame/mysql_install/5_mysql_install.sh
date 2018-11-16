tar xvf /tmp/mysql_install/mysql-5.6.38-linux-glibc2.12-x86_64.tar.gz
cp /tmp/mysql_install/my.cnf /u01/my3306/my.cnf
cp -r /tmp/mysql_install/mysql-5.6.38-linux-glibc2.12-x86_64/* /u01/my3306
cd /u01/my3306
/u01/my3306/scripts/mysql_install_db --basedir=/u01/my3306 --datadir=/u01/my3306/data --defaults-file=/u01/my3306/my.cnf --user=mysql


