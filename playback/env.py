import argparse
import os
from playback import config
from fabric.api import *
from fabric.colors import red
import sys


parser = argparse.ArgumentParser()
parser.add_argument('--user', help='the target user', action='store', dest='user')
parser.add_argument('--hosts', help='the target address', action='store', dest='hosts')
subparsers = parser.add_subparsers(dest="subparser_name") 
prepare_host = subparsers.add_parser('prepare-host', help='prepare the OpenStack environment')
gen_pass = subparsers.add_parser('gen-pass', help='generate the password')
cmd = subparsers.add_parser('cmd', help='run command line on the target host')
cmd.add_argument('--run', help='the command running on the remote node',
                 action='store',
                 default=None,
                 dest='run')

args = parser.parse_args()



def main():
    if args.subparser_name == 'gen-pass':
        os.system('openssl rand -hex 10')
    if args.subparser_name == 'prepare-host':
        from playback import prepare_host
        try:
            remote = prepare_host.PrepareHost(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            print red('No hosts found. Please using --hosts param.')
            sys.exit(1)

        # host networking
        execute(remote.setup_external_interface)

        # ntp
        execute(remote.setup_ntp)

        # openstack packages
        execute(remote.set_openstack_repository)

    if args.subparser_name == 'cmd':
        from playback import cmd
        try:
            remote = cmd.Cmd(user=args.user, hosts=args.hosts.split(','))
        except AttributeError:
            print red('No hosts found. Please using --hosts param.')
            sys.exit(1)
        execute(remote.cmd, args.run)

if __name__ == '__main__':
    main()