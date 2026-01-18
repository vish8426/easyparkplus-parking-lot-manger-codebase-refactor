"""
Parking Lot Manager - Refactored
Major Improvements:
1. STRATEGY PATTERN - Different parking strategies for regular vs EV vehicles
2. OBSERVER PATTERN - Decoupled GUI from business logic
3. Removed all anti-patterns (magic numbers, code duplication, global variables, etc.)
    a. Information outlined in accompanying system optimisation outline documentation
"""

import tkinter as tk
from tkinter import messagebox
from Vehicle import Vehicle, ElectricVehicle, VehicleFactory
from abc import ABC, abstractmethod
from typing import List, Optional
from enum import Enum


# Constants
EMPTY_SLOT = None 


# Strategy pattern 

class ParkingStrategy(ABC):
    """
    Strategy interface for parking operations
    Allows different algorithms for regular vs EV parking
    """
    
    @abstractmethod
    def can_park(self, vehicle, occupied_count, capacity):
        # Check if vehicle can be parked
        pass
    
    @abstractmethod
    def find_empty_slot(self, slots):
        # Find first available slot
        pass

class StandardParkingStrategy(ParkingStrategy):
    # Strategy for regular (non-electric) vehicles
    
    def can_park(self, vehicle, occupied_count, capacity):
        # Regular vehicles need regular slots
        return not isinstance(vehicle, ElectricVehicle) and occupied_count < capacity
    
    def find_empty_slot(self, slots):
        # Find first none slot
        for index, slot in enumerate(slots):
            if slot is EMPTY_SLOT:
                return index
        return -1

class EVParkingStrategy(ParkingStrategy):
    # Strategy for electric vehicles - requires charging stations
    
    def can_park(self, vehicle, occupied_count, capacity):
        # Only electric vehicles in EV slots
        return isinstance(vehicle, ElectricVehicle) and occupied_count < capacity
    
    def find_empty_slot(self, slots):
        # Find first none slot
        for index, slot in enumerate(slots):
            if slot is EMPTY_SLOT:
                return index
        return -1


# Observer pattern - For GUI updates

class ParkingEventType(Enum):
    # Types of events that can occur in parking lot
    LOT_CREATED = "lot_created"
    VEHICLE_PARKED = "vehicle_parked"
    VEHICLE_REMOVED = "vehicle_removed"
    PARKING_FAILED = "parking_failed"
    REMOVAL_FAILED = "removal_failed"

class ParkingObserver(ABC):
    # Observer interface - observers react to parking lot events
    
    @abstractmethod
    def update(self, event_type, message):
        # Called when parking lot state changes
        pass

class GUIObserver(ParkingObserver):
    # Concrete observer that updates the GUI
    
    def __init__(self, text_widget):
        self.text_widget = text_widget
    
    def update(self, event_type, message):
        # Display message in GUI with color coding
        if event_type == ParkingEventType.LOT_CREATED:
            self._insert_colored("SUCCESS " + message + "\n", "green")
        elif event_type == ParkingEventType.VEHICLE_PARKED:
            self._insert_colored("SUCCESS " + message + "\n", "blue")
        elif event_type == ParkingEventType.VEHICLE_REMOVED:
            self._insert_colored("SUCCESS " + message + "\n", "purple")
        elif event_type in [ParkingEventType.PARKING_FAILED, ParkingEventType.REMOVAL_FAILED]:
            self._insert_colored("FAILED " + message + "\n", "red")
        else:
            self.text_widget.insert(tk.INSERT, message + "\n")

        # Auto-scroll
        self.text_widget.see(tk.END)  
    
    def _insert_colored(self, text, color):
        # Insert colored text
        tag_name = f"color_{color}"
        self.text_widget.tag_config(tag_name, foreground=color)
        self.text_widget.insert(tk.INSERT, text, tag_name)
    
    def display_status(self, regular_vehicles, ev_vehicles, level):
        # Display formatted status table
        # Regular vehicles
        self.text_widget.insert(tk.INSERT, "\n" + "="*70 + "\n")
        self.text_widget.insert(tk.INSERT, "REGULAR VEHICLES\n")
        self.text_widget.insert(tk.INSERT, "="*70 + "\n")
        self.text_widget.insert(tk.INSERT, f"{'Slot':<6}{'Floor':<8}{'Reg No.':<15}{'Color':<12}{'Make':<12}{'Model'}\n")
        self.text_widget.insert(tk.INSERT, "-"*70 + "\n")
        
        if not regular_vehicles:
            self.text_widget.insert(tk.INSERT, "  (No vehicles parked)\n")
        else:
            for slot_num, vehicle in regular_vehicles:
                line = f"{slot_num:<6}{level:<8}{vehicle.regnum:<15}{vehicle.color:<12}{vehicle.make:<12}{vehicle.model}\n"
                self.text_widget.insert(tk.INSERT, line)
        
        # EV vehicles
        self.text_widget.insert(tk.INSERT, "\n" + "="*70 + "\n")
        self.text_widget.insert(tk.INSERT, "ELECTRIC VEHICLES\n")
        self.text_widget.insert(tk.INSERT, "="*70 + "\n")
        self.text_widget.insert(tk.INSERT, f"{'Slot':<6}{'Floor':<8}{'Reg No.':<15}{'Color':<12}{'Make':<12}{'Model'}\n")
        self.text_widget.insert(tk.INSERT, "-"*70 + "\n")
        
        if not ev_vehicles:
            self.text_widget.insert(tk.INSERT, "  (No electric vehicles parked)\n")
        else:
            for slot_num, vehicle in ev_vehicles:
                line = f"{slot_num:<6}{level:<8}{vehicle.regnum:<15}{vehicle.color:<12}{vehicle.make:<12}{vehicle.model}\n"
                self.text_widget.insert(tk.INSERT, line)
        
        self.text_widget.insert(tk.INSERT, "="*70 + "\n\n")
        self.text_widget.see(tk.END)
    
    def display_charge_status(self, ev_vehicles, level):
        # Display EV charge levels
        self.text_widget.insert(tk.INSERT, "\n" + "="*60 + "\n")
        self.text_widget.insert(tk.INSERT, "EV CHARGE LEVELS\n")
        self.text_widget.insert(tk.INSERT, "="*60 + "\n")
        self.text_widget.insert(tk.INSERT, f"{'Slot':<6}{'Floor':<8}{'Reg No.':<15}{'Charge %'}\n")
        self.text_widget.insert(tk.INSERT, "-"*60 + "\n")
        
        if not ev_vehicles:
            self.text_widget.insert(tk.INSERT, "  (No electric vehicles parked)\n")
        else:
            for slot_num, vehicle in ev_vehicles:
                charge = vehicle.charge if hasattr(vehicle, 'charge') else 0
                line = f"{slot_num:<6}{level:<8}{vehicle.regnum:<15}{charge}%\n"
                
                # Color code by charge level
                if charge < 20:
                    self._insert_colored(line, "red")
                elif charge < 50:
                    self._insert_colored(line, "orange")
                else:
                    self._insert_colored(line, "green")
        
        self.text_widget.insert(tk.INSERT, "="*60 + "\n\n")
        self.text_widget.see(tk.END)


# Business Logic - Separated from GUI

class ParkingLot:
    # Core parking lot business logic
    
    def __init__(self):
        # Initialize parking lot with strategies
        self.level = 0
        self.regular_capacity = 0
        self.ev_capacity = 0

        self.regular_slots = []
        self.ev_slots = []
        
        # Strategy pattern - different behavior for regular vs EV
        self.regular_strategy = StandardParkingStrategy()
        self.ev_strategy = EVParkingStrategy()
        
        # Observer pattern - list of observers to notify
        self.observers = []
        
        self.is_initialized = False
    
    def attach_observer(self, observer):
        # Add an observer 
        if observer not in self.observers:
            self.observers.append(observer)
    
    def notify_observers(self, event_type, message):
        # Notify all observers of an event 
        for observer in self.observers:
            observer.update(event_type, message)
    
    def create_parking_lot(self, regular_capacity, ev_capacity, level):
        # Initialize parking lot
        
        self.regular_capacity = regular_capacity
        self.ev_capacity = ev_capacity
        self.level = level

        self.regular_slots = [EMPTY_SLOT] * regular_capacity
        self.ev_slots = [EMPTY_SLOT] * ev_capacity
        
        self.is_initialized = True
        
        message = f"Created parking lot with {regular_capacity} regular slots and {ev_capacity} EV slots on level {level}"
        self.notify_observers(ParkingEventType.LOT_CREATED, message)
    
    def park_vehicle(self, registration_number, make, model, color, is_electric, is_motorcycle):
        # Park a vehicle using appropriate strategy
        if not self.is_initialized:
            self.notify_observers(ParkingEventType.PARKING_FAILED, "Please create parking lot first")
            return -1
        
        try:
            # Factory pattern - create appropriate vehicle
            vehicle = VehicleFactory.create_vehicle(registration_number, make, model, color, is_electric, is_motorcycle)
            
            # Strategy pattern - use appropriate parking strategy
            if isinstance(vehicle, ElectricVehicle):
                occupied_count = sum(1 for slot in self.ev_slots if slot is not EMPTY_SLOT)
                
                if self.ev_strategy.can_park(vehicle, occupied_count, self.ev_capacity):
                    slot_index = self.ev_strategy.find_empty_slot(self.ev_slots)
                    if slot_index >= 0:
                        self.ev_slots[slot_index] = vehicle
                        slot_number = slot_index + 1
                        message = f"Allocated EV slot number: {slot_number} for {vehicle.get_type()} - {registration_number}"
                        self.notify_observers(ParkingEventType.VEHICLE_PARKED, message)
                        return slot_number
            else:
                occupied_count = sum(1 for slot in self.regular_slots if slot is not EMPTY_SLOT)
                
                if self.regular_strategy.can_park(vehicle, occupied_count, self.regular_capacity):
                    slot_index = self.regular_strategy.find_empty_slot(self.regular_slots)
                    if slot_index >= 0:
                        self.regular_slots[slot_index] = vehicle
                        slot_number = slot_index + 1
                        message = f"Allocated regular slot number: {slot_number} for {vehicle.get_type()} - {registration_number}"
                        self.notify_observers(ParkingEventType.VEHICLE_PARKED, message)
                        return slot_number
            
            # If we get here, parking failed
            slot_type = "EV" if isinstance(vehicle, ElectricVehicle) else "regular"
            self.notify_observers(ParkingEventType.PARKING_FAILED, f"Sorry, {slot_type} parking lot is full")
            return -1
            
        except Exception as error:
            self.notify_observers(ParkingEventType.PARKING_FAILED, f"Error: {str(error)}")
            return -1
    
    def remove_vehicle(self, slot_number, is_ev_slot):
        # Remove vehicle from slot
        try:
            slot_index = slot_number - 1
            slots = self.ev_slots if is_ev_slot else self.regular_slots
            slot_type = "EV" if is_ev_slot else "regular"
            
            if 0 <= slot_index < len(slots) and slots[slot_index] is not EMPTY_SLOT:
                vehicle = slots[slot_index]
                slots[slot_index] = EMPTY_SLOT
                message = f"Slot number {slot_number} ({slot_type}) is now free - was {vehicle.regnum}"
                self.notify_observers(ParkingEventType.VEHICLE_REMOVED, message)
                return True
            else:
                self.notify_observers(ParkingEventType.REMOVAL_FAILED, f"Unable to remove vehicle from {slot_type} slot {slot_number}")
                return False
        except Exception as error:
            self.notify_observers(ParkingEventType.REMOVAL_FAILED, f"Error: {str(error)}")
            return False
    
    def get_all_regular_vehicles(self):
        # Get list of (slot_number, vehicle) tuples for regular vehicles
        return [(i+1, vehicle) for i, vehicle in enumerate(self.regular_slots) if vehicle is not EMPTY_SLOT]
    
    def get_all_ev_vehicles(self):
        # Get list of (slot_number, vehicle) tuples for EV vehicles
        return [(i+1, vehicle) for i, vehicle in enumerate(self.ev_slots) if vehicle is not EMPTY_SLOT]
    
    def find_slot_by_registration(self, registration):
        # Find slot by registration number

        # Check regular slots
        for i, vehicle in enumerate(self.regular_slots):
            if vehicle is not EMPTY_SLOT and vehicle.regnum == registration:
                return {"slot_number": i+1, "type": "regular", "found": True}
        
        # Check EV slots
        for i, vehicle in enumerate(self.ev_slots):
            if vehicle is not EMPTY_SLOT and vehicle.regnum == registration:
                return {"slot_number": i+1, "type": "EV", "found": True}
        
        return {"found": False}
    
    def find_vehicles_by_color(self, color):
        # Find all vehicles matching color

        regular_vehicles = [
            (i+1, vehicle) for i, vehicle in enumerate(self.regular_slots)
            if vehicle is not EMPTY_SLOT and vehicle.color.lower() == color.lower()
        ]
        
        ev_vehicles = [
            (i+1, vehicle) for i, vehicle in enumerate(self.ev_slots)
            if vehicle is not EMPTY_SLOT and vehicle.color.lower() == color.lower()
        ]
        
        return {"regular": regular_vehicles, "ev": ev_vehicles}


# GUI

class ParkingLotGUI:
    # GUI Controller - ONLY handles user interface
    # (Claude AI - Prompts for Analysing GUI & Global Variable with Tkinter, 2026)
    
    def __init__(self, root):
        self.root = root
        self.root.geometry("700x900")
        self.root.resizable(False, False)
        self.root.title("EasyParkPlus - Parking Lot Manager")
        
        # Business logic 
        self.parking_lot = ParkingLot()
        
        # GUI variables
        self.regular_capacity_var = tk.StringVar()
        self.ev_capacity_var = tk.StringVar()
        self.level_var = tk.StringVar(value="1")
        self.make_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.color_var = tk.StringVar()
        self.registration_var = tk.StringVar()
        self.is_electric_var = tk.IntVar()
        self.is_motorcycle_var = tk.IntVar()
        self.slot_number_var = tk.StringVar()
        self.is_ev_slot_var = tk.IntVar()
        self.search_registration_var = tk.StringVar()
        self.search_color_var = tk.StringVar()
        
        # Create GUI
        self._create_widgets()
        
        # Setup observer pattern
        self.gui_observer = GUIObserver(self.output_text)
        self.parking_lot.attach_observer(self.gui_observer)
    
    def _create_widgets(self):
        # Create all GUI widgets
        row = 0
        
        # Header
        tk.Label(self.root, text='EasyParkPlus - Parking Lot Manager', font='Arial 14 bold').grid(
            row=row, column=0, padx=10, pady=10, columnspan=4)
        row += 1
        
        # Lot Creation Section
        tk.Label(self.root, text='Lot Creation', font='Arial 12 bold').grid(
            row=row, column=0, padx=10, pady=(10,5), columnspan=4)
        row += 1
        
        tk.Label(self.root, text='Regular Spaces', font='Arial 12').grid(
            row=row, column=0, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.regular_capacity_var, width=6, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=2)
        tk.Label(self.root, text='EV Spaces', font='Arial 12').grid(
            row=row, column=2, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.ev_capacity_var, width=6, font='Arial 12').grid(
            row=row, column=3, padx=4, pady=2)
        row += 1
        
        tk.Label(self.root, text='Floor Level', font='Arial 12').grid(
            row=row, column=0, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.level_var, width=6, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=4)
        row += 1
        
        tk.Button(self.root, command=self._create_lot, text="Create Parking Lot", font="Arial 12",
                bg='lightblue', fg='black', activebackground="teal", padx=5, pady=5).grid(
                    row=row, column=0, padx=4, pady=4, columnspan=2)
        row += 1
        
        # Vehicle Management Section
        tk.Label(self.root, text='Vehicle Management', font='Arial 12 bold').grid(
            row=row, column=0, padx=10, pady=(10,5), columnspan=4)
        row += 1
        
        tk.Label(self.root, text='Make', font='Arial 12').grid(
            row=row, column=0, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.make_var, width=12, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=4)
        tk.Label(self.root, text='Model', font='Arial 12').grid(
            row=row, column=2, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.model_var, width=12, font='Arial 12').grid(
            row=row, column=3, padx=4, pady=4)
        row += 1
        
        tk.Label(self.root, text='Color', font='Arial 12').grid(
            row=row, column=0, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.color_var, width=12, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=4)
        tk.Label(self.root, text='Registration #', font='Arial 12').grid(
            row=row, column=2, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.registration_var, width=12, font='Arial 12').grid(
            row=row, column=3, padx=4, pady=4)
        row += 1
        
        tk.Checkbutton(self.root, text='Electric', variable=self.is_electric_var, onvalue=1, offvalue=0, font='Arial 12').grid(
            row=row, column=0, padx=4, pady=4)
        tk.Checkbutton(self.root, text='Motorcycle', variable=self.is_motorcycle_var, onvalue=1, offvalue=0, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=4)
        row += 1
        
        tk.Button(self.root, command=self._park_vehicle, text="Park Vehicle", font="Arial 11",
                bg='lightblue', fg='black', activebackground="teal", padx=5, pady=5).grid(
                    row=row, column=0, padx=4, pady=4)
        row += 1
        
        tk.Label(self.root, text='Slot #', font='Arial 12').grid(
            row=row, column=0, padx=5, sticky='e')
        tk.Entry(self.root, textvariable=self.slot_number_var, width=12, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=4)
        tk.Checkbutton(self.root, text='EV Slot?', variable=self.is_ev_slot_var, onvalue=1, offvalue=0, font='Arial 12').grid(
            row=row, column=2, padx=4, pady=4)
        row += 1
        
        tk.Button(self.root, command=self._remove_vehicle, text="Remove Vehicle", font="Arial 11",
                bg='lightblue', fg='black', activebackground="teal", padx=5, pady=5).grid(
                    row=row, column=0, padx=4, pady=4)
        row += 1
        
        # Query Section
        tk.Label(self.root, text="").grid(row=row, column=0)
        row += 1
        
        tk.Button(self.root, command=self._find_by_registration, text="Find by Registration", font="Arial 11",
                bg='lightblue', fg='black', activebackground="teal", padx=5, pady=5).grid(
                    row=row, column=0, padx=4, pady=4)
        tk.Entry(self.root, textvariable=self.search_registration_var, width=12, font='Arial 12').grid(
            row=row, column=1, padx=4, pady=4)
        
        tk.Button(self.root, command=self._find_by_color, text="Find by Color", font="Arial 11",
                bg='lightblue', fg='black', activebackground="teal", padx=5, pady=5).grid(
                    row=row, column=2, padx=4, pady=4)
        tk.Entry(self.root, textvariable=self.search_color_var, width=12, font='Arial 12').grid(
            row=row, column=3, padx=4, pady=4)
        row += 1
        
        tk.Button(self.root, command=self._show_charge_status, text="EV Charge Status", font="Arial 11",
                bg='lightblue', fg='black', activebackground="teal", padx=5, pady=5).grid(
                    row=row, column=0, padx=4, pady=4)
        tk.Button(self.root, command=self._show_status, text="Lot Status", font="Arial 11",
                bg='PaleGreen1', fg='black', activebackground="PaleGreen3", padx=5, pady=5).grid(
                    row=row, column=1, padx=4, pady=4, columnspan=2)
        tk.Button(self.root, command=self._clear_output, text="Clear", font="Arial 11",
                bg='#ffcccc', fg='black', activebackground='#ff9999', padx=5, pady=5).grid(
                    row=row, column=3, padx=4, pady=4)
        row += 1
        
        # Output text area
        self.output_text = tk.Text(self.root, width=75, height=15, font='Courier 10')
        self.output_text.grid(
            row=row, column=0, padx=10, pady=10, columnspan=4)
    
    # Event handlers - delegate to business logic
    
    def _create_lot(self):
        # Create parking lot
        try:
            regular_capacity = int(self.regular_capacity_var.get())
            ev_capacity = int(self.ev_capacity_var.get())
            level = int(self.level_var.get())
            self.parking_lot.create_parking_lot(regular_capacity, ev_capacity, level)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers")
    
    def _park_vehicle(self):
        # Park vehicle
        if not self.registration_var.get().strip():
            messagebox.showwarning("Missing Info", "Please enter registration number")
            return
        
        self.parking_lot.park_vehicle(
            self.registration_var.get().strip(),
            self.make_var.get().strip(),
            self.model_var.get().strip(),
            self.color_var.get().strip() or "Unknown",
            bool(self.is_electric_var.get()),
            bool(self.is_motorcycle_var.get())
        )
        
        # Clear form
        self.make_var.set("")
        self.model_var.set("")
        self.color_var.set("")
        self.registration_var.set("")
        self.is_electric_var.set(0)
        self.is_motorcycle_var.set(0)
    
    def _remove_vehicle(self):
        # Remove vehicle
        try:
            slot_number = int(self.slot_number_var.get())
            is_ev_slot = bool(self.is_ev_slot_var.get())
            self.parking_lot.remove_vehicle(slot_number, is_ev_slot)
            self.slot_number_var.set("")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter valid slot number")
    
    def _find_by_registration(self):
        # Find vehicle by registration
        registration = self.search_registration_var.get().strip()
        if not registration:
            return
        
        result = self.parking_lot.find_slot_by_registration(registration)
        if result.get("found"):
            self.output_text.insert(tk.INSERT, f"SUCCESS Vehicle {registration} found in {result['type']} slot {result['slot_number']}\n")
        else:
            self.output_text.insert(tk.INSERT, f"FAILED Vehicle {registration} not found\n")
    
    def _find_by_color(self):
        # Find vehicles by color
        color = self.search_color_var.get().strip()
        if not color:
            return
        
        results = self.parking_lot.find_vehicles_by_color(color)
        self.output_text.insert(tk.INSERT, f"\nVehicles with color '{color}':\n")
        
        if results["regular"]:
            slots = ", ".join(str(slot) for slot, _ in results["regular"])
            self.output_text.insert(tk.INSERT, f"Regular slots: {slots}\n")
        else:
            self.output_text.insert(tk.INSERT, "Regular slots: (none)\n")
        
        if results["ev"]:
            slots = ", ".join(str(slot) for slot, _ in results["ev"])
            self.output_text.insert(tk.INSERT, f"EV slots: {slots}\n")
        else:
            self.output_text.insert(tk.INSERT, "EV slots: (none)\n")
        
        self.output_text.insert(tk.INSERT, "\n")
    
    def _show_status(self):
        # Show parking lot status
        if not self.parking_lot.is_initialized:
            messagebox.showwarning("Not Initialized", "Please create parking lot first")
            return
        
        regular = self.parking_lot.get_all_regular_vehicles()
        ev = self.parking_lot.get_all_ev_vehicles()
        self.gui_observer.display_status(regular, ev, self.parking_lot.level)
    
    def _show_charge_status(self):
        # Show EV charge status
        if not self.parking_lot.is_initialized:
            messagebox.showwarning("Not Initialized", "Please create parking lot first")
            return
        
        ev_vehicles = self.parking_lot.get_all_ev_vehicles()
        self.gui_observer.display_charge_status(ev_vehicles, self.parking_lot.level)
    
    def _clear_output(self):
        # Clear output
        self.output_text.delete(1.0, tk.END)


# Main

def main():
    # Application entry point
    root = tk.Tk()
    app = ParkingLotGUI(root)
    root.mainloop()

if __name__ == '__main__':
    main()