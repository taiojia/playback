__author__ = 'Taio'

import playback

conf = playback.config.Config()

ha = playback.haproxy.Haproxy()
for i in ha.host_string():
    print i



