import yaml
import json

def get_resorts():
    with open('data/resorts.yaml', 'r') as file:
        resorts = yaml.load(file, Loader=yaml.CLoader)

        return json.dumps(resorts['data'])