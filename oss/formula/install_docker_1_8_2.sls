install docker-engine 1.8.2 on ubuntu 14.04:
  cmd.run:
    - name: |
        wget -qO- https://get.docker.com/ | sed 's/docker-engine/docker-engine=1.8.2-0~trusty/' | sh
        wget -qO- https://get.docker.com/gpg | sudo apt-key add -
