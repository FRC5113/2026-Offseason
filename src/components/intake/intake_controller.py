from wpilib import Joystick, RobotState

from components.intake.intake import Intake

from libs import BasicPriority


class IntakeController:
    """
    Controls the intake via teleoperation.
    """
    intake: Intake
    controller: Joystick
    
    def _safe_defaults(self) -> None:
        """
        Requests safe values to the Intake.
        """
        self.intake.request_percent(0.0, BasicPriority.SAFETY, "safety")

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

        if self.controller.getRawButton(4):
            self.intake.request_percent(1.0, BasicPriority.TELEOP, "teleop")
        elif self.controller.getRawButton(5):
            self.intake.request_percent(-1.0, BasicPriority.TELEOP, "teleop")
        else:
            self.intake.request_percent(0.0, BasicPriority.TELEOP, "teleop")
