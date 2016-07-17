# Additional Settings

## Neutron

### Create the public provider network

    source admin-openrc.sh
    neutron net-create --shared --provider:physical_network provider --provider:network_type flat provider
    neutron subnet-create --name provider --allocation-pool start=192.168.0.10,end=192.168.0.254 --dns-nameserver 192.168.1.1 --gateway 192.168.0.1 provider 192.168.0.0/24

### Create the self service network

    source admin-openrc.sh
    neutron net-create selfservice
    neutron subnet-create --name selfservice --dns-nameserver 192.168.1.1 --gateway 172.16.1.1 selfservice 172.16.1.0/24

### Create a router

    source admin-openrc.sh
    neutron net-update provider --router:external
    neutron router-create router
    neutron router-interface-add router selfservice
    neutron router-gateway-set router provider

## Glance

### create image

    source admin-openrc.sh
    openstack image create "ubuntu1404" --file ubuntu-14.04-server-cloudimg-amd64-disk1.img --disk-format qcow2 --container-format bare --public
    openstack image create "ubuntu1604" --file ubuntu-16.04-server-cloudimg-amd64-disk1.img --disk-format qcow2 --container-format bare --public

If create image failed, you neet to restart `glance-api` service on controllers

## Horizon

### Redirect / to /horizon/

Edit `/etc/apache2/sites-enabled/000-default.conf` and add the following lines:

    <Directory /var/www/html>
        RedirectMatch 301 ^/$ /horizon/
    </Directory>

## Manila

### Create the service image for manila

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila.html

### Create shares with share servers management support

http://docs.openstack.org/mitaka/install-guide-ubuntu/launch-instance-manila-dhss-true-option2.html
