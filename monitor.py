import uuid
from getpass import getpass

from pynput.keyboard import Key, KeyCode
from speech import Speech_Handler
from hotkeys import Hot_Keys
from db_handler import DB_Handler

"""
TODO
  - Accept password/username as command line params
  - Specify custom keybinding through command line
    - Read from config DB/json if no command line keybinding is specified
  - Support for keywords (i.e. "label")
"""
class Prod_Monitor():
    def __init__(self):
        #Voice to text setup
        self.speech = Speech_Handler()

        #DB setup
        user = input("Database username: ")
        password = getpass()

        self.db = DB_Handler(user, password)
        
        #Task context
        self.curr_task = Task()

        #Hotkey setup
        bindings = {
            frozenset([Key.shift, KeyCode(vk=65)]): self.handle_input # Shift-a
        }
        self.hot_keys = Hot_Keys(bindings)
        self.hot_keys.setup_listener()

    def reset_task_context(self):
        """Resets the current task to a new Task object"""
        self.curr_task = Task()
        
    def handle_input(self):
        """Parses and stores audio input"""
        task = self.parse_input()
        if task:
            self.db.store_task(task)
            self.reset_task_context() #TODO - Special case this reset
    
    def parse_input(self):
        """Extracts and processes text from audio input"""
        input = self.speech.transcribe_input()

        #Labels
        #TODO - Fix obvious "label" conflicts, re-enable labels
        try:
            if False and input.startswith("label"):
                label_idx = input.find("label") + len("label")
                processed_input = input[label_idx:].strip()
                self.curr_task.addLabel(processed_input);
            else:
                self.curr_task.setName(input)
            return self.curr_task
        except:
            return None

    
class Task():
    def __init__(self, name: str=None, category: str="default", labels: list=[]):        
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
    pm = Prod_Monitor()
