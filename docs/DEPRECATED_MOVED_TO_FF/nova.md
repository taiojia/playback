# OpenStack Nova HA

## Deploy Nova

Create nova database

    nova-deploy --user ubuntu --hosts controller1.maas create-nova-db --root-db-pass changeme --nova-db-pass changeme

Create service credentials

    nova-deploy --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --nova-pass changeme --public-endpoint 'http://CONTROLLER_VIP:8774/v2.1/%\(tenant_id\)s' --internal-endpoint 'http://CONTROLLER_VIP:8774/v2.1/%\(tenant_id\)s' --admin-endpoint 'http://CONTROLLER_VIP:8774/v2.1/%\(tenant_id\)s'

Install nova on controller1.maas

    nova-deploy --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --api-connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass changeme --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme --populate

Install nova on controller2.maas

    nova-deploy --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --api-connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controler3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass changeme --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme

Install nova on controller3.maas

    nova-deploy --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova --api-connection mysql+pymysql://nova:NOVA_PASS@CONTROLLER_VIP/nova_api --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --nova-pass changeme --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controler3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass changeme --glance-api-servers http://CONTROLLER_VIP:9292 --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass changeme --metadata-proxy-shared-secret changeme

### Arguments

* --my-ip: the management interface ip of the current nova controller node

Using `nova-deploy --help` to see the details.
