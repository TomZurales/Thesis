from manimlib import *

class SpinningPizza(Scene):
  def construct(self):
    # Create a pizza slice using a triangle and a circle for the crust
    pizza_slice = VGroup()
    triangle = Polygon(
      ORIGIN, 
      2 * LEFT + 3 * UP, 
      2 * RIGHT + 3 * UP, 
      color=YELLOW, 
      fill_opacity=1
    )
    crust = Arc(
      radius=2, 
      start_angle=PI, 
      angle=PI, 
      color=ORANGE, 
      stroke_width=8
    )
    pizza_slice.add(triangle, crust)

    # Add the pizza slice to the scene
    self.add(pizza_slice)

    # Rotate the pizza slice to create the spinning effect
    self.play(Rotate(pizza_slice, angle=2 * PI, run_time=4, rate_func=linear))