from libs import BasicPriority, RequestArbitrator

from wpilib import RobotController, SmartDashboard
from wpimath.units import meters_per_second

from components.shooter.shooter_io.io_base import ShooterIOBase
from components.shooter.shooter_constants import ShooterConstants


class Shooter:
    """
    Represents a subsystem containing a full-length robot drum with a static hood.
    """
    io: ShooterIOBase

    def setup(self) -> None:
        self.velocity_controller = RequestArbitrator()

    def request_velocity(
        self,
        percent: meters_per_second,
        priority: BasicPriority, 
        source: str = "unknown"
    ) -> None:
        """
        Requests a velocity to the shooters velocity controller.
        """
        self.velocity_controller.request(percent, priority.value, source)

    def _safe_defaults(self) -> None:
        """
        Directly commands safe default values to the Shooter.
        """
        self.io.set_voltage(0.0)

    def on_enable(self) -> None:
        """
        Runs once when the robot enters an enabled mode.
        """
        self._safe_defaults()

    def on_disable(self) -> None:
        """
        Runs once when the robot enters a disabled mode.
        """
        self._safe_defaults()

    def publish_telemetry(self) -> None:
        """
        Runs each iteration at the beginning of component execution.
        """
        SmartDashboard.putNumber("Shooter/sensorData/voltage", self.io.get_voltage())
        resolved = self.velocity_controller.resolve()
        SmartDashboard.putNumber("Shooter/resolvedVelocity/velocity", resolved.value)
        SmartDashboard.putString("Shooter/resolvedVelocity/source", resolved.source)
        SmartDashboard.putNumber("Shooter/resolvedVelocity/priority", resolved.priority)

    def execute(self) -> None:
        """
        Directly moves the robot each iteration.
        """
        self.publish_telemetry()

        resolved_velocity = self.velocity_controller.resolve().value  # Linear velocity in m/s

        # Convert linear velocity in mps to angular velocity in radps
        angular_velocity = resolved_velocity / ShooterConstants.FLYWHEEL_RADIUS
        percent = angular_velocity / ShooterConstants.MAX_VELOCITY
        self.io.set_voltage(percent * RobotController.getBatteryVoltage())

        self.io.update()
