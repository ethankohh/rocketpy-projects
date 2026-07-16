import datetime
import matplotlib.pyplot as plt
from rocketpy import Environment, SolidMotor, Rocket, Flight

# 1. Environment Setup (Spaceport America, NM)
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))  # Midday UTC
env.set_atmospheric_model(type="standard_atmosphere")

# 2. Reusable Solid Motor Definition
thrust_curve = [
    (0, 1000), (0.5, 1400), (1.0, 1600), (2.0, 1500), 
    (3.0, 1200), (3.5, 800), (3.9, 0)
]

motor = SolidMotor(
    thrust_source=thrust_curve, 
    dry_mass=1.815, 
    dry_inertia=(0.125, 0.125, 0.002),
    nozzle_radius=0.033, 
    grain_number=5, 
    grain_density=1815, 
    grain_outer_radius=0.033,
    grain_initial_inner_radius=0.015, 
    grain_initial_height=0.120, 
    grain_separation=0.005,
    center_of_dry_mass_position=0.317, 
    grains_center_of_mass_position=0.397, 
    burn_time=3.9
)

# Adjusted dims to keep Case A stable enough to simulate without hanging the ODE solver
cases = {
    "Case A (Small)":  {"root": 0.10, "tip": 0.05, "span": 0.08},
    "Case B (Medium)": {"root": 0.12, "tip": 0.06, "span": 0.11},
    "Case C (Large)":  {"root": 0.16, "tip": 0.08, "span": 0.14}
}

stability_margins = []
apogees = []
fin_areas = []

print(f"\n{'Configuration':<16} | {'Fin Area (m²)':<13} | {'Stability Margin (cal)':<22} | {'Apogee (m)':<10}", flush=True)
print("-" * 75, flush=True)

# 3. Dynamic Loop over Fin Configurations
for label, dims in cases.items():
    # Rebuild the dry rocket base for each iteration
    rocket = Rocket(
        radius=0.0635, 
        mass=14.426, 
        inertia=(6.321, 6.321, 0.034), 
        power_off_drag=0.4, 
        power_on_drag=0.4,
        center_of_mass_without_motor=0,                
        coordinate_system_orientation="tail_to_nose"   
    )
    
    rocket.add_motor(motor, position=-1.255)
    rocket.add_nose(length=0.55829, kind="vonKarman", position=1.278)
    
    rocket.add_trapezoidal_fins(
        n=4, 
        root_chord=dims["root"], 
        tip_chord=dims["tip"], 
        span=dims["span"], 
        position=-1.04956
    )
    
    # Calculate total area of 4 fins: 4 * [0.5 * (root + tip) * span]
    area = 2.0 * (dims["root"] + dims["tip"]) * dims["span"]
    fin_areas.append(area)
    
    # Run Flight Simulation to gather performance
    flight = Flight(rocket=rocket, environment=env, rail_length=5.2, inclination=85, heading=0)
    
    # --- VERSION-SAFE STATIC MARGIN EXTRACTION ---
    # RocketPy handles static_margin differently depending on library version (Float vs Function)
    rocket.evaluate_static_margin() # calculate
    raw_margin = rocket.static_margin 
    
    if callable(raw_margin):
        margin = raw_margin(0)  # Call at t=0 (ignition / fully loaded)
    elif hasattr(raw_margin, "get_value"):
        margin = raw_margin.get_value(0)
    elif hasattr(raw_margin, "value_with_units"):
        margin = raw_margin.value_with_units
    else:
        margin = float(raw_margin)
    
    stability_margins.append(margin)
    apogees.append(flight.apogee)
    
    print(f"{label:<16} | {area:<13.4f} | {margin:<22.2f} | {flight.apogee:<10.2f}", flush=True)

# 4. Generate the required Plot: Fin Area vs Stability Margin
plt.figure(figsize=(8, 5))
plt.plot(fin_areas, stability_margins, marker='o', color='purple', linestyle='-', linewidth=2)
plt.title("Fin Area vs. Stability Margin")
plt.xlabel("Total Fin Area (m²)")
plt.ylabel("Loaded Static Stability Margin (calibers)")
plt.grid(True)
plt.show()
