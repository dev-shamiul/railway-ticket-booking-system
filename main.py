import users
import login
import booking

def user_menu(username):
    """Show logged-in user menu until they choose to logout/exit."""
    while True:
        print(f"\nWelcome, {username}!")
        print("1️⃣ Book Ticket")
        print("2️⃣ View My Bookings")
        print("3️⃣ Cancel Ticket")
        print("4️⃣ Logout")

        opt = input("Choose your option (1-4): ").strip()
        if opt == "1":
            booking.book_ticket(username)
        elif opt == "2":
            booking.view_bookings(username)
        elif opt == "3":
            booking.cancel_ticket(username)
        elif opt == "4":
            print(f"👋 Logging out {username}...\n")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, 3 or 4.")

def main():
    print("==== Welcome to Indian Railway ====")
    while True:
        print("\nMain Menu:")
        print("1️⃣ Register User")
        print("2️⃣ Login User")
        print("3️⃣ Exit")

        choice = input("Choose your option (1-3): ").strip()

        if choice == "1":
            users.register_user()
            # After registration, attempt auto-login
            username = login.login_user()
            if username:
                user_menu(username)

        elif choice == "2":
            username = login.login_user()
            if username:
                user_menu(username)
            else:
                pass  # login_user already prints error message

        elif choice == "3":
            print("Thank you for visiting Indian Railway 🚉")
            break

        else:
            print("❌ Invalid input! Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
