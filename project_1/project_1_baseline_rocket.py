import datetime
import matplotlib.pyplot as plt
from rocketpy import Environment, SolidMotor, Rocket, Flight

# Define launch location at Spaceport America, NM, and set atmospheric model to International Standard Atmosphere (ISA)
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
env.set_date((tomorrow.year, tomorrow.month, tomorrow.day, 12))
env.set_atmospheric_model(type="standard_atmosphere")

# Define thrust profile as a list of (time, thrust) tuples; RocketPy interpolates between these points
thrust_curve = [
    (0, 1000), (0.5, 1400), (1.0, 1600), (2.0, 1500), 
    (3.0, 1200), (3.5, 800), (3.9, 0)
]

# Initialize solid rocket motor with physical properties including grain geometry and mass distribution
motor = SolidMotor(
    thrust_source=thrust_curve,
    dry_mass=1.815,
    dry_inertia=(0.125, 0.125, 0.002),
    nozzle_radius=33 / 1000,
    grain_number=5,
    grain_density=1815,
    grain_outer_radius=33 / 1000,
    grain_initial_inner_radius=15 / 1000,
    grain_initial_height=120 / 1000,
    grain_separation=5 / 1000,
    center_of_dry_mass_position=0.317,
    grains_center_of_mass_position=0.397,
    burn_time=3.9
)

# Initialize rocket airframe with geometric properties and drag coefficients
rocket = Rocket(
    radius=127 / 2000,
    mass=14.426,
    inertia=(6.321, 6.321, 0.034),
    power_off_drag=0.4,
    power_on_drag=0.4,
    center_of_mass_without_motor=0,
    coordinate_system_orientation="tail_to_nose"
)
# Attach motor and define rail button locations for launch stability
rocket.add_motor(motor, position=-1.255)
rocket.set_rail_buttons(upper_button_position=0.0818, lower_button_position=-0.6182)

# Define aerodynamic surfaces (nose cone, fins, and tail cone)
rocket.add_nose(length=0.55829, kind="vonKarman", position=1.278)
rocket.add_trapezoidal_fins(
    n=4, root_chord=0.120, tip_chord=0.060, span=0.110, position=-1.04956
)
rocket.add_tail(top_radius=0.0635, bottom_radius=0.0435, length=0.060, position=-1.194656)

# Configure dual-deployment recovery system
rocket.add_parachute("Drogue", cd_s=1.0, trigger="apogee")
rocket.add_parachute("Main", cd_s=10.0, trigger=800)

# Execute 6-DOF flight simulation from an 85-degree inclined launch rail
flight = Flight(rocket=rocket, environment=env, rail_length=5.2, inclination=85, heading=0)

# Display key performance indicators to console
print(f"{'Metric':<25} {'Value'}")
print("-" * 35)
print(f"{'Max altitude':<25} {flight.apogee:.2f} m")
print(f"{'Max velocity':<25} {flight.max_speed:.2f} m/s")
print(f"{'Burn time':<25} {motor.burn_duration:.2f} s")
print(f"{'Flight duration':<25} {flight.t_final:.2f} s")

# Generate interactive 3D trajectory plot and kinematic time-series data
flight.plots.trajectory_3d()
flight.plots.linear_kinematics_data()
