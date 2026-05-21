import json
import os
from datetime import datetime
import math

# --- PRICING STRATEGIES ---
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
        return min(math.ceil(hours) * self.rate, self.cap)

    def get_type(self):
        return "Hourly Rate with Cap"


# --- LANDSCAPE PROPERTIES ---
class Mall:
    def __init__(self, name, capacity, pricing):
        self.name = name
        self.capacity = capacity
        self.pricing = pricing
        self.current = []

    def has_space(self):
        return len(self.current) < self.capacity


# --- USER ENTITIES ---
class User:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


class Customer(User):
    def __init__(self, username, password):
        super().__init__(username, password, "customer")


class Admin(User):
    def __init__(self, username, password, mall="ALL"):
        super().__init__(username, password, "admin")
        self.mall = mall


class Owner(User):
    def __init__(self, username, password):
        super().__init__(username, password, "owner")


# --- RECORD TRANSACTION ---
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
        self.hours = (self.exit - self.entry).total_seconds() / 3600
        self.fee = pricing.calculate_fee(self.hours)


# --- TRANS-LOGS ---
class Payment:
    def __init__(self, user, amount, mall):
        self.user = user
        self.amount = amount
        self.mall = mall
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# --- CORE PARKING UTILITY ---
class ParkingSystem:
    def __init__(self):
        self.users = []
        self.records = []
        self.payments = []

        self.malls = {
            "1": Mall("Gateway Theatre of Shopping", 250, FlatRate(15)),
            "2": Mall("Pavilion Shopping Centre", 180, HourlyRate(10)),
            "3": Mall("La Lucia Mall", 150, CappedHourly(12, 60))
        }

        self.load()
        self.default_users()

    def default_users(self):
        if not any(u.username == "owner" for u in self.users):
            self.users.append(Owner("owner", "1234"))

        if not any(u.username == "mainadmin" for u in self.users):
            self.users.append(Admin("mainadmin", "1234", "ALL"))

        staff = [
            ("staff1", "1234", "Gateway Theatre of Shopping"),
            ("staff2", "1234", "Pavilion Shopping Centre"),
            ("staff3", "1234", "La Lucia Mall"),
            ("staff4", "1234", "Gateway Theatre of Shopping")
        ]

        for u, p, m in staff:
            if not any(x.username == u for x in self.users):
                self.users.append(Admin(u, p, m))

    def signup(self):
        print("\n--- CUSTOMER SIGN UP ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        if not username or not password:
            print("Username or password cannot be blank.")
            return

        if any(x.username == username for x in self.users):
            print("User already exists!")
            return

        self.users.append(Customer(username, password))
        self.save()
        print("Account created successfully!")

    def select_mall(self):
        print("\n--- AVAILABLE MALLS ---")
        for k, m in self.malls.items():
            print(f"{k}. {m.name}")

        choice = input("Choice: ").strip()
        if choice in self.malls:
            return self.malls[choice]
        print("Invalid choice.")
        return None

    def entry(self, user):
        print("\n--- VEHICLE CHECK-IN ---")
        mall = self.select_mall()
        if not mall:
            return

        reg = input("Enter Vehicle Registration: ").strip().upper()
        if not reg:
            print("Invalid registration entry.")
            return

        # Check if vehicle is already inside ANY mall active tracking loop
        for r in self.records:
            if r.reg == reg and r.exit is None:
                print(f"Vehicle already parked inside: {r.mall}")
                return

        if not mall.has_space():
            print("Drop operations halted: Parking capacity reached full utilization.")
            return

        record = Record(user.username, reg, mall.name)
        self.records.append(record)
        mall.current.append(reg)
        self.save()

        print("\nENTRY SUCCESSFUL")
        print("Vehicle:", reg)
        print("Location:", mall.name)
        print("Timestamp:", record.entry.strftime('%Y-%m-%d %H:%M:%S'))

    def exit(self, user):
        print("\n--- VEHICLE CHECK-OUT ---")
        reg = input("Enter Vehicle Registration: ").strip().upper()

        record = None
        for r in self.records:
            if r.reg == reg and r.user == user.username and r.exit is None:
                record = r
                break

        if not record:
            print("No active entry matching your credentials found for this vehicle.")
            return

        # Dynamically link the correct mall configurations via recorded asset string
        mall = next((m for m in self.malls.values() if m.name == record.mall), None)
        if not mall:
            print("Configuration mapping fault. Contact support.")
            return

        record.close(mall.pricing)

        print("\n--- PARKING BILL ---")
        print("Vehicle:", reg)
        print("Mall Location:", record.mall)
        print("Duration Calculated:", round(record.hours, 2), "Hours")
        print("Billing Strategy applied:", mall.pricing.get_type())
        print("Total Processing Fee: R", record.fee)

        pay = input("Settle invoice balance now? (y/n): ").lower().strip()
        if pay == "y":
            self.process_payment(record)
        else:
            print("Outstanding balance logged against user account profile.")

        if reg in mall.current:
            mall.current.remove(reg)

        self.save()

    def process_payment(self, record):
        print("\n--- PAYMENT STAGE ---")
        card = input("Enter Card Number: ").strip()
        pin = input("Enter 4 Digit PIN: ").strip()

        if len(pin) != 4 or not pin.isdigit():
            print("Declined: Invalid PIN Format.")
            return

        if len(card) < 8 or not card.isdigit():
            print("Declined: Invalid Primary Account Number Configuration.")
            return

        payment = Payment(record.user, record.fee, record.mall)
        self.payments.append(payment)
        record.paid = True
        self.save()
        print(f"\nPAYMENT SUCCESSFUL! R{record.fee} received cleanly.")

    def view_outstanding(self, user):
        print("\n--- OUTSTANDING BILLING LOGS ---")
        unpaid = [r for r in self.records if r.user == user.username and r.exit is not None and not r.paid]

        if not unpaid:
            print("No outstanding payments due.")
            return

        for i, r in enumerate(unpaid, start=1):
            print(f"{i}. Vehicle: {r.reg} | Mall: {r.mall} | Due: R{r.fee}")

        choice = input("\nSelect invoice sequence to settle (Press ENTER to close out loop): ").strip()
        if not choice:
            return

        if not choice.isdigit() or not (1 <= int(choice) <= len(unpaid)):
            print("Invalid numerical reference chosen.")
            return

        self.process_payment(unpaid[int(choice) - 1])

    def history(self, user):
        print("\n--- ARCHIVED PARKING HISTOGRAMS ---")
        found = False
        for r in self.records:
            if r.user == user.username:
                found = True
                status = "Paid" if r.paid else "Outstanding"
                exit_str = r.exit.strftime('%Y-%m-%d %H:%M:%S') if r.exit else "Active Session"
                print(f"\nVehicle: {r.reg} | Mall: {r.mall}")
                print(f"  Timeline: [{r.entry.strftime('%H:%M:%S')}] -> [{exit_str}]")
                print(f"  Accounting status: R{r.fee} Total Charges | {status}")
        if not found:
            print("No chronological records tracked under this account profile identifier.")

    def reports(self):
        print("\n=== SYSTEM OVERVIEW GENERAL AUDITS ===")
        for m in self.malls.values():
            total_visits = 0
            closed_visits = 0
            revenue = 0
            cumulative_hours = 0

            for r in self.records:
                if r.mall == m.name:
                    total_visits += 1
                    revenue += r.fee
                    if r.exit is not None:
                        closed_visits += 1
                        cumulative_hours += r.hours

            avg = (cumulative_hours / closed_visits) if closed_visits > 0 else 0

            print(f"\nMall Identity Properties: {m.name}")
            print(f"  Aggregated Traffic Metrics: {total_visits} entries processed")
            print(f"  Gross Revenue Tracked:      R {revenue}")
            print(f"  Average Completed Stay:     {round(avg, 2)} hours")

    def view_currently_parked(self, admin_mall):
        print(f"\n--- ACTIVE BAY LEASES ({admin_mall.upper()}) ---")
        parked_vehicles = [r for r in self.records if r.mall == admin_mall and r.exit is None]

        if not parked_vehicles:
            print("No active vehicles monitored in structure current pools.")
            return

        for r in parked_vehicles:
            print(f"Reg Mark: {r.reg} | Driver: {r.user} | Entry Window: {r.entry.strftime('%Y-%m-%d %H:%M:%S')}")

    def monitor_capacity(self, admin_mall):
        print(f"\n--- REAL-TIME VOLUMETRICS ---")
        mall_obj = next((m for m in self.malls.values() if m.name == admin_mall), None)

        if mall_obj:
            current_count = len(mall_obj.current)
            available = mall_obj.capacity - current_count
            pct_full = (current_count / mall_obj.capacity) * 100

            print(f"Property Entity:   {mall_obj.name}")
            print(f"Hardware Maximum:  {mall_obj.capacity} bays configured")
            print(f"Committed/Leased:  {current_count} units occupied")
            print(f"Physical Free space:{available} footprints clear")
            print(f"Utilization Ratio: {round(pct_full, 2)}% overall saturation")

    def view_daily_activity(self, admin_mall):
        print(f"\n--- DAILY LEDGER EVENT STRINGS ({admin_mall.upper()}) ---")
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_records = [r for r in self.records if r.mall == admin_mall and r.entry.strftime("%Y-%m-%d") == today_str]

        if not daily_records:
            print("No logistical telemetry items written to transaction logs for today's timeline.")
            return

        for r in daily_records:
            status = "STILL PARKED" if r.exit is None else "EXITED"
            exit_time = r.exit.strftime('%H:%M:%S') if r.exit else "N/A"
            print(f"[{status}] Reg: {r.reg} | In: {r.entry.strftime('%H:%M:%S')} | Out: {exit_time} | Paid: {r.paid}")

    def login(self, role):
        print(f"\n--- {role.upper()} AUTHENTICATION DISPATCH ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        for x in self.users:
            if x.username == username and x.password == password and x.role == role:
                return x
        print("Access Refused: Evaluation credentials mismatch structural entries.")
        return None

    def save(self):
        data = {
            "users": [vars(u) for u in self.users],
            "payments": [vars(p) for p in self.payments],
            "records": []
        }

        for r in self.records:
            data["records"].append({
                "user": r.user,
                "reg": r.reg,
                "mall": r.mall,
                "entry": r.entry.strftime("%Y-%m-%d %H:%M:%S"),
                "exit": r.exit.strftime("%Y-%m-%d %H:%M:%S") if r.exit else None,
                "hours": r.hours,
                "fee": r.fee,
                "paid": r.paid
            })

        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        if not os.path.exists("data.json"):
            return

        try:
            with open("data.json", "r") as f:
                data = json.load(f)
        except Exception:
            return

        for u in data.get("users", []):
            role = u.get("role")
            if role == "customer":
                self.users.append(Customer(u["username"], u["password"]))
            elif role == "admin":
                self.users.append(Admin(u["username"], u["password"], u.get("mall", "ALL")))
            elif role == "owner":
                self.users.append(Owner(u["username"], u["password"]))

        for r in data.get("records", []):
            record = Record(r["user"], r["reg"], r["mall"])
            record.entry = datetime.strptime(r["entry"], "%Y-%m-%d %H:%M:%S")
            if r["exit"]:
                record.exit = datetime.strptime(r["exit"], "%Y-%m-%d %H:%M:%S")
            record.hours = r["hours"]
            record.fee = r["fee"]
            record.paid = r["paid"]
            self.records.append(record)

            if record.exit is None:
                for m in self.malls.values():
                    if m.name == record.mall and record.reg not in m.current:
                        m.current.append(record.reg)

        for p in data.get("payments", []):
            payment = Payment(p["user"], p["amount"], p["mall"])
            payment.date = p["date"]
            self.payments.append(payment)

    def run(self):
        while True:
            print("\n===============================")
            print("     KZN PARKING MASTERWAY     ")
            print("===============================")
            print("1. Customer Sign Up")
            print("2. Customer Login")
            print("3. Admin Login")
            print("4. Owner Login")
            print("5. Terminate Engine")

            choice = input("> ").strip()

            if choice == "1":
                self.signup()
            elif choice == "2":
                user = self.login("customer")
                if user:
                    while True:
                        print("\n--- CUSTOMER MANAGEMENT CONTROLS ---")
                        print("1. Vehicle Entry Check")
                        print("2. Vehicle Exit Settle")
                        print("3. View Unpaid Ledger BAL")
                        print("4. Run Session History Logs")
                        print("5. Sign-off Session")
                        c = input("> ").strip()

                        if c == "1":
                            self.entry(user)
                        elif c == "2":
                            self.exit(user)
                        elif c == "3":
                            self.view_outstanding(user)
                        elif c == "4":
                            self.history(user)
                        else:
                            break
            elif choice == "3":
                user = self.login("admin")
                if user:
                    while True:
                        print(f"\n--- PROPERTY CONSOLE: {user.username.upper()} ---")
                        print(f"Location Domain Matrix: {user.mall}")
                        print("1. Track Floor Footprints")
                        print("2. Infrastructure Capacity Meter")
                        print("3. Check Daily Activity Sequence")
                        print("4. Safe Logout Command")
                        admin_choice = input("> ").strip()

                        if admin_choice == "1":
                            if user.mall == "ALL":
                                print("\nAccess Exception: Elevate via local base station user context.")
                            else:
                                self.view_currently_parked(user.mall)
                        elif admin_choice == "2":
                            if user.mall == "ALL":
                                for m_key in self.malls:
                                    self.monitor_capacity(self.malls[m_key].name)
                            else:
                                self.monitor_capacity(user.mall)
                        elif admin_choice == "3":
                            if user.mall == "ALL":
                                print("\nAccess Exception: Run metrics scoping specific local properties.")
                            else:
                                self.view_daily_activity(user.mall)
                        else:
                            break
            elif choice == "4":
                user = self.login("owner")
                if user:
                    self.reports()
            elif choice == "5":
                print("\nShutting down engine matrix loops cleanly. Goodbye.")
                break
            else:
                print("Invalid operational command string entered.")


if __name__ == "__main__":
    ParkingSystem().run()