import traceback
from typing import final
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

import wpilib

from libs.faults.faults import Fault, FaultSeverity
from libs.utils.json_io import log_json_data


fault_loggable_type = int | float | str | bool


class FaultLogger:
    """
    Logs faults to a file each iteration, given a directory.
    Automatically generates session-unique filenames with FRC timestamp format.
    Faults can be queried into the logger and will be cleared at the end of run().
    """
    def __init__(self, logging_folder: str) -> None:
        log_path = Path(logging_folder)
        try:
            log_path.mkdir(parents=True, exist_ok=True)
        except Exception:
            raise RuntimeError(f"Unable to create fault directory {logging_folder}.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FRC_{timestamp}_faults.json"

        self.logging_directory = str(log_path / filename)
        self.faults_to_be_logged: list[dict[str, fault_loggable_type]] = []
        self.stored_faults: list[Fault] = []

    @final
    def log_fault(
        self,
        component_name: str | None,
        severity: FaultSeverity,
        description: str,
        exception: Exception | None = None
    ) -> None:
        """
        Stores the given info as a Fault object into the logger to be logged to a JSON once run() is called.
        """
        exception_type = exception.__class__.__name__ if exception is not None else None
        backtrace = traceback.format_exc() if exception is not None else None

        fault = Fault(
            component_name=component_name if component_name else None,
            severity=severity,
            description=description,
            timestamp=wpilib.Timer.getFPGATimestamp(),
            exception_type=exception_type,
            traceback=backtrace
        )
        self.stored_faults.append(fault)

    @final
    def run(self) -> None:
        """
        Logs the provided stored Fault objects into the directory attatched to the scheduler.
        Clears all stored faults upon a successful file write.
        """
        for fault in self.stored_faults:
            fault_dict = asdict(fault)
            self.faults_to_be_logged.append(fault_dict)
        if self.faults_to_be_logged:
            try:
                log_json_data(
                    file_path=self.logging_directory, 
                    data=self.faults_to_be_logged,
                    indent=2,
                    ensure_ascii=True,
                    append=True
                )
                self.faults_to_be_logged = []
                self.stored_faults = []
            except Exception as e:
                wpilib.reportError(
                    f"Fault logging exception occured: {e}\n"
                    "Trying next iteration..."
                )
