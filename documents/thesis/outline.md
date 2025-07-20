* Definitions
* Introduction
  * paragraph - The problem with map reuse in long term SLAM, the solution using a viewpoint-aware model of map point observability, and the results of the work.
  * Problem context
    * paragraph - Talk about time on the astrobee project and the problems encountered
    * paragraph - Key takeaways - We need map reuse for performant episodic operation, oudated maps are a problem for localization
  * Problem Statement
    * 
    * paragraph - Describe what bad things happen when SLAM systems fail, including the psychological 

    * paragraph - Describe why current SLAM systems struggle to operate over long periods of time; map size increase, outdated map points leading to localization errors, bad loop closures, etc.
    * paragraph - Describe the problems with existing methods for map reuse; they do not cull old map points(size increase), they are not lightweight(slows down SLAM), they do not account for viewpoint (leading to overly aggressive pruning).
    * paragraph - Describe the need for a point-level model of map point observability that is lightweight and effective at identifying outdated map points.
  * Research Questions
    * paragraph - Is a point-level model of map point observability accurate at identifying outdated map points?
    * paragraph - What are the effects of this model on SLAM performance?
    * paragraph - Can this be implemented in a lightweight way capable of running on low-compute power platforms?
  * Objectives and Scope
    * paragraph - Define the scope of this work, focusing exclusively on map reuse between runs of SLAM in semi-static environments.
    * paragraph - Define the objectives of the model; to be lightweight and effective at identifying outdated map points, and to be usable in real-time SLAM systems.
    * paragraph - Define the objectives of the implementation, not to hurt performance in static environments, and to improve performance with previously generated maps in semi-static environments.
    * paragraph - Define specifically what is not in scope; not a new SLAM system, not a new mapping method, strictly focused as an enhancement to existing keypoint-based visual SLAM.
  * Contribution
    * paragraph - The library: a lightweight, viewpoint-aware model of map point existence, designed to be utilized in keypoint-based visual SLAM systems.
    * paragraph - The SLAM implementation: An implementation of the library in ORB-SLAM 3 to demonstrate its effectiveness. Clarify that I'm not creating a new SLAM system, just an enhancement.
    * paragraph - The datasets: A set of datasets and experimental results demonstrating how the library improves SLAM performance.
  * Road Map
    * paragraph - Outline Chapter 2
    * paragraph - Outline Chapter 3
    * paragraph - Outline Chapter 4
    * paragraph - Outline Chapter 5
* Background
  * Keypoint-Based Visual SLAM
    * paragraph - What is SLAM, what are its goals, what are its use cases?
    * paragraph - What are the defining characteristics of keypoint based visual SLAM as opposed to other SLAM methods?
    * paragraph - Describe the structure of a map in kvSKAM, including keyframes, map points, and their relationships.
    * paragraph - Explain how data flows through a keypoint-based visual SLAM system, from sensor input to map and pose output.
    * paragraph - High level overview of the challenges of KV-SLAM
    * paragraph - Describe the role of map points in SLAM, include how they are used for localization, loop closure, and map reuse.
    * Explain why having a good set of map points is important for SLAM performance, and how outdated or irrelevant map points can lead to localization errors, and slower performance.
    * ORB-SLAM3
      * paragraph - Description of ORB-SLAM3 and its core features
      * paragraph - Justification for why it's a good research platform
      * paragraph - Discussion of strengths and weaknesses; Where does it perform best? What situations make it struggle? Motivate the need for this work.
  * Von Mises-Fisher Distribution
    * paragraph - What is the von Mises-Fisher distribution, what are its properties?
    * paragraph - How is it used in directional statistics to model directional data?
    * paragraph - Why is it a good fit for modeling directional observability of map points?
* Related Work
  * Map Reuse
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
    * paragraph - Describe why the robotics world would benefit from SLAM systems that can operate over long periods of time in changing environments.
    * paragraph - Explain what we mean by long term, multi-session SLAM; The ability to reuse maps between runs of SLAM in a semi-static environment.
