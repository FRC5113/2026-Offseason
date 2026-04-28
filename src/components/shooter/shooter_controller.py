import math

from wpilib import Joystick, RobotState
from wpimath.geometry import Translation2d

from components.shooter.shooter import Shooter
from components.shooter.shooter_constants import ShooterConstants
from components.shooter.shooter_calculations import calculate_optimal_velocity

from components.drivetrain.drivetrain import Drivetrain

from libs import BasicPriority

from constants import JoystickButton


class ShooterController:
    """
    Controls the Shooter via teleoperation.
    """
    shooter: Shooter
    drivetrain: Drivetrain
    controller: Joystick
    
    def _safe_defaults(self) -> None:
        """
        Requests safe values to the Shooter.
        """
        self.shooter.request_velocity(0.0, BasicPriority.SAFETY, "safety")

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

        if self.controller.getRawButton(JoystickButton.SHOOTER_SPINNING):
            current_pose = self.drivetrain.get_pose()
            current_translation = Translation2d(current_pose.X(), current_pose.Y())

            # Calculate horizontal distance
            dx = current_translation.X() - ShooterConstants.HUB_POSITION.X()
            dy = current_translation.Y() - ShooterConstants.HUB_POSITION.Y()
            horizontal_distance = math.hypot(dx, dy)

            vertical_difference = ShooterConstants.HUB_HEIGHT - ShooterConstants.SHOOTER_HEIGHT

            target_translation = Translation2d(
                x=horizontal_distance,
                y=vertical_difference
            )

            desired_velocity = calculate_optimal_velocity(target_translation)
            if desired_velocity.velocity is None:
                return

            self.shooter.request_velocity(desired_velocity.velocity, BasicPriority.TELEOP, "teleop")
        else:
            self.shooter.request_velocity(0.0, BasicPriority.TELEOP, "teleop")
