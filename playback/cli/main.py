import sys

from playback import __version__ as VERSION

from cliff.app import App
from cliff.commandmanager import CommandManager


class Playback(App):

    def __init__(self):
        super(Playback, self).__init__(
            description='OpenStack provisioning and orchestration library with command-line tools',
            version=VERSION,
            command_manager=CommandManager('cliff.playback'),
            deferred_help=True
        )

    def initialize_playback(self, argv):
        self.LOG.debug('initialize_playback')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)


def main(argv=sys.argv[1:]):
    playback = Playback()
    return playback.run(argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
