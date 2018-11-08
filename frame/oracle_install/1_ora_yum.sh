yum list
yum -y install binutils compat-libcap1 compat-libstdc++ gcc gcc-c++ glibc glibc-devel ksh libgcc libstdc++ libstdc++-devel libaio libaio-devel make sysstat
yum list | grep compat-libstdc++
yum -y install compat-libstdc++-33.x86_64
yum -y install compat-libstdc++-33.i686