# OpenStack Horizon HA

## Deploy Horizon

Install horizon on controller nodes

    playback-horizon --user ubuntu --hosts controller1.maas,controller2.maas,controller3.maas install --openstack-host CONTROLLER_VIP  --memcache controller1.maas:11211 --time-zone Asia/Shanghai

Using `playback-horizon --help` to see the details.