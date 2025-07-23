from datetime import datetime
import random

class Utils:

    @staticmethod
    def current_date() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def current_time() -> str:
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def get_current_datetime() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def generate_random_int(min_value, max_value):
        if min_value > max_value:
          raise Exception("minimum must be below maximum")
        return random.randint(min_value, max_value)

    @staticmethod
    def generate_random_float(min_value: float, max_value: float) -> float:
        if min_value > max_value:
          raise Exception("minimum must be below maximum")
        return random.uniform(min_value, max_value)

