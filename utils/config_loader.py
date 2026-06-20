import os
import yaml

_CONFIG = None

def load_config():
    global _CONFIG
    if _CONFIG is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        with open(config_path, 'r') as f:
            _CONFIG = yaml.safe_load(f)
    return _CONFIG

def get_setting(key, default=None):
    config = load_config()
    keys = key.split('.')
    data = config
    for k in keys:
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return default
    return data