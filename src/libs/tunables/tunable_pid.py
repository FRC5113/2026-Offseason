from typing import SupportsFloat

import wpilib

from wpimath.units import seconds
from wpimath.controller import PIDController

from libs.tunables.tunable_float import TunableFloat


class TunablePIDController(PIDController):
    def __init__(
        self, 
        kp: float, 
        ki: float, 
        kd: float,
        directory: str,
        period: seconds = 0.02
    ) -> None:
        if period <= 0:
            raise ValueError(
                f"period must be positive, got {period}. "
                f"This parameter controls the update rate of the PID controller in seconds."
            )
        
        super().__init__(kp, ki, kd, period)

        if kp < 0:
            wpilib.reportWarning(
                f"PID constant kp has been set to a value less "
                f"than zero ({kp}) during initialization."
            )
        if ki < 0:
            wpilib.reportWarning(
                f"PID constant ki has been set to a value less "
                f"than zero ({ki}) during initialization."
            )
        if kd < 0:
            wpilib.reportWarning(
                f"PID constant kd has been set to a value less "
                f"than zero ({kd}) during initialization."
            )

        self._kp = TunableFloat(directory + "/kp", kp)
        self._ki = TunableFloat(directory + "/ki", ki)
        self._kd = TunableFloat(directory + "/kd", kd)

    def __str__(self) -> str:
        return f"Kp: {self._kp.value}, Ki: {self._ki.value}, Kd: {self._kd.value}"

    def calculate(self, measurement: SupportsFloat, setpoint: SupportsFloat = 0.0) -> float:
        """
        Returns the next output of the PID controller and internally syncs
        tunable gains first.

        :param measurement: The current measurement of the process variable.
        :param setpoint: The new setpoint of the controller.
        """
        self._update_from_tunables()
        return super().calculate(measurement, setpoint)

    def _update_from_tunables(self) -> None:
        """
        Checks if any tunable value has changed and updates the PID constants if changed.
        """
        changed = False
        if self._kp.update():
            changed = True
        if self._ki.update():
            changed = True
        if self._kd.update():
            changed = True
        
        if changed:
            self.setPID(self._kp.value, self._ki.value, self._kd.value)

            if self._kp.value < 0:
                wpilib.reportWarning(
                    f"PID constant kp has been set to a value less "
                    f"than zero ({self._kp.value}) during runtime."
                )
            if self._ki.value < 0:
                wpilib.reportWarning(
                    f"PID constant ki has been set to a value less "
                    f"than zero ({self._ki.value}) during runtime."
                )
            if self._kd.value < 0:
                wpilib.reportWarning(
                    f"PID constant kd has been set to a value less "
                    f"than zero ({self._kd.value}) during runtime."
                )
