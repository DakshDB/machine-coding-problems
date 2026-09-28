import math
from abc import ABC, abstractmethod
from datetime import datetime

from models import constants
from models.enum import VehicleType


class PricingStrategy(ABC):

    @abstractmethod
    def calculate_fare(self, vehicle_type: VehicleType, entry_time: datetime, exit_time: datetime) -> int:
        ...


class SlabPricing(PricingStrategy):
    """base price covers the first n hours, then per hour, capped per day"""

    def __init__(self, slabs=None, base_hours=None):
        self.slabs = slabs if slabs is not None else constants.Pricing
        self.base_hours = base_hours if base_hours is not None else constants.MinParkingHours

    def calculate_fare(self, vehicle_type, entry_time, exit_time) -> int:
        pricing = self.slabs[vehicle_type]
        time_parked = exit_time - entry_time
        charge_hours = math.ceil(time_parked.total_seconds() / 3600)

        base_price = pricing['base_price']
        fare = base_price

        if charge_hours > self.base_hours:
            charge_hours -= self.base_hours

            daily_cap = pricing['daily_cap']
            days = math.floor(charge_hours / 24)
            charge_hours = charge_hours - (days * 24)
            fare += days * daily_cap

            daily_cap_hours = math.ceil((daily_cap - base_price) / pricing['each_hour'])
            if charge_hours >= daily_cap_hours:
                fare += (daily_cap - base_price)
            else:
                fare += charge_hours * pricing['each_hour']

        return fare


class FlatRatePricing(PricingStrategy):
    """one rate per hour, same for every vehicle"""

    def __init__(self, rate_per_hour: int):
        self.rate_per_hour = rate_per_hour

    def calculate_fare(self, vehicle_type, entry_time, exit_time) -> int:
        charge_hours = math.ceil((exit_time - entry_time).total_seconds() / 3600)
        return max(charge_hours, 1) * self.rate_per_hour


class WeekendPricing(PricingStrategy):
    """wraps any other strategy and applies a multiplier on weekends"""

    def __init__(self, base_strategy: PricingStrategy, multiplier: float = 1.5):
        self.base_strategy = base_strategy
        self.multiplier = multiplier

    def calculate_fare(self, vehicle_type, entry_time, exit_time) -> int:
        fare = self.base_strategy.calculate_fare(vehicle_type, entry_time, exit_time)
        if entry_time.weekday() >= 5:
            fare = round(fare * self.multiplier)
        return fare
