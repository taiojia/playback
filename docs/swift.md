# OpenStack Swift Proxy HA

## Deploy OpenStack Swift Proxy

Create the Identity service credentials

    swift-deploy --user ubuntu --hosts controller1.maas create-service-credentials --os-password changeme --os-auth-url http://CONTROLLER_VIP:35357/v3 --swift-pass changeme --public-endpoint 'http://CONTROLLER_VIP:8080/v1/AUTH_%\(tenant_id\)s' --internal-endpoint 'http://CONTROLLER_VIP:8080/v1/AUTH_%\(tenant_id\)s' --admin-endpoint http://CONTROLLER_VIP:8080/v1

Install swift proxy

    swift-deploy --user ubuntu --hosts controller1.maas,controller2.maas,controller3.maas install --auth-uri http://CONTROLLER_VIP:5000 --auth-url http://CONTROLLER_VIP:35357 --swift-pass changeme --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas:11211

Using `swift-deploy --help` to see the details.