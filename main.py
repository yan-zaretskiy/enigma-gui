from enigma.machine import EnigmaMachine

from kivy.config import Config

Config.set("graphics", "width", "1200")
Config.set("graphics", "height", "700")

from kivy.app import App
from kivy.core.window import Window
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from knob import Knob
from string import ascii_uppercase

letter_to_number = {l: n for (n, l) in enumerate(ascii_uppercase)}


class ColoredLabel(Label):
    bgcolor = ListProperty([51 / 255, 51 / 255, 51 / 255, 1])
    thickness = NumericProperty(5)


class EnigmaWindow(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_keyboard()

        self.letters = "QWERTYUIOPASDFGHJKLZXCVBNM"
        self.lamps = self.ids["lamps"]
        self.knobs = [self.ids["knob1"], self.ids["knob2"], self.ids["knob3"]]
        self.labels = {}
        self.active_lamp = None

        self.enigma = EnigmaMachine.from_key_sheet(
            rotors="II IV V",
            reflector="B",
            ring_settings=[1, 20, 11],
            plugboard_settings="AV BS CG DL FU HZ IN KM OW RX",
        )
        self.enigma.set_display("AAA")
        for knob in self.knobs:
            knob.bind(value=self.on_knob_turned)

        for letter in self.letters:
            lbl = ColoredLabel(text="[b]{}[/b]".format(letter), markup=True)
            self.lamps.add_widget(lbl)
            self.labels[letter] = lbl

    def request_keyboard(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, "text")
        if self._keyboard.widget:
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self._keyboard.bind(on_key_up=self._on_keyboard_up)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] == "escape":
            app = App.get_running_app()
            app.stop()
        elif keycode[1].upper() in self.letters and self.active_lamp is None:
            pressed_letter = keycode[1].upper()
            c = self.enigma.key_press(pressed_letter)
            self.update_knobs()
            self.labels[c].color = [1, 1, 1, 1]
            self.active_lamp = c
        return True

    def _on_keyboard_up(self, keyboard, keycode):
        if self.active_lamp is not None:
            self.labels[self.active_lamp].color = [64 / 255, 64 / 255, 64 / 255, 1.0]
            self.active_lamp = None
        return True

    def on_knob_turned(self, instance, value):
        letters = [ascii_uppercase[int(knob.value)] for knob in self.knobs]
        self.enigma.set_display("".join(letters))

    def update_knobs(self):
        display = self.enigma.get_display()
        for knob, value in zip(self.knobs, display):
            knob.value = letter_to_number[value]


class EnigmaApp(App):
    def build(self):
        return EnigmaWindow()


if __name__ == "__main__":
    #    Window.fullscreen = 'auto'
    EnigmaApp().run()
