from libs import BasicPriority, RequestArbitrator

from wpilib import RobotController, SmartDashboard
from wpimath.units import percent

from components.intake.intake_io.io_base import IntakeIOBase


class Intake:
    """
    Represents a subsystem containing rollers that fling fuel into the bason.
    """
    io: IntakeIOBase

    def setup(self) -> None:
        self.percent_controller = RequestArbitrator()

    def request_percent(
        self,
        percent: percent,
        priority: BasicPriority, 
        source: str = "unknown"
    ) -> None:
        """
        Requests a velocity to the intake's percent controller.
        """
        self.percent_controller.request(percent, priority.value, source)

    def _safe_defaults(self) -> None:
        """
        Directly commands safe default values to the intake.
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
        SmartDashboard.putNumber("Intake/sensorData/voltage", self.io.get_voltage())
        resolved = self.percent_controller.resolve()
        SmartDashboard.putNumber("Intake/resolvedPercent/percent", resolved.value)
        SmartDashboard.putString("Intake/resolvedPercent/source", resolved.source)
        SmartDashboard.putNumber("Intake/resolvedPercent/priority", resolved.priority)

    def execute(self) -> None:
        """
        Directly moves the robot each iteration.
        """
        self.publish_telemetry()

        resolved_percent = self.percent_controller.resolve().value
        self.io.set_voltage(resolved_percent * RobotController.getBatteryVoltage())

        self.io.update()
