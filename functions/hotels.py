import yaml
import json
import uuid

def get_resort_hotels(resort_id):
    with open('data/hotels.yaml', 'r') as file:
        hotels = yaml.load(file, Loader=yaml.CLoader)
        hotels = filter(lambda x: x["resort_id"] == resort_id, hotels['hotels'])
        return json.dumps(list(hotels))

def booking_resort_hotels(booking):
    with open('data/bookings.yaml', 'r') as file:
        data = yaml.load(file, Loader=yaml.CLoader)

    booking["bookingId"] = str(uuid.uuid4())
    data["bookings"].append(booking)
    with open('data/bookings.yaml', 'w') as file:
        yaml.dump(data, file, allow_unicode=True)
    return json.dumps(booking)
