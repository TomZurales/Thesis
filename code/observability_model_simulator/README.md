# Observability Model Simulator

Allows for a simulated 2D map point's true observability to be calculated and compared to the estimated observability of the map point over time

## Structure
This application uses PyGame to create the environments, and generate the visualizations.

## Classes
### observability_model.py
Contains the structure of an observability model, and the model implementations being compared.
    add_observation(position, seen) - Tell the model whether the map point is seen from a given position
    query(position) - Estimates the probability that the map point will be seen from the given position