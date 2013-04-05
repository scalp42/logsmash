import os
import re
from fabric.api import *
from fabric.colors import *
from fabric.contrib import *
from fabtools import require
import fabtools

#env.use_ssh_config = True
env.disable_known_hosts = True
env.skip_bad_hosts = True
env.keepalive = True
env.connection_attempts = '2'
env.warn_only = 1
env.output_prefix = 1
env.vagrant_user = 'vagrant'
env.local_dir = os.getcwd()
env.sites = ['elasticsearch-head', 'kibana', 'bigdesk']
env.es_version = '0.20.1'
env.es_running = ''
env.kibana_php_running = ''
env.openresty_version = '1.2.7.3'


@task
@with_settings(hide('everything'), warn_only=True)
def dev():
    """Get information about current Vagrant dev environment"""
    running = local('vagrant status | sed 1,2d | grep running | tr -s \' \' | awk \'{print $1}\'', capture=True).splitlines()
    if running:
        for vm in running:
            ssh_info = local('vagrant ssh-config %s' % vm, capture=True).splitlines()[1:]
            vagrant_info = dict([l.strip().split(' ', 1) for l in ssh_info if l.strip()])
            env.key_filename = vagrant_info['IdentityFile']
            env.hosts.append('%(User)s@%(HostName)s:%(Port)s' % vagrant_info)
        else:
            print(red('Please start a VM with `vagrant up VM` first. Exiting.'))
            exit()


def notification(status, app, host):
    """Output notification"""
    env.macos = local('sw_vers -productVersion', capture=True)
    if(env.macos == '10.8.2' and status == 'started'):
        local('terminal-notifier -message "Deployment of %(app)s on %(host)s %(status)s." -title "Fabric"' % {'app': app, 'host': host, 'status': status})
        #local('say -v Vicki "Deployment to %(app)s started.' % {'app': env.application})
    if(env.macos == '10.8.2' and status == 'finished'):
        local('terminal-notifier -message "Deployment of %(app)s on %(host)s is %(status)s !" -title "Fabric" -subtitle "DONE"' % {'app': app, 'host': host, 'status': status})
        #local('say -v Vicki "Deployment to %(app)s is finished. Have fun."' % {'app': env.application})


@task
def kibana_php():
    """Install (or replace) Kibana installation"""
    if env.host_string is None:
        print(red('\nPlease run the \'dev\' task before.\n'))
        print(yellow('-> fab dev %(command)s' % env))
        print(red('\nExiting...'))
        exit()
    with quiet():
        host = run('hostname')
        if re.match('^es[0-9]+', host):
            print(yellow('%s is not a Kibana PHP VM, skipping deployment.\n' % host))
            return
        if re.match('^queue[0-9]', host):
            print(yellow('%s is not a Kibana PHP VM, skipping deployment.\n' % host))
            return
    with quiet():
        notification('started', 'Kibana', host)
        sudo('rm -f /root/nginx_kibana_php.tar.gz')
    with settings(hide('everything')):
        print(green('Installing / Upgrading required deb packages on %s...' % host))
    require.directory('/home/vagrant/fabric', owner='%(vagrant_user)s' % env)
    require.deb.packages(['php5-fpm', 'nginx-extras', 'php5-curl', 'php5-cgi', 'php5-suhosin', 'php5-cli'], update=False)
    with quiet():
        print(green('Stopping nginx and php5-fpm services if running on %s...' % host))
        require.service.stopped('nginx')
        require.service.stopped('php5-fpm')
        with cd('/etc/php5/fpm/pool.d'), quiet():
            sudo('sed -i \'s/^listen = 127.0.0.1:9000/;listen = 127.0.0.1:9000/\' www.conf')
            sudo('sed -i \'/^;listen = 127.0.0.1:9000/ a\listen = /var/run/php5-fpm.sock\' www.conf')
    with quiet():
        print(green('Uploading nginx conf from %s/conf/nginx_kibana_php.tar.gz to %s.' % (env.local_dir, host)))
        require.file('/home/vagrant/fabric/nginx_kibana_php.tar.gz', source='%(local_dir)s/conf/nginx_kibana_php.tar.gz' % env, verify_remote=True)
        with cd('fabric'), settings(warn_only=False), hide('everything'):
            sudo('cp nginx_kibana_php.tar.gz /root')
            print(green('Extracting nginx conf on %s...' % host))
            sudo('tar -xpzf /root/nginx_kibana_php.tar.gz -C /')
    with quiet():
        sudo('sed -i \'2s/worker_processes [0-9]*;/worker_processes 2;/\'')
        with settings(hide('everything')):
            for site in env.sites:
                sudo('chown -R www-data:www-data /usr/local/share/%s' % site)
                sudo('rm -f /etc/nginx/sites-enabled/%s' % site)
                sudo('ln -s /etc/nginx/sites-available/%s /etc/nginx/sites-enabled/%s' % (site, site), warn_only=False)
                require.directory('/usr/local/share/%s' % site, owner='www-data', group='www-data', use_sudo=True)
            with cd('/usr/local/share/%s' % site):
                if (sudo('git reset HEAD --hard').succeeded):
                    if site == 'kibana':
                        sudo('git pull origin php-deprecated')
                    else:
                        sudo('git pull origin master')
                else:
                    sudo('git init')
                    sudo('git remote add origin https://github.com/scalp42/%s' % site)
                    if site == 'kibana':
                        sudo('git pull -q origin php-deprecated')
                    else:
                        sudo('git pull -q origin master')
            sudo('chown -R www-data:www-data /usr/local/share/%s' % site)
    with settings(hide('everything'), warn_only=False):
        print(green('Starting nginx and php5-fpm services on %s if not running...' % host))
        require.service.started('nginx')
        require.service.started('php5-fpm')
    with quiet():
        print(green('Cleaning up %s.' % host))
        sudo('rm -f /root/nginx_kibana_php.tar.gz')
    with quiet():
        notification('finished', 'Kibana', host)


@task
def es():
    """Set up a ES node"""
    if env.host_string is None:
        print(red('\nPlease run the \'dev\' task before.\n'))
        print(yellow('-> fab dev %(command)s' % env))
        print(red('\nExiting...'))
        exit()
    with quiet():
        host = run('hostname')
    if re.match('^kibana', host):
        print(yellow('%s is not an ElasticSearch VM, skipping deployment.\n' % host))
        return
    if re.match('^queue[0-9]', host):
        print(yellow('%s is not an ElasticSearch VM, skipping deployment.\n' % host))
        return
    with quiet():
        notification('started', 'ES', host)
        ip = fabtools.network.address('eth1')
    with settings(hide('everything')):
        print(green('Installing / Upgrading required deb packages on %s...' % host))
        require.directory('/home/vagrant/fabric', owner='%(vagrant_user)s' % env)
        require.deb.packages(['unzip', 'curl', 'python-software-properties', 'openjdk-7-jre-headless'], update=True)
        if (sudo('dpkg --get-selections | grep elasticsearch', quiet=True).succeeded):
            vagrant_es_version = sudo('dpkg -s elasticsearch | grep -i version | awk \'{print $2}\'', quiet=True)
            if vagrant_es_version < env.es_version:
                print(yellow("ES version on the node %s is %s, should be %s. Upgrading." % (host, vagrant_es_version, env.es_version)))
                with cd('/home/vagrant/fabric'), settings(hide('everything'), warn_only=False):
                    require.file(url='http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-%(es_version)s.deb' % env)
                    sudo('dpkg -i elasticsearch-%(es_version)s.deb' % env)
            else:
                print(green("ES version is up-to-date on \'%s\'. Moving on." % host))
        else:
            with cd('/home/vagrant/fabric'), settings(hide('everything'), warn_only=False):
                print(green("Installing ElasticSearch on \'%s\'..." % host))
                require.file(url='http://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-%(es_version)s.deb' % env)
                sudo('dpkg -i elasticsearch-%(es_version)s.deb' % env)
    with settings(hide('everything'), warn_only=False):
        print(green('Stopping elasticsearch service if running on %s...' % host))
        require.service.stopped('elasticsearch')
    with settings(hide('everything'), warn_only=False):
        print(green('Setting up ES node configuration on %s...' % host))
        sudo('sed -i \'s/# cluster.name: elasticsearch/cluster.name: logsmash/\' /etc/elasticsearch/elasticsearch.yml')
        sudo('host=`hostname` ; sed -i \'s/# node.name: "Franz Kafka"/node.name: "\'$host\'"/\' /etc/elasticsearch/elasticsearch.yml')
    with settings(hide('everything')):
        if (sudo('ifconfig -a | grep -C 1 eth1 | tr -s \' \' | grep addr | awk \'{print $2}\' | sed 1d | awk -F \':\' \'{print $2}\'').failed):
            print(red('Could not figure IP of %(host_string)s. Please double check Vagrantfile config and run `vagrant reload %s`.') % env, host)
        else:
            with settings(hide('everything')):
                #sudo('ifconfig -a | grep -C 1 eth1 | tr -s \' \' | grep addr | awk \'{print $2}\' | sed 1d | awk -F \':\' \'{print $2}\'')
                sudo('sed -i \'s/# network.host: 192.168.0.1/network.host: \'%s\'/\' /etc/elasticsearch/elasticsearch.yml' % ip)
                sudo('sed -i \'210d\' /etc/elasticsearch/elasticsearch.yml')
                sudo('sed -i \'210i network.host: \'%s\'\' /etc/elasticsearch/elasticsearch.yml' % ip)
    with quiet():
        print(green('Installing Redis River on %s...' % host))
        sudo('/usr/share/elasticsearch/bin/plugin -install scalp42/elasticsearch-redis-river/')
    with settings(hide('everything')):
        print(green('Starting elasticsearch service if not running on %s...' % host))
        require.service.started('elasticsearch')
    with quiet():
        notification('finished', 'ES', host)


@task
def q():
    """Set up a Redis queue"""
    if env.host_string == None:
        print(red('\nPlease run the \'dev\' task before.\n'))
        print(yellow('-> fab dev %(command)s' % env))
        print(red('\nExiting...'))
        exit()
    with quiet():
        host = run('hostname')
        if re.match('^kibana', host):
            print(yellow('%s is not a Redis queue VM, skipping deployment.\n' % host))
            return
        if re.match('^es[0-9]+', host):
            print(yellow('%s is not a Redis queue VM, skipping deployment.\n' % host))
            return
    with quiet():
        notification('started', 'Redis/Nginx', host)
    print(green('\n--- NGINX ---'))
    with settings(hide('everything')):
        print(green('Stopping Nginx if running on %s...' % host))
        require.service.stopped('nginx')
        print(green('Installing / Upgrading required Nginx deb packages on %s...' % host))
        require.directory('/home/vagrant/fabric', owner='%(vagrant_user)s' % env)
        require.deb.packages(['libreadline-dev', 'libncurses5-dev', 'libpcre3-dev', 'libssl-dev', 'perl'], update=True)
        if (sudo('ls /opt/nginx/sites-enabled', quiet=True).succeeded):
            vagrant_openresty_version = sudo('/opt/nginx/sbin/nginx -V 2>&1 | head -n 1 | awk \'{print $3}\' | awk -F \'/\' \'{print $2}\'', quiet=True)
            if vagrant_openresty_version < env.openresty_version:
                print(yellow("Nginx version on the node %s is '%s', should be '%s'. Upgrading." % (host, vagrant_openresty_version, env.openresty_version)))
                with cd('/home/vagrant/fabric'), settings(hide('everything'), warn_only=False):
                    require.file(url='http://agentzh.org/misc/nginx/ngx_openresty-%(openresty_version)s.tar.gz' % env)
                    sudo('tar xzvf ngx_openresty-%(openresty_version)s.tar.gz -C /tmp' % env)
                with cd('/tmp/ngx_openresty-%(openresty_version)s' % env), settings(hide('everything'), warn_only=False):
                    print(green('Compiling Nginx on %s...' % host))
                    sudo('./configure --with-luajit --prefix=/opt -j2')
                    sudo('make -j2')
                    sudo('make install')
            else:
                print(green("Nginx version is up-to-date on \'%s\'. Moving on." % host))
        else:
            with cd('/home/vagrant/fabric'), settings(hide('everything'), warn_only=False):
                print(yellow("Nginx was not found on \'%s\'. Proceeding with installation." % host))
                require.file(url='http://agentzh.org/misc/nginx/ngx_openresty-%(openresty_version)s.tar.gz' % env)
                sudo('tar xzvf ngx_openresty-%(openresty_version)s.tar.gz -C /tmp' % env)
            with cd('/tmp/ngx_openresty-%(openresty_version)s' % env), settings(hide('everything'), warn_only=False):
                print(green('Compiling Nginx on %s...' % host))
                sudo('./configure --with-luajit --prefix=/opt -j2')
                sudo('make -j2')
                sudo('make install')
    with quiet():
        print(green('Uploading nginx conf from %s/conf/nginx_redis_queue.tar.gz to %s.' % (env.local_dir, host)))
        require.file('/home/vagrant/fabric/nginx_redis_queue.tar.gz', source='%(local_dir)s/conf/nginx_redis_queue.tar.gz' % env, verify_remote=True)
        with cd('fabric'), settings(warn_only=False), hide('everything'):
            sudo('cp nginx_redis_queue.tar.gz /root')
            print(green('Extracting nginx conf on %s...' % host))
            sudo('tar -xpzf /root/nginx_redis_queue.tar.gz -C /')
        with cd('/opt/nginx'), settings(hide('everything'), warn_only=False):
            print(green('Fixing perms, linking sites and creating init.d script on %s...' % host))
            sudo('rm -f /opt/nginx/sites-available/default')
            sudo('ln -fs /opt/nginx/sites-available/generic /opt/nginx/sites-enabled/generic')
            sudo('ln -fs /opt/nginx/sites-available/mozilla /opt/nginx/sites-enabled/mozilla')
            sudo('chown -R www-data:www-data ../nginx')
            sudo('cp nginx_service /etc/init.d/nginx && chmod 755 /etc/init.d/nginx')
    print(green('\n--- REDIS ---'))
    with settings(hide('everything'), warn_only=False):
        print(green('Installing / Upgrading required Redis packages on %s...' % host))
        require.directory('/home/vagrant/fabric', owner='%(vagrant_user)s' % env)
        require.deb.packages(['redis-server'], update=True)
        print(green('Stopping Redis if running on %s...' % host))
        require.service.stopped('redis-server')
        print(green('Setting up Redis on %s...' % host))
        require.file('/home/vagrant/fabric/redis.conf', source='%(local_dir)s/conf/redis/redis.conf' % env, verify_remote=True)
    with cd('/home/vagrant/fabric'), settings(warn_only=False):
#       sudo('sed -i \'s/^listen = 127.0.0.1:9000/;listen = 127.0.0.1:9000/\' www.conf')
#       sudo('sed -i \'/^;listen = 127.0.0.1:9000/ a\listen = /var/run/php5-fpm.sock\' www.conf')
        sudo('sed -i \'s/^bind 127.0.0.1/#bind 127.0.0.1/\' redis.conf ')
#       sudo('ip=`ifconfig -a | grep -C 1 eth1 | tr -s \' \' | grep addr | awk \'{print $2}\' | sed 1d | awk -F \':\' \'{print $2}\'` ; sed -i \'/^#bind 127.0.0.1/ a\bind $ip\' redis.conf')
        sudo('sed -i \'s/^#bind 127.0.0.1/bind 0.0.0.0/\' redis.conf')
        sudo('cp redis.conf /etc/redis/redis.conf && chmod 644 /etc/redis/redis.conf')
        print(green('Starting Redis if not running on %s...' % host))
        require.service.started('redis-server')
        print(green('Starting Nginx if not running on %s...' % host))
        require.service.started('nginx')
        notification('finished', 'Redis/Nginx', host)


@task
def php():
    """ Alias to 'kibana_php' task """
    kibana_php()


@task
def queue():
    """ Alias to 'q' task """
    q()


@task
def elastic():
    """ Alias to 'es' task """
    es()


@task
def ips():
    """ Return IPs of all VMs currently running """
    with quiet():
        host = run('hostname')
        print("\nFound the following IPs for " + green("%s" % host) + ":")
        print(cyan(fabtools.network.address('eth1')) + "\n")
