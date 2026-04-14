from client.enums.anchor import Anchor
from client.ui.button import Button
from client.ui.text import Text


class DropDownMenu:
    def __init__(
        self,
        name,
        position,
        values,
        width,
        heigth,
        values_width,
        values_heigth,
        anchor: Anchor = Anchor.MIDBOTTOM,
    ):
        self.name = name
        self.posistion = position
        self.values = values

        self.show_values = False

        def toogle():
            self.show_values = not self.show_values

        self.nameComp = Button(
            self.name,
            width=width,
            height=heigth,
            position=(position[0], position[1]),
            anchor=anchor,
            onclickFunction=toogle,
        )
        self.valuesComp = [
            Button(
                val[0],
                position=(position[0], position[1] + values_heigth * (i + 1)),
                height=values_heigth,
                width=values_width,
                anchor=anchor,
                color=(0, 0, 0),
                bg_color=(200, 200, 200),
                hover_color=(180, 180, 180),
                onclickFunction=val[1],
            )
            for i, val in enumerate(self.values)
        ]

    def draw(self, window):
        self.nameComp.draw(window)
        if self.show_values:
            for val in self.valuesComp:
                val.draw(window)

    def handle_event(self, event):
        self.nameComp.handle_event(event)
        if self.show_values:
            for val in self.valuesComp:
                val.handle_event(event)
