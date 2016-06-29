# OpenStack Horizon HA

## Deploy Horizon

Install horizon on controller nodes

    horizon-deploy --user ubuntu --hosts controller1.maas,controller2.maas,controller3.maas install --openstack-host CONTROLLER_VIP  --memcached-servers controller1.maas:11211 --time-zone Asia/Shanghai

Using `horizon-deploy --help` to see the details.