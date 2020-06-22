from pynput.keyboard import Key, KeyCode, Listener

class Hot_Keys():
    def __init__(self, bindings):
        self.bindings = bindings
        self.pressed_vks = set()

    def get_vk(self, key: Key):
        """Returns the virtual keycode for a given key

        Args:
            key - A pynput.keyboard Key object

        Returns:
            int - Contextual {key}'s virtual keycode
        """
        return key.vk if hasattr(key, 'vk') else key.value.vk

    def is_combination_pressed(self, combination: frozenset):
        """Determines if a given key combination is currently pressed

        Returns:
            bool - True if all keys in the combination are pressed
        """
        return all([self.get_vk(key) in self.pressed_vks for key in combination])

    def on_press(self, key):
        """Event call activating on key press

        Updates the status of the pressed key. Activates satisfied hotkey bindings 

        Args:
            key - A pynput.keyboard Key object
        """
        vk = self.get_vk(key)  # Get the key's vk
        self.pressed_vks.add(vk)  # Add it to the set of currently pressed keys

        for combination in self.bindings:  # Loop through each combination
            if self.is_combination_pressed(combination):  # Check if all keys in the combination are pressed
                self.bindings[combination]()  # If so, execute the function

    def on_release(self, key):
        """Event call activating on key release

        Updates the status of the pressed key

        Args:
            key - A pynput.keyboard Key object
        """
        vk = self.get_vk(key)  # Get the key's vk
        if vk in self.pressed_vks:
            self.pressed_vks.remove(vk)  # Remove it from the set of currently pressed keys

    def setup_listener(self):
        """Creates a daemon listening for hotkey bindings"""
        with Listener(on_press=self.on_press, on_release=self.on_release) as listener:
            listener.join()
    
