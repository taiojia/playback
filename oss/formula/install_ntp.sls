set the time zone to shanghai:
  cmd.run:
    - name: |
        echo 'Asia/Shanghai' > /etc/timezone
        cat /usr/share/zoneinfo/Asia/Shanghai | tee /etc/localtime

install ntp:
  pkg.installed:
    - name: ntp
    - require:
      - cmd: set the time zone to shanghai