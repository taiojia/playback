# The external interface uses a special configuration without an IP address assigned to it. Configure the second interface as the external interface:

* Edit the `/etc/network/interfaces` file to contain the following contents. Replace `INTERFACE_NAME` with the actual interface name. For example, eth1 or eth2. 
    
        # The external network interface
        auto INTERFACE_NAME
        iface INTERFACE_NAME inet manual
                up ip link set dev $IFACE up
                down ip link set dev $IFACE down
                