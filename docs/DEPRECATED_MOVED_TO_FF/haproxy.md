# OpenStack HAProxy HA

HAProxy as the load balancer for OpenStack APIs and MySQL Master node. We are using 2 nodes to deploy the HAProxy with Keepalived.

## Deploy HAProxy

Deploy to haproxy1.maas

    haproxy-deploy --user ubuntu --hosts haproxy1.maas install

Deploy to haproxy2.maas

    haproxy-deploy --user ubuntu --hosts haproxy2.maas install

Generate the HAProxy configuration and upload to target hosts(Do not forget to edit the generated configuration: `haproxy.cfg`, the generated configruation is the example, you must change the IP address at last.)

    haproxy-deploy gen-conf
    haproxy-deploy --user ubuntu --hosts haproxy1.maas,haproxy2.maas config --upload-conf haproxy.cfg

Configure Keepalived, `haproxy1.maas` as master node and `haproxy2.maas` as slave node.

    haproxy-deploy --user ubuntu --hosts haproxy1.maas config --configure-keepalived --router_id lb1 --priority 150 --state MASTER --interface eth0 --vip CONTROLLER_VIP
    haproxy-deploy --user ubuntu --hosts haproxy2.maas config --configure-keepalived --router_id lb2 --priority 100 --state SLAVE --interface eth0 --vip CONTROLLER_VIP

Using `haproxy-deploy --help` to see the details.