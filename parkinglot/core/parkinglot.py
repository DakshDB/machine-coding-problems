from datetime import datetime
from uuid import uuid4

from core.pricing import PricingStrategy, SlabPricing
from models import constants
from models.enum import SpotSize
from models.models import Floor, ParkingSpot, Ticket, Vehicle


class ParkingLotCore:

    def __init__(self, pricing: PricingStrategy = None):
        self.pricing = pricing if pricing is not None else SlabPricing()
        self.tickets: dict[str, Ticket] = {}
        self.floors: dict[int, Floor] = {}

        for floor_id in range(0, constants.ParkingFloors):
            floor = Floor(id=floor_id)
            for spot_size, spots_each_floor in constants.SpotsEachFloor.items():
                for _ in range(0, spots_each_floor):
                    floor.add_spot(ParkingSpot(id=str(uuid4()), size=spot_size, floor_id=floor_id))
            self.floors[floor_id] = floor

    def park_vehicle(self, vehicle: Vehicle) -> Ticket:
        park_spot = self._allocate_spot(vehicle)

        if park_spot is None:
            raise Exception("Parking Spot Not Found")

        ticket = Ticket(
            id=str(uuid4()),
            vehicle=vehicle,
            parking_spot=park_spot,
            entryTime=datetime.now()
        )
        self.tickets[ticket.id] = ticket

        return ticket

    def _allocate_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        compatible_sizes = constants.SpotCompatibility[vehicle.vehicle_type]

        for size in compatible_sizes:
            for floor in self.floors.values():
                spot = floor.take(size)
                if spot is not None:
                    return spot

        return None

    def unpark_vehicle(self, ticket_id, exit_time=None) -> int:
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise Exception("Ticket Not found")

        self.tickets.pop(ticket_id)
        self.floors[ticket.parking_spot.floor_id].release(ticket.parking_spot)

        if exit_time is None:
            exit_time = datetime.now()

        return self.pricing.calculate_fare(ticket.vehicle.vehicle_type, ticket.entryTime, exit_time)

    def get_free_spots_count(self, floor_id, spot_size: SpotSize) -> int:
        return self.floors[floor_id].free_count(spot_size)

    def get_availability(self) -> dict:
        return {f"Floor {floor_id}": floor.total_free() for floor_id, floor in self.floors.items()}
