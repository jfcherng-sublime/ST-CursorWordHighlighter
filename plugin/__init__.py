from . import CursorWordHighlighter

def set_up() -> None:
    """ plugin_loaded """

    CursorWordHighlighter.set_up()


def tear_down() -> None:
    """ plugin_unloaded """

    pass
