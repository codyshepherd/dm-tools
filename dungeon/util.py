import yaml

COUNT = 0

def get_yaml(yaml_file, field):
    with open(yaml_file, 'r') as fh:
        y = yaml.safe_load(fh)
        return y[field]

def global_count() -> int:
    global COUNT
    to_return = COUNT
    COUNT += 1
    return to_return
