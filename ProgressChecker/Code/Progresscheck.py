import datetime
import mysql.connector
import bcrypt

#Database connection 
conn = mysql.connector.connect(
    host="YOUR_HOST",
    user="YOUR_USERNAME",
    password="YOUR_PASSWORD",
    database="YOUR_DATABASE"
)
cursor = conn.cursor()

#Password helpers
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

#Account functions
def create_account():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed)
        )
        conn.commit()
        print("Account created successfully.")
    except mysql.connector.IntegrityError:
        print("Username already exists.")

def login():
    username = input("Username: ")
    password = input("Password: ")

    cursor.execute(
        "SELECT id, password_hash FROM users WHERE username=%s",
        (username,)
    )
    result = cursor.fetchone()

    if not result:
        print("Login failed.")
        return None

    user_id, stored_hash = result

    # Ensure hash is bytes
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode()

    if check_password(password, stored_hash):
        print("Login successful.")
        return user_id
    else:
        print("Login failed.")
        return None

#Counters 
def create_counter(user_id):
    name = input("Counter name: ").strip().lower()


    try:
        cursor.execute(
            "INSERT INTO counters (user_id, name) VALUES (%s, %s)",
            (user_id, name)
        )
        conn.commit()
        print("Counter created.")
    except mysql.connector.IntegrityError:
        print("Counter already exists.")

def update_counter(user_id):
    name = input("Which counter to increment?: ").lower()
    amount = int(input("Increase by how much?: "))

    cursor.execute(
        "UPDATE counters SET total = total + %s WHERE user_id=%s AND name=%s",
        (amount, user_id, name)
    )

    if cursor.rowcount == 0:
        print("Counter not found.")
    else:
        conn.commit()
        print("Counter updated.")

def view_counters(user_id):
    cursor.execute(
        "SELECT name, total FROM counters WHERE user_id=%s",
        (user_id,)
    )
    counters = cursor.fetchall()

    if not counters:
        print("No counters yet.")
        return

    print("\n--- Your Counters ---")
    for name, total in counters:
        print(f"{name}: {total}")
    print("---------------------")

def ensure_counter(user_id, name):
    cursor.execute(
        "SELECT id FROM counters WHERE user_id=%s AND name=%s",
        (user_id, name)
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO counters (user_id, name, total) VALUES (%s,%s,0)",
            (user_id, name)
        )

# Daily progress
def get_daily_progress(user_id):
    today = datetime.date.today()

    cursor.execute(
        "SELECT id FROM daily_progress WHERE user_id=%s AND date=%s",
        (user_id, today)
    )
    if cursor.fetchone():
        print("Already logged today.")
        return

    show_up = input("Did you show up today? (yes/no): ").lower()
    learn_thing = input("What did you learn?: ").strip()
    finish_small = input("What did you finish?: ").strip()
    avoid_quitting = input("Avoid quitting? (yes/no): ").lower()
    idea_day = input("Idea of the day: ")
    bible_study = input("Bible study notes: ")
    thoughts = input("Other thoughts: ")

    cursor.execute("""
        INSERT INTO daily_progress
        (user_id, date, show_up, learn_thing, finish_small,
         avoid_quitting, idea_day, bible_study, thoughts)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (user_id, today, show_up, learn_thing, finish_small,
          avoid_quitting, idea_day, bible_study, thoughts))

    # #Preset auto-counters ---
    # presets = {
    #     "Amount Of Days I did not give up": avoid_quitting == "yes",
    #     "Days learned something New": bool(learn_thing),
    # }

    # for counter, should_increment in presets.items():
    #     if should_increment:
    #         ensure_counter(user_id, counter)
    #         cursor.execute(
    #             "UPDATE counters SET total = total + 1 WHERE user_id=%s AND name=%s",
    #             (user_id, counter)
    #         )

    #Custom counters ---
    cursor.execute(
        "SELECT name FROM counters WHERE user_id=%s AND name NOT IN (%s,%s,%s,%s)",
        (user_id, "show_up_days", "no_quit_days", "learn_days", "finish_days")
    )
    custom_counters = cursor.fetchall()

    if custom_counters:
        print("\n--- Custom Counter Updates ---")
        for (name,) in custom_counters:
            try:
                amt = int(input(f"Add to '{name}' today? (0 if none): "))
                if amt > 0:
                    cursor.execute(
                        "UPDATE counters SET total = total + %s WHERE user_id=%s AND name=%s",
                        (amt, user_id, name)
                    )
            except ValueError:
                print("Skipped invalid input.")

    conn.commit()
    print("Daily progress + preset counters saved.")

    #Auto-update counters
    cursor.execute(
        "SELECT name FROM counters WHERE user_id=%s",
        (user_id,)
    )
    counters = cursor.fetchall()

    if counters:
        print("\n--- Daily Counter Updates ---")
        for (name,) in counters:
            try:
                amount = int(input(f"How much to add to '{name}' today? (0 if none): "))
                if amount > 0:
                    cursor.execute(
                        "UPDATE counters SET total = total + %s WHERE user_id=%s AND name=%s",
                        (amount, user_id, name)
                    )
            except ValueError:
                print("Invalid number. Skipped.")

    conn.commit()
    print("Daily progress + counters saved.")

def get_counters(user_id):
    cursor.execute(
        "SELECT name, total FROM counters WHERE user_id=%s ORDER BY name",
        (user_id,)
    )
    return cursor.fetchall()


# Progress summary
def view_progress_summary(user_id):
    print("\n====== PROGRESS SUMMARY ======\n")

    # Show counters first
    cursor.execute(
        "SELECT name, total FROM counters WHERE user_id=%s ORDER BY name",
        (user_id,)
    )
    counters = cursor.fetchall()

    print("--- Counters ---")
    if counters:
        for name, total in counters:
            print(f"{name}: {total}")
    else:
        print("No counters yet.")

    # Show all daily progress
    cursor.execute("""
        SELECT date, show_up, learn_thing, finish_small,
               avoid_quitting, idea_day, bible_study, thoughts
        FROM daily_progress
        WHERE user_id=%s
        ORDER BY date DESC
    """, (user_id,))

    records = cursor.fetchall()

    print("\n--- Daily Progress Logs ---")
    if records:
        for r in records:
            print("\nDate:", r[0])
            print("Showed up:", r[1])
            print("Learned:", r[2])
            print("Finished:", r[3])
            print("Avoid quit:", r[4])
            print("Idea of the day:", r[5])
            print("Bible study:", r[6])
            print("Thoughts:", r[7])
            print("-" * 30)
    else:
        print("No daily progress yet.")

    print("\n==============================\n")

# Main Menu
def user_menu(user_id):
    while True:
        counters = get_counters(user_id)

        print("\n====== DASHBOARD ======")
        if counters:
            for name, total in counters:
                print(f"{name}: {total}")
        else:
            print("No counters yet.")
        print("=======================\n")

        print("""
1. Log daily progress
2. View progress summary
3. Create counter
4. Update counter
5. Exit
""")
        choice = input("Choose: ")

        if choice == '1':
            get_daily_progress(user_id)
        elif choice == '2':
            view_progress_summary(user_id)
        elif choice == '3':
            create_counter(user_id)
        elif choice == '4':
            update_counter(user_id)
        elif choice == '5':
            break
        else:
            print("Invalid choice.")


#Program start
def main():
    while True:
        print("""
Welcome to Progress Tracker !
1. Create account
2. Login
3. Exit
""")
        action = input("Choose: ")

        if action == '1':
            create_account()
        elif action == '2':
            user_id = login()
            if user_id:
                user_menu(user_id)
        elif action == '3':
            break
        else:
            print("Invalid option.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
