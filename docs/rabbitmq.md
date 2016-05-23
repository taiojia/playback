# OpenStack RabbitMQ HA

## Deploy RabbitMQ

Deploy RabbitMQ to controller1.maas, controller2.maas and controller3.maas

    playback-rabbitmq --user ubuntu --hosts controller1.maas,controller2.maas,controller3.maas install --erlang-cookie changemechangeme --rabbit-user openstack --rabbit-pass changeme

Create the cluster, note that `controller2.maas` and `controller3.maas` can be access `controller1.maas` using hostname:`controller1`. RabbitMQ Cluster use the short hostname to access each other, hostnames of all cluster members must be resolvable from all cluster nodes. If you want to use To use FQDNs, see `RABBITMQ_USE_LONGNAME` in the [Configuration guide](https://www.rabbitmq.com/configure.html#define-environment-variables). 

    playback-rabbitmq --user ubuntu --hosts controller2.maas join-cluster --name rabbit@controller1
    playback-rabbitmq --user ubuntu --hosts controller3.maas join-cluster --name rabbit@controller1

Using `playback-rabbitmq --help` to see the details.