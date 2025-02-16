# Dataset Generation
I need to create 3D environments for SLAM datasets. The controlable aspects of the dataset include: Movable "dynamic" objects, Force control over the body with the camera, and lockable axes. The outputs are stereo video, IMU readings, and ground truth positions.

# Plugins
We have a couple of different plugins
## Force Controller
Reads timestamped forces from a file. These forces are applied to the body at the given timestamp.
## Object Controller
Reads timestamped manipulations from a file. When the timestamp hits, the object moves to the new pose specified.

# Output
We are outputting undistorted stereo images, and IMU readings to a directory specified.