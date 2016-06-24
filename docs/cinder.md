# OpenStack Cinder HA

## Deploy Cinder

Create cinder database

    cinder-deploy --user ubuntu --hosts controller1.maas create-cinder-db --root-db-pass changeme --cinder-db-pass changeme

Create cinder service creadentials

    cinder-deploy --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --cinder-pass changeme --public-endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --internal-endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --admin-endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --public-endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s' --internal-endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s' --admin-endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s'

Install cinder-api and cinder-volume on controller nodes, the volume backend defaults to ceph (you must have ceph installed)

    cinder-deploy --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-user openstack --rabbit-pass changeme --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --populate
    cinder-deploy --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-user openstack --rabbit-pass changeme --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211
    cinder-deploy --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-user openstack --rabbit-pass changeme --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211

### Arguments

* --my-ip: the management interface ip of the current controller node

Using `cinder-deploy --help` to see the details.