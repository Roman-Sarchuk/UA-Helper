from random import randrange
import json
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class Dictionary:
    def __init__(self, js_filename: str, mod: str):
        """
        :param js_filename: file.js name OR path to file.js
        :param mod: "alph" OR "rand"
        """
        self.mod = mod
        self.js_filename = js_filename
        self.phrases = []
        self.load_phrases()

    def get_alphabetically(self) -> dict or None:
        if not self.phrases:
            return None

        return self.phrases.pop(0)

    def get_random(self) -> dict or None:
        if not self.phrases:
            return None

        return self.phrases.pop(randrange(len(self.phrases)))

    def get(self) -> dict or None:
        if self.mod == "alph":
            return self.get_alphabetically()
        elif self.mod == "rand":
            return self.get_random()

    def load_phrases(self):
        try:
            with open(self.js_filename, "r", encoding="utf-8") as f:
                self.phrases = json.load(f)
        except (FileExistsError, FileNotFoundError):
            self.phrases.append({"incorrect": "Error with json file (dictionary)",
                                 "correct": "Error with json file (dictionary)"})


# region --- Screen classes ---
# region *** Templates ***
class BaseWindow(Screen):
    main_layout = ObjectProperty(BoxLayout())
    nav_layout = ObjectProperty(BoxLayout())

    def __init__(self, **kwargs):
        super(BaseWindow, self).__init__(**kwargs)
        # Menu's Buttons
        self.btn_lst = []
        self.nav_btn_lst = []

    def add_button(self, text="Button"):
        self.btn_lst.append(Button(text=text))
        self.main_layout.add_widget(self.btn_lst[-1])

    def add_nav_button(self, text="Button"):
        self.nav_btn_lst.append(Button(text=text))
        self.nav_layout.add_widget(self.nav_btn_lst[-1])


class PlayableWindow(BaseWindow):
    def __init__(self, **kwargs):
        super(PlayableWindow, self).__init__(**kwargs)
        self.nav_layout.size_hint = 0.1, 0.25

        # Navigate area
        self.add_nav_button(text="x")
        self.nav_btn_lst[-1].bind(on_release=lambda instance: app.set_screen("main_menu", "down"))
        self.add_nav_button(text="<-")
        self.nav_btn_lst[-1].bind(on_release=lambda instance: app.set_screen("IFM", "right"))
        self.add_nav_button(text="R")

        # Main area
        self.lbl_phrase = Label(text="~ some phrase ~", font_size=25)
        self.main_layout.add_widget(self.lbl_phrase)
        self.btn_phrase = Button(text="-<·>-", size_hint=(1, 0.5), font_size=60)
        self.main_layout.add_widget(self.btn_phrase)
# endregion


# region *** Menus ***
class MainMenu(BaseWindow):
    def __init__(self, **kwargs):
        super(MainMenu, self).__init__(**kwargs)

        self.main_layout.add_widget(Label(text=": Menu Title :", font_size=50))

        # Main area
        self.add_button("Incorrect Forms")
        self.btn_lst[-1].bind(on_release=lambda instance: app.set_screen("IFM"))
        self.add_button("=== In Developing ===")
        self.add_button("Quit")
        self.btn_lst[-1].bind(on_release=lambda instance: app.stop())


class IncorrectFormMenu(BaseWindow):    # IFM
    def __init__(self, **kwargs):
        super(IncorrectFormMenu, self).__init__(**kwargs)

        self.main_layout.add_widget(Label(text=": Incorrect Form :", font_size=50))

        # Main area
        self.add_button("Simple")
        self.btn_lst[-1].bind(on_release=lambda instance: app.set_screen("IFM_simple"))
        self.add_button("Random")
        self.btn_lst[-1].bind(on_release=lambda instance: app.set_screen("IFM_rand"))
        self.add_button("=== Dictionary ===")
        # self.nav_btn_lst[-1].bind(on_release=lambda instance: app.set_screen("IFM_dict"))

        # Navigate area
        self.add_nav_button("<-")
        self.nav_btn_lst[-1].bind(on_release=lambda instance: app.set_screen("main_menu", "right"))
# endregion


# region *** Incorrect Form Windows ***
class SimpleIFMWindow(PlayableWindow):
    dictionary = Dictionary("dictionary.json", "alph")
    btn_status = {"next": "> > >", "show": "-<·>-", "none": "..."}
    color_status = {"incorrect": (0.24, 0.68, 0.91, 1), "correct": (0.11, 0.85, 0.5, 1),
                    "none": (1, 1, 1, 1), "restart": (0.9, 0.49, 0.9, 1)}
    phrase = []

    def __init__(self, **kwargs):
        super(SimpleIFMWindow, self).__init__(**kwargs)
        self._init()
        self.btn_phrase.bind(on_press=self.switch_phrase)
        self.nav_btn_lst[-1].bind(on_press=self.restart)

    def _init(self):
        self.phrase = self.dictionary.get()
        self.lbl_phrase.text = self.phrase["incorrect"]
        self.btn_phrase.text = self.btn_status["show"]
        self.btn_phrase.color = self.color_status["incorrect"]

    def switch_phrase(self, instance):
        if self.btn_phrase.text == self.btn_status["none"]:
            return
        elif self.btn_phrase.text == self.btn_status["show"]:
            self.lbl_phrase.text = self.phrase["correct"]
            self.btn_phrase.text = self.btn_status["next"]
            self.btn_phrase.color = self.color_status["correct"]
        elif self.btn_phrase.text == self.btn_status["next"]:
            self.phrase = self.dictionary.get()
            if self.phrase is None:
                self.lbl_phrase.text = "~ ви дійшли до кінця ~\n         ! мої вітання !"
                self.btn_phrase.text = self.btn_status["none"]
                self.btn_phrase.color = self.color_status["none"]
                self.nav_btn_lst[-1].color = self.color_status["restart"]
                return
            self.lbl_phrase.text = self.phrase["incorrect"]
            self.btn_phrase.text = self.btn_status["show"]
            self.btn_phrase.color = self.color_status["incorrect"]

    def restart(self, instance):
        self.dictionary.load_phrases()
        self.nav_btn_lst[-1].color = self.color_status["none"]
        self._init()


class RandIFMWindow(SimpleIFMWindow):
    dictionary = Dictionary("dictionary.json", "rand")


class DictIFMWindow(PlayableWindow):
    pass
# endregion
# endregion


# region --- App ---
class MyApp(App):
    sm = ScreenManager()

    def build(self):
        # Menus
        self.sm.add_widget(MainMenu(name="main_menu"))
        self.sm.add_widget(IncorrectFormMenu(name="IFM"))
        # IFM windows
        self.sm.add_widget(SimpleIFMWindow(name="IFM_simple"))
        self.sm.add_widget(RandIFMWindow(name="IFM_rand"))
        return self.sm

    def set_screen(self, name, direction="left"):
        self.sm.current = name
        self.sm.transition.direction = direction


if __name__ == '__main__':
    app = MyApp()
    app.run()
# endregion
