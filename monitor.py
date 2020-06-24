import uuid
from getpass import getpass
from typing import Optional

from pynput.keyboard import Key, KeyCode
from speech import SpeechHandler
from hotkeys import HotKeys
from db_handler import DatabaseHandler, DatabaseInfo


class ProductivityMonitor:
    """
    TODO
      - Accept password/username as command line params
      - Specify custom keybinding through command line
        - Read from config DB/json if no command line keybinding is specified
      - Support for keywords (i.e. "label")
    """

    def __init__(self):
        # Voice to text setup
        self.speech = SpeechHandler()

        # DB setup
        user = input("Database username: ")
        password = getpass()

        self.db = DatabaseHandler(DatabaseInfo(user=user, password=password))

        # Task context
        self.curr_task = Task()

        # Hotkey setup
        bindings = {
            frozenset([Key.shift, KeyCode(vk=65)]): self.handle_input  # Shift-a
        }
        self.hot_keys = HotKeys(bindings)
        self.hot_keys.setup_listener()

    def reset_task_context(self):
        """Resets the current task to a new Task object"""
        self.curr_task = Task()

    def handle_input(self):
        """Parses and stores audio input"""
        task = self.parse_input()
        if task:
            self.db.store_task(task)
            self.reset_task_context()  # TODO - Special case this reset

    def parse_input(self) -> Optional['Task']:
        """Extracts and processes text from audio input"""
        transcribed_input = self.speech.transcribe_input()

        # Labels
        # TODO - Fix obvious "label" conflicts, re-enable labels
        try:
            if False and transcribed_input.startswith("label"):  # TODO: why are we using False here?
                label_idx = transcribed_input.find("label") + len("label")
                processed_input = transcribed_input[label_idx:].strip()
                self.curr_task.addLabel(processed_input)
            else:
                self.curr_task.setName(transcribed_input)
            return self.curr_task
        except:
            return None


class Task:
    def __init__(self, name: str = None, category: str = "default", labels=None):
        if labels is None:
            labels = []
        self.id = uuid.uuid1()
        self.name = name
        self.category = category
        self.labels = labels

    def __str__(self):
        return f"Id: {self.id} Name: {self.name} Category: {self.category} Labels: {self.labels}"

    def setName(self, name: str):
        """Setter method for {self.name}"""
        self.name = name.title()

    def addLabel(self, label: str):
        """Appends a label to {self.labels}"""
        self.labels.append(label)


if __name__ == "__main__":
    ProductivityMonitor()
