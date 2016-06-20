conf_keepalived_conf = """global_defs {
  router_id {{ router_id }}
}
vrrp_script haproxy {
  script "killall -0 haproxy"
  interval 2
}
vrrp_instance 50 {
  virtual_router_id 50
  advert_int 1
  priority {{ priority }}
  state {{ state }}
  interface {{ interface }}
  virtual_ipaddress {
    {{ vip }} dev {{ interface }}
  }
  track_script {
    haproxy
  }
}"""
