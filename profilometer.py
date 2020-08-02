from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import pandas as pd
import matplotlib.pyplot as plt
import csv

class Profilometer:
    
    def __init__(self, *args):
      # initialize MotorKit controller
      self.kit = MotorKit()
      
      # set motor pins here
      self.X_AXIS_MOTOR = 
      self.Z_AXIS_MOTOR = 

      # set sensor pins here
      self.RAW_SENSOR_READING = 

      # set limit switch pins here
      self.X_LIMIT_SWITCH = 
      self.Z_LIMIT_SWITCH = 

      # reset stylus
      self.reset_stylus()
      self.sensor_zeroed = False
      if args:
        self.x_limit = args[0]
      else:
        self.x_limit = 300

      # save neutral sensor reading so we know what value to expect when the sensor is not touching the sample
      self.sensor_neutral_value = self.RAW_SENSOR_READING

      # initialize arrays to store data about x and z readings
      self.x_data = []
      self.z_data = []

    def reset_stylus(self):
      # move stylus to origin (determined by limit switch activation)
      while not self.Z_LIMIT_SWITCH:
        self.move_z_axis_motor(1)
      
      while not self.X_LIMIT_SWITCH:
        self.move_x_axis_motor(-1)

      # reset the x and z step counters
      self.x = 0
      self.z = 0

    def move_x_axis_motor(self, steps):
      if steps > 0:
        motor_direction = stepper.FORWARD
      else:
        motor_direction = stepper.BACKWARD

      # move the stepper motor by the amount of steps specified and update the counter
      for i in range(steps):
        self.x += self.kit.stepper1.onestep(direction=motor_direction)

    def move_z_axis_motor(self, steps):
      if steps > 0:
        motor_direction = stepper.FORWARD
      else:
        motor_direction = stepper.BACKWARD

      # move the stepper motor by the amount of steps specified and update the counter
      for i in range(steps):
        self.z += self.kit.stepper2.onestep(direction=motor_direction)

    def level_stylus(self):
      # lower the stylus a predetermined amount of steps to level the stylus
      self.move_z_axis_motor(-5)

    def stylus_touching_sample(self):
      # return true if stylus is touching the sample
      # we determine the stylus to be touching the sample if the sensor reads a value outside a 5% margin of error of the sensor neutral value
      upper_bound = 1.05*self.sensor_neutral_value
      lower_bound = 0.95*self.sensor_neutral_value

      if self.RAW_SENSOR_READING < lower_bound or self.RAW_SENSOR_READING > upper_bound:
        return True
      else:
        return False

    def record_height(self):
      # map the height to the x-axis step
      self.x_data.append(self.x)
      self.z_data.append(self.RAW_SENSOR_READING - self.sensor_zero_value)

    def save_data(self):
      # save data to CSV
      df = pd.DataFrame({'x_data': self.x_data, 'z_data': self.z_data})
      df.to_csv('profilometer_data.csv')

    def visualize_data(self):
      # generate a plot of the sensor readings vs x-axis steps
      plt.plot(self.x_data, self.z_data)
      plt.ylabel("Sensor Reading")
      plt.xlabel("X-Axis Step")
      plt.show()

      # save the plot
      plt.savefig('profilometer_plot.png')

if __name__ == "__main__":
  prof = Profilometer()
  prof.reset_stylus()

  # loop executes while we are under the predetermined safety limit for the x-axis stepper motor
  while prof.x < prof.x_limit:
    if prof.stylus_touching_sample():
      # yes, stylus is touching sample
      
      if prof.sensor_zeroed:
        # yes, the sensor has been zeroed

        prof.record_height()
        prof.move_x_axis_motor(1)
      else:
        # no, the sensor has not been zeroed

        # level the stylus so that we can begin the measurement process
        prof.level_stylus()
        prof.sensor_zero_value = prof.RAW_SENSOR_READING
        prof.sensor_zeroed = True

    else:
      # no, stylus is not touching sample
      
      if prof.sensor_zeroed:
        # yes, the sensor has been zeroed

        # since the sensor has been zeroed, that indicates we were touching the sample previously, but we are no longer touching the sample so we break out of the movement loop
        break
      else:
        # no, the sensor has not been zeroed

        # lower the z-axis stepper motor by one step
        prof.move_z_axis_motor(-1)

  prof.save_data()
  prof.visualize_data()
  prof.reset_stylus()
