import argparse
import os
from playback import config
from fabric.api import *
from fabric.colors import red
from fabric.network import disconnect_all
import sys
from playback.cli import cli_description
from playback import __version__

def prepare_host(user, hosts, key_filename, password, public_interface):
    from playback.api import PrepareHost
    try:
        remote = PrepareHost(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)

    # host networking
    remote.setup_external_interface(public_interface)

    # ntp
    remote.setup_ntp()

    # openstack packages
    remote.set_openstack_repository()

def gen_pass():
    os.system('openssl rand -hex 10')
    
def cmd(user, hosts, key_filename, password, run):
    from playback.api import Cmd
    try:
        remote = Cmd(user, hosts, key_filename, password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    remote.cmd(run)
     
def parser():
    p = argparse.ArgumentParser(prog='env-deploy', description=cli_description+'this command used for provision OpenStack basic environments')
    p.add_argument('-v', '--version', action='version', version=__version__)
    p.add_argument('--user', help='the target user', action='store', dest='user')
    p.add_argument('--hosts', help='the target address', action='store', dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)
   
    s = p.add_subparsers(dest="subparser_name", help="commands")
    
    def prepare_host_f(args):
        prepare_host(args.user, args.hosts.split(','), args.key_filename, args.password, args.public_interface)
    prepare_host_parser = s.add_parser('prepare-host', help='prepare the OpenStack environment')
    prepare_host_parser.add_argument('--public-interface', help='public interface e.g. eth1', action='store', default='eth1', dest='public_interface')
    prepare_host_parser.set_defaults(func=prepare_host_f)
    
    def gen_pass_f(args):
        gen_pass()
    gen_pass_parser = s.add_parser('gen-pass', help='generate the password')
    gen_pass_parser.set_defaults(func=gen_pass_f)
    
    def cmd_f(args):
        cmd(args.user, args.hosts.split(','), args.key_filename, args.password, args.run)
    cmd_parser = s.add_parser('cmd', help='run command line on the target host')
    cmd_parser.add_argument('--run', help='the command running on the remote node', action='store', default=None, dest='run')
    cmd_parser.set_defaults(func=cmd_f)
    
    return p

def main():
    p = parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
    else:
        # XXX on Python 3.3 we get 'args has no func' rather than short help.
        try:
            args.func(args)
            disconnect_all()
            return 0
        except Exception as e:
            sys.stderr.write(e.message)
            sys.exit(1)
    return 1
    
if __name__ == '__main__':
    main()
