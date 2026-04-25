from magicbot import MagicRobot

from wpilib import Joystick

from components.drivetrain.drivetrain import Drivetrain
from components.drivetrain.drivetrain_io.io_base import DrivetrainIOBase
from components.drivetrain.drivetrain_controller import DrivetrainController
from components.drivetrain.drivetrain_io.real_io import RealDrivetrainIO
from components.drivetrain.drivetrain_io.simulated_io import SimulatedDrivetrainIO

from components.arm.arm import Arm
from components.arm.arm_io.io_base import ArmIOBase
from components.arm.arm_controller import ArmController
from components.arm.arm_io.real_io import RealArmIO
from components.arm.arm_io.simulated_io import SimulatedArmIO

from components.intake.intake import Intake
from components.intake.intake_io.io_base import IntakeIOBase
from components.intake.intake_controller import IntakeController
from components.intake.intake_io.real_io import RealIntakeIO
from components.intake.intake_io.simulated_io import SimulatedIntakeIO

from components.shooter.shooter import Shooter
from components.shooter.shooter_io.io_base import ShooterIOBase
from components.shooter.shooter_controller import ShooterController
from components.shooter.shooter_io.real_io import RealShooterIO
from components.shooter.shooter_io.simulated_io import SimulatedShooterIO

from libs import FaultLogger, ActionScheduler

from actions.taxi_drive import taxi_drive


class MyRobot(MagicRobot):
    fault_logger: FaultLogger
    controller: Joystick

    drivetrain_controller: DrivetrainController
    arm_controller: ArmController
    intake_controller: IntakeController
    shooter_controller: ShooterController

    drivetrain: Drivetrain
    arm: Arm
    intake: Intake
    shooter: Shooter

    drivetrain_io: DrivetrainIOBase
    arm_io: ArmIOBase
    intake_io: IntakeIOBase
    shooter_io: ShooterIOBase

    def createObjects(self) -> None:
        self.controller = Joystick(0)
        self.fault_logger = FaultLogger("faults/")
        self.action_scheduler = ActionScheduler(self.fault_logger)

        if self.isSimulation():
            self.drivetrain_io = SimulatedDrivetrainIO()
            self.arm_io = SimulatedArmIO()
            self.intake_io = SimulatedIntakeIO()
            self.shooter_io = SimulatedShooterIO()
        else:
            self.drivetrain_io = RealDrivetrainIO(self.fault_logger)
            self.arm_io = RealArmIO(self.fault_logger)
            self.intake_io = RealIntakeIO(self.fault_logger)
            self.shooter_io = RealShooterIO(self.fault_logger)

    def robotPeriodic(self) -> None:
        self.fault_logger.run()
        self.action_scheduler.run()
    
    def autonomousInit(self) -> None:
        self.action_scheduler.schedule(taxi_drive(self.drivetrain), "taxi_drive")
