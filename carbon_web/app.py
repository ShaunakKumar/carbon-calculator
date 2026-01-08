from flask import Flask, render_template, request

app = Flask(__name__)

# =========================
# EMISSION FACTORS
# =========================
ELECTRICITY_FACTOR = 0.82
SOLAR_CREDIT_FACTOR = 0.82
LPG_FACTOR = 14.2
GENERATOR_FACTOR = 2.5
INVERTER_FACTOR = 0.6

AC_FACTOR = 1.6
FAN_FACTOR = 0.075
FRIDGE_FACTOR = 1.2
TV_FACTOR = 0.1
WASHING_MACHINE_FACTOR = 0.6

PETROL_FACTOR = 2.31
DIESEL_FACTOR = 2.68
BUS_FACTOR = 0.089
TRAIN_FACTOR = 0.041

FLIGHT_SHORT = 0.15
FLIGHT_LONG = 0.11

WATER_FACTOR = 0.0003
WASTE_FACTOR = 0.5
PAPER_FACTOR = 0.005
CLOTHING_FACTOR = 6
ONLINE_ORDER_FACTOR = 1.8

VEG_DIET = 50
NON_VEG_DIET = 120

INTERNET_FACTOR = 0.06
MOBILE_FACTOR = 0.005
LAPTOP_FACTOR = 0.02
ELEVATOR_FACTOR = 0.015

TREE_OFFSET = 21

# =========================
# CALCULATION FUNCTIONS
# =========================
def energy_emission(d):
    gross = (
        d["electricity"] * ELECTRICITY_FACTOR +
        d["lpg"] * LPG_FACTOR +
        d["generator_liters"] * GENERATOR_FACTOR +
        d["inverter_units"] * INVERTER_FACTOR
    )
    solar_credit = d["solar_units"] * SOLAR_CREDIT_FACTOR
    return gross - solar_credit

def appliance_emission(d):
    return (
        d["ac_hours"] * AC_FACTOR +
        d["fan_hours"] * FAN_FACTOR +
        d["fridge_days"] * FRIDGE_FACTOR +
        d["tv_hours"] * TV_FACTOR +
        d["washing_cycles"] * WASHING_MACHINE_FACTOR
    )

def transport_emission(d):
    fuel = 0
    if d["fuel_type"] == "petrol":
        fuel = d["fuel_liters"] * PETROL_FACTOR
    elif d["fuel_type"] == "diesel":
        fuel = d["fuel_liters"] * DIESEL_FACTOR

    public = d["bus_km"] * BUS_FACTOR + d["train_km"] * TRAIN_FACTOR
    flights = d["short_flight_km"] * FLIGHT_SHORT + d["long_flight_km"] * FLIGHT_LONG
    return fuel + public + flights

def lifestyle_emission(d):
    food = VEG_DIET if d["food_type"] == "veg" else NON_VEG_DIET
    return (
        food +
        d["water_liters"] * WATER_FACTOR +
        d["waste_kg"] * WASTE_FACTOR +
        d["paper_sheets"] * PAPER_FACTOR +
        d["clothes_bought"] * CLOTHING_FACTOR +
        d["online_orders"] * ONLINE_ORDER_FACTOR
    )

def digital_emission(d):
    return (
        d["internet_gb"] * INTERNET_FACTOR +
        d["mobile_hours"] * MOBILE_FACTOR +
        d["laptop_hours"] * LAPTOP_FACTOR +
        d["elevator_trips"] * ELEVATOR_FACTOR
    )

def carbon_offset(d):
    return (d["trees_planted"] * TREE_OFFSET) / 12

def impact_level(total):
    if total < 300:
        return "LOW"
    elif total < 750:
        return "MEDIUM"
    else:
        return "HIGH"

# =========================
# FLASK ROUTE
# =========================
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        d = {
            "electricity": float(request.form.get("electricity", 0)),
            "solar_units": float(request.form.get("solar_units", 0)),
            "lpg": float(request.form.get("lpg", 0)),
            "generator_liters": float(request.form.get("generator_liters", 0)),
            "inverter_units": float(request.form.get("inverter_units", 0)),

            "ac_hours": float(request.form.get("ac_hours", 0)),
            "fan_hours": float(request.form.get("fan_hours", 0)),
            "fridge_days": float(request.form.get("fridge_days", 0)),
            "tv_hours": float(request.form.get("tv_hours", 0)),
            "washing_cycles": float(request.form.get("washing_cycles", 0)),

            "fuel_type": request.form.get("fuel_type"),
            "fuel_liters": float(request.form.get("fuel_liters", 0)),
            "bus_km": float(request.form.get("bus_km", 0)),
            "train_km": float(request.form.get("train_km", 0)),

            "short_flight_km": float(request.form.get("short_flight_km", 0)),
            "long_flight_km": float(request.form.get("long_flight_km", 0)),

            "food_type": request.form.get("food_type"),
            "water_liters": float(request.form.get("water_liters", 0)),
            "waste_kg": float(request.form.get("waste_kg", 0)),
            "paper_sheets": float(request.form.get("paper_sheets", 0)),
            "clothes_bought": float(request.form.get("clothes_bought", 0)),
            "online_orders": float(request.form.get("online_orders", 0)),

            "internet_gb": float(request.form.get("internet_gb", 0)),
            "mobile_hours": float(request.form.get("mobile_hours", 0)),
            "laptop_hours": float(request.form.get("laptop_hours", 0)),
            "elevator_trips": float(request.form.get("elevator_trips", 0)),

            "trees_planted": float(request.form.get("trees_planted", 0))
        }

        total = (
            energy_emission(d) +
            appliance_emission(d) +
            transport_emission(d) +
            lifestyle_emission(d) +
            digital_emission(d)
        )

        offset = carbon_offset(d)
        net = total - offset
        level = impact_level(net)

        result = {
            "total": round(total, 2),
            "offset": round(offset, 2),
            "net": round(net, 2),
            "level": level
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
