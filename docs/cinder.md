# OpenStack Cinder HA

## Deploy Cinder

Create cinder database

    playback-cinder --user ubuntu --hosts controller1.maas create-cinder-db --root-db-pass changeme --cinder-db-pass changeme

Create cinder service creadentials

    playback-cinder --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --cinder-pass changeme --endpoint-v1 'http://CONTROLLER_VIP:8776/v1/%\(tenant_id\)s' --endpoint-v2 'http://CONTROLLER_VIP:8776/v2/%\(tenant_id\)s'

Install cinder-api and cinder-volume on controller nodes, the volume backend defaults to ceph (you must have ceph installed)

    playback-cinder --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-pass changeme --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme --populate
    playback-cinder --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-pass changeme --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme
    playback-cinder --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://cinder:CINDER_PASS@CONTROLLER_VIP/cinder --rabbit-pass changeme --rabbit-hosts controller1.maas,controller2.maas,controller3.maas --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --cinder-pass changeme --my-ip MANAGEMENT_INTERFACE_IP --glance-api-servers http://CONTROLLER_VIP:9292 --rbd-secret-uuid changeme-changeme-changeme-changeme

### Arguments

* --my-ip: the management interface ip of the current controller node

Using `playback-cinder --help` to see the details.