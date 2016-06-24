# OpenStack Keystone HA

## Deploy Keystone

Create keystone database

    keystone-deploy --user ubuntu --hosts controller1.maas create-keystone-db --root-db-pass changeme --keystone-db-pass changeme

Install keystone on controller1.maas, controller2.maas and controller3.maas. Note that you must specify the `CONTROLLER_VIP` for three controllers Virtual IP

    keystone-deploy --user ubuntu --hosts controller1.maas install --admin-token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas --populate
    keystone-deploy --user ubuntu --hosts controller2.maas install --admin-token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas
    keystone-deploy --user ubuntu --hosts controller3.maas install --admin-token changeme --connection mysql+pymysql://keystone:changeme@CONTROLLER_VIP/keystone --memcached-servers controller1.maas:11211,controller2.maas:11211,controller3.maas

Create the service entity and API endpoints

    keystone-deploy --user ubuntu --hosts controller1.maas create-entity-and-endpoint --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --public-endpoint http://CONTROLLER_VIP:5000/v3 --internal-endpoint http://CONTROLLER_VIP:5000/v3 --admin-endpoint http://CONTROLLER_vip:35357/v3

Create projects, users, and roles

    keystone-deploy --user ubuntu --hosts controller1.maas create-projects-users-roles --os-token changeme --os-url http://CONTROLLER_VIP:35357/v3 --admin-pass changeme --demo-pass changeme

(OPTION) you will need to create OpenStack client environment scripts
admin-openrc.sh

    export OS_PROJECT_DOMAIN_ID=default
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_NAME=admin
    export OS_TENANT_NAME=admin
    export OS_USERNAME=admin
    export OS_PASSWORD=changeme
    export OS_AUTH_URL=http://CONTROLLER_VIP:35357/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    export OS_AUTH_VERSION=3

demo-openrc.sh

    export OS_PROJECT_DOMAIN_ID=default
    export OS_USER_DOMAIN_ID=default
    export OS_PROJECT_NAME=demo
    export OS_TENANT_NAME=demo
    export OS_USERNAME=demo
    export OS_PASSWORD=changeme
    export OS_AUTH_URL=http://CONTROLLER_VIP:5000/v3
    export OS_IDENTITY_API_VERSION=3
    export OS_IMAGE_API_VERSION=2
    export OS_AUTH_VERSION=3

Using `keystone-deploy --help` to see the details.