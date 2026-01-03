# Slide - Title


# Slide - Motivation - The Issue of Old Maps
Mobile robots are being trusted to operate in homes, schools, hospitals, etc., without the assistance of human operators. Delivery robots, self-driving cars, and service robots are all expected to perform their tasks safely and effectively, in environments that can change significantly over time.

Let's consider a hypothetical security robot that's designed to patrol an office building after hours. The robot has a static internal map of the environment, which it matches against its sensor readings to figure out its location. Now if the building never changes, this system is fine, the robot can always figure out its location by matching its sensor data to the map.

But in reality, things are going to change over time. This office building has people in it during the day, and their activity is going to impact the environment. Furniture might be moved, a door could be closed, any number of any changes. But the effect is that the robot's map no longer matches reality. When the robot is in an area that disagree with its map, it now struggles to match its sensor data, and its ability to accurately determine its location suffers.

Now there are options on how to handle this situation. The robot could always be mapping while its patrolling, and just replace the old map with the new map after every patrol. But, if the robot doesn't map the entire environment, it will end up deleting previously mapped areas which will now need to be remapped. Another option would be to merge the two maps into one, overlaying the new map data onto the old and saving this as the result. This has the desired effect, since the sensor data can again always be matched to the map. But now the map grows monotonically, and over time as more changes accumulate, the proportion of the map that matches reality becomes smaller and smaller.

Ideally, there would be some middle ground between the two options, a way to intelligently identify the parts of the old map that no longer match reality, so they can be deleted before merging. But determining the parts of a map that are outdated is non-trivial. A map feature not observed during a patrol might still be valid, but only visible from a different viewpoint.

# Slide - Background - Keypoint-Based Visual SLAM
Ok, so that example is intentionally simplified to illustrate the core issue, but these problems do occur in real navigation systems when operating in the same environment over long time horizons. This research studies that problem in the context of Keypoint-Based Visual SLAM.

Now because KV-SLAM is so central to the rest of this presentation, I'm going to take a minute to introduce it here before we go any deeper. So SLAM stands for Simultaneous Localization and Mapping. SLAM algorithms take in sensor data, and generate a map and estimate the sensor's location within that map simultaneously. Visual SLAM refers to systems which use images as their primary input, as opposed to something like LIDAR or RGBD data. And finally, keypoint-based means that the system tracks image features generated from sparse keypoints extracted from the image, rather than estimating the relative motion of every pixel like in dense-SLAM, or identifying more abstract features like planes or lines like in PL-SLAM, or identifiable objects like in semantic SLAM.

There are many implementations of KV-SLAM, but in general, they work like this.
An image is received as input
Image features are extracted
Correspondences are found between sequential images (or simultaneous images in the case of stereo SLAM) by comparing feature descriptors
The relative transformation between the images and the depths of the matched points are calculated, providing our first 3D map points
For each subsequent image, the relative position of the image is determined through 2D-3D correspondences
New map points are triangulated from the 2D-2D correspondences between sequential images

# Slide - Terminology and Definitions
So I want to define some terms I'll be using throughout the presentation. Let's break down the title: Viewpoint-Based Map Point Existence Estimation for Episodic Keypoint-Based Visual SLAM.

We've already discussed KV-SLAM, but let's formalize everything else.

A map point is the 3D extension of an image feature. It has a 3D position, and a descriptor.
A viewpoint is a 3D camera position relative to a map point.
An observation is the combination of a viewpoint and a visibility status s. So if a map point is visible from a viewpoint v, then we have an observation (v, s)
Existence is the random variable representing whether the map point still exists.

And finally, episodic SLAM is going to refer to the methodology of running SLAM described in the first example, where the previous run's map is loaded for each run, the robot starts and ends each run in the same place, there are no environmental changes during a run, but there are potentially environmental changes between runs.

# Slide - The Problem
Let's formalize the problem.

Over long time horizons, maps generated and used in episodic KV-SLAM operations can accumulate map points that no longer represent real features in the environment. As the proportion of outdated map points increases, the search space for 2D-3D correspondences grows, increasing processing time and potentially leading to reduced localization and tracking performance.

Therefore, removing outdated map points is necessary for long-term operations. But the decision of which map points to eliminate is not trivial. Depending on the path taken through the environment, a given run or set of runs may not observe every valid map point. So, naive methods like removing points that have not been seen recently risk deleting useful data. 

This work addresses the problem of distinguishing between truly outdated map points, and those that have just not been observed recently in long-term episodic KV-SLAM operations.

# Slide - Related Work
Now at its core the idea here is to sparsify the map in such a way that it becomes more consistent with the current state of the world. Some SLAM implementations exist that do this in various ways. 

<!-- Discuss some lower-level map sparsification examples -->

Now since compute is cheap and math is hard, a lot of modern SLAM methods operate at a higher level of abstraction than Keypoint based visual SLAM. The scope of this research is limited to KB slam, but many methods of outdated feature identification are simpler at these higher levels of abstraction so they are worth mentioning

<!-- Discuss some high-level map sparsification examples -->

# Slide - Objectives and Contributions
The objective of this research is to provide a method of estimating the probability that a map point still exists, based on its

The title of this research Calls this viewpoint based existence estimation. The theory behind this is that Having an understanding of a map points global observability meaning where can the point be seen and where can the point not be seen will lead to a reduction in incorrect map point eliminations And improve performance of KV slam overtime

So the research questions I'm going to attempt to answer are
one. Can a map points global observability the accurately modeled
2. Can the existence of a map point Be accurately determined Using Bayesian statistics integrating a map points estimated chances of being observed from a given viewpoint
three dot. How does the integration of such an existence estimation affect the performance of existing visual science systems keypoint based visual slime systems

In an attempt to answer these questions, this research has contributed A library implementing AK nearest neighbors Observability estimation model, And an existence estimation framework Capable of being integrated into many existing keypoint based visual SLAM systems. Additionally a an implementation of ORBSLAM 3 integrating this library for MAP point existence estimation and sparsification it was created. For the purposes of characterizing the library, a data set of 390 ish unique observability scenarios is provided. And finally to test and characterize the performance of the integrated SLAM system, a stereo visual SLAM data set was created, Containing scenarios specific to the challenge being researched.

# Slide - Methodology - libVBEE - Architectural Overview
The library created for this research is called libv BEE, standing for viewpoint based existence estimation estimator. The external interface of AVBEE object provides the single method update . This method handles estimating The likelihood that the point would be seen from the observed position , determining a posterior probability of existence for the map point based on that observation and estimation , and updates the model observability model to keep it accurate . Finally the New estimation of the map points existence is returned. Internally, The system is architected as framework, capable of accepting various observability model implementations. An observability model provides The methods estimate and update, Which return the models estimation likelihood that the map point can be seen from a given viewpoint and integrate A new observation into the model respectively. However as is, The system only ships with AK nearest neighbors based observability model.

A SLAM system looking to implement this library would Create AVBEE instance for each map point, Giving the system the ability to estimate the existence probability of every map point in the map.

# Slide - Methodology - libVBEE Internal Model
The goal of any observability model is to Provide a boolean answer of whether or not the map point can be seen from a given viewpoint a viewpoint being a point in 3D space relative to the map point at the origin. To provide this estimation perfectly would require The observer to go to every possible viewpoint around the map point and determine whether the point can be seen or not. Instead the KNN observability model works on the principle of believing that if all previous observations of the of the point near a given viewpoint we're able to see the point then it is likely that the point will be able to be seen from the given viewpoint.

The K and N observability model is parameterized by This vector of values, The most important of which being N which represents the Maximum number of historical observations that can be saved and K which represents the number of past observations Which are used for the estimation. The estimation step takes in a viewpoint, Finds the At most K neighbors that our nearest and returns the weighted average of those historical observations waited by distance to the new viewpoint.

The update step looks at the number of Observations Historical observations that were valid neighbors and the difference between the estimated observability and the true observability and either does nothing if the estimation was confident and correct or replaces a historical observation in the in the in the vector otherwise. The selection of this of the historical observation to erase replace is done in a way to attempt to maximize The spread of historical observations around the map point, which has the effect of overtime creating a global estimation Of the map points observability.

The existence probability estimator is responsible for performing the Bayesian update step determining a new probability of existence based on the output of the observability model and the new observation. Because sensor data Always has some amount of noise This component is parameterized by a false negative rate and a false positive rate representing the probabilities that a point will be seen when it does not exist and and that a point will not be seen when it does exist and is observable.

The Existence estimation framework ties the observability model and the existence probability estimator together generating a final new probability of existence based on the observation. This Module applies various weights to the prior and posterior estimations to ensure that The probability of existence does not change too rapidly and that the point achieves some defined a number of observations before it is fully realized.

# Slide - Methodology - libVBEE Characterization Dataset (Observability Scenarios)
Alright so a map point exists at some position in the world frame. So for every coordinate in the world frame an observer at that coordinate facing the map point would fall into one of three scenarios it could either see the point, not see the point, or be in an area that is inaccessible. If we take the observer coordinate in the world frame minus the map points coordinate in the world frame, we get a vector pointing from the map point to the observer, which we call the viewpoint. The combination of the set of viewpoints where the from which the point is visible invisible and points that are inexp and viewpoints that are inaccessible are what I am calling and observability scenario. To cover the domain of possible observability scenarios We need A combination of scenarios where the point is observable from many viewpoints hidden from many viewpoints accessible and inaccessible for many viewpoints. A generator was created to create observability Scenarios with a desired proportion of observable locations to in observable locations and accessible locations to inaccessible locations. The generator was used to create observability scenarios for all pairs of accessability and visibility ratios from 5% to 95% for a total of 361 unique scenarios.

# Slide - Methodology - libVBEE Parameter Tuning and Selection 
The VB library has a total of nine parameters That need to be set. To determine performant values for these parameters, The performance of the VB library needs to be characterized for a given parameter set. Let's take a quick aside to look at the implementation of the observability scenarios data set and how it's used to characterize libVBEE.

To characterize the library for a given parameterization, the following characterization procedure was run
For each observability scenario, a new vbee instance is created. Then for 1000 random we generated observations, we perform a VB update, and calculate the current error as one minus probability of existence. After these 1000 observations, the global observability error is determined by taking the sum of 5000 random observations minus the Observability models estimate of the of that observation's viewpoint. Finally the point is marked as removed such that no observation will see it anymore, and 1000 more random Observations are taken again aggregating the total error now using zero rather than one as the true existence.

While many more metrics Exist and could have been monitored, A truly optimal solution is difficult to find in a high dimensional space. Therefore these two metrics were selected as the key Performance indicators for a given parameterization.

The Python library Optuna was used to minimize these objectives Using multivariate multi objective optimization. Initial parameters were set Based on a Best guess of what would perform well, and after a study of 1000 trials, The results can be seen here.

With the optimization provides is a Pareto front, where the changing of anyone parameter would result in poorer performance Of the system. The final parameterization was selected From the Parado front based on strong performance, balanced between both objectives. We can compare the metrics both before and after optimization to see that new parameterization does perform better. These values were then hard coded into the VB library For testing of The SLIME integration.

# Slide - Methodology - ORB-SLAM3 Integration

# Slide - Methodology - Stereo-Visual Changing Episodic Dataset

# Slide - Methodology - Test Plan

# Slide - Results - Analysis Method

# Slide - Results - libVBEE Performance

# Slide - Analysis - libVBEE Results Analysis

# Slide - Results - Integrated SLAM Performance

# Slide - Analysis - Integrated SLAM Results Analysis

# Slide - Analysis - Key Takeaways

# Slide - Conclusions

# Slide - Future Work

# Slide - Q & A