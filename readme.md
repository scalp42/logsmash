# Logsmash

> ####Smash all these logs.


## Overview


![image](http://i.imgur.com/I2taY8S.png)


## Requirements

Add the following in your `hosts` file **(use sudo)**:

	10.10.10.10     search.logsmash.dev cluster.logsmash.dev bigdesk.logsmash.dev
	10.10.10.31 	mozilla.logsmash.dev
	10.10.10.31 	generic.logsmash.dev

Install **python**:

	$> brew update ; brew install python
	
Add this to your **.zshrc/.bash_profile** and source it:

	export PYTHONPATH=$(brew --prefix)/lib/python2.7/site-packages

	export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/X11/bin:/opt/local/bin:/usr/local/sbin:/usr/local/share/python:$PATH

If you use **[oh-my-zsh](https://github.com/robbyrussell/oh-my-zsh)**, enable **Vagrant** completion in **.zshrc** and source it:

	plugins=(git textmate rails ruby sublime ssh-agent terminalapp screen rvm redis-cli rbenv rake pip osx perl npm node macports knife gnu-utils gem cpanm cap bundler brew vagrant)
	
	You should then be able to tab:
	
	$> vagrant box                                                                                                                                                                     	box         -- Box commands
	destroy     -- Destroys the vagrant environment
	halt        -- Halts the currently running vagrant environment
	help        -- [TASK] Describe available tasks or one specific task
	init        -- [box_name] [box_url] Initializes current folder for Vagrant usage
	package     -- Packages a vagrant environment for distribution
	provision   -- Run the provisioner
	reload      -- Reload the vagrant environment
	resume      -- Resumes a suspend vagrant environment
	ssh         -- SSH into the currently running environment
	ssh_config  -- outputs .ssh/config valid syntax for connecting to this environment via ssh.
	status      -- Shows the status of the current Vagrant environment.
	suspend     -- Suspends the currently running vagrant environment
	up          -- Creates the vagrant environment
	version     -- Prints the Vagrant version information

	
Install **fabric** and **fabtools**:

	$> pip install --upgrade fabric fabtools

Install the required gems for the dev environment:

	$> bundle install --binstubs

Once Vagrant is installed, you need to download the ISO template for Ubuntu 12.04:

	$> vagrant box add precise64_new http://dl.dropbox.com/u/1537815/precise64.box

**It will take some time**. Once downloaded, you're ready to start, thanks to the `Vagrantfile`.

## Infrastructure

The repo ships with **7** VMs in the `Vagrantfile` preconfigured in `host_only` mode (not bridged on your LAN):

	$> vagrant status
	Current VM states:
	
	kibana_php               not created
	es1                      not created
	es2                      not created
	es3                      not created
	queue1                   not created
	queue2                   not created
	queue3                   not created
	
	This environment represents multiple VMs. The VMs are all listed
	above with their current state. For more information about a specific
	VM, run `vagrant status NAME`.



 **You do not have to run them all.** Here is the rundown:
 
 
###### kibana_php

 - points to `search.logsmash.dev`, used to display logs with `Kibana` (PHP)
 - points to `cluster.logsmash.dev`, used to see the state of the ES indexes
 - points to `bigdesk.logsmash.dev`, used to see the current states of the ES JVMs
 
###### es[1-3]

- those VMs are the ES nodes (which form a cluster automatically **if** there are more than 2 running)
- you **need** at least 1 node UP
- ES listens on its private IP, in the IP range of `10.10.10.2x`
	- so es1 is accessible on `10.10.10.21`
	- es3 is accessible on `10.10.10.23` **(if the node is UP)**

###### queue[1-3]

- those VMs contain the combo Nginx + Redis , in the IP range of `10.10.10.3x`
	- Nginx is used for the subdomain `generic.logsmash.dev` or `mozilla.logsmash.dev` for ex
	- Redis is used to store the logs waiting to be processed by **es[1-3]**
- Redis store one list per host/subdomain
- Redis is bound on 0.0.0.0

##### The first time you start a VM, it will take some time to provision it.

##### ~~Also, you only need `es1` to be UP for Rails.~~ (WIP, Rails app is not available)


## How to deploy

Vagrant cheat sheet:

- `vagrant up` : start the VM or create it if it doesn't exist.
- `vagrant halt` : stop the VM. You rarely need this and usually go for `vagrant suspend`. See below.
- `vagrant suspend` : suspend the VM.
- `vagrant destroy [--force]` : nuke the VM, [running or not].
- `vagrant provision` : **re-[provision](http://vagrantup.com/v1/docs/provisioners.html)** a VM (from `provision/*.sh`). Should not be needed.

Once your VMs are UP, use **fabric** to get the list of the tasks available:

	$> fab -l
	Available commands:
	
	    dev         Get information about current Vagrant dev environment
	    elastic     Alias to 'es' task
	    es          Set up a ES node
	    ips         Return IPs of all VMs currently running
	    kibana_php  Install (or replace) Kibana installation
	    php         Alias to 'kibana_php' task
	    q           Set up a Redis queue
	    queue       Alias to 'q' task



Run **any or all** of the following tasks:

	$> fab dev kibana_php es queue


## How to test from command line


Just use `curl` to simulate some data coming to `mozilla.logsmash.dev` (correct token is `firefox`):

If the token is **wrong**, it should drop the connection:

	$> curl mozilla.logsmash.dev -d "fake logs hacker!" --header "X-Logsmash-token: peekaboo" 
	curl: (52) Empty reply from server

It the token is **good**, you should get a return from it:

	$> curl mozilla.logsmash.dev -d "some log blabla" --header "X-Logsmash-token: firefox" 
	Verified token: mozilla  <-- Output whose token it is
	:42 <-- How many values in the `mozilla` key (its a list)

If you want to put some data in your ES cluster, you can also use `curl`:

	$> curl -XPUT http://10.10.10.21:9200/twitter/user/scalp42 -d '{ "name" : "Anthony Scalisi", "skills" : "devops" }' 
	
	{"ok":true,"_index":"twitter","_type":"user","_id":"scalp42","_version":2}
	
You should then have an index named 'twitter' in your ES cluster:

	$> curl -XGET http://10.10.10.21:9200/twitter/user/scalp42
	{"_index":"twitter","_type":"user","_id":"scalp42","_version":2,"exists":true, "_source" : { "name" : "Anthony Scalisi", "skills" : "devops" }}


## How to visually input some data in the ES cluster

Make sure you have `kibana_php` up and deployed, then head to `cluster.logsmash.dev`.

You should be able to manually input whatever log you want using the `Any Request` tab at the top.

## How to ship logs

Make sure you have your **3** VMs (**kibana_php**, **es1** and **queue1**) started:

	$> vagrant status
	Current VM states:
	
	kibana_php               running
	es1                      running
	es2                      not created
	es3                      not created
	queue1                   running
	queue2                   not created
	queue3                   not created 

If not `vagrant up kibana_php es1 queue1` and `fab -P dev php q es`.

From the main repo, download **[Logstash](https://logstash.objects.dreamhost.com/release/logstash-1.1.5-monolithic.jar)** to replicate a host sending logs by passing a config file to it (located in `conf/logstash/`). All the demo config files ship the logs from your laptop by default to generate some traffic. For mozilla example:

	$> sudo java -jar logstash-1.1.5-monolithic.jar agent -f conf/logstash/mozilla.conf
	
Stop it after 30 sec.

If you log in queue1, using `vagrant ssh queue1`, log in Redis to see the key `mozilla` present:

	root@queue1:~# redis-cli keys mozilla
	1) "mozilla"

You can get the number of values in the list `mozilla`:

	root@queue1:~# redis-cli lrange mozilla 0 2
	1) "{\"index\":{\"_index\":\"mozilla-2012-12-29\",\"_type\":\"log\"}\n{\"@source\":	\"file://mbp/var/log/system.log\",\"@tags\":[],\"@fields\":{},\"@timestamp\":	\"2012-12-29T09:51:28.754Z\",\"@source_host\":\"mbp\",\"@source_path\":\"/var/log/	system.log\",\"@message\":\"Dec 29 01:51:28 mbp EVE[492]: UIElement not in the filter.\",	\"@type\":\"linux-syslog\"}\n"
	2) "{\"index\":{\"_index\":\"mozilla-2012-12-29\",\"_type\":\"log\"}\n{\"@source\":	\"file://mbp/var/log/system.log\",\"@tags\":[],\"@fields\":{},\"@timestamp\":\"2012-12-29T09:51:28.754Z\",\"@source_host\":\"mbp\",\"@source_path\":\"/var/log/system.log\",\"@message\":\"Dec 29 01:51:28 mbp iTerm[19404]: -[__NSCFConstantString accessibilityAttributeValue:]: unrecognized selector sent to instance 0x7fff7ed98680\",\"@type\":\"linux-syslog\"}\n"
	3) "{\"index\":{\"_index\":\"mozilla-2012-12-29\",\"_type\":\"log\"}\n{\"@source\":\"file://mbp/var/log/system.log\",\"@tags\":[],\"@fields\":{},\"@timestamp\":\"2012-12-29T09:51:22.732Z\",\"@source_host\":\"mbp\",\"@source_path\":\"/var/log/system.log\",\"@message\":\"Dec 29 01:51:22 mbp EVE[492]: UIElement not in the filter.\",\"@type\":\"linux-syslog\"}\n"

Those are the logs from your local laptop. As long as you see the key `mozilla`, it's working. You can issue `redis-cli flushall` and reship logs, the key **should reappear**.

Ask **any** ElasticSearch to pick up the logs from Redis (called a **[river](http://www.elasticsearch.org/guide/reference/river/)**) using `curl`:

	curl -XPUT '10.10.10.21:9200/_river/mozilla_river/_meta' -d '{
		  "type" : "redis",
		  "redis" : {
		 		"host"     : "10.10.10.31", 
			    "port"     : 6379,
          		"key"      : "mozilla",
			    "mode"     : "list",
			    "database" : 0  			},
		 "index" : {
	     		"bulk_size" : 5,
    	 		"bulk_timeout" : 5 		     	
    	 									}
	}'

Check for the return:

	{"ok":true,"_index":"_river","_type":"mozilla_river","_id":"_meta","_version":4}

Your logs should be now gone from `queue1`. Check with `redis-cli`:

	root@queue1:~# redis-cli llen mozilla
	(integer) 0


You should be able to see your logs on Kibana (VM kibana_php), `search.logsmash.dev`.

**Strong.**


## VAGRANT TRICKS

Reload all the VMs in parallel **(needed)** to change VM network conf) and print all the IPs:

	vagrant status | sed 1,2d | grep running | tr -s ' ' | awk '{print $1}' | xargs -n 1 -P 10 vagrant reload && fab dev ips
	
	
Shutdown all the VMs in parallel:

	vagrant status | sed 1,2d | grep running | tr -s ' ' | awk '{print $1}' | xargs -n 1 -P 10 vagrant halt
	

Suspend all the VMs in parallel **(SSD recommended)**:

	vagrant status | sed 1,2d | grep running | tr -s ' ' | awk '{print $1}' | xargs -n 1 -P 10 vagrant suspend
	
Start all the VMs already created in parallel:

	vagrant status | sed 1,2d | egrep "running|poweroff|saved"| tr -s ' ' | awk '{print $1}' | xargs -n 1 -P 10 vagrant up

Destroy all the VMs created in parallel:

	vagrant status | sed 1,2d | egrep "running|saved|poweroff" | tr -s ' ' | awk '{print $1}' | xargs -n 1 -P 10 vagrant destroy --force
	
	
## FAQ

Q: "Where are these `tokens`?"

A: The tokens live on each `queue` servers in `/opt/nginx/sites-enabled/tokens`. You should not need to tweak Nginx configuration for the tokens.
Please use `generic.logsmash.dev` (token `generictoken`) and `mozilla.logsmash.dev` (token `firefox`) for testing purposes.

Q: "I get this error when deploying X task"

		W: Failed to fetch mirror://mirrors.ubuntu.com/mirrors.txt/dists/precise-security/multiverse/binary-i386/Packages  404  Not Found [Mirror: http://mirror.thelinuxfix.com/ubuntu/]
	
		E: Some index files failed to download. They have been ignored, or old ones used instead.
		
	
A: The VMs are configured to look for the fastest mirror related to `apt-get update`. Try to redeploy again, or if it **really** does not work, destroy the VM with `vagrant destroy VM --force` and recreate it with `vagrant up VM`.

Q: "When I access `search.logsmash.dev` I get a 502 from Nginx"

A: Please redeploy again with `fab dev php` or `fab dev kibana_php`, php5-fpm ghost issue that I can't figure.

Q: "I don't see any logs on `search.logsmash.dev` ?"

A: Please **make sure** `es1` is up and running. You can verify through Vagrant or using `cluster.logsmash.dev` and entering the IP of any ES VMs for example `10.10.10.21:9200` (which should be `es1`)

Q: "But what about AWS ?"

A: Soon.™