from wpilib import SmartDashboard

from wpimath.units import radians
from wpimath.controller import ArmFeedforward

from components.arm.arm_constants import ArmFF, ArmPID
from components.arm.arm_io.io_base import ArmIOBase
from components.arm.arm_constants import ArmConstants

from libs import RequestArbitrator, BasicPriority, TunablePIDController
from libs.utils.math_utils import clamp


class Arm:
    """
    Represents the basic arm mechanism of a simulated robot (single joint).
    Uses PID control to reach requested angles with gravity compensation.
    """
    io: ArmIOBase

    def setup(self) -> None:
        self.arm_position_ff = ArmFeedforward(
            kS=ArmFF.KS,
            kG=ArmFF.KG,
            kV=ArmFF.KV,
            kA=ArmFF.KA
        )
        self.arm_position_pid = TunablePIDController(
            kp=ArmPID.KP, 
            ki=ArmPID.KI, 
            kd=ArmPID.KD,
            directory="Tunables/ArmPID"
        )

        self.angle_controller = RequestArbitrator()

    def request_angle(
        self,
        angle: radians,
        priority: BasicPriority, 
        source: str = "unknown"
    ) -> None:
        """
        Requests a velocity to the arms angle controller.
        """
        self.angle_controller.request(angle, priority.value, source)

    def _safe_defaults(self) -> None:
        """
        Directly commands safe default values to the arm.
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
        SmartDashboard.putNumber("Arm/sensorData/position", self.io.get_position())
        SmartDashboard.putNumber("Arm/sensorData/velocity", self.io.get_velocity())
        SmartDashboard.putNumber("Arm/sensorData/appliedVoltage", self.io.get_voltage())

        resolved = self.angle_controller.resolve()
        SmartDashboard.putNumber("Arm/resolvedAngle/angle", resolved.value)
        SmartDashboard.putString("Arm/resolvedAngle/source", resolved.source)
        SmartDashboard.putNumber("Arm/resolvedAngle/priority", resolved.priority)

    def _move_to_angle(self, angle: radians) -> None:
        """
        Moves the arm to an angle via closed loop control.
        """
        current_angle = self.io.get_position()
        current_velocity = self.io.get_velocity()

        ff_volts = self.arm_position_ff.calculate(current_angle, current_velocity)
        pid_volts = self.arm_position_pid.calculate(current_angle, angle)

        self.io.set_voltage(ff_volts + pid_volts)

    def execute(self) -> None:
        """
        Method that directly moves the robot each iteration.
        """
        self.publish_telemetry()

        target_angle = self.angle_controller.resolve().value
        target_angle = clamp(target_angle, ArmConstants.MIN_ANGLE, ArmConstants.MAX_ANGLE)

        self._move_to_angle(target_angle)
        self.io.update()
