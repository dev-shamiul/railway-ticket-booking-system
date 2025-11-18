🚆 Railway Ticket Booking System

A simple and user-friendly Python-based Railway Ticket Booking System that allows users to register, log in, book tickets, view bookings, and cancel reservations. The system uses CSV files for data storage, making the project lightweight and easy to run without any database setup.

⭐ Features
👤 User Features

Create a new account (Registration)

Login with username & password

Book tickets (Supports 1–6 passengers at a time)

Validates passenger name, age & gender

Smart station suggestions & route selection

Travel date selection (Next 7 days)

Automatically generates unique PNR

View all active bookings

Cancel one or multiple bookings

Restores train seats after cancellation

🛠 Admin Features

Admin login

Add new trains (Train number, name, source, destination, seats)

View all trains in a clean table format

Auto-create trains.csv if missing

📁 Technology Used

Python 3

CSV file handling

Modular programming

Command Line Interface (CLI)

Optional Input Enhancement: prompt_toolkit (If installed)

📂 Project Structure
│── main.py               # Main menu
│── login.py              # User login system
│── users.py              # Registration & validation
│── admin.py              # Admin panel & train management
│── booking.py            # Ticket booking, cancellation, PNR
│── trains.csv            # Train data storage
│── users.csv             # User list storage
│── bookings.csv          # Booking records
│── .gitignore            # Ignore unnecessary files
│── README.md             # Project documentation

▶️ How to Run the Project
1. Clone the Repository
git clone https://github.com/YOUR_USERNAME/railway-ticket-booking-system.git

2. Open the Folder
cd railway-ticket-booking-system

3. Run the Python Application
python main.py

🔐 Default Admin Credentials
Username	Password
roboboy	roboboy
📝 CSV Files Used
✔ users.csv

Stores username & password

✔ trains.csv

Stores train number, name, route, seats

✔ bookings.csv

Stores PNR, passenger details, route, date, time

🎯 Project Purpose

This system is designed for:

Python beginners

College/Mini projects

Understanding File Handling

Learning Project Structure

Practicing modular & clean code

🚀 Future Improvements

GUI version using Tkinter/PyQt

Database integration (MySQL/MongoDB)

PDF ticket generation

Train search filters

User profile system

Online seat map view

❤️ Authors

Shouvik, Sasroto, Akash, Shamiul

📌 Feel free to contribute

Pull requests are welcome!!
