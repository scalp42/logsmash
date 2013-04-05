Vagrant::Config.run do |config|
  config.vm.define :kibana_php, :primary => true do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "kibanaphp"
    vconfig.vm.network :hostonly, "10.10.10.10"
    #vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 256, "--cpus", 1, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2210, :auto => true)
    #vconfig.vm.forward_port(80, 8080, :auto => true)
    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
    vconfig.vbguest.auto_update = true
  end

  config.vm.define :es1 do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "es1"
    vconfig.vm.network :hostonly, "10.10.10.21"
    #vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 512, "--cpus", 1, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2221, :auto => true)
    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
    vconfig.vbguest.auto_update = true
  end

  config.vm.define :es2 do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "es2"
    vconfig.vm.network :hostonly, "10.10.10.22"
    #vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 512, "--cpus", 1, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2222, :auto => true)
    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
    vconfig.vbguest.auto_update = true
  end

  config.vm.define :es3 do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "es3"
    vconfig.vm.network :hostonly, "10.10.10.23"
    vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 512, "--cpus", 1, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2223, :auto => true)
    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
    vconfig.vbguest.auto_update = true
  end

  config.vm.define :queue1 do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "queue1"
    #vconfig.vm.network :hostonly, "10.10.10.31"
    vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 512, "--cpus", 2, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2231, :auto => true)
    vconfig.vm.forward_port(80, 8080, :auto => true)
#    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
    vconfig.vbguest.auto_update = true
  end

  config.vm.define :queue2 do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "queue2"
    vconfig.vm.network :hostonly, "10.10.10.32"
    #vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 512, "--cpus", 2, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2232, :auto => true)
#    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
#    vconfig.vbguest.auto_update = true
  end

  config.vm.define :queue3 do |vconfig|
    vconfig.vm.box = "precise64_new"
    vconfig.vm.box_url = "http://dl.dropbox.com/u/1537815/precise64.box"
    vconfig.vm.host_name = "queue3"
    vconfig.vm.network :hostonly, "10.10.10.33"
    #vconfig.vm.network :bridged,:bridge => 'en0: Wi-Fi (AirPort)'
    vconfig.vm.customize ["modifyvm", :id, "--memory", 512, "--cpus", 2, "--ioapic", "on", "--hwvirtex", "on", "--nestedpaging", "on", "--usbehci", "on", "--audio", "none"]
    vconfig.vm.forward_port(22, 2233, :auto => true)
    vconfig.vm.provision :shell, :path => "provision/ubuntu12_04.sh"
    vconfig.vbguest.auto_update = true
  end

end
