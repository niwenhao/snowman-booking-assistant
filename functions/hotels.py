import yaml
import json

def get_resort_hotels(resort_id):
    with open('data/hotels.yaml', 'r') as file:
        hotels = yaml.load(file, Loader=yaml.CLoader)
        hotels = filter(lambda x: x["resort_id"] == resort_id, hotels['hotels'])
        return json.dumps(list(hotels))
