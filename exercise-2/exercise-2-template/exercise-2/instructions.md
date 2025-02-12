# CMPUT 412/503 Exercise 2: ROS Development and Kinematics


## Part One: Getting Comfortable with ROS

### 1. ROS Duckiebot Setup
a. Setup DTROS interface
b. Create catkin package
c. Implement first ROS publisher and subscriber
d. Create camera subscriber

### 2. Basic ROS Operations
a. **Robot Hostname Management**
   - Store robot hostname in a variable
   - Use variable for topic interactions

b. **Camera Image Processing**
   - Subscribe to camera topic
   - Print image dimensions
   - Convert image to grayscale
   - Annotate image with:
     * Robot hostname
     * Image size
     * Text: "Duck {name} says, 'Cheese! Capturing {size} – quack-tastic!'"
   - Publish annotated image to custom topic
   - Use `rqt_image_view` to verify image

## Part Two: Odometry Using Wheel Encoders

### 1. Wheel Encoder Basics
- Learn wheel odometry model for differential drive robots
- Practice subscribing to encoder data
- Learn publishing data to wheels

### 2. Straight Line Task
a. Movement Objectives
   - Drive forward 1.25 meters
   - Drive backward 1.25 meters

b. Experimental Analysis
   - Compare actual vs. desired location
   - Record used speed
   - Observe speed impact on movement

### 3. Rotation Task
a. Rotation Objectives
   - Rotate 90 degrees (π/2 radians) clockwise
   - Rotate back to 0 degrees counterclockwise

b. Rotation Analysis
   - Document rotation deviations
   - Investigate potential causes

### 4. Odometry Data Handling
a. ROS Bag Recording
   - Save odometry messages to rosbag file

b. Trajectory Visualization
   - Load rosbag in Python
   - Calculate (x,y,θ) from velocity data
   - Plot robot trajectory

## Part Three: Advanced Duckiebot Path Following

### ROS Service and LED Control
1. Implement LED color change service
   - Create distinct colors for different states
   - Document color-state mapping

### Node Structure
1. Main Navigation Node
2. LED Control Service Node

### State Machine Implementation

#### State 1: Stop
- Remain stationary for 5 seconds
- Set specific LED color

#### State 2: D-Path Tracing
- Move forward 1 meter (straight segment)
- Perform clockwise semi-circle
- Maintain consistent LED color

#### State 3: Return to Start
- Navigate back to initial position
- Wait 5 seconds
- Revert to initial state LED color

### Additional Requirements
- Proper node termination
- Full odometry data recording
- Trajectory plotting
- Total task execution time logging

## Bonus Challenges

### Implementation Challenges
- Trace alternative path shapes
- Implement reverse driving scenarios
- Explore advanced navigation techniques