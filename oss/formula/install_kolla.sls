clone kolla repo:
  git.latest:
    - name: https://git.openstack.org/openstack/kolla
    - target: /opt/kolla
    - rev: stable/liberty
    - force_clone: True

install pbr:
  pip.installed:
    - name: pbr
    - upgrade: True
 
install kolla:
  cmd.run:
    - name: |
        pip install kolla/
    - cwd: /opt
    - require:
      - git: clone kolla repo
      - pip: install pbr

copy kolla configuration:
  cmd.run:
    - name: |
        cp -r cp -r kolla/etc/kolla /etc/
    - cwd: /opt
