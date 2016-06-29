conf_external_interface = """# The external network interface
auto eth1
iface eth1 inet manual
up ip link set dev $IFACE up
down ip link set dev $IFACE down"""
