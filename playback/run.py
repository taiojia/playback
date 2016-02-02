import argparse
import os
from playback import config
from playback import prepare_host
from fabric.api import *



config_file = config.Config('/etc/playback/playback.yaml')
conf = config_file.get_config()

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('--prepare-host', help='Prepare the OpenStack environment', action='store_true', default=False, dest='prepare')
group.add_argument('--gen-pass', help='Generate the password', action='store_true',default=False, dest='genpass')
parser.add_argument('--hosts', help='hosts which to apply', action='store', dest='hosts')
args = parser.parse_args()



def main():
    if args.genpass:
        os.system('openssl rand -hex 10')
    if args.prepare:
        from playback import prepare_host   
        remote = prepare_host.PrepareHost(user=conf['user'], hosts=args.hosts.split(','))
        #execute(remote.setup_external_interface)
        execute(remote.setup_ntp)

if __name__ == '__main__':
    main()