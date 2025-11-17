import csv

def login_user():
    print("Please login with your registered username and password.")
    username = input("Enter username: ")
    password = input("Enter password: ")

    found = False

    with open("users.csv", mode="r") as f:
        s = csv.reader(f)
        for row in s:
            if row[0] == username and row[1] == password:
                print("✅ Login successfully!")
                found = True
                return username  

    if not found:
        print("❌ The password or Username is incorrect")
        return None   
