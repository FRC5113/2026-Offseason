from wpimath.units import meters, percent, volts, radians, radians_per_second


class ShooterConstants:
    MAX_VOLTAGE: volts = 12.0
    MAX_VELOCITY: radians_per_second = 110.2
    FLYWHEEL_RADIUS: meters = 0.0508
    GEAR_RATIO = 1.5

    SHOOTER_HEIGHT: meters = 0.635 # Height of the shooter relative to the ground
    SHOOTER_HOOD_ANGLE: radians = 0.610

    SHOOTER_PERCENT: percent = 0.3 # Static shooter percent; TODO: to be replaced


class ShooterCAN:
    """
    Holds the CAN ids for each motor used in the component.
    """
    LEFT_SHOOTER_MOTOR = 8
    RIGHT_SHOOTER_MOTOR = 9
