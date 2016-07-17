# OpenStack MySQL HA

We are using Galera Cluster for MySQL to build the MySQL Cluster on controller1/2/3.maas. The HAProxy will forward the requests to MySQL.
controller1.maas as the master node, and others as the slave.

## Deploy MySQL

Deploy to controller1.maas.

    mysql-deploy --user ubuntu --hosts controller1.maas install
    mysql-deploy --user ubuntu --hosts controller1.maas config \
    --wsrep-cluster-address "gcomm://controller1.maas,controller2.maas,controller3.maas" \
    --wsrep-node-name="galera1" \
    --wsrep-node-address="controller1.maas"

Deploy to controller2.maas.

    mysql-deploy --user ubuntu --hosts controller2.maas install
    mysql-deploy --user ubuntu --hosts controller2.maas config \
    --wsrep-cluster-address "gcomm://controller1.maas,controller2.maas,controller3.maas" \
    --wsrep-node-name="galera2" \
    --wsrep-node-address="controller2.maas"

Deploy to controller3.maas.

    mysql-deploy --user ubuntu --hosts controller3.maas install
    mysql-deploy --user ubuntu --hosts controller3.maas config \
    --wsrep-cluster-address "gcomm://controller1.maas,controller2.maas,controller3.maas" \
    --wsrep-node-name="galera3" \
    --wsrep-node-address="controller3.maas"

Start the cluster.

    mysql-deploy --user ubuntu --hosts controller1.maas manage --wsrep-new-cluster
    mysql-deploy --user ubuntu --hosts controller2.maas manage --start
    mysql-deploy --user ubuntu --hosts controller3.maas manage --start
    mysql-deploy --user ubuntu --hosts controller1.maas manage --change-root-password changeme

Show the cluster status.

    mysql-deploy --user ubuntu --hosts controller1.maas manage --show-cluster-status --root-db-pass changeme

For more information about [testing cluster](http://galeracluster.com/documentation-webpages/testingcluster.html)

Using `mysql-deploy --help` to see the details.
