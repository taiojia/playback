import argparse
import os
from playback import config
from fabric.api import *
from fabric.colors import red


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()

group.add_argument('--prepare-host', help='Prepare the OpenStack environment', action='store_true', default=False, dest='prepare')
group.add_argument('--gen-pass', help='Generate the password', action='store_true',default=False, dest='genpass')
group.add_argument('--cmd', help='Run command line on the target host', action='store', dest='cmd')
parser.add_argument('--user', help='The target user', action='store', dest='user')
parser.add_argument('--hosts', help='The target address', action='store', dest='hosts')
args = parser.parse_args()



def main():
    if args.genpass:
        os.system('openssl rand -hex 10')
    if args.prepare:
        from playback import prepare_host
        try:
            remote = prepare_host.PrepareHost(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            print red('No hosts found. Please using --hosts param.')

        # host networking
        execute(remote.setup_external_interface)

        # ntp
        execute(remote.setup_ntp)

        # openstack packages
        execute(remote.set_openstack_repository)

    if args.cmd:
        from playback import cmd
        try:
            remote = cmd.Cmd(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            print red('No hosts found. Please using --hosts param.')
        execute(remote.cmd, args.cmd)

if __name__ == '__main__':
    main()