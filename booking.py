import csv
import random
import datetime
import os

TRAINS_FILE = "trains.csv"
BOOKINGS_FILE = "bookings.csv"

# Try to import prompt_toolkit (optional)
try:
    from prompt_toolkit import prompt
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.shortcuts import CompleteStyle
    HAS_PROMPT_TOOLKIT = True
except Exception:
    HAS_PROMPT_TOOLKIT = False

# === Generate Unique PNR ===
def generate_pnr():
    prefix = "PNR"
    unique_id = random.randint(100000, 999999)
    return f"{prefix}{unique_id}"

# === Validate Passenger Name ===
def is_valid_name(name):
    return name.replace(" ", "").isalpha()

# === Validate Age ===
def is_valid_age(age):
    return age.isdigit() and 0 < int(age) < 120

# === Helpers to normalise train CSV header names ===
def detect_train_fieldnames(original_fieldnames):
    """
    Given a list of original headers from trains.csv (as read),
    return a mapping of canonical keys -> original header names.
    Canonical keys: 'train_no', 'train_name', 'source', 'destination', 'seats'
    """
    mapping = {}
    lower_fields = [f.lower().strip() for f in original_fieldnames]

    for idx, lf in enumerate(lower_fields):
        if ("train" in lf and "no" in lf) or lf in ("train_no", "train no", "trainno", "train-number"):
            mapping["train_no"] = original_fieldnames[idx]
        elif ("train" in lf and ("name" in lf or "nama" in lf)) or lf in ("train_name", "train name", "trainname"):
            mapping["train_name"] = original_fieldnames[idx]
        elif "source" in lf or "from" in lf or lf in ("src",):
            mapping["source"] = original_fieldnames[idx]
        elif "destination" in lf or "to" in lf or lf in ("dest",):
            mapping["destination"] = original_fieldnames[idx]
        elif ("seat" in lf and ("no" in lf or "count" in lf)) or lf in ("no_of_seats", "no of seats", "seats", "seat"):
            mapping["seats"] = original_fieldnames[idx]
    # Fallbacks: try to pick by position if some not found
    # prefer common default positions: train_no, train_name, source, destination, seats
    if len(mapping) < 5:
        remaining = [f for f in original_fieldnames if f not in mapping.values()]
        defaults = ["train_no", "train_name", "source", "destination", "seats"]
        for d, r in zip(defaults, remaining):
            if d not in mapping:
                mapping[d] = r
    return mapping

# === Load train details directly from trains.csv (robust to header variations) ===
def load_trains():
    trains = {}
    if not os.path.exists(TRAINS_FILE):
        print(f"❌ '{TRAINS_FILE}' file not found!")
        return trains

    with open(TRAINS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows or len(rows) <= 1:
        # no data
        return trains

    header = rows[0]
    mapping = detect_train_fieldnames(header)

    # Build trains dict
    for r in rows[1:]:
        # pad row if shorter
        row = r + [""] * (len(header) - len(r))
        row_dict = {h: row[i].strip() if i < len(row) else "" for i, h in enumerate(header)}
        train_no = row_dict.get(mapping.get("train_no"), "").strip()
        if not train_no:
            continue
        # attempt to parse seats
        seats_raw = row_dict.get(mapping.get("seats"), "0").strip()
        try:
            seats = int(seats_raw)
        except (ValueError, TypeError):
            seats = 0
        trains[train_no] = {
            "name": row_dict.get(mapping.get("train_name"), "").strip(),
            "source": row_dict.get(mapping.get("source"), "").strip(),
            "destination": row_dict.get(mapping.get("destination"), "").strip(),
            "seats": seats
        }
    return trains

# ===== Helper: build station list from loaded trains =====
def get_unique_stations(trains):
    """Return a sorted list of unique station names from trains dict."""
    stations = set()
    for t in trains.values():
        src = t.get("source", "")
        dst = t.get("destination", "")
        if src:
            stations.add(src.title())
        if dst:
            stations.add(dst.title())
    return sorted(stations)

# ===== Helper: get destinations for a given source =====
def get_destinations_for_source(trains, source):
    """
    Return a sorted list of unique destinations reachable from `source`.
    Matching is case-insensitive.
    """
    if not source:
        return []
    dests = set()
    src_lower = source.strip().lower()
    for t in trains.values():
        t_src = (t.get("source") or "").strip().lower()
        t_dst = (t.get("destination") or "").strip()
        if t_src == src_lower and t_dst:
            dests.add(t_dst.title())
    return sorted(dests)

# ===== Helper: suggest station input (interactive if prompt_toolkit available) =====
def suggest_station_input(prompt_text, stations):
    """
    Returns chosen station (title-cased).
    If prompt_toolkit is available, show interactive dropdown with mouse support.
    Otherwise, fallback to numbered-suggestion input flow.
    """
    if not stations:
        return input(prompt_text).strip().title()

    # If prompt_toolkit installed — use it (supports mouse selection in many terminals)
    if HAS_PROMPT_TOOLKIT:
        try:
            completer = WordCompleter(stations, ignore_case=True, match_middle=True)
            result = prompt(
                prompt_text,
                completer=completer,
                complete_while_typing=True,
                complete_style=CompleteStyle.COLUMN,
                mouse_support=True
            )
            return result.strip().title()
        except Exception:
            # fallback to non-interactive below
            pass

    # Fallback non-interactive suggestion UI (safe)
    while True:
        typed = input(prompt_text).strip()
        if typed == "":
            print("❗ Enter at least 1 character to see suggestions.")
            continue

        typed_title = typed.title()
        prefix = typed.lower()
        # contains-based matching (more forgiving)
        matches = [s for s in stations if prefix in s.lower()]

        if matches:
            print("\n🔎 Suggestions:")
            for i, s in enumerate(matches[:10], start=1):
                print(f"{i}. {s}")
            choice = input("Choose number (e.g. 1) or press Enter to use typed value: ").strip()
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(matches[:10]):
                    return matches[idx]
                else:
                    print("❌ Invalid number. Try again.")
                    continue
            else:
                if typed_title in stations:
                    return typed_title
                else:
                    confirm = input(f"'{typed_title}' not found in suggestions. Use it anyway? (y/n): ").strip().lower()
                    if confirm == "y":
                        return typed_title
                    else:
                        continue
        else:
            confirm = input(f"No suggestions found for '{typed_title}'. Use it anyway? (y/n): ").strip().lower()
            if confirm == "y":
                return typed_title
            else:
                continue

# === Smart Date Selection ===
def select_travel_date():
    print("\n📅 Choose Travel Date:")
    today = datetime.date.today()
    for i in range(7):
        future_date = today + datetime.timedelta(days=i)
        print(f"{i+1}. {future_date.strftime('%d-%m-%Y')}")

    while True:
        try:
            choice = int(input("Select your travel date (1–7): "))
            if 1 <= choice <= 7:
                selected_date = today + datetime.timedelta(days=choice - 1)
                return selected_date.strftime("%d-%m-%Y")
            else:
                print("❌ Invalid choice! Choose between 1–7.")
        except ValueError:
            print("❌ Please enter a number.")

# === Update Seat Count in trains.csv (reduce seats when booking) ===
def update_seat_count(train_no, seats_to_reduce):
    if not os.path.exists(TRAINS_FILE):
        print("❌ trains file missing.")
        return False

    with open(TRAINS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        print("❌ trains file is empty.")
        return False

    header = rows[0]
    mapping = detect_train_fieldnames(header)
    updated_rows = [header]

    updated = False
    for r in rows[1:]:
        row = r + [""] * (len(header) - len(r))
        row_dict = {h: row[i].strip() if i < len(row) else "" for i, h in enumerate(header)}
        tno = row_dict.get(mapping.get("train_no"), "").strip()
        if tno == train_no:
            # parse seats
            seats_key = mapping.get("seats")
            try:
                current = int(row_dict.get(seats_key, "0"))
            except (ValueError, TypeError):
                current = 0
            if current >= seats_to_reduce:
                row_dict[seats_key] = str(current - seats_to_reduce)
                updated = True
            else:
                print("❌ Not enough seats available on this train!")
                return False
        # rebuild row preserving original header order
        updated_row = [row_dict.get(h, "") for h in header]
        updated_rows.append(updated_row)

    # write back
    with open(TRAINS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

    return updated

# === Restore Seat After Cancellation (adds seats back to trains.csv) ===
def restore_seat(train_no, seats_to_add):
    if not os.path.exists(TRAINS_FILE):
        # no trains file — nothing to restore
        return

    with open(TRAINS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if not rows:
        return

    header = rows[0]
    mapping = detect_train_fieldnames(header)
    updated_rows = [header]

    for r in rows[1:]:
        row = r + [""] * (len(header) - len(r))
        row_dict = {h: row[i].strip() if i < len(row) else "" for i, h in enumerate(header)}
        tno = row_dict.get(mapping.get("train_no"), "").strip()
        if tno == train_no:
            seats_key = mapping.get("seats")
            try:
                current = int(row_dict.get(seats_key, "0"))
            except (ValueError, TypeError):
                current = 0
            row_dict[seats_key] = str(current + seats_to_add)
        updated_row = [row_dict.get(h, "") for h in header]
        updated_rows.append(updated_row)

    with open(TRAINS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

# === Ticket Booking (MULTI-PASSENGER ENABLED) ===
def book_ticket(username):
    print("\n==== Railway Ticket Booking ====")

    trains = load_trains()
    if not trains:
        print("❌ No trains available! Please contact admin.")
        return

    # --- smart station input with destination filtered by chosen source ---
    stations = get_unique_stations(trains)
    if not stations:
        print("❌ No station data available.")
        return

    source = suggest_station_input("Enter Source Station (type to search): ", stations)

    # Build destination list only for trains that depart from the chosen source
    destinations = get_destinations_for_source(trains, source)
    if not destinations:
        print(f"❌ No destinations found departing from {source}.")
        return

    destination = suggest_station_input(f"Enter Destination Station (from {source}): ", destinations)

    if source.lower() == destination.lower():
        print("❌ Source and destination cannot be the same.")
        return

    # Step 1: Find Available Trains
    available_trains = []
    for no, info in trains.items():
        if info["source"].lower() == source.lower() and info["destination"].lower() == destination.lower():
            available_trains.append((no, info["name"], info["seats"]))

    if not available_trains:
        print(f"❌ No trains found from {source} to {destination}.")
        return

    # Step 2: Show Available Trains
    print(f"\n✅ Available Trains from {source} → {destination}:")
    for i, (no, name, seats) in enumerate(available_trains, start=1):
        print(f"{i}. {name} ({no}) — Seats Available: {seats}")

    # Step 3: Choose Train
    while True:
        try:
            choice = int(input("Select Train (1/2/3...): "))
            if 1 <= choice <= len(available_trains):
                train_no, train_name, available_seats = available_trains[choice - 1]
                break
            else:
                print("❌ Invalid choice! Try again.")
        except ValueError:
            print("❌ Enter a valid number.")

    # Step 4: How Many Tickets
    while True:
        try:
            num_passengers = int(input("How many passengers to book (1–6): "))
            if 1 <= num_passengers <= 6:
                if num_passengers > available_seats:
                    print(f"❌ Only {available_seats} seats are available. Try fewer passengers.")
                else:
                    break
            else:
                print("❌ You can book between 1–6 passengers at a time.")
        except ValueError:
            print("❌ Enter a valid number.")

    # Step 5: Travel Date
    travel_date = select_travel_date()
    booking_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(BOOKINGS_FILE)

    with open(BOOKINGS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "PNR", "Username", "Passenger Name", "Age", "Gender",
                "Source", "Destination", "Travel Date",
                "Train Name", "Train No", "Booking Time"
            ])

        for i in range(num_passengers):
            print(f"\n👤 Enter details for Passenger {i+1}:")
            while True:
                name = input("Passenger Name: ").strip().title()
                if not is_valid_name(name):
                    print("❌ Name should contain only letters (A–Z). Try again.")
                else:
                    break

            while True:
                age = input("Age: ").strip()
                if not is_valid_age(age):
                    print("❌ Age should be a valid number between 1–120.")
                else:
                    break

            gender = input("Gender (M/F/O): ").upper().strip()
            pnr = generate_pnr()

            ticket_data = [
                pnr, username, name, age, gender,
                source, destination, travel_date, train_name, train_no, booking_time
            ]
            writer.writerow(ticket_data)

            print(f"✅ Passenger {i+1} booked successfully! PNR: {pnr}")

    # Step 6: Update Seat Count
    if update_seat_count(train_no, num_passengers):
        print(f"\n🎫 {num_passengers} Ticket(s) booked successfully!")
        print(f"🚆 Train: {train_name} ({train_no})")
        print(f"📍 Route: {source} → {destination}")
        print(f"🗓️ Date: {travel_date}")
        print(f"🕒 Booking Time: {booking_time}")
        print("==================================")
    else:
        print("❌ Booking failed due to seat unavailability.")

# === View Bookings ===
def view_bookings(username):
    if not os.path.exists(BOOKINGS_FILE):
        print("No bookings found.")
        return

    print(f"\n==== Your Bookings ({username}) ====")
    with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        print("😕 You have no active bookings.")
        return

    header = rows[0]
    bookings = [row for row in rows[1:] if len(row) > 1 and row[1] == username]

    if bookings:
        print(f"{'SL No.':<7}{'PNR':<12}{'Journey Date':<15}{'From → To':<30}{'Train Name':<25}{'Train No.':<10}")
        print("-" * 100)
        for i, row in enumerate(bookings, start=1):
            pnr = row[0]
            journey_date = row[7]
            route = f"{row[5]} → {row[6]}"
            train_name = row[8]
            train_no = row[9]
            print(f"{i:<7}{pnr:<12}{journey_date:<15}{route:<30}{train_name:<25}{train_no:<10}")
        print("-" * 100)
    else:
        print("😕 You have no active bookings.")

# === Cancel Ticket (improved: supports multiple cancel & safer matching) ===
def cancel_ticket(username):
    if not os.path.exists(BOOKINGS_FILE):
        print("❌ No bookings available to cancel.")
        return

    # read all rows
    with open(BOOKINGS_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)

    if len(rows) <= 1:
        print("❌ No bookings found.")
        return

    header = rows[0]
    user_bookings = [row for row in rows[1:] if len(row) > 1 and row[1] == username]

    if not user_bookings:
        print("😕 You have no bookings to cancel.")
        return

    # show bookings
    print(f"\n==== Your Active Bookings ({username}) ====")
    print(f"{'No.':<5}{'PNR':<12}{'Train Name':<25}{'From → To':<30}{'Date':<15}")
    print("-" * 100)
    for i, row in enumerate(user_bookings, start=1):
        pnr = row[0]
        train_name = row[8] if len(row) > 8 else ""
        from_st = row[5] if len(row) > 5 else ""
        to_st = row[6] if len(row) > 6 else ""
        date = row[7] if len(row) > 7 else ""
        print(f"{i:<5}{pnr:<12}{train_name:<25}{from_st} → {to_st:<25}{date:<15}")
    print("-" * 100)

    # allow multiple selection like: 1 or 1,3 or 2-4
    selection = input("Enter booking numbers to cancel (e.g. 1 or 1,3 or 2-4) or 0 to exit: ").strip()
    if selection == "0" or selection == "":
        print("Cancellation aborted.")
        return

    # parse selection into indices
    to_cancel_indices = set()
    try:
        parts = [p.strip() for p in selection.split(",") if p.strip() != ""]
        for p in parts:
            if "-" in p:
                a, b = p.split("-", 1)
                a = int(a); b = int(b)
                if a <= 0 or b <= 0:
                    raise ValueError
                for idx in range(min(a,b), max(a,b)+1):
                    to_cancel_indices.add(idx-1)  # zero-based
            else:
                idx = int(p)
                if idx <= 0:
                    raise ValueError
                to_cancel_indices.add(idx-1)
    except ValueError:
        print("❌ Invalid selection format. Use numbers like '1' or '1,3' or '2-4'.")
        return

    # validate indices
    valid_indices = [i for i in sorted(to_cancel_indices) if 0 <= i < len(user_bookings)]
    if not valid_indices:
        print("❌ No valid bookings selected.")
        return

    # collect PNRs and train_nos to restore seats
    pnrs_to_cancel = []
    train_restore_count = {}  # train_no -> seats to restore

    for i in valid_indices:
        row = user_bookings[i]
        if len(row) < 10:
            # if format unexpected, skip
            continue
        pnr = row[0]
        train_no = row[9]
        pnrs_to_cancel.append(pnr)
        train_restore_count[train_no] = train_restore_count.get(train_no, 0) + 1

    if not pnrs_to_cancel:
        print("❌ Couldn't parse selected bookings.")
        return

    # Remove selected bookings from rows (match by PNR)
    updated_rows = [rows[0]] + [r for r in rows[1:] if r[0] not in pnrs_to_cancel]
    with open(BOOKINGS_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

    # Restore seats for each train
    for train_no, seats in train_restore_count.items():
        restore_seat(train_no, seats)

    print(f"✅ Cancelled {len(pnrs_to_cancel)} booking(s): {', '.join(pnrs_to_cancel)}")
