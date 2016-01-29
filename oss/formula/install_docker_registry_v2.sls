install docker registry v2:
  cmd.run:
    - name: |
        docker run -d -p 4000:5000 --restart=always --name registry registry:2
