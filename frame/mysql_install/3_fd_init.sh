mkdir -p /u01/my3306
groupadd mysql
useradd -d /home/mysql -g mysql -m mysql
mkdir -p /u01/my3306/log/iblog
mkdir -p /u01/my3306/log/binlog
mkdir -p /u01/my3306/run
mkdir -p /u01/my3306/tmp
chown -R mysql:mysql /u01/my3306
chmod 755 /u01/my3306
