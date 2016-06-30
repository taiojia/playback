import argparse
from fabric.api import *
from fabric.network import disconnect_all
from fabric.colors import red
import sys
from playback.cli import cli_description
from playback import __version__
from playback.templates.haproxy_cfg import conf_haproxy_cfg

def install(args):
    from playback import haproxy_install
    try:
        target = haproxy_install.HaproxyInstall(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError as e:
        sys.stderr.write(e.message)
        sys.exit(1)
    execute(target._install)

def config(args):
    from playback import haproxy_config
    try:
        target = haproxy_config.HaproxyConfig(user=args.user, hosts=args.hosts.split(','), key_filename=args.key_filename, password=args.password)
    except AttributeError:
        sys.stderr.write(red('No hosts found. Please using --hosts param.'))
        sys.exit(1)
    if args.upload_conf:
        execute(target._upload_conf, args.upload_conf)
    if args.configure_keepalived:
        execute(target._configure_keepalived, args.router_id, args.priority, 
                args.state, args.interface, args.vip)

def gen_conf():
    with open('haproxy.cfg', 'w') as f:
        f.write(conf_haproxy_cfg)

def parser():
    p = argparse.ArgumentParser(prog='haproxy-deploy', description=cli_description+'this command used for provision HAProxy')
    p.add_argument('-v', '--version', action='version', version=__version__)
    p.add_argument('--user', help='the target user', action='store', default='ubuntu', dest='user')
    p.add_argument('--hosts', help='the target address', action='store', dest='hosts')
    p.add_argument('-i', '--key-filename', help='referencing file paths to SSH key files to try when connecting', action='store', dest='key_filename', default=None)
    p.add_argument('--password', help='the password used by the SSH layer when connecting to remote hosts', action='store', dest='password', default=None)

    s = p.add_subparsers(dest="subparser_name") 

    def install_f(args):
        install(args)
    install_parser = s.add_parser('install', help='install HAProxy')
    install_parser.set_defaults(func=install_f)

    def config_f(args):
        config(args)
    config_parser = s.add_parser('config', help='configure HAProxy')
    config_parser.add_argument('--upload-conf', help='upload configuration file to the target host', 
                               action='store', default=False, dest='upload_conf')
    config_parser.add_argument('--configure-keepalived', help='configure keepalived', 
                               action='store_true', default=False, dest='configure_keepalived')
    config_parser.add_argument('--router_id', help='Keepalived router id e.g. lb1', 
                               action='store', default=False, dest='router_id')
    config_parser.add_argument('--priority', help='Keepalived priority e.g. 150', 
                               action='store', default=False, dest='priority')
    config_parser.add_argument('--state', help='Keepalived state e.g. MASTER', 
                               action='store', default=False, dest='state')
    config_parser.add_argument('--interface', help='Keepalived binding interface e.g. eth0', 
                               action='store', default=False, dest='interface')
    config_parser.add_argument('--vip', help='Keepalived virtual ip e.g. CONTROLLER_VIP', 
                               action='store', default=False, dest='vip')
    config_parser.set_defaults(func=config_f)

    def gen_conf_f(args):
        gen_conf()
    gen_conf_parser = s.add_parser('gen-conf', help='generate the example configuration to the current location')
    gen_conf_parser.set_defaults(func=gen_conf_f)

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
