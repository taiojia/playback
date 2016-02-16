# Playback
Playback is an OpenStack provisioning DevOps tool that all of the OpenStack components can be deployed automation with high availability on Ubuntu based operating system.

#### Requirement
The OpenStack bare metal hosts are in MAAS environment(recommend), and all hosts are two NICs at least(external and internal).

#### Install Playback
Use pip:

    pip install playback

Or form source:

    git clone https://github.com/jiasir/playback.git
    cd playback
    git checkout liberty
    sudo python setup.py install

#### Prepare environment
Prepare the OpenStack environment.
DO NOT setup eth1 in /etc/network/interfaces

    playback-env --prepare-host --user ubuntu --hosts os02.node,os03.node,os04.node,os05.node,os06.node,os07.node,os08.node,os09.node,os10.node,os11.node,os12.node,os13.node,os14.node,os15.node,os16.node,os18.node,os19.node

Reboot the target hosts to take effect:

    playback-env --cmd "reboot" --user ubuntu --hosts os02.node,os03.node,os04.node,os05.node,os06.node,os07.node,os08.node,os09.node,os10.node,os11.node,os12.node,os13.node,os14.node,os15.node,os16.node,os18.node,os19.node

#### MySQL HA
Deploy to os02.node

    playback-mysql --install --user ubuntu --hosts os02.node
    playback-mysql --config --user ubuntu --hosts os02.node --wsrep_cluster_address "gcomm://os02.node,os03.node" --wsrep_node_name="galera1" --wsrep_node_address="os02.node"

Deploy to os03.node

    playback-mysql --install --user ubuntu --hosts os03.node
    playback-mysql --config --user ubuntu --hosts os03.node --wsrep_cluster_address "gcomm://os02.node,os03.node" --wsrep_node_name="galera2" --wsrep_node_address="os03.node"

Start cluster

    playback-mysql --user ubuntu --hosts os02.maas --manage --wsrep-new-cluster
    playback-mysql --user ubuntu --hosts os03.maas --manage --start
    playback-mysql --user ubuntu --hosts os02.maas --manage --change-root-password changeme

#### HAProxy HA
Deploy to os04.node

    playback-haproxy --install --user ubuntu --hosts os04.node

Deploy to os05.node

    playback-haproxy --install --user ubuntu --hosts os05.node

Generate the HAProxy configuration and upload to target hosts(Do not forget to edit the generated configuration)

    playback-haproxy --gen-conf 
    playback-haproxy --config --upload-conf haproxy.cfg --user ubuntu --hosts os04.node,os05.node

Configure Keepalived

    playback-haproxy --config --configure-keepalived --router_id lb1 --priority 150 --state MASTER --interface eth0 --vip 10.0.0.3 --user ubuntu --hosts os04.node
    playback-haproxy --config --configure-keepalived --router_id lb2 --priority 100 --state SLAVE --interface eth0 --vip 10.0.0.3 --user ubuntu --hosts os05.node

#### RabbitMQ HA
Deploy to os02.node and os03.node

    playback-rabbitmq --install --user ubuntu --hosts os02.node,os03.node --erlang-cookie YXUNUSYXOKXUQUIJMPRY --rabbit-user guest --rabbit-pass guest
    
Create cluster

    playback-rabbitmq --user ubuntu --hosts os03.node --join-cluster rabbit@os02
