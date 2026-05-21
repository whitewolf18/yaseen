import json
import os
from datetime import datetime
import math


# ==========================================
# PRICING STRATEGIES
# ==========================================

class PricingStrategy:

    def calculate_fee(self, hours):
        pass

    def get_type(self):
        pass


class FlatRate(PricingStrategy):

    def __init__(self, fee):
        self.fee = fee

    def calculate_fee(self, hours):
        return self.fee

    def get_type(self):
        return "Flat Rate"


class HourlyRate(PricingStrategy):

    def __init__(self, rate):
        self.rate = rate

    def calculate_fee(self, hours):
        return math.ceil(hours) * self.rate

    def get_type(self):
        return "Hourly Rate"


class CappedHourly(PricingStrategy):

    def __init__(self, rate, cap):
        self.rate = rate
        self.cap = cap

    def calculate_fee(self, hours):
        return min(
            math.ceil(hours) * self.rate,
            self.cap
        )

    def get_type(self):
        return "Hourly Rate with Cap"


# ==========================================
# MALL
# ==========================================

class Mall:

    def __init__(self, name, capacity, pricing):

        self.name = name
        self.capacity = capacity
        self.pricing = pricing
        self.current = []

    def has_space(self):

        return len(self.current) < self.capacity


# ==========================================
# USERS
# ==========================================

class User:

    def __init__(self, username, password, role):

        self.username = username
        self.password = password
        self.role = role


class Customer(User):

    def __init__(self, username, password):

        super().__init__(
            username,
            password,
            "customer"
        )


class Admin(User):

    def __init__(self, username, password, mall):

        super().__init__(
            username,
            password,
            "admin"
        )

        self.mall = mall


class Owner(User):

    def __init__(self, username, password):

        super().__init__(
            username,
            password,
            "owner"
        )


# ==========================================
# RECORDS
# ==========================================

class Record:

    def __init__(self, user, reg, mall):

        self.user = user
        self.reg = reg
        self.mall = mall

        self.entry = datetime.now()

        self.exit = None
        self.hours = 0
        self.fee = 0
        self.paid = False

    def close(self, pricing):

        self.exit = datetime.now()

        self.hours = (
            self.exit - self.entry
        ).total_seconds() / 3600

        self.fee = pricing.calculate_fee(
            self.hours
        )


# ==========================================
# PAYMENTS
# ==========================================

class Payment:

    def __init__(self, user, amount, mall):

        self.user = user
        self.amount = amount
        self.mall = mall

        self.date = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


# ==========================================
# MAIN SYSTEM
# ==========================================

class ParkingSystem:

    def __init__(self):

        self.users = []
        self.records = []
        self.payments = []

        self.active_mall = None

        self.malls = {

            "1": Mall(
                "Gateway Theatre of Shopping",
                250,
                FlatRate(15)
            ),

            "2": Mall(
                "Pavilion Shopping Centre",
                180,
                HourlyRate(10)
            ),

            "3": Mall(
                "La Lucia Mall",
                150,
                CappedHourly(12, 60)
            )
        }

        self.load()
        self.default_users()

    # ==========================================
    # DEFAULT USERS
    # ==========================================

    def default_users(self):

        if not any(
            u.username == "owner"
            for u in self.users
        ):

            self.users.append(
                Owner("owner", "1234")
            )

        if not any(
            u.username == "mainadmin"
            for u in self.users
        ):

            self.users.append(
                Admin(
                    "mainadmin",
                    "1234",
                    "ALL"
                )
            )

        staff = [

            (
                "staff1",
                "1234",
                "Gateway Theatre of Shopping"
            ),

            (
                "staff2",
                "1234",
                "Pavilion Shopping Centre"
            ),

            (
                "staff3",
                "1234",
                "La Lucia Mall"
            ),

            (
                "staff4",
                "1234",
                "Gateway Theatre of Shopping"
            )
        ]

        for u, p, m in staff:

            if not any(
                x.username == u
                for x in self.users
            ):

                self.users.append(
                    Admin(u, p, m)
                )

    # ==========================================
    # SIGNUP
    # ==========================================

    def signup(self):

        print("\n===================")
        print("CUSTOMER SIGN UP")
        print("===================")

        username = input(
            "Username: "
        )

        password = input(
            "Password: "
        )

        if any(
            x.username == username
            for x in self.users
        ):

            print("User already exists")
            return

        self.users.append(
            Customer(username, password)
        )

        self.save()

        print("Account created")

    # ==========================================
    # SELECT MALL
    # ==========================================

    def select_mall(self):

        print("\n===================")
        print("SELECT MALL")
        print("===================")

        for k, m in self.malls.items():

            print(k, m.name)

        choice = input("Choice: ")

        if choice in self.malls:

            self.active_mall = self.malls[choice]

            print(
                "Active Mall:",
                self.active_mall.name
            )

        else:

            print("Invalid choice")

    # ==========================================
    # ENTRY
    # ==========================================

    def entry(self, user):

        if not self.active_mall:

            print("Select mall first")
            return

        mall = self.active_mall

        print("\n===================")
        print("VEHICLE ENTRY")
        print("===================")

        reg = input(
            "Enter Vehicle Registration: "
        ).strip().upper()

        if not reg:

            print("Invalid registration")
            return

        for r in self.records:

            if (
                r.reg == reg
                and r.exit is None
            ):

                print(
                    "Vehicle already parked"
                )

                return

        if not mall.has_space():

            print("Parking FULL")
            return

        record = Record(
            user.username,
            reg,
            mall.name
        )

        self.records.append(record)

        mall.current.append(reg)

        self.save()

        print("\nENTRY SUCCESSFUL")
        print("Vehicle:", reg)
        print("Mall:", mall.name)
        print("Entry Time:", record.entry)

    # ==========================================
    # EXIT
    # ==========================================

    def exit(self, user):

        if not self.active_mall:

            print("Select mall first")
            return

        print("\n===================")
        print("VEHICLE EXIT")
        print("===================")

        reg = input(
            "Enter Vehicle Registration: "
        ).strip().upper()

        record = None

        for r in self.records:

            if (
                r.reg == reg
                and r.user == user.username
                and r.exit is None
            ):

                record = r
                break

        if not record:

            print(
                "No active entry found"
            )

            return

        mall = self.active_mall

        record.close(mall.pricing)

        print("\n===================")
        print("PARKING BILL")
        print("===================")

        print("Vehicle:", reg)
        print("Mall:", record.mall)

        print(
            "Hours:",
            round(record.hours, 2)
        )

        print(
            "Pricing Type:",
            mall.pricing.get_type()
        )

        print(
            "Amount Due: R",
            record.fee
        )

        pay = input(
            "Pay now? (y/n): "
        ).lower()

        if pay == "y":

            self.process_payment(record)

        else:

            print(
                "Outstanding bill saved"
            )

        if reg in mall.current:

            mall.current.remove(reg)

        self.save()

    # ==========================================
    # PROCESS PAYMENT
    # ==========================================

    def process_payment(self, record):

        print("\n===================")
        print("PAYMENT")
        print("===================")

        card = input(
            "Enter Card Number: "
        )

        pin = input(
            "Enter 4 Digit PIN: "
        )

        if len(pin) != 4 or not pin.isdigit():

            print("Invalid PIN")
            return

        if len(card) < 8:

            print("Invalid Card Number")
            return

        payment = Payment(
            record.user,
            record.fee,
            record.mall
        )

        self.payments.append(payment)

        record.paid = True

        self.save()

        print("\nPAYMENT SUCCESSFUL")
        print(
            f"Amount Paid: R{record.fee}"
        )

    # ==========================================
    # OUTSTANDING PAYMENTS
    # ==========================================

    def view_outstanding(self, user):

        print("\n===================")
        print("OUTSTANDING PAYMENTS")
        print("===================")

        unpaid = []

        for r in self.records:

            if (
                r.user == user.username
                and r.exit is not None
                and not r.paid
            ):

                unpaid.append(r)

        if len(unpaid) == 0:

            print("No outstanding payments")
            return

        for i, r in enumerate(
            unpaid,
            start=1
        ):

            print("\n-------------------")

            print(f"{i}. Vehicle:", r.reg)
            print("Mall:", r.mall)
            print(f"Amount: R{r.fee}")

        choice = input(
            "\nSelect bill to pay "
            "(ENTER to cancel): "
        )

        if choice == "":
            return

        if not choice.isdigit():

            print("Invalid selection")
            return

        choice = int(choice)

        if (
            choice < 1
            or choice > len(unpaid)
        ):

            print("Invalid selection")
            return

        record = unpaid[choice - 1]

        self.process_payment(record)

    # ==========================================
    # VIEW HISTORY
    # ==========================================

    def history(self, user):

        print("\n===================")
        print("PARKING HISTORY")
        print("===================")

        found = False

        for r in self.records:

            if r.user == user.username:

                found = True

                print("\n-------------------")

                print("Vehicle:", r.reg)
                print("Mall:", r.mall)
                print("Entry:", r.entry)
                print("Exit:", r.exit)

                print(
                    "Fee: R",
                    r.fee
                )

                print(
                    "Paid:",
                    r.paid
                )

        if not found:

            print("No history found")

    # ==========================================
    # REPORTS
    # ==========================================

    def reports(self):

        print("\n===================")
        print("MALL REPORTS")
        print("===================")

        for m in self.malls.values():

            total = 0
            revenue = 0
            time = 0

            for r in self.records:

                if r.mall == m.name:

                    total += 1
                    revenue += r.fee
                    time += r.hours

            avg = (
                time / total
                if total else 0
            )

            print("\n-------------------")

            print("Mall:", m.name)

            print(
                "Vehicles:",
                total
            )

            print(
                "Revenue: R",
                revenue
            )

            print(
                "Average Hours:",
                round(avg, 2)
            )

    # ==========================================
    # ADMIN EXTRA FUNCTIONALITIES
    # ==========================================

    def view_currently_parked(self, admin_mall):
        print(f"\n========================================")
        print(f"VEHICLES CURRENTLY PARKED ({admin_mall.upper()})")
        print(f"========================================")
        
        # Cross-reference records to get active details for vehicles in this mall
        parked_vehicles = [r for r in self.records if r.mall == admin_mall and r.exit is None]
        
        if not parked_vehicles:
            print("No vehicles currently parked.")
            return

        for r in parked_vehicles:
            print(f"Registration: {r.reg} | Checked in by: {r.user} | Entry Time: {r.entry.strftime('%Y-%m-%d %H:%M:%S')}")

    def monitor_capacity(self, admin_mall):
        print(f"\n========================================")
        print(f"PARKING CAPACITY MONITOR")
        print(f"========================================")
        
        # Find the specific mall object from our system
        mall_obj = next((m for m in self.malls.values() if m.name == admin_mall), None)
        
        if mall_obj:
            current_count = len(mall_obj.current)
            available = mall_obj.capacity - current_count
            pct_full = (current_count / mall_obj.capacity) * 100
            
            print(f"Mall Name:      {mall_obj.name}")
            print(f"Total Capacity: {mall_obj.capacity} bays")
            print(f"Occupied Bays:  {current_count} bays")
            print(f"Available Bays: {available} bays")
            print(f"Utilization:    {round(pct_full, 2)}% full")
        else:
            print("Error: Mall configuration details not found.")

    def view_daily_activity(self, admin_mall):
        print(f"\n========================================")
        print(f"DAILY PARKING ACTIVITY ({admin_mall.upper()})")
        print(f"========================================")
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_records = []
        
        for r in self.records:
            if r.mall == admin_mall and r.entry.strftime("%Y-%m-%d") == today_str:
                daily_records.append(r)
                
        if not daily_records:
            print("No activity recorded for today yet.")
            return
            
        print(f"Activity logs for: {today_str}\n")
        for r in daily_records:
            status = "STILL PARKED" if r.exit is None else "EXITED"
            exit_time = r.exit.strftime('%H:%M:%S') if r.exit else "N/A"
            print(f"[{status}] Reg: {r.reg} | In: {r.entry.strftime('%H:%M:%S')} | Out: {exit_time} | Fee: R{r.fee} | Paid: {r.paid}")

    # ==========================================
    # LOGIN
    # ==========================================

    def login(self, role):

        print("\n===================")
        print(role.upper(), "LOGIN")
        print("===================")

        username = input("Username: ")

        password = input("Password: ")

        for x in self.users:

            if (
                x.username == username
                and x.password == password
                and x.role == role
            ):

                return x

        print("Login failed")
        return None

    # ==========================================
    # SAVE
    # ==========================================

    def save(self):

        data = {

            "users": [
                {k: v for k, v in vars(u).items()} # Standardized to plain dict parsing safely
                for u in self.users
            ],

            "payments": [
                vars(p)
                for p in self.payments
            ],

            "records": []

        }

        for r in self.records:

            data["records"].append({

                "user": r.user,
                "reg": r.reg,
                "mall": r.mall,

                "entry": r.entry.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

                "exit":
                r.exit.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if r.exit else None,

                "hours": r.hours,
                "fee": r.fee,
                "paid": r.paid
            })

        with open("data.json", "w") as f:

            json.dump(
                data,
                f,
                indent=4
            )

    # ==========================================
    # LOAD
    # ==========================================

    def load(self):

        if not os.path.exists(
            "data.json"
        ):

            return

        try:

            with open(
                "data.json",
                "r"
            ) as f:

                data = json.load(f)

        except:

            return

        for u in data.get(
            "users",
            []
        ):

            if u["role"] == "customer":

                self.users.append(
                    Customer(
                        u["username"],
                        u["password"]
                    )
                )

            elif u["role"] == "admin":

                self.users.append(
                    Admin(
                        u["username"],
                        u["password"],
                        u.get("mall", "ALL")
                    )
                )

            elif u["role"] == "owner":

                self.users.append(
                    Owner(
                        u["username"],
                        u["password"]
                    )
                )

        for r in data.get(
            "records",
            []
        ):

            record = Record(
                r["user"],
                r["reg"],
                r["mall"]
            )

            record.entry = datetime.strptime(
                r["entry"],
                "%Y-%m-%d %H:%M:%S"
            )

            if r["exit"]:

                record.exit = datetime.strptime(
                    r["exit"],
                    "%Y-%m-%d %H:%M:%S"
                )

            record.hours = r["hours"]
            record.fee = r["fee"]
            record.paid = r["paid"]

            self.records.append(record)
            
            # Repopulate active memory tracking list for malls
            if record.exit is None:
                for m in self.malls.values():
                    if m.name == record.mall:
                        m.current.append(record.reg)

        for p in data.get(
            "payments",
            []
        ):

            payment = Payment(
                p["user"],
                p["amount"],
                p["mall"]
            )

            payment.date = p["date"]

            self.payments.append(payment)

    # ==========================================
    # RUN
    # ==========================================

    def run(self):

        while True:

            print("\n===================")
            print("KZN PARKING SYSTEM")
            print("===================")

            print("1. Customer Sign Up")
            print("2. Customer Login")
            print("3. Admin Login")
            print("4. Owner Login")
            print("5. Exit")

            choice = input("> ")

            # ==========================
            # SIGNUP
            # ==========================

            if choice == "1":

                self.signup()

            # CUSTOMER
            

            elif choice == "2":

                user = self.login(
                    "customer"
                )

                if user:

                    while True:

                        print(
                            "CUSTOMER MENU"
                        )

                        print(
                            "1. Select Mall"
                        )

                        print(
                            "2. Vehicle Entry"
                        )

                        print(
                            "3. Vehicle Exit"
                        )

                        print(
                            "4. Outstanding Bills"
                        )

                        print(
                            "5. Parking History"
                        )

                        print(
                            "6. Logout"
                        )

                        c = input("> ")

                        if c == "1":

                            self.select_mall()

                        elif c == "2":

                            self.entry(user)

                        elif c == "3":

                            self.exit(user)

                        elif c == "4":

                            self.view_outstanding(
                                user
                            )

                        elif c == "5":

                            self.history(user)

                        else:

                            break

            # ADMIN

            elif choice == "3":

                user = self.login(
                    "admin"
                )

                if user:
                    print("\nADMIN LOGIN SUCCESSFUL")
                    
                    while True:
                        print("\n==============================")
                        print(f"ADMIN MENU: {user.username.upper()}")
                        print(f"Assigned Mall: {user.mall}")
                        print("==============================")
                        print("1. View Currently Parked Vehicles")
                        print("2. Monitor Parking Capacity")
                        print("3. View Daily Parking Activity")
                        print("4. Logout")
                        
                        admin_choice = input("> ")
                        
                        if admin_choice == "1":
                            if user.mall == "ALL":
                                print("\nMain Admin: Please log in with a location staff account to view specific properties.")
                            else:
                                self.view_currently_parked(user.mall)
                                
                        elif admin_choice == "2":
                            if user.mall == "ALL":
                                # Quick iteration to show all malls if it's the main admin
                                for m_key in self.malls:
                                    self.monitor_capacity(self.malls[m_key].name)
                            else:
                                self.monitor_capacity(user.mall)
                                
                        elif admin_choice == "3":
                            if user.mall == "ALL":
                                print("\nMain Admin: Please log in with a location staff account to view specific timeline metrics.")
                            else:
                                self.view_daily_activity(user.mall)
                                
                        elif admin_choice == "4":
                            print("Logged out of Admin Space.")
                            break
                        else:
                            print("Invalid selection.")

            # OWNER
            
            elif choice == "4":

                user = self.login(
                    "owner"
                )

                if user:

                    self.reports()

            # EXIT

            else:

                print("System Closed")
                break

# START

if __name__ == "__main__":

    ParkingSystem().run()