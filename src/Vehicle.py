"""
Vehicle Module - Refactored
"""

from abc import ABC, abstractmethod


class Vehicle(ABC):
    # Base class for all vehicles
    
    def __init__(self, registration_number, make, model, color):
        # Initialize vehicle with basic attributes
        self._registration_number = registration_number
        self._make = make
        self._model = model
        self._color = color
    
    # Properties
    @property
    def registration_number(self):
        return self._registration_number
    
    @property
    def make(self):
        return self._make
    
    @property
    def model(self):
        return self._model
    
    @property
    def color(self):
        return self._color
    
    @property
    def regnum(self):
        return self._registration_number
    
    @abstractmethod
    def get_type(self):
        # Must be implemented by subclasses
        pass

class Car(Vehicle):
    # Standard car - properly inherits from Vehicle
    
    def __init__(self, registration_number, make, model, color):
        super().__init__(registration_number, make, model, color)
    
    def get_type(self):
        return "Car"

class Motorcycle(Vehicle):
    # Motorcycle - properly inherits from Vehicle
    
    def __init__(self, registration_number, make, model, color):
        super().__init__(registration_number, make, model, color)
    
    def get_type(self):
        return "Motorcycle"

class ElectricVehicle(Vehicle):
    # Electric vehicle base class
    
    def __init__(self, registration_number, make, model, color, charge=0):
        super().__init__(registration_number, make, model, color)
        self._charge = charge
    
    @property
    def charge(self):
        return self._charge
    
    @charge.setter
    # Clamp between 0-100
    def charge(self, value):
        self._charge = max(0, min(100, value))  

class ElectricCar(ElectricVehicle):
    # Electric car 
    
    def __init__(self, registration_number, make, model, color):
        super().__init__(registration_number, make, model, color)  
    
    def get_type(self):
        return "Car"

class ElectricMotorcycle(ElectricVehicle):
    # Electric motorcycle
    
    def __init__(self, registration_number, make, model, color):
        super().__init__(registration_number, make, model, color)
    
    def get_type(self):
        return "Motorcycle"

class VehicleFactory:
    # Factory pattern - Centralizes vehicle creation logic
    
    @staticmethod
    def create_vehicle(registration_number, make, model, color, is_electric=False, is_motorcycle=False):
        """
        Create appropriate vehicle based on parameters
        
        Args:
            registration_number: Vehicle registration
            make: Manufacturer
            model: Model name
            color: Color
            is_electric: True for electric vehicles
            is_motorcycle: True for motorcycles
            
        Returns:
            Appropriate Vehicle subclass instance
        """
        if is_electric:
            if is_motorcycle:
                return ElectricMotorcycle(registration_number, make, model, color)
            else:
                return ElectricCar(registration_number, make, model, color)
        else:
            if is_motorcycle:
                return Motorcycle(registration_number, make, model, color)
            else:
                return Car(registration_number, make, model, color)