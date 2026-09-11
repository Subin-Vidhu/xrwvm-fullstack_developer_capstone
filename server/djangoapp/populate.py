import json
import os
from django.conf import settings
from .models import CarMake, CarModel


def initiate():
    json_path = os.path.join(
        settings.BASE_DIR, 'database', 'data', 'car_records.json'
    )

    with open(json_path, 'r') as f:
        car_data = json.load(f)

    # car_records.json is a list of car dicts (make, model, bodyType, year, dealer_id, mileage)
    cars = car_data if isinstance(car_data, list) else car_data.get('cars', [])

    make_cache = {}

    for car in cars:
        make_name = car['make']

        if make_name not in make_cache:
            car_make, _ = CarMake.objects.get_or_create(
                name=make_name,
                defaults={"description": f"{make_name} vehicles"}
            )
            make_cache[make_name] = car_make

        car_make = make_cache[make_name]

        # Normalize bodyType (e.g. "SUV", "Sedan") to match model's CAR_TYPES choices
        body_type = car.get('bodyType', 'SUV').upper()
        valid_types = [choice[0] for choice in CarModel.CAR_TYPES]
        if body_type not in valid_types:
            body_type = 'SUV'

        year = car.get('year', 2023)
        year = max(2015, min(2023, year))  # clamp to valid range

        CarModel.objects.get_or_create(
            car_make=car_make,
            name=car['model'],
            defaults={"type": body_type, "year": year}
        )