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
      * paragraph - Mapping
      * paragraph - Optimization
    * Common Enhancements
      * Loop Closure
      * Relocalization
      * Bundle Adjustment
      * Map Management
    * Keypoint-Based Visual SLAM
      * paragraph - Defining characteristics of Keypoint-Based Visual SLAM; using image features, and determining motion through keypoint correspondences
      * paragraph - Revisitation of the SLAM data pipeline from the perspective of keypoint-based visual SLAM; talk about initialization through 2D-2D correspondences, pose estimation through 2D-3D correspondences
      * paragraph - Revisitation of how enhancements are implemented in keypoint based visual slam
    * ORB-SLAM3
      * paragraph - an implementation of keypoint based visual SLAM with many enhancements built in
      * paragraph - Justification for why it's a good research platform
      * paragraph - Discussion of strengths and weaknesses; Where does it perform best? What situations make it struggle?
  * Directional Statistics Background
    * Von Mises-Fisher Distribution
* Related Work
  * Localization in Pre-generated Maps
    * Localizers
    * Map Updating Methodologies
  * Visual Map Point Culling
    * Semantic Based Methods
    * Probability Based Methods
  * Lifelong SLAM
* Implementation
  * Method Overview
    * Directional Observability of Map Points
    * Observability Shell Representations
      * Finite Shell (e.g., icosahedral partitioning)
      * Continuous Shell (e.g., von Mises–Fisher kernel) (if I get to it)
    * Existence Probability and Update Rule
      * Observations
      * Non-observations
    * Application to Point Pruning and Selection
  * System Implementation
    * Directional Shell Data Structures
      * Storage Format (texture, face array, etc.)
      * Update Function Implementation
    * Confidence Accumulation and Decay
    * Existence Probability Calculation
    * Selection Weighting for RANSAC / Loop Closure
  * ORB-SLAM3 Integration
    * Interfaces and Module Boundaries
      * Tracking / MapPoint API changes
      * New fields in MapPoint / KeyFrame
    * Directional Update Hookpoints
    * Point Removal Strategy
    * Serialization and Persistence
  * Dataset Creation
    * Hardware Setup
      * 3D Printed Mount for Camera, LiDAR, and Jetson
      * Diagram and Explanation of Coordinate Frames
    * Software Tools
      * LiDAR-Visual Co-registration
      * Point Annotation for Ground Truth Disappearance
  * Experimentation Setup
    * SLAM Configuration (e.g. ORB-SLAM3 settings, sensors)
    * Parameter Exposure and Logging
    * Dataset Management Tools
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
