#!/usr/bin/env python3

import os
import numpy as np
import matplotlib.pyplot as plt
import rosbag

def plot_trajectory(vehicle_name, bag_filename):
    # Open the rosbag file
    bag = rosbag.Bag(bag_filename)
    time = []
    left_v = []
    right_v = []

    wheels_topic = f"/{vehicle_name}/wheels_driver_node/wheels_cmd"
    
    # Read wheel commands from the rosbag
    for _, msg, t in bag.read_messages(topics=[wheels_topic]):
        time.append(t.to_sec())
        left_v.append(msg.vel_left)
        right_v.append(msg.vel_right)

    bag.close()
    
    x, y, theta = 0, 0, 0
    wheel_separation = 0.05/2
    dt = np.mean(np.diff(time))

    trajectory = [(0, 0)]

    # Compute the trajectory based on wheel velocities
    for i in range(1, len(time)):
        v_left = left_v[i]
        v_right = right_v[i]
        v = (v_left + v_right) / 2
        omega = (v_right - v_left) / wheel_separation
        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        theta += omega * dt
        trajectory.append((x, y))

    trajectory = np.array(trajectory)
    
    # Plot the trajectory
    plt.figure(figsize=(10, 6))
    plt.plot(trajectory[:, 0], trajectory[:, 1], 'r')
    plt.title('Vehicle Trajectory')
    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.axis('equal')
    plt.tight_layout()
    plt.grid()
    plt.show()

if __name__ == '__main__':
    # Get vehicle name and bag filename from environment variables
    vehicle_name = os.environ['VEHICLE_NAME']
    bag_filename = f'/{vehicle_name}_path.bag'
    plot_trajectory(vehicle_name, bag_filename)