import json
import os
from datetime import datetime
import math

# ==============================================================================
# PRICING STRATEGIES (STRATEGY PATTERN LOGIC)
# Defines polymorphic components responsible for processing financial calculations.
# Dynamic runtime evaluation allows properties to switch billing models effortlessly.
# ==============================================================================

class PricingStrategy:
    """
    Abstract interface detailing core transactional blueprints.
    Guarantees consistent runtime behaviors across varying tariff regimes.
    """
    def calculate_fee(self, hours):
        pass

    def get_type(self):
        pass


class FlatRate(PricingStrategy):
    """
    Static single-tier billing. Offers zero-variance entry regardless of operational
    duration; optimal for high-capacity commuter domains where rotation is secondary.
    """
    def __init__(self, fee):
        self.fee = fee

    def calculate_fee(self, hours):
        return self.fee

    def get_type(self):
        return "Flat Rate"


class HourlyRate(PricingStrategy):
    """
    Linear progressive tariff layout. Scales proportionally to elapsed duration cycles;
    utilizes structural ceiling rounding via ceiling evaluations to enforce strict hourly slices.
    """
    def __init__(self, rate):
        self.rate = rate

    def calculate_fee(self, hours):
        return math.ceil(hours) * self.rate

    def get_type(self):
        return "Hourly Rate"


class CappedHourly(PricingStrategy):
    """
    Hybrid tier matrix combining variable scalability with an absolute threshold cap.
    Protects long-term occupants from infinite charge aggregation, stabilizing transaction risk.
    """
    def __init__(self, rate, cap):
        self.rate = rate
        self.cap = cap

    def calculate_fee(self, hours):
        return min(math.ceil(hours) * self.rate, self.cap)

    def get_type(self):
        return "Hourly Rate with Cap"


# ==============================================================================
# LANDSCAPE PROPERTIES (STRUCTURAL INFRASTRUCTURE NODES)
# Data nodes representing physical entities with capacity maps and billing behaviors.
# ==============================================================================

class Mall:
    """
    Structural asset entity. Controls internal allocation tables, monitors resource 
    saturation metrics, and links instance properties to their respective pricing nodes.
    """
    def __init__(self, name, capacity, pricing):
        self.name = name
        self.capacity = capacity
        self.pricing = pricing
        self.current = []  # Runtime track vector monitoring active spatial commitments

    def has_space(self):
        # Operational query checking if current entity allocation bounds are exceeded
        return len(self.current) < self.capacity


# ==============================================================================
# USER ENTITIES (AUTHENTICATION & ACCESS PRIORITY HIERARCHIES)
# Encapsulates behavioral configurations across permission-sensitive domains.
# ==============================================================================

class User:
    """Base user data structure encapsulating authentication schemas and profile tags."""
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role


class Customer(User):
    """Client-facing user node. Permissions are limited to session check-ins and payments."""
    def __init__(self, username, password):
        super().__init__(username, password, "customer")


class Admin(User):
    """
    Site manager sub-entity. Possesses visibility bounds restricted either to local 
    property environments or configured global scopes ("ALL").
    """
    def __init__(self, username, password, mall="ALL"):
        super().__init__(username, password, "admin")
        self.mall = mall


class Owner(User):
    """Root superuser configuration. Bypasses domain checks to aggregate analytical audits."""
    def __init__(self, username, password):
        super().__init__(username, password, "owner")


# ==============================================================================
# TRANSACTIONAL RECORD ENGINE (STATE TRACKERS & LOGGING COROUTINES)
# Tracks timelines and financial calculations during system check-ins.
# ==============================================================================

class Record:
    """
    Persistent log tracking individual terminal sessions.
    Maintains timeline markers from initial generation down to calculation cycles.
    """
    def __init__(self, user, reg, mall):
        self.user = user
        self.reg = reg
        self.mall = mall
        self.entry = datetime.now()  # High-resolution time window capture on node creation
        self.exit = None
        self.hours = 0
        self.fee = 0
        self.paid = False

    def close(self, pricing):
        # Register teardown window frame timestamp
        self.exit = datetime.now()
        # Compute delta transform isolating raw hours via precision float separation
        self.hours = (self.exit - self.entry).total_seconds() / 3600
        # Pipeline elapsed delta into bound strategy processor to resolve balance
        self.fee = pricing.calculate_fee(self.hours)


class Payment:
    """Immutable ledger record representing processed, verified currency entries."""
    def __init__(self, user, amount, mall):
        self.user = user
        self.amount = amount
        self.mall = mall
        self.date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==============================================================================
# CORE PARKING UTILITY (THE CORE SIMULATION CONTROLLER)
# Orchestrates active states, files, inputs, and validation loops.
# ==============================================================================

class ParkingSystem:
    """
    Central processing engine. Handles input/output routines, data marshaling, 
    and session state tracking for all active assets.
    """
    def __init__(self):
        self.users = []      # Dynamic runtime pool containing verified identity profiles
        self.records = []    # Historical transaction strings tracking all bay rentals
        self.payments = []   # Financial processing streams tracking settlement activity

        # Environmental Node Matrix Generation
        self.malls = {
            "1": Mall("Gateway Theatre of Shopping", 250, FlatRate(15)),
            "2": Mall("Pavilion Shopping Centre", 180, HourlyRate(10)),
            "3": Mall("La Lucia Mall", 150, CappedHourly(12, 60))
        }

        self.load()           # Parse structural data states from disk storage
        self.default_users()  # Inject default system and admin user roles

    def default_users(self):
        # Verify if master superuser credentials are initialized inside data array
        if not any(u.username == "owner" for u in self.users):
            self.users.append(Owner("owner", "1234"))

        # Verify presence of overarching system administrator actor profile
        if not any(u.username == "mainadmin" for u in self.users):
            self.users.append(Admin("mainadmin", "1234", "ALL"))

        # Array holding regional local property security context assignments
        staff = [
            ("staff1", "1234", "Gateway Theatre of Shopping"),
            ("staff2", "1234", "Pavilion Shopping Centre"),
            ("staff3", "1234", "La Lucia Mall"),
            ("staff4", "1234", "Gateway Theatre of Shopping")
        ]

        # Scan and register missing localized admin entities to keep domain scope correct
        for u, p, m in staff:
            if not any(x.username == u for x in self.users):
                self.users.append(Admin(u, p, m))

    def signup(self):
        print("\nCUSTOMER SIGN UP")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        # Sanity check: abort registration routines if character data is empty
        if not username or not password:
            print("Username or password cannot be blank.")
            return

        # Conflict verification query to block duplicate identification profiles
        if any(x.username == username for x in self.users):
            print("User already exists!")
            return

        # Instantiate new client profile context block and serialize state to JSON disk
        self.users.append(Customer(username, password))
        self.save()  
        print("Account created successfully!")

    def forgot_password(self):
        print("\nACCOUNT PASSWORD RECOVERY")
        username = input("Enter your username: ").strip()

        # Search memory arrays matching specified unique profile identity string
        user = next((x for x in self.users if x.username == username), None)

        # Handle lookup mismatch errors safely without breaking engine execution
        if not user:
            print("Error: Username identifier not found in the system.")
            return

        print(f"Account verified! (Role: {user.role.upper()})")
        new_password = input("Enter your new password: ").strip()

        # Block zero-character string submission attempts to maintain secure accounts
        if not new_password:
            print("Password field cannot be blank.")
            return

        # Mutate object reference memory variables with newly validated values
        user.password = new_password
        self.save()
        print("Success: Password has been updated. You can now log in.")

    def select_mall(self):
        print("\nAVAILABLE MALLS")
        for k, m in self.malls.items():
            print(f"{k}. {m.name}")

        choice = input("Choice: ").strip()
        # Direct lookup mapping user raw input indexes to actual memory map addresses
        if choice in self.malls:
            return self.malls[choice]
        print("Invalid choice.")
        return None

    def entry(self, user):
        print("\nVEHICLE CHECK-IN")
        mall = self.select_mall()
        if not mall:
            return

        # Clean string inputs for uniform internal tracking codes
        reg = input("Enter Vehicle Registration: ").strip().upper()
        if not reg:
            print("Invalid registration entry.")
            return

        # Structural integrity check: verify vehicle tracking index isn't already active in any structure
        for r in self.records:
            if r.reg == reg and r.exit is None:
                print(f"Vehicle already parked inside: {r.mall}")
                return

        # Volumetric threshold gate blocking new arrivals when capacity calculations equal zero
        if not mall.has_space():
            print("Drop operations halted: Parking capacity reached full utilization.")
            return

        # Create new unique entry object and append tracking mark to property current list
        record = Record(user.username, reg, mall.name)
        self.records.append(record)
        mall.current.append(reg)
        self.save()

        print("\nENTRY SUCCESSFUL")
        print("Vehicle:", reg)
        print("Location:", mall.name)
        print("Timestamp:", record.entry.strftime('%Y-%m-%d %H:%M:%S'))

    def exit(self, user):
        print("\nVEHICLE CHECK-OUT")
        reg = input("Enter Vehicle Registration: ").strip().upper()

        # Query transactional array matching registration target, owner ID, and empty close stamp
        record = None
        for r in self.records:
            if r.reg == reg and r.user == user.username and r.exit is None:
                record = r
                break

        # Abort operational logic if the data entity lookup comes up empty
        if not record:
            print("No active entry matching your credentials found for this vehicle.")
            return

        # Inverse mapping: pinpoint exact physical node where tracking sequence originally started
        mall = next((m for m in self.malls.values() if m.name == record.mall), None)
        if not mall:
            print("Configuration mapping fault. Contact support.")
            return

        # Process mathematical duration conversions and call strategy parameters
        record.close(mall.pricing)

        print("\nPARKING BILL")
        print("Vehicle:", reg)
        print("Mall Location:", record.mall)
        print("Duration Calculated:", round(record.hours, 2), "Hours")
        print("Billing Strategy applied:", mall.pricing.get_type())
        print("Total Processing Fee: R", record.fee)

        pay = input("Settle invoice balance now? (y/n): ").lower().strip()
        if pay == "y":
            self.process_payment(record)
        else:
            # Leave paid state flag set to false, storing the uncollected balance in the ledger tracking array
            print("Outstanding balance logged against user account profile.")

        # De-allocate physical asset marker footprint out of mall active track array
        if reg in mall.current:
            mall.current.remove(reg)

        self.save()

    def process_payment(self, record):
        print("\nPAYMENT STAGE")
        card = input("Enter Card Number: ").strip()
        pin = input("Enter 4 Digit PIN: ").strip()

        # Security check: ensure user card inputs meet expected character length parameters
        if len(pin) != 4 or not pin.isdigit():
            print("Declined: Invalid PIN Format.")
            return

        if len(card) < 8 or not card.isdigit():
            print("Declined: Invalid Primary Account Number Configuration.")
            return

        # Generate an unchangeable payment event object and store inside memory system array
        payment = Payment(record.user, record.fee, record.mall)
        self.payments.append(payment)
        # Flip internal record variable state flag to true
        record.paid = True
        self.save()
        print(f"\nPAYMENT SUCCESSFUL! R{record.fee} received cleanly.")

    def view_outstanding(self, user):
        print("\nOUTSTANDING BILLING LOGS")
        # List comprehension filtering for matching user items that have closed sessions but remain unpaid
        unpaid = [r for r in self.records if r.user == user.username and r.exit is not None and not r.paid]

        if not unpaid:
            print("No outstanding payments due.")
            return

        # Enumerate over array entries to format structural elements with an user index counter
        for i, r in enumerate(unpaid, start=1):
            print(f"{i}. Vehicle: {r.reg} | Mall: {r.mall} | Due: R{r.fee}")

        choice = input("\nSelect invoice sequence to settle (Press ENTER to close out loop): ").strip()
        if not choice:
            return

        # Boundary logic evaluating user input choices against available index lengths
        if not choice.isdigit() or not (1 <= int(choice) <= len(unpaid)):
            print("Invalid numerical reference chosen.")
            return

        # Route specified target index cleanly back into processing pipeline
        self.process_payment(unpaid[int(choice) - 1])

    def history(self, user):
        print("\nARCHIVED PARKING HISTOGRAMS")
        found = False
        # Sequentially evaluate all records to extract past structural logs for matching actors
        for r in self.records:
            if r.user == user.username:
                found = True
                # Conditional inline assignment to configure output display values dynamically
                status = "Paid" if r.paid else "Outstanding"
                exit_str = r.exit.strftime('%Y-%m-%d %H:%M:%S') if r.exit else "Active Session"
                print(f"\nVehicle: {r.reg} | Mall: {r.mall}")
                print(f"  Timeline: [{r.entry.strftime('%H:%M:%S')}] -> [{exit_str}]")
                print(f"  Accounting status: R{r.fee} Total Charges | {status}")
        if not found:
            print("No chronological records tracked under this account profile identifier.")

    def reports(self):
        print("\n______________________________________")
        print("     SYSTEM OVERVIEW GENERAL AUDITS    ")
        print("______________________________________")
        # Loop over property keys to sum performance data across isolated zones
        for m in self.malls.values():
            total_visits = 0
            closed_visits = 0
            revenue = 0
            cumulative_hours = 0

            # Step through system history files to isolate context data for current mall node
            for r in self.records:
                if r.mall == m.name:
                    total_visits += 1
                    revenue += r.fee
                    # Accumulate tracking performance metrics for completed stay files
                    if r.exit is not None:
                        closed_visits += 1
                        cumulative_hours += r.hours

            # Mathematical safety gate logic tracking averages without triggering divide-by-zero exceptions
            avg = (cumulative_hours / closed_visits) if closed_visits > 0 else 0

            print(f"\nMall Identity Properties: {m.name}")
            print(f"  Aggregated Traffic Metrics: {total_visits} entries processed")
            print(f"  Gross Revenue Tracked:      R {revenue}")
            print(f"  Average Completed Stay:     {round(avg, 2)} hours")

    def view_currently_parked(self, admin_mall):
        print(f"\nACTIVE BAY LEASES ({admin_mall.upper()})")
        # Isolate tracking object footprints whose destination property handles match and lack checkout values
        parked_vehicles = [r for r in self.records if r.mall == admin_mall and r.exit is None]

        if not parked_vehicles:
            print("No active vehicles monitored in structure current pools.")
            return

        for r in parked_vehicles:
            print(f"Reg Mark: {r.reg} | Driver: {r.user} | Entry Window: {r.entry.strftime('%Y-%m-%d %H:%M:%S')}")

    def monitor_capacity(self, admin_mall):
        print(f"\nREAL-TIME VOLUMETRICS")
        # Map localized admin property name directly to the core infrastructure memory handle
        mall_obj = next((m for m in self.malls.values() if m.name == admin_mall), None)

        if mall_obj:
            # Query runtime tracker array size to analyze structural deployment saturation profiles
            current_count = len(mall_obj.current)
            available = mall_obj.capacity - current_count
            pct_full = (current_count / mall_obj.capacity) * 100

            print(f"Property Entity:   {mall_obj.name}")
            print(f"Hardware Maximum:  {mall_obj.capacity} bays configured")
            print(f"Committed/Leased:  {current_count} units occupied")
            print(f"Physical Free space:{available} footprints clear")
            print(f"Utilization Ratio: {round(pct_full, 2)}% overall saturation")

    def view_daily_activity(self, admin_mall):
        print(f"\nDAILY LEDGER EVENT STRINGS ({admin_mall.upper()})")
        today_str = datetime.now().strftime("%Y-%m-%d")
        # Extract logistical records matching the exact target environment and current date stamp
        daily_records = [r for r in self.records if r.mall == admin_mall and r.entry.strftime("%Y-%m-%d") == today_str]

        if not daily_records:
            print("No logistical telemetry items written to transaction logs for today's timeline.")
            return

        for r in daily_records:
            # Format state trackers context output based on active/inactive tracking states
            status = "STILL PARKED" if r.exit is None else "EXITED"
            exit_time = r.exit.strftime('%H:%M:%S') if r.exit else "N/A"
            print(f"[{status}] Reg: {r.reg} | In: {r.entry.strftime('%H:%M:%S')} | Out: {exit_time} | Paid: {r.paid}")

    def login(self, role):
        print(f"\n{role.upper()} AUTHENTICATION DISPATCH")
        username = input("Username: ").strip()
        password = input("Password: ").strip()

        # Iterate over structural identity map objects verifying key credentials and role scope
        for x in self.users:
            if x.username == username and x.password == password and x.role == role:
                return x # Return found object reference directly as authenticated scope context token
        print("Access Refused: Evaluation credentials mismatch structural entries.")
        return None

    # ==============================================================================
    # DATA PERSISTENCE LAYER (JSON DATA MARSHALING AND HYDRATION COROUTINES)
    # Serialization routines managing state conversion to persistent disk storage.
    # ==============================================================================

    def save(self):
        # Convert internal tracking object array structures directly down into flat standard primitive formats
        data = {
            "users": [vars(u) for u in self.users],
            "payments": [vars(p) for p in self.payments],
            "records": []
        }

        # Convert complex datetime structural objects into clean strings to avoid JSON compile errors
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

        # Open file write streaming stream, overwriting old disk states with current system snapshots
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)

    def load(self):
        # Gracefully halt file parse execution if target datastore does not exist on local disk paths
        if not os.path.exists("data.json"):
            return

        try:
            with open("data.json", "r") as f:
                data = json.load(f)
        except Exception:
            return

        # Re-populate runtime context arrays with their corresponding polymorph account object classes
        for u in data.get("users", []):
            role = u.get("role")
            if role == "customer":
                self.users.append(Customer(u["username"], u["password"]))
            elif role == "admin":
                self.users.append(Admin(u["username"], u["password"], u.get("mall", "ALL")))
            elif role == "owner":
                self.users.append(Owner(u["username"], u["password"]))

        # Restore transaction log objects and parse raw timeline strings back into high-precision types
        for r in data.get("records", []):
            record = Record(r["user"], r["reg"], r["mall"])
            record.entry = datetime.strptime(r["entry"], "%Y-%m-%d %H:%M:%S")
            if r["exit"]:
                record.exit = datetime.strptime(r["exit"], "%Y-%m-%d %H:%M:%S")
            record.hours = r["hours"]
            record.fee = r["fee"]
            record.paid = r["paid"]
            self.records.append(record)

            # Re-fill the mall tracking lists for any checked-in logs that never completed check-out sequences
            if record.exit is None:
                for m in self.malls.values():
                    if m.name == record.mall and record.reg not in m.current:
                        m.current.append(record.reg)

        # Restore payment streaming history array logs back into application state memory arrays
        for p in data.get("payments", []):
            payment = Payment(p["user"], p["amount"], p["mall"])
            payment.date = p["date"]
            self.payments.append(payment)


    # ==============================================================================
    # APPLICATION RUNTIME LOOP (CONSOLE USER MENU ROUTER)
    # Manages user experience routing and continuous update loops.
    # ==============================================================================

    def run(self):
        """Launches continuous application frame processing loops."""
        while True:
            print("\n_______________________________")
            print("     KZN PARKING MASTERWAY     ")
            print("_______________________________")
            print("1. Customer Sign Up")
            print("2. Customer Login")
            print("3. Admin Login")
            print("4. Owner Login")
            print("5. Forgot Password")
            print("6. Terminate Engine")

            choice = input("> ").strip()

            if choice == "1":
                self.signup()
            elif choice == "2":
                user = self.login("customer")
                if user:
                    # Traps operation execution in continuous frame update loops until user signs off session
                    while True:
                        print("\nCUSTOMER MANAGEMENT CONTROLS")
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
                            # Break command escapes out of active nested client logic frame structure
                            break
            elif choice == "3":
                user = self.login("admin")
                if user:
                    while True:
                        print(f"\nPROPERTY CONSOLE: {user.username.upper()}")
                        print(f"Location Domain Matrix: {user.mall}")
                        print("1. Track Floor Footprints")
                        print("2. Infrastructure Capacity Meter")
                        print("3. Check Daily Activity Sequence")
                        print("4. Safe Logout Command")
                        admin_choice = input("> ").strip()

                        if admin_choice == "1":
                            # Security intercept preventing macro admins from reading localized track channels
                            if user.mall == "ALL":
                                print("\nAccess Exception: Elevate via local base station user context.")
                            else:
                                self.view_currently_parked(user.mall)
                        elif admin_choice == "2":
                            # Macro branch routing logic allowing high tier admins to loop across every available site
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
                self.forgot_password()
            elif choice == "6":
                print("\nShutting down engine matrix loops cleanly. Goodbye.")
                # Kill core processing while loop, ending script thread execution environment smoothly
                break
            else:
                print("Invalid operational command string entered.")


if __name__ == "__main__":
    # Boot target environment loop sequence
    ParkingSystem().run()