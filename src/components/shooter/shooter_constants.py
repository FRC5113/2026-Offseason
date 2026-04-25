from wpimath.units import volts


class ShooterConstants:
    MAX_VOLTAGE: volts = 12.0


class ShooterCAN:
    """
    Holds the CAN ids for each motor used in the component.
    """
    LEFT_SHOOTER_MOTOR = 8
    RIGHT_SHOOTER_MOTOR = 9
