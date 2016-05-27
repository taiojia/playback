def main():
    p = parser()
    args = p.parse_args()
    if not hasattr(args, 'func'):
        p.print_help()
    else:
        # XXX on Python 3.3 we get 'args has no func' rather than short help.
        try:
            args.func(args)
            return 0
        except WheelError as e:
            sys.stderr.write(e.message + "\n")
    return 1
    