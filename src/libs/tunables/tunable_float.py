from ntcore import NetworkTableInstance


class TunableFloat:
    """
    TunableValue creates a double value that can be changed through NetworkTables and will update
    in the codebase. 

    TunableValue does not change any values (including objects) previously made with the value on update.
    """
    def __init__(self, directory: str, default: float) -> None:
        """
        Creates an entry that can be altered through NetworkTables.
        
        :param directory: The directory that the value will be saved under in NetworkTables
        :param default: The default value published at runtime
        """
        self._default = default

        nt = NetworkTableInstance.getDefault()
        self._entry = nt.getEntry(directory)

        self._entry.setDouble(default)
        self._getter = lambda: self._entry.getDouble(default)

        self._last_value = self._getter()

    @property
    def value(self) -> float:
        """
        Returns the last recorded value of the tunable object.
        """
        return self._last_value

    def update(self) -> bool:
        """
        Updates the internal value and returns True if the value has been changed since last checked.
        """
        current = self._getter()
        if current != self._last_value:
            self._last_value = current
            return True
        return False
