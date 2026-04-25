from libs import BasicPriority

from wpilib import Joystick, RobotState

from components.arm.arm import Arm
from components.arm.arm_constants import ArmConstants


class ArmController:
    """
    Controls the arm via teleoperation.
    """
    arm: Arm
    controller: Joystick

    def setup(self) -> None:
        self.sticky_angle = 0.0

    def _safe_defaults(self) -> None:
        """
        Requests safe values to the Arm.
        """
        self.arm.request_angle(0.0, BasicPriority.SAFETY, "safety")

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
        Method called each iteration.
        """
        if not RobotState.isTeleop():
            return

        if self.controller.getRawButton(1):
            self.sticky_angle = ArmConstants.MAX_ANGLE
        elif self.controller.getRawButton(2):
            self.sticky_angle = ArmConstants.MAX_ANGLE / 2
        elif self.controller.getRawButton(3):
            self.sticky_angle = ArmConstants.MIN_ANGLE
        
        self.arm.request_angle(self.sticky_angle, BasicPriority.TELEOP, "teleop")