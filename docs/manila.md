# OpenStack Manila HA

## Deploy Manila

Create manila database and service credentials

    manila-deploy --user ubuntu --hosts CONTROLLER1 create-manila-db --root-db-pass CHANGEME --manila-db-pass CHANGEME
    manila-deploy --user ubuntu --hosts CONTROLLER1 create-service-credentials --os-password CHANGEME --os-auth-url http://CONTROLLER_VIP:35357/v3 --manila-pass CHANGEME --public-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --internal-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --admin-endpoint-v1 "http://CONTROLLER_VIP:8786/v1/%\(tenant_id\)s" --public-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s" --internal-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s" --admin-endpoint-v2 "http://CONTROLLER_VIP:8786/v2/%\(tenant_id\)s"

Install manila on CONTROLLER1 and CONTROLLER2

    manila-deploy --user ubuntu --hosts CONTROLLER1 install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER1 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211,CONTROLLER3:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2,CONTROLLER3 --rabbit-user openstack --rabbit-pass CHANGEME --populate
    manila-deploy --user ubuntu --hosts CONTROLLER2 install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER2 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211,CONTROLLER3:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2,CONTROLLER3 --rabbit-user openstack --rabbit-pass CHANGEME
    manila-deploy --user ubuntu --hosts CONTROLLER3 install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER3 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211,CONTROLLER3:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2,CONTROLLER3 --rabbit-user openstack --rabbit-pass CHANGEME

Install manila share on CONTROLLER1 and CONTROLLER2

    manila-share-deploy --user ubuntu --hosts CONTROLLER1 install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER1 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211,CONTROLLER3:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2,CONTROLLER3 --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME
    manila-share-deploy --user ubuntu --hosts CONTROLLER2 install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER2 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211,CONTROLLER3:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2,CONTROLLER3 --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME
    manila-share-deploy --user ubuntu --hosts CONTROLLER3 install --connection mysql+pymysql://manila:CHANGEME@CONTROLLER_VIP/manila --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --manila-pass CHANGEME --my-ip CONTROLLER2 --memcached-servers CONTROLLER1:11211,CONTROLLER2:11211,CONTROLLER3:11211 --rabbit-hosts CONTROLLER1,CONTROLLER2,CONTROLLER3 --rabbit-user openstack --rabbit-pass CHANGEME --neutron-endpoint http://CONTROLLER_VIP:9696 --neutron-pass CHANGEME --nova-pass CHANGEME --cinder-pass CHANGEME

Create the service image for manila

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila.html

Create shares with share servers management support

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila-dhss-true-option2.html

### Arguments

* --my-ip: the management interface ip of the current controller node

Using `manila-deploy --help` and `manila-share-deploy --help`to see the details.