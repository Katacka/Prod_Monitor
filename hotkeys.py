from typing import Dict, FrozenSet, Callable, Union

from pynput.keyboard import Key, Listener, KeyCode

KeySet = FrozenSet[Union[Key, KeyCode]]
KeyListenerFunction = Callable[[], None]


class HotKeys:
    """TODO: add Mac support for the key bindings."""
    
    def __init__(self, bindings: Dict[KeySet, KeyListenerFunction]):
        self.bindings = bindings
        self.pressed_vks = set()

    @staticmethod
    def get_vk(key: Union[Key, KeyCode]) -> Union[int, str]:
        """Returns the virtual keycode for a given key

        Args:
            key - A pynput.keyboard Key or KeyCode object

        Returns (EITHER int or str):
            int - Contextual {key}'s virtual keycode
            str - Contextual {key}'s string value
        """
        if isinstance(key, Key):
            return key.value.vk

        if isinstance(key, KeyCode):
            return key.char

        raise ValueError("Wrong type passed to get_vk!")

    def is_combination_pressed(self, combination: frozenset) -> bool:
        """Determines if a given key combination is currently pressed

        Returns:
            bool - True if all keys in the combination are pressed
        """
        return all([self.get_vk(key) in self.pressed_vks for key in combination])

    def on_press(self, key: Key) -> None:
        """Event call activating on key press

        Updates the status of the pressed key. Activates satisfied hotkey bindings 

        Args:
            key - A pynput.keyboard Key object
        """
        print("An on_press event was registered with key: " + str(key))

        vk = self.get_vk(key)  # Get the key's vk
        self.pressed_vks.add(vk)  # Add it to the set of currently pressed keys

        print("Current pressed keys: " + str(self.pressed_vks))

        for combination in self.bindings:  # Loop through each combination
            if self.is_combination_pressed(combination):  # Check if all keys in the combination are pressed
                self.bindings[combination]()  # If so, execute the function

    def on_release(self, key: Key) -> None:
        """Event call activating on key release

        Updates the status of the pressed key

        Args:
            key - A pynput.keyboard Key object
        """

        print("An on_release event was registered with key: " + str(key))

        vk = self.get_vk(key)  # Get the key's vk
        if vk in self.pressed_vks:
            self.pressed_vks.remove(vk)  # Remove it from the set of currently pressed keys

    def setup_listener(self) -> None:
        """Creates a daemon listening for hotkey bindings"""
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            print("Listener joining...")
            listener.join()
