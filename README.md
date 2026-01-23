# EasyParkPlus - Parking Lot Manager

A refactored parking lot management system demonstrating software design patterns (Strategy, Observer, Factory) and clean architecture principles.

## Requirements

- Python 3.7 or higher
- No external dependencies required (uses built-in `tkinter`)

## Running the Program

1. Clone the repository:
```bash
git clone https://github.com/vish8426/easyparkplus-parking-lot-manger-codebase-refactor.git
cd easyparkplus-parking-lot-manger-codebase-refactor
```

2. Run the application:
```bash
python src/ParkingManager.py
```

Or on Windows:
```bash
python .\src\ParkingManager.py
```

## Usage

The GUI application opens with the following workflow:

1. **Create Parking Lot**: Set the number of regular and EV parking slots, and specify the floor level.
2. **Park Vehicle**: Enter vehicle details (make, model, color, registration) and check if electric/motorcycle.
3. **Remove Vehicle**: Enter slot number to remove a parked vehicle.
4. **Query Operations**:
   - Find vehicle by registration number
   - Find vehicles by color
   - View EV charge status
   - View lot status

## Project Structure

```
src/
├── ParkingManager.py    # Main application entry point
└── Vehicle.py           # Vehicle classes and factory
```

## License

MIT License - See [LICENSE](LICENSE) for details
