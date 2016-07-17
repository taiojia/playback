# OpenStack Glance HA

## Deploy Glance

Create glance database

    glance-deploy --user ubuntu --hosts controller1.maas create-glance-db --root-db-pass changeme --glance-db-pass changeme

Create service credentials

    glance-deploy --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --glance-pass changeme --public-endpoint http://CONTROLLER_VIP:9292 --internal-endpoint http://CONTROLLER_VIP:9292 --admin-endpoint http://CONTROLLER_VIP:9292

Install glance on controller1.maas, controller2.maas and controller3.maas

    glance-deploy --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211 --populate
    glance-deploy --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211
    glance-deploy --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211

Using `glance-deploy --help` to see the details.