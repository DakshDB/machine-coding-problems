from datetime import datetime

from models.enum import SpotSize, VehicleType


class ParkingSpot:

    def __init__(self, id: str, size: SpotSize, floor_id: int, is_occupied: bool = False):
        self.id = id
        self.size = size
        self.floor_id = floor_id
        self.is_occupied = is_occupied


class Floor:

    def __init__(self, id: int):
        self.id = id
        self.free_spots: dict[SpotSize, set[ParkingSpot]] = {size: set() for size in SpotSize}

    def add_spot(self, spot: ParkingSpot):
        self.free_spots[spot.size].add(spot)

    def take(self, size: SpotSize) -> ParkingSpot | None:
        pool = self.free_spots[size]
        if not pool:
            return None

        spot = pool.pop()
        spot.is_occupied = True
        return spot

    def release(self, spot: ParkingSpot):
        spot.is_occupied = False
        self.free_spots[spot.size].add(spot)

    def free_count(self, size: SpotSize) -> int:
        return len(self.free_spots[size])

    def total_free(self) -> int:
        return sum(len(pool) for pool in self.free_spots.values())


class Vehicle:

    def __init__(self, licence_plate: str, vehicle_type: VehicleType):
        self.licence_plate: str = licence_plate
        self.vehicle_type: VehicleType = vehicle_type


class Ticket:

    def __init__(self, id: str, vehicle: Vehicle, parking_spot: ParkingSpot, entryTime: datetime):
        self.id: str = id
        self.vehicle: Vehicle = vehicle
        self.parking_spot: ParkingSpot = parking_spot
        self.entryTime: datetime = entryTime
