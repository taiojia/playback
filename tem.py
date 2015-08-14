__author__ = 'Taio'

import playback

conf = playback.config.Config()

print conf.load_conf()['VIP_DB']
