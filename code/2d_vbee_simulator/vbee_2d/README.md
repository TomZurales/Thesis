# 2D version of the VBEE library for a single map point

* Observations arrive in chunks of all observations for a single run
    * Observations are in the form (x: float, y: float, seen: bool)
* Steps
    1. Count the number of seen observations
    2. If num seen is 0, perform bayesian update to calculate new P(E). Else, P(E) = 0.9
    3. Integrate observations into observability model
    4. Calculate total impact
    5. Update P(E) based on step 2 and impact