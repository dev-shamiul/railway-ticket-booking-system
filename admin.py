# admin.py
import csv
import os

TRAINS_FILE = "trains.csv"
ADMIN_USERNAME = "roboboy"
ADMIN_PASSWORD = "roboboy"

def ensure_trains_file():
    """Create trains.csv with header if it doesn't exist."""
    if not os.path.exists(TRAINS_FILE):
        with open(TRAINS_FILE, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["train_no", "train_name", "source", "destination", "seats"])

def admin_login():
    """Return True if credentials match, False otherwise."""
    username = input("Enter admin username: ").strip()
    password = input("Enter admin password: ").strip()
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("\n✅ Admin login successful.\n")
        return True
    else:
        print("\n❌ Invalid admin credentials!\n")
        return False

def add_train():
    """Add a new train to trains.csv (with basic validation)."""
    ensure_trains_file()
    train_no = input("Enter train no: ").strip()
    train_name = input("Enter train name: ").strip()
    source = input("Enter source station: ").strip()
    destination = input("Enter destination station: ").strip()
    seats = input("Enter no. of seats: ").strip()

    # Basic validation
    if not train_no or not train_name or not seats.isdigit():
        print("\nInvalid input! Train not added.")
        print("Make sure Train No and Train Name are provided and Seats is a number.\n")
        return

    with open(TRAINS_FILE, mode="a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([train_no, train_name, source, destination, seats])

    print(f"\n✅ Train {train_no} - '{train_name}' added successfully.\n")

def view_trains():
    """Read and display all trains in a simple table format."""
    if not os.path.exists(TRAINS_FILE):
        print("No trains found! Add trains first.\n")
        return

    with open(TRAINS_FILE, mode="r", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if len(rows) <= 1:
        print("No trains found! Add trains first.\n")
        return

    header = rows[0]
    print("{:<10} {:<25} {:<15} {:<15} {:<6}".format(*header))
    print("-" * 75)
    for r in rows[1:]:
        print("{:<10} {:<25} {:<15} {:<15} {:<6}".format(*r))
    print()

def admin_panel():
    """Admin control panel for managing trains."""
    if not admin_login():
        return

    while True:
        print("=== ADMIN PANEL ===")
        print("1️⃣ Add New Train")
        print("2️⃣ View All Trains")
        print("3️⃣ Exit Admin Panel")

        choice = input("Choose an option (1-3): ").strip()
        if choice == "1":
            add_train()
        elif choice == "2":
            view_trains()
        elif choice == "3":
            print("\nExiting Admin Panel... 👋\n")
            break
        else:
            print("\nInvalid choice! Please select 1, 2, or 3.\n")

# Run admin panel
if __name__ == "__main__":
    admin_panel()
