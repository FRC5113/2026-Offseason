from wpimath.units import volts

from components.shooter.shooter_io.io_base import ShooterIOBase
from components.shooter.shooter_constants import ShooterConstants

from libs.utils.math_utils import clamp


class SimulatedShooterIO(ShooterIOBase):
    """
    IO that allows the robot to run without real hardware.
    """
    def __init__(self) -> None:
        self._voltage = 0.0

    def get_voltage(self) -> volts:
        return self._voltage

    def set_voltage(self, voltage: volts) -> None:
        self._voltage = clamp(voltage, -ShooterConstants.MAX_VOLTAGE, ShooterConstants.MAX_VOLTAGE)

    def update(self) -> None:
        pass
