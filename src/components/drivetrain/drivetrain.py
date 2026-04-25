from enum import Enum, auto

from wpilib import Field2d, SmartDashboard

from wpimath.geometry import Pose2d
from wpimath.units import meters_per_second, radians_per_second
from wpimath.kinematics import DifferentialDriveOdometry, ChassisSpeeds, DifferentialDriveKinematics
from wpimath.controller import SimpleMotorFeedforwardMeters

from components.drivetrain.drivetrain_io.io_base import DrivetrainIOBase
from components.drivetrain.drivetrain_constants import (
    DriveConstants, 
    DriveLeftFF,
    DriveRightFF,
    DriveLeftPID,
    DriveRightPID
)

from libs import RequestArbitrator, BasicPriority, TunablePIDController


class DriveMode(Enum):
    OPEN_LOOP = auto()
    CLOSED_LOOP = auto()


class Drivetrain:
    """
    Represents a differential drivetrain with two motors moving each wheel side.
    """
    io: DrivetrainIOBase

    def setup(self) -> None:
        self.odometry = DifferentialDriveOdometry(
            gyroAngle=self.io.get_angle(),
            leftDistance=self.io.get_left_distance(),
            rightDistance=self.io.get_right_distance()
        )

        self.kinematics = DifferentialDriveKinematics(DriveConstants.TRACK_WIDTH)

        self.left_pid = TunablePIDController(
            kp=DriveLeftPID.KP,
            ki=DriveLeftPID.KI,
            kd=DriveLeftPID.KD,
            directory="Tunables/DrivetrainLeftPID/"
        )
        self.right_pid = TunablePIDController(
            kp=DriveRightPID.KP,
            ki=DriveRightPID.KI,
            kd=DriveRightPID.KD,
            directory="Tunables/DrivetrainRightPID/"
        )

        self.left_ff = SimpleMotorFeedforwardMeters(
            kS=DriveLeftFF.KS,
            kV=DriveLeftFF.KV,
            kA=DriveLeftFF.KA
        )
        self.right_ff = SimpleMotorFeedforwardMeters(
            kS=DriveRightFF.KS,
            kV=DriveRightFF.KV,
            kA=DriveRightFF.KA
        )

        self.linear_velocity_controller = RequestArbitrator()
        self.angular_velocity_controller = RequestArbitrator()

        self.drive_mode = DriveMode.CLOSED_LOOP

        self.simulated_field = Field2d()
        SmartDashboard.putData("Field", self.simulated_field)

    def get_pose(self) -> Pose2d:
        """
        Returns the current estimated robot pose.
        """
        return self.odometry.getPose()

    def request_linear_velocity(
        self,
        linear_velocity: meters_per_second,
        priority: BasicPriority,
        source: str = "unknown"
    ) -> None:
        """
        Requests a velocity to the drivetrain's linear velocity controller.
        """
        self.linear_velocity_controller.request(linear_velocity, priority.value, source)

    def request_angular_velocity(
        self,
        angular_velocity: radians_per_second,
        priority: BasicPriority,
        source: str = "unknown"
    ) -> None:
        """
        Requests a velocity to the drivetrain's angular velocity controller.
        """
        self.angular_velocity_controller.request(angular_velocity, priority.value, source)

    def _safe_defaults(self) -> None:
        """
        Directly commands safe default values to the IO.
        """
        self.io.set_left_voltage(0.0)
        self.io.set_right_voltage(0.0)

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
        SmartDashboard.putString("Drivetrain/driveMode", self.drive_mode.name)

        resolved_linear = self.linear_velocity_controller.resolve()
        SmartDashboard.putNumber("Drivetrain/resolvedLinear/value", resolved_linear.value)
        SmartDashboard.putString("Drivetrain/resolvedLinear/source", resolved_linear.source)
        SmartDashboard.putNumber("Drivetrain/resolvedLinear/priority", resolved_linear.priority)

        resolved_angular = self.angular_velocity_controller.resolve()
        SmartDashboard.putNumber("Drivetrain/resolvedAngular/value", resolved_angular.value)
        SmartDashboard.putString("Drivetrain/resolvedAngular/source", resolved_angular.source)
        SmartDashboard.putNumber("Drivetrain/resolvedAngular/priority", resolved_angular.priority)

        SmartDashboard.putNumber("Drivetrain/sensorData/leftVelocity", self.io.get_left_velocity())
        SmartDashboard.putNumber("Drivetrain/sensorData/rightVelocity", self.io.get_right_velocity())
        SmartDashboard.putNumber("Drivetrain/sensorData/leftVoltage", self.io.get_left_voltage())
        SmartDashboard.putNumber("Drivetrain/sensorData/rightVoltage", self.io.get_right_voltage())

    def _drive_closed_loop(
        self, 
        left_velocity: meters_per_second, 
        right_velocity: meters_per_second
    ) -> None:
        """
        Drives the component with PID + FF.
        """
        current_left_velocity = self.io.get_left_velocity()
        current_right_velocity = self.io.get_right_velocity()

        left_ff_volts = self.left_ff.calculate(current_left_velocity, left_velocity)
        right_ff_volts = self.right_ff.calculate(current_right_velocity, right_velocity)

        left_pid_volts = self.left_pid.calculate(current_left_velocity, left_velocity)
        right_pid_volts = self.right_pid.calculate(current_right_velocity, right_velocity)

        self.io.set_left_voltage(left_ff_volts + left_pid_volts)
        self.io.set_right_voltage(right_ff_volts + right_pid_volts)

    def _drive_open_loop(
        self,
        left_velocity: meters_per_second, 
        right_velocity: meters_per_second
    ) -> None:
        """
        Drives the component without PID + FF.
        """
        self.io.set_left_voltage(left_velocity / DriveConstants.MAX_LINEAR_SPEED)
        self.io.set_right_voltage(right_velocity / DriveConstants.MAX_LINEAR_SPEED)

    def execute(self) -> None:
        """
        Method that directly moves the robot each iteration.
        """
        self.publish_telemetry()

        linear_velocity = self.linear_velocity_controller.resolve().value
        angular_velocity = self.angular_velocity_controller.resolve().value
        chassis = ChassisSpeeds(linear_velocity, 0.0, angular_velocity)
        
        wheel_speeds = self.kinematics.toWheelSpeeds(chassis)
        wheel_speeds.desaturate(DriveConstants.MAX_LINEAR_SPEED)

        if self.drive_mode == DriveMode.OPEN_LOOP:
            self._drive_open_loop(wheel_speeds.left, wheel_speeds.right)
        else:
            self._drive_closed_loop(wheel_speeds.left, wheel_speeds.right)
        
        self.odometry.update(
            gyroAngle=self.io.get_angle(),
            leftDistance=self.io.get_left_distance(),
            rightDistance=self.io.get_right_distance()
        )

        self.simulated_field.setRobotPose(self.get_pose())

        self.io.update()
