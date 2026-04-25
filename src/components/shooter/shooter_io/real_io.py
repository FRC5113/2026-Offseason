from wpimath.units import volts

from components.shooter.shooter_io.io_base import ShooterIOBase
from components.shooter.shooter_constants import ShooterConstants, ShooterCAN

from libs import FaultLogger
from libs.utils.talon_faults import TalonFaultLogger
from libs.utils.math_utils import clamp

from phoenix6.hardware import TalonFXS
from phoenix6.controls import Follower
from phoenix6.signals import MotorAlignmentValue


class RealShooterIO(ShooterIOBase):
    """
    IO that allows the robot to run with real hardware.
    """
    def __init__(self, fault_logger: FaultLogger) -> None:
        self.fault_logger = fault_logger

        self.left_shooter_motor = TalonFXS(ShooterCAN.LEFT_SHOOTER_MOTOR)
        self.right_shooter_motor = TalonFXS(ShooterCAN.RIGHT_SHOOTER_MOTOR)

        self.right_shooter_motor.set_control(Follower(ShooterCAN.LEFT_SHOOTER_MOTOR, MotorAlignmentValue.OPPOSED))

        self._check_motor_faults()

    def _check_motor_faults(self) -> None:
        """
        Checks for all motor faults and logs them.
        """
        talonfx_logger = TalonFaultLogger(self.fault_logger)

        for motor in (self.left_shooter_motor, self.right_shooter_motor):
            talonfx_logger.report_talon_faults(motor, False, f"{motor.device_id}")
            talonfx_logger.report_talon_faults(motor, True, f"{motor.device_id}")

    def get_voltage(self) -> volts:
        return self.left_shooter_motor.get_motor_voltage().value

    def set_voltage(self, voltage: volts) -> None:
        self.left_shooter_motor.setVoltage(
            clamp(voltage, -ShooterConstants.MAX_VOLTAGE, ShooterConstants.MAX_VOLTAGE)
        )
    
    def update(self) -> None:
        pass
