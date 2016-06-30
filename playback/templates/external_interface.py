conf_external_interface = """# The external network interface
auto {{ public_interface }}
iface {{ public_interface }} inet manual
up ip link set dev $IFACE up
down ip link set dev $IFACE down"""
