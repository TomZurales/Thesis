# Dataset Generation
Datasets for my thesis consist of:
* A stereo image stream
* A stereo segmented image stream, highlighting the objects which are 

# Plugins
We have a couple of different plugins
## Force Controller
Reads timestamped forces from a file. These forces are applied to the body at the given timestamp.
## Object Controller
Reads timestamped manipulations from a file. When the timestamp hits, the object moves to the new pose specified.

# Output
We are outputting undistorted stereo images, and IMU readings to a directory specified.