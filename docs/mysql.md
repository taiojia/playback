#### MySQL HA
We are using Galera Cluster for MySQL to build the MySQL Cluster on controller1/2/3.maas. The HAProxy will forward the requests to MySQL.
controller1.maas as the master node, and others as the slave.

Deploy to controller1.maas.
```bash
playback-mysql --user ubuntu --hosts controller1.maas install 
playback-mysql --user ubuntu --hosts controller1.maas config \
--wsrep-cluster-address "gcomm://controller1.maas,controller2.maas,controller3.maas" \
--wsrep-node-name="galera1" \
--wsrep-node-address="controller1.maas"
```

Deploy to controller2.maas.
```bash
playback-mysql --user ubuntu --hosts controller2.maas install 
playback-mysql --user ubuntu --hosts controller2.maas config \
--wsrep-cluster-address "gcomm://controller1.maas,controller2.maas,controller3.maas" \
--wsrep-node-name="galera2" \
--wsrep-node-address="controller2.maas"
```

Deploy to controller3.maas.
```
playback-mysql --user ubuntu --hosts controller3.maas install 
playback-mysql --user ubuntu --hosts controller3.maas config \
--wsrep-cluster-address "gcomm://controller1.maas,controller2.maas,controller3.maas" \
--wsrep-node-name="galera3" \
--wsrep-node-address="controller3.maas"
```

Start the cluster.
```
playback-mysql --user ubuntu --hosts controller1.maas manage --wsrep-new-cluster
playback-mysql --user ubuntu --hosts controller2.maas manage --start
playback-mysql --user ubuntu --hosts controller3.maas manage --start
playback-mysql --user ubuntu --hosts controller1.maas manage --change-root-password changeme
```

Using `playback-mysql --help` to see the details.
