import numpy as np
import matplotlib.pyplot as plt
from rocketpy import Environment, SolidMotor, Rocket, Flight

def main():
    # Define an expanded set of wind conditions for the weather effects study (in m/s)
    # Wind will be simulated blowing constantly along the X-axis (wind_u)
    wind_cases = {
        "Calm Day": 0.0,
        "Light Breeze": 2.5,
        "Moderate Wind": 5.0,
        "Fresh Breeze": 7.5,
        "Strong Wind": 10.0,
        "Near Gale": 15.0,
        "Gale Force": 20.0
    }

    # Initialize a solid rocket motor with standard properties and a synthetic thrust curve
    # We use a single motor configuration across all flights to isolate the effect of wind
    motor = SolidMotor(
        thrust_source=[[0, 0], [0.1, 700], [1.4, 700], [1.5, 0]],
        burn_time=1.5,
        dry_mass=1.0,
        dry_inertia=(0.01, 0.01, 0.001),
        center_of_dry_mass_position=0.2,
        nozzle_position=0,
        grain_number=3,
        grain_density=1815,
        nozzle_radius=0.015,
        grain_outer_radius=0.02,
        grain_initial_inner_radius=0.01,
        grain_initial_height=0.05,
        grain_separation=0.005,                
        grains_center_of_mass_position=0.25,   
        coordinate_system_orientation="nozzle_to_combustion_chamber"
    )

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
    
    # Attach the motor, nose cone, and fins to the rocket assembly
    rocket.add_motor(motor, position=-1.0)
    rocket.add_nose(length=0.5, kind="vonKarman", position=1.0)
    rocket.add_trapezoidal_fins(n=4, root_chord=0.1, tip_chord=0.05, span=0.1, position=-0.8)
    
    # ADD a parachute to simulate a realistic recovery and make the horizontal drift prominent
    # The parachute is configured to deploy precisely at the apogee (highest point of flight)
    rocket.add_parachute(
        name="Main",
        cd_s=5.0,           # Coefficient of drag times reference area
        trigger="apogee"    # Deployment condition
    )

    # Initialize lists to store metrics for plotting after the simulation loop
    wind_speeds = []
    drift_distances = []

    # Print table header to the console for tracking simulation results
    print("Project 4: Weather Effects on Landing Location\n")
    print(f"{'Condition':<15} | {'Wind (m/s)':<10} | {'Max Altitude (m)':<18} | {'Drift Dist. (m)':<15} | {'Landing (X, Y)':<20}")
    print("-" * 87)

    # Iterate through each wind condition, setting up a new environment and simulating the flight
    for label, wind_speed in wind_cases.items():
        
        # Define launch location at Spaceport America, NM
        env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)
        
        # Set a custom atmosphere with standard pressure/temp but a constant wind profile in the X direction
        env.set_atmospheric_model(
            type="custom_atmosphere", 
            wind_u=wind_speed,  # Constant wind blowing along the X-axis
            wind_v=0.0          # No wind along the Y-axis
        )

        # Execute 6-DOF flight simulation from an 85-degree inclined launch rail
        # We DO NOT terminate on apogee here, because we need to simulate the parachute descent to the ground
        flight = Flight(
            rocket=rocket, 
            environment=env, 
            rail_length=5.0, 
            inclination=85, 
            heading=0,
            terminate_on_apogee=False
        )
        
        # Extract flight metrics: max altitude (apogee) and final impact time
        apogee = flight.apogee
        t_impact = flight.t_final
        
        # Evaluate the X and Y coordinates at the exact moment of impact
        x_impact = flight.x(t_impact)
        y_impact = flight.y(t_impact)
        
        # Calculate the total horizontal drift distance from the launch pad (0,0) using the Pythagorean theorem
        drift = np.sqrt(x_impact**2 + y_impact**2)
        
        # Store results for the matplotlib plot
        wind_speeds.append(wind_speed)
        drift_distances.append(drift)
        
        # Format landing coordinates as a clean string for the table
        landing_coords = f"({x_impact:.1f}, {y_impact:.1f})"
        
        # Print the current iteration's metrics to the console
        print(f"{label:<15} | {wind_speed:<10.1f} | {apogee:<18.2f} | {drift:<15.2f} | {landing_coords:<20}")

    # Generate a matplotlib figure to visualize the relationship between wind speed and horizontal drift
    plt.figure(figsize=(10, 6))
    
    # Plot the drift distance vs wind speed with custom markers and styling
    plt.plot(wind_speeds, drift_distances, marker='o', markersize=8, color='crimson', linestyle='-', linewidth=2)
    
    # Format the plot with titles, labels, and grid lines for readability
    plt.title("Project 4: Wind Speed vs. Landing Drift Distance", fontsize=14, fontweight='bold')
    plt.xlabel("Constant Wind Speed (m/s)", fontsize=12)
    plt.ylabel("Total Horizontal Drift Distance (m)", fontsize=12)
    
    # Label the X-axis ticks with both the speed and the condition name, rotated for fit
    labels = [f"{w} m/s\n({list(wind_cases.keys())[i]})" for i, w in enumerate(wind_speeds)]
    plt.xticks(wind_speeds, labels, rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Apply tight layout to prevent overlapping text and display the plot
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()