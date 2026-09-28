from models.enum import SpotSize
from models.enum import VehicleType


# Parking Lot Size
ParkingFloors = 1
SpotsEachFloor = {
    SpotSize.SMALL: 1,
    SpotSize.MEDIUM: 1,
    SpotSize.LARGE: 1
}



# Spot Compatibitiy
SpotCompatibility = {
    VehicleType.BIKE : [SpotSize.SMALL, SpotSize.MEDIUM, SpotSize.LARGE] ,
    VehicleType.CAR : [SpotSize.MEDIUM, SpotSize.LARGE] ,
    VehicleType.TRUCK : [SpotSize.LARGE] 
}

MinParkingHours = 2

# Pricing
Pricing = {
    VehicleType.BIKE: {
        "base_price": 20,
        "each_hour": 10,
        "daily_cap": 100,
    },
    VehicleType.CAR: {
        "base_price": 50,
        "each_hour": 30,
        "daily_cap": 300,
    },
    VehicleType.TRUCK: {
        "base_price": 100,
        "each_hour": 50,
        "daily_cap": 600,
    },
    
}