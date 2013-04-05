sudo sed -i 's/^# deb http:\/\/archive.canonical.com\/ubuntu precise partner/deb http:\/\/archive.canonical.com\/ubuntu precise partner/' /etc/apt/sources.list
sudo sed -i 's/^# deb-src http:\/\/archive.canonical.com\/ubuntu precise partner/deb-src http:\/\/archive.canonical.com\/ubuntu precise partner/' /etc/apt/sources.list
sudo sed -i 's/^# deb http:\/\/extras.ubuntu.com\/ubuntu precise main/deb http:\/\/extras.ubuntu.com\/ubuntu precise main/' /etc/apt/sources.list
sudo sed -i 's/^# deb-src http:\/\/extras.ubuntu.com\/ubuntu precise main/deb-src http:\/\/extras.ubuntu.com\/ubuntu precise main/' /etc/apt/sources.list

check=$(grep 'mirrors.ubuntu.com/mirrors.txt' /etc/apt/sources.list)
if [ $? -ne 0 ]; then
sudo sed -i '1i\deb mirror://mirrors.ubuntu.com/mirrors.txt precise main restricted universe multiverse\' /etc/apt/sources.list
sudo sed -i '2i\deb mirror://mirrors.ubuntu.com/mirrors.txt precise-updates main restricted universe multiverse\' /etc/apt/sources.list
sudo sed -i '3i\deb mirror://mirrors.ubuntu.com/mirrors.txt precise-backports main restricted universe multiverse\' /etc/apt/sources.list
sudo sed -i '4i\deb mirror://mirrors.ubuntu.com/mirrors.txt precise-security main restricted universe multiverse\' /etc/apt/sources.list
sudo sed -i '10 d' ~/.bashrc /root/.bashrc
sudo sed -i '10 i HISTCONTROL=ignoredups:ignorespace:erasedups' ~/.bashrc
sudo sed -i '11 i HISTIGNORE="&:[ ]*:exit:ll:la:ls:xi:htop:top:iotop:history:cd:cd -:&:[bf]g:exit:pwd:clear:[ \t]*:man *:date:* --help:cleanhist:historyclean"' ~/.bashrc
sudo sed -i 's/HISTSIZE=1000/HISTSIZE=10000/' ~/.bashrc
sudo sed -i 's/HISTFILESIZE=2000/HISTFILESIZE=20000/' ~/.bashrc

sudo apt-get update ;
sudo apt-get install python-software-properties -y;
sleep 1
sudo add-apt-repository ppa:nginx/stable -y ;
sudo add-apt-repository ppa:nilarimogard/webupd8 -y ;
sudo add-apt-repository ppa:chris-lea/node.js -y ;
sudo add-apt-repository ppa:chris-lea/redis-server -y ;
sudo add-apt-repository ppa:chris-lea/fabric -y ;

if ! grep -q 'mirrors.ubuntu.com/mirrors.txt' /etc/apt/sources.list; then
echo "alias apti='sudo apt-get -y install'" > /tmp/.bash_aliases
echo "alias aptu='sudo apt-get update; sudo apt-get upgrade'" >> /tmp/.bash_aliases
echo "alias aptr='sudo apt-get remove'" >> /tmp/.bash_aliases
echo "alias aptp='sudo apt-get --purge remove'" >> /tmp/.bash_aliases
echo "alias aptdu='sudo apt-get update ; sudo  apt-get dist-upgrade'" >> /tmp/.bash_aliases
echo "alias aptc='sudo apt-get autoclean ; sudo apt-get autoremove'" >> /tmp/.bash_aliases
echo "alias nginxr='sudo service nginx restart'" >> /tmp/.bash_aliases
echo "alias xi='exit'" >> /tmp/.bash_aliases
echo "alias vf='cd'" >> /tmp/.bash_aliases
echo "alias ll='ls -lFh'" >> /tmp/.bash_aliases
echo "alias la='ls -Ah'" >> /tmp/.bash_aliases
echo "alias l='ls -CFh'" >> /tmp/.bash_aliases
echo "alias esr='sudo service elasticsearch restart'" >> /tmp/.bash_aliases
sudo cp /tmp/.bash_aliases /home/vagrant/.bash_aliases /root/.bash_aliases
sudo chown -R vagrant:vagrant /home/vagrant
sudo chown -R root:root /root
fi

sudo apt-get update ;
source ~/.bashrc

if ! grep -q 'mirrors.ubuntu.com/mirrors.txt' /etc/apt/sources.list; then
sudo apt-get install launchpad-getkeys ;
sleep 1
sudo launchpad-getkeys ;
sleep 1
fi
echo "America/Los_Angeles" > /etc/timezone
sudo DEBIAN_FRONTEND=noninteractive dpkg-reconfigure -f noninteractive tzdata
echo "localepurge localepurge/nopurge multiselect en_US, fr_FR" | sudo debconf-set-selections
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" upgrade
sudo apt-get -y install linux-headers-$(uname -r) build-essential
sudo apt-get -y install zlib1g-dev libssl-dev libreadline-gplv2-dev
sudo apt-get -y install vim localepurge
sudo apt-get -y install  debconf-utils apt-file wajig htop python-setuptools python-dev build-essential launchpad-getkeys xinetd python-setuptools python-dev build-essential python-pip sysv-rc-conf autoconf libtool gettext libxml2-dev gdal-bin binutils libxslt-dev libxml2-dev libedit-dev libgeos-c1 libgeos-dev libxml2 libxml2-dev libxml2-dev checkinstall proj libpq-dev openssl zlib1g zlib1g-dev libxml2 libxslt-dev libssl-dev git-core libcurl4-openssl-dev libmysqlclient-dev mysql-client  libqt4-dev wajig python-dev python-pip toilet figlet apt-file graphviz build-essential ghostscript libreadline-gplv2-dev iotop dkms nfs-common libnss-mdns  zip unzip
sudo DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" dist-upgrade
sudo updatedb;
sudo apt-get autoremove ; sudo apt-get autoclean
#sudo DEBIAN_FRONTEND=noninteractive dpkg-reconfigure -f noninteractive localepurge
#sudo apt-get -y install php5-fpm nginx-extras php5-curl php5-cgi php5-suhosin php5-cli