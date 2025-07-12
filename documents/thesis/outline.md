* Introduction
  * Motivation
    * Problem Statement
    * Research Questions
  * Objectives and Scope
  * Contribution
  * Road Map
* Background
  * SLAM Background
    * Keypoint-Based Visual SLAM
      * Differences with Other SLAM Modalities
      * Data Pipeline
      * Common Enhancements
        * Loop Closure
        * Map Management
    * ORB_SLAM3 Overview
  * Directional Statistics
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
