install python clients requirements:
  pkg.installed:
    - pkgs:
      - python-dev
      - libffi-dev
      - libssl-dev
      - gcc
      - python-pip

install python clients:
  pip.installed:
    - name: python-openstackclient
    - upgrade: True
    - require:
      - pkg: install python clients requirements