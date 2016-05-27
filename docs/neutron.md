# OpenStack Neutron HA

## Deploy Neutron

Create nova database

    playback-neutron --user ubuntu --hosts controller1.maas create-neutron-db --root-db-pass changeme --neutron-db-pass changeme

Create service credentials

    playback-neutron --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --neutron-pass changeme --endpoint http://CONTROLLER_VIP:9696

Install Neutron for self-service

    playback-neutron --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme --populate
    playback-neutron --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme
    playback-neutron --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://neutron:NEUTRON_PASS@CONTROLLER_VIP/neutron --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-pass changeme --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --neutron-pass changeme --nova-url http://CONTROLLER_VIP:8774/v2 --nova-pass changeme --public-interface eth1 --local-ip MANAGEMENT_INTERFACE_IP --nova-metadata-ip CONTROLLER_VIP --metadata-proxy-shared-secret changeme-changeme-changeme-changeme

### Arguments

* --local-ip: the management interface ip of the current controller node

Using `playback-neutron --help` to see the details.