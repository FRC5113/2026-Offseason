from wpilib import Joystick, RobotState

from components.drivetrain.drivetrain import Drivetrain
from components.drivetrain.drivetrain_constants import DriveConstants

from libs import BasicPriority

from constants import JoystickAxis


class DrivetrainController:
    """
    Controls the Drivetrain via teleoperation.
    """
    drivetrain: Drivetrain
    controller: Joystick

    def _safe_defaults(self) -> None:
        """
        Requests safe values to the Drivetrain.
        """
        self.drivetrain.request_linear_velocity(0.0, BasicPriority.SAFETY, "safety")
        self.drivetrain.request_angular_velocity(0.0, BasicPriority.SAFETY, "safety")

    def on_enable(self) -> None:
        """
        Method called once when the robot enters a enabled state.
        """
        self._safe_defaults()

    def on_disable(self) -> None:
        """
        Method called once when the robot enters a disabled state.
        """
        self._safe_defaults()

    def execute(self) -> None:
        """
        Method called each iteration if the component is healthy.
        """
        if not RobotState.isTeleop():
            return

        linear_percent = self.controller.getRawAxis(JoystickAxis.DRIVE_LINEAR)
        angular_percent = self.controller.getRawAxis(JoystickAxis.DRIVE_ANGULAR)

        linear_velocity = linear_percent * DriveConstants.MAX_LINEAR_SPEED
        angular_velocity = angular_percent * DriveConstants.MAX_ANGULAR_SPEED

        self.drivetrain.request_linear_velocity(linear_velocity, BasicPriority.TELEOP, "teleop")
        self.drivetrain.request_angular_velocity(angular_velocity, BasicPriority.TELEOP, "teleop")
