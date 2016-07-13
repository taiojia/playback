# OpenStack Manila HA

## Deploy Manila

Create manila database and service credentials

    manila-deploy --user ubuntu --hosts controller1.maas create-manila-db --root-db-pass CHANGEME --manila-db-pass CHANGEME
    manila-deploy --user ubuntu --hosts controller1.maas create-service-credentials --os-password CHANGEME --os-auth-url http://CONTROLLER_VIP:35357/v3 --manila-pass CHANGEME --public-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --internal-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --admin-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --public-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s" --internal-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s" --admin-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s"

Install manila on controller1.maas, controller2.maas and controller3.maas

    manila-deploy --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass CHANGEME --populate
    manila-deploy --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass CHANGEME
    manila-deploy --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass CHANGEME

Install manila share on controller1.maas, controller2.maas and controller3.maas

    manila-share-deploy --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME
    manila-share-deploy --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME
    manila-share-deploy --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip MANAGEMENT_IP --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME

Create the service image for manila

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila.html

Create shares with share servers management support

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila-dhss-true-option2.html

### Arguments

* --my-ip: the management interface ip of the current controller node

Using `manila-deploy --help` and `manila-share-deploy --help`to see the details.