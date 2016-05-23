# OpenStack Glance HA

## Deploy Glance

Create glance database

    playback-glance --user ubuntu --hosts controller1.maas create-glance-db --root-db-pass changeme --glance-db-pass changeme

Create service credentials

    playback-glance --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --glance-pass changeme --endpoint http://CONTROLLER_VIP:9292

Install glance on controller1.maas, controller2.maas and controller3.maas

    playback-glance --user ubuntu --hosts controller1.maas install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme  --swift-store-auth-address http://CONTROLLER_VIP:5000/v2.0/ --populate
    playback-glance --user ubuntu --hosts controller2.maas install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme  --swift-store-auth-address http://CONTROLLER_VIP:5000/v2.0/
    playback-glance --user ubuntu --hosts controller3.maas install --connection mysql+pymysql://glance:GLANCE_PASS@CONTROLLER_VIP/glance --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --glance-pass changeme  --swift-store-auth-address http://CONTROLLER_VIP:5000/v2.0/

Using `playback-keystone --help` to see the details.