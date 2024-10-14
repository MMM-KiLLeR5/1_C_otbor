import json
import os

DISHES_FILE = 'dishes.json'
CONSUMPTION_FILE = 'consumption.json'

class DataManager:
    def load_dishes(self):
        if os.path.exists(DISHES_FILE):
            with open(DISHES_FILE, 'r') as f:
                dishes = json.load(f)
        else:
            dishes = {}
        return dishes

    def save_dishes(self, dishes):
        with open(DISHES_FILE, 'w') as f:
            json.dump(dishes, f)

    def load_consumption_logs(self):
        if os.path.exists(CONSUMPTION_FILE):
            with open(CONSUMPTION_FILE, 'r') as f:
                consumption_logs = json.load(f)
        else:
            consumption_logs = []
        return consumption_logs

    def save_consumption_logs(self, consumption_logs):
        with open(CONSUMPTION_FILE, 'w') as f:
            json.dump(consumption_logs, f)
