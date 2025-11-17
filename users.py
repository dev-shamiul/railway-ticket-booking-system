import csv
import os

# === ataaaa holo Password Validation Function ===
def is_valid_password(password):
    has_letter = any(c.isalpha() for c in password)   # minimum 1 letter
    has_digit = any(c.isdigit() for c in password)    # minimum 1 digit
    return has_letter and has_digit

# === ataaa holo  Username Already Exists kina check korba===
def username_exists(username):
    if not os.path.exists("users.csv"):
        return False

    with open("users.csv", mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) >= 1 and row[0].strip() == username.strip():
                return True
    return False

# === Register Function ===
def register_user():
    print("Create a new account. It's quick and easy.")

    while True:
        username = input("Enter username: ").strip()
        if username_exists(username):
            print("❌ Username already taken! Please choose another.")
        elif username == "":
            print("❌ Username cannot be empty!")
        else:
            break

    while True:
        password = input("Enter password (must contain both letters & numbers): ").strip()

        if is_valid_password(password):
            break
        else:
            print("❌ Invalid password! It must contain both letters and numbers. Try again.")

    #csv te new line ar por blank line asbee na
    with open("users.csv", mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([username, password])

    print(f"✅ User '{username}' registered successfully!")
