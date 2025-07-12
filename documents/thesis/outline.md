* Introduction
  * Motivation
    * Problem Statement
    * Research Questions
  * Objectives
  * Contribution
  * Road Map
* Background
  * Keypoint Based Visual SLAM
    * Differences with other SLAM modalities
    * Data Pipeline
    * Common Enhancements
      * RANSAC
      * Bag of Words Based Loop Closure
    * Description of ORB SLAM3
  * Related Work
    * Localization in Pre-generated Maps
      * AstroLoc
      * Map Updating Methodologies
    * Visual Map Point Clulling
      * Semantic Based Methods
      * Probability Based Methods
    * Directional Statistics
      * Von Meiser Fisher Distribution
* Implementation
  * A Method for modeling the historical directional observability of a 3D map points
    * Method Overview
    * Implementation Details
    * Integration with ORB_SLAM3
      * Implementing Interfaces
      * Point Removal
      * Serialization Integration 
  * Dataset Creation
    * Hardware
      * 3D printed mount for camera, lidar, and Jetson
      * Diagram of Coordinate Frames
    * Software 
      * Co-registration
      * Annotating Areas for Point Removal
  * Experimentation Methodology
    * System Configuration
    * Parameter Tuneing
* Analysis
  * Evaluation Metrics
    * Performance Comparisons
    * Map Quality Comparisons
  * Results
    * Quantitave Evaluation
    * Qualitative Evaluation
    * Effects of Parameter Tuneing

* Discussion
* Conclusion