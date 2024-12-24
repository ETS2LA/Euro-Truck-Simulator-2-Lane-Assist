from ETS2LA.Module import *

class Module(ETS2LAModule):
    def Initialize(self):
        self.Kp = 1
        self.Ki = 1
        self.Kd = 1
        self.setpoint = 0

        self._prev_error = 0  # To store the previous error for derivative calculation
        self._integral = 0  # To store the integral of the error

    def UpdateValues(self, Kp : float, Ki : float, Kd : float, setpoint : float = 0):
        '''Update the PID values'''
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint

    def run(self, value : float):
        error = self.setpoint - value
        P = self.Kp * error
        self._integral += error
        I = self.Ki * self._integral
        D = self.Kd * (error - self._prev_error)
        self._prev_error = error
        output = P + I + D
        return output