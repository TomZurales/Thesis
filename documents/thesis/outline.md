* Introduction
  * paragraph - The problem with map reuse in long term SLAM, the solution using a viewpoint-aware model of map point observability, and the results of the work.
  * Motivation
    * paragraph - Describe the project that inspired this work; astrobee map reuse on the ISS.
    * paragraph - Describe how issues with long-term SLAM prevent wide usage in dynamic environments; maps can be used for other tasks
    * paragraph - Describe what benefits we can gain from solving these problems; more robustness, better maps, more accurate localization, etc.
  * Problem Statement
    * paragraph - Describe why current SLAM systems struggle to operate over long periods of time; map size increase, outdated map points leading to localization errors, bad loop closures...
    * paragraph - Describe the problems with existing map point culling methods, and why they are bad for low-compute platforms
  * Research Questions
    * paragraph - Is a viewpoint-aware model of map point existence an effective way to detect and cull outdated map points?
    * paragraph - What are the effects of this model on SLAM performance?
    * paragraph - Can this be implemented in a lightweight way capable of running on low-compute power platforms?
  * Objectives and Scope
    * paragraph - Define the scope of this work, focusing exclusively on map reuse between runs of SLAM in semi-static environments.
    * paragraph - Define the objectives of the model; to be lightweight and effective at identifying outdated map points, and to be usable in real-time SLAM systems.
    * paragraph - Define the objectives of the implementation, not to hurt performance in static environments, and to improve performance with previously generated maps in semi-static environments.
  * Contribution
    * paragraph - The library: a lightweight, viewpoint-aware model of map point existence, designed to be utilized in keypoint-based visual SLAM systems.
    * paragraph - The SLAM implementation: An implementation of the library in ORB-SLAM 3 to demonstrate its effectiveness.
    * paragraph - The datasets: A set of datasets and experimental results demonstrating how the library improves SLAM performance.
  * Road Map
    * paragraph - Outline Chapter 2
    * paragraph - Outline Chapter 3
    * paragraph - Outline Chapter 4
    * paragraph - Outline Chapter 5
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
      * paragraph - Revisitation of how enhancements are implemented in keypoint based visual SLAM
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
      * paragraph - define what we mean by directional observability; a mapping between observation unit direction vector and seen/not seen binary observations
      * paragraph - Justify why distance needs to be accounted for, use a diagram to show that by including distance, we can account for occlusions in the model
      * paragraph - Say what we are trying to build; a model which can produce a probability that a point will be seen given an observation direction and a distance
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
