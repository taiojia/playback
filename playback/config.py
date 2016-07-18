import yaml

class Config(object):
    """
    Parse the playback configuration
    """
    def __init__(self, path):
        self.path = path

    def get_config(self):
        """
        Read config file
        
        :returns: the configuration of path to the dict or list
        """
        with open(self.path) as f:
            return yaml.safe_load(f)

