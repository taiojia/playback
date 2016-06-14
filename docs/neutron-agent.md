# OpenStack Neutron Agent

## Deploy Neutron Agent

Install neutron agent on compute nodes

    playback-neutron-agent --user ubuntu --hosts compute1.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute2.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute3.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute4.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute5.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute6.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute7.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute8.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute9.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP
    playback-neutron-agent --user ubuntu --hosts compute10.maas install --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP

### Arguments

* --local-ip: the management interface ip of the current compute node

Using `playback-neutron-agent --help` to see the details.