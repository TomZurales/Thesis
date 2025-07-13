* Introduction
  * Motivation
    * Problem Statement
    * Research Questions
  * Objectives and Scope
  * Contribution
  * Road Map
* Background
  * SLAM Background
    * paragraph - What is SLAM, what are its goals, what are its use cases?
    * paragraph - Quick discussion of SLAM modalities to motivate discussion on keypoint SLAM.
      * Sensor Modality Comparison
        * paragraph - Quick description of other SLAM sensor modalities; LIDAR, RGBD, etc
        * paragraph - Quick description of other visual modalities; stereo, mutli-camera
        * paragraph - Description of direct and keypoint method, and a quick comparison
        * paragraph - Comparison sensor modalities
    * SLAM Data Pipeline
      * paragraph - Data Acquisition
      * paragraph - data association
      * paragraph - Pose Estimation
    * Common Enhancements
      * Loop Closure
        * paragraph - 
      * Bundle Adjustment
      * Map Management
    * Keypoint-Based Visual SLAM
      * paragraph - Defining characteristics of Keypoint-Based Visual SLAM; using image features, and determining motion through keypoint correspondences
      * ORB_SLAM3 Overview
  * Directional Statistics Background
    * Von Mises-Fisher Distribution
* Related Work
  * Localization in Pre-generated Maps
    * AstroLoc
    * Map Updating Methodologies
  * Visual Map Point Culling
    * Semantic Based Methods
    * Probability Based Methods
  * Lifelong SLAM
* Implementation
  * Modeling Historical Directional Observability for 3D Map Points
    * Method Overview
    * Implementation Details
    * ORB-SLAM3 Integration
      * Interfaces
      * Point Removal
      * Serialization
  * Experimentation Methodology
    * System Configuration
    * Parameter Tuning
  * Dataset Creation
    * Hardware
      * 3D printed mount for camera, lidar, and Jetson
      * Diagram of Coordinate Frames
    * Software 
      * Co-registration
      * Annotating Areas for Point Removal
* Analysis
  * Evaluation Metrics
    * Performance Comparisons
    * Map Quality Comparisons
  * Results
    * Quantitative Evaluation
    * Qualitative Evaluation
    * Effects of Parameter Tuning
* Discussion
  * Performance Comparison
  * Computational Load Comparison
  * Limitations
* Conclusion
  * Contribution Summary
  * Results Summary
  * Future Directions
