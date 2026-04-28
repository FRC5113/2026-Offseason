from wpilib import Joystick, RobotState

from components.game_sim.game_peice_sim import GamePieceSim

from constants import JoystickButton


class GamePieceController:
    """
    Controls the game piece simulator via teleoperation.
    """
    game_piece_sim: GamePieceSim
    controller: Joystick

    def execute(self) -> None:
        """
        Method called each iteration if the component is healthy.
        """
        if not RobotState.isTeleop():
            return

        if self.controller.getRawButton(JoystickButton.GAME_SIM_CLEAR):
            self.game_piece_sim.clear_all_fuel()
        if self.controller.getRawButton(JoystickButton.GAME_SIM_SPAWN):
            self.game_piece_sim.spawn_fuel_line()
        if self.controller.getRawButton(JoystickButton.GAME_SIM_SHOOT):
            self.game_piece_sim.shoot_fuel()
