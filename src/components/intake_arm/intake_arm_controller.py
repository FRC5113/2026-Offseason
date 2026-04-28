from libs import BasicPriority

from wpilib import Joystick, RobotState

from components.intake_arm.intake_arm import IntakeArm
from components.intake_arm.intake_arm_constants import IntakeArmConstants

from constants import JoystickButton


class IntakeArmController:
    """
    Controls the intake arm via teleoperation.
    """
    intake_arm: IntakeArm
    controller: Joystick

    def setup(self) -> None:
        self.sticky_angle = 0.0

    def _safe_defaults(self) -> None:
        """
        Requests safe values to the IntakeArm.
        """
        self.intake_arm.request_angle(0.0, BasicPriority.SAFETY, "safety")

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

        if self.controller.getRawButton(JoystickButton.INTAKE_ARM_UP):
            self.sticky_angle = IntakeArmConstants.MAX_ANGLE
        elif self.controller.getRawButton(JoystickButton.INTAKE_ARM_DOWN):
            self.sticky_angle = IntakeArmConstants.MIN_ANGLE
        
        self.intake_arm.request_angle(self.sticky_angle, BasicPriority.TELEOP, "teleop")