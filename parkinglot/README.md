# Entities

- ParkingLot
- PackingSpot
- Vehicle
- Ticket

# Operation 
- park_vehicle(vehicle) → returns a Ticket
- unpark_vehicle(ticket_id) → returns the fee charged
- get_free_spot_count(floor_id, spot_size) → returns an integer
- get_availability() → floor-by-floor free counts, for the display board at the entrance
