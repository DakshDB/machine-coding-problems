from datetime import timedelta
from datetime import datetime
from models.enum import VehicleType
from models.models import Vehicle
from models.enum import SpotSize
from core.parkinglot import ParkingLotCore
from core.pricing import FlatRatePricing, SlabPricing, WeekendPricing

if __name__ == '__main__':
    print("Welcome to Parking Lot")

    parking_lot = ParkingLotCore()

    print("\nParking Lot Availability by Floor")
    print(parking_lot.get_availability())

    print("\nParking Lot Floor Availability - 1st Floor, Medium Spots")
    print(parking_lot.get_free_spots_count(0,SpotSize.MEDIUM))

    car1 = Vehicle("C1", VehicleType.CAR)
    car2 = Vehicle("C2", VehicleType.CAR)
    car3 = Vehicle("C3", VehicleType.CAR)
    
    ticket1 = parking_lot.park_vehicle(car1)
    print(f"Parked {ticket1.id} ")

    print("\nParking Lot Availability by Floor")
    print(parking_lot.get_availability())

    print("\nParking Lot Floor Availability - 1st Floor, Medium Spots")
    print(parking_lot.get_free_spots_count(0,SpotSize.MEDIUM))

    ticket2 = parking_lot.park_vehicle(car2)
    print(f"Parked {ticket2.id} ")

    print("\nParking Lot Availability by Floor")
    print(parking_lot.get_availability())

    exit_time = datetime.now() + timedelta(hours=9)

    fare = parking_lot.unpark_vehicle(ticket1.id, exit_time)
    print(f"\nFare for {ticket1.vehicle.licence_plate} is {fare}")

    print("\nParking Lot Availability by Floor")
    print(parking_lot.get_availability())

    fare = parking_lot.unpark_vehicle(ticket2.id)
    print(f"\nFare for {ticket2.vehicle.licence_plate} is {fare}")

    print("\nParking Lot Availability by Floor")
    print(parking_lot.get_availability())

    # the same lot, priced three different ways, with no change to parking or exit logic
    print("\nSwapping the pricing strategy")
    entry = datetime(2026, 9, 5, 10, 0, 0)      # a Saturday
    exit_at = entry + timedelta(hours=5)

    strategies = {
        "slab (default)": SlabPricing(),
        "flat 40/hour": FlatRatePricing(rate_per_hour=40),
        "weekend 1.5x on slab": WeekendPricing(SlabPricing(), multiplier=1.5),
    }

    for name, strategy in strategies.items():
        lot = ParkingLotCore(pricing=strategy)
        ticket = lot.park_vehicle(Vehicle("C9", VehicleType.CAR))
        ticket.entryTime = entry
        print(f"  {name:<22} 5h car -> {lot.unpark_vehicle(ticket.id, exit_at)}")
