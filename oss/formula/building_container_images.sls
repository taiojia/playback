building container images:
  cmd.run:
    - name: |
        kolla-build -base ubuntu --registry os02.maas:4000 --push