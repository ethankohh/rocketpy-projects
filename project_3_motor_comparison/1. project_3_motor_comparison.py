import numpy as np
import matplotlib.pyplot as plt
from rocketpy import Environment, SolidMotor, Rocket, Flight

def main():
    # Define launch location at Spaceport America, NM, and set atmospheric model to standard atmosphere
    env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
    env.set_atmospheric_model(type="standard_atmosphere")

    # Define a helper function to generate solid rocket motors with varying thrust profiles and mass properties
    def create_motor(thrust_val, burn_time, dry_mass, grain_number):
        # The thrust curve is defined as a simple synthetic square wave that ramps up, holds, and drops to 0
        thrust_curve = [
            [0, 0], 
            [0.1, thrust_val], 
            [burn_time - 0.1, thrust_val], 
            [burn_time, 0]
        ]
        
        # Initialize solid rocket motor with physical properties including grain geometry and mass distribution
        return SolidMotor(
            thrust_source=thrust_curve,
            burn_time=burn_time,
            dry_mass=dry_mass,
            dry_inertia=(0.01, 0.01, 0.001),
            center_of_dry_mass_position=0.2,
            nozzle_position=0,
            grain_number=grain_number,
            grain_density=1815,
            nozzle_radius=0.015,
            grain_outer_radius=0.02,
            grain_initial_inner_radius=0.01,
            grain_initial_height=0.05,
            grain_separation=0.005,                
            grains_center_of_mass_position=0.25,   
            coordinate_system_orientation="nozzle_to_combustion_chamber"
        )

    # Define motor variations as a dictionary representing three distinct classes for the altitude study
    motors = {
        "Motor A (Small)":  create_motor(thrust_val=300, burn_time=1.0, dry_mass=0.5, grain_number=2),
        "Motor B (Medium)": create_motor(thrust_val=700, burn_time=1.5, dry_mass=1.0, grain_number=3),
        "Motor C (Large)":  create_motor(thrust_val=1200, burn_time=2.0, dry_mass=1.5, grain_number=4)
    }

    # Initialize a dictionary to store the resulting flight objects for data extraction later
    flights = {}
    
    # Iterate through each motor configuration to rebuild the rocket and execute flight simulations
    for motor_name, motor in motors.items():
        
        # Initialize rocket airframe with mass properties, center of gravity, and coordinate orientation
        rocket = Rocket(
            radius=0.06, 
            mass=10.0, 
            inertia=(1, 1, 0.05),
            power_off_drag=0.4, 
            power_on_drag=0.4, 
            center_of_mass_without_motor=0,
            coordinate_system_orientation="tail_to_nose"
        )
        
        # Attach the selected motor, nose cone, and trapezoidal fins to the rocket assembly
        rocket.add_motor(motor, position=-1.0)
        rocket.add_nose(length=0.5, kind="vonKarman", position=1.0) # <-- FIXED: Changed to add_nose()
        rocket.add_trapezoidal_fins(n=4, root_chord=0.1, tip_chord=0.05, span=0.1, position=-0.8)

        # Execute 6-DOF flight simulation from an 85-degree inclined launch rail, terminating at apogee
        flight = Flight(
            rocket=rocket, 
            environment=env, 
            rail_length=5.0, 
            inclination=85, 
            heading=0, 
            terminate_on_apogee=True
        )
        
        # Store the completed flight simulation in our dictionary
        flights[motor_name] = flight

    # Print table header to the console for tracking simulation results across all motor choices
    print("Project 3: Motor Comparison\n")
    print(f"{'Motor':<20} | {'Max Altitude (m)':<20} | {'Max Velocity (m/s)':<20}")
    print("-" * 66)
    
    # Extract and format the maximum altitude and velocity for each simulated flight configuration
    for name, flight in flights.items():
        max_alt = flight.apogee
        max_vel = flight.max_speed
        print(f"{name:<20} | {max_alt:<20.2f} | {max_vel:<20.2f}")

    # Generate a matplotlib figure with side-by-side subplots to visualize altitude and velocity profiles
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Project 3: Motor Choice vs. Flight Performance", fontsize=14, fontweight='bold')

    # Iterate through the stored flights to plot the altitude curve for each motor
    for name, flight in flights.items():
        time_data = flight.z[:, 0]
        # Subtract the environment's base elevation from the raw Z coordinate to get Altitude Above Ground Level
        alt_data = flight.z[:, 1] - env.elevation 
        ax1.plot(time_data, alt_data, label=name, linewidth=2)

    # Format the Altitude Comparison subplot with labels, grids, and a legend
    ax1.set_title("Altitude Comparison")
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Altitude Above Ground Level (m)")
    ax1.grid(True, linestyle='--', alpha=0.7)
    ax1.legend()

    # Iterate through the stored flights to plot the velocity curve for each motor
    for name, flight in flights.items():
        time_data = flight.speed[:, 0]
        vel_data = flight.speed[:, 1]
        ax2.plot(time_data, vel_data, label=name, linewidth=2)

    # Format the Velocity Comparison subplot with labels, grids, and a legend
    ax2.set_title("Velocity Comparison")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Velocity (m/s)")
    ax2.grid(True, linestyle='--', alpha=0.7)
    ax2.legend()

    # Apply tight layout to prevent overlapping text and display the final plots
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
