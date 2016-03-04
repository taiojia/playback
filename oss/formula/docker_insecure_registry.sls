enable insecure registry for ubuntu:
  file.append:
    - name: /etc/default/docker
    - text: 'DOCKER_OPTS="--insecure-registry os02.maas:4000"'
  cmd.run:
    - name: |
        service docker restart
