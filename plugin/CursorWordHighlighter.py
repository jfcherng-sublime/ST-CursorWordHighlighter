import jieba
import re
import sublime
import sublime_plugin

from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Tuple,
)


# Global variables
chinese_regex_obj = re.compile("[\u4E00-\u9FD5]+", re.U)
search_limit = 20000
file_size_limit = 4194304
settings = None  # type: Optional[sublime.Settings]
word_separators = ""
word_separators_re_escaped = ""
highlighter_enabled = True
case_sensitive = True
whole_word = True
draw_outline = True
color_scope = "comment"
highlight_on_gutter = False
gutter_icon_type = ""
search_flags = 0
draw_flags = sublime.DRAW_NO_FILL
min_active_length = 2
min_active_length_persist = 1

color_highlight_scopes = [
    "entity.name.class",
    "support.function",
    "variable.parameter",
    "invalid.deprecated",
    "invalid",
    "string",
]

# 1就在今天進行測試了bbb，你好嗎
# bbb-b測試bbbasdbn
# ggg測試ascxias
# 測試你好嗎
# 你好嗎
# 測試
# 測試


def set_up() -> None:
    global settings

    settings = sublime.load_settings("Preferences.sublime-settings")

    settings.add_on_change("Preferences-reload", update_settings)
    sublime.set_timeout_async(jieba.initialize, 0)


def tear_down() -> None:
    pass


def update_settings() -> None:
    global settings, highlighter_enabled, case_sensitive, whole_word, draw_outline, color_scope
    global highlight_on_gutter, gutter_icon_type, search_flags, draw_flags
    global word_separators, word_separators_re_escaped
    global min_active_length, min_active_length_persist

    if not settings:
        settings = sublime.load_settings("Preferences.sublime-settings")

    word_separators = str(settings.get("word_separators", ""))
    word_separators_re_escaped = re.escape(word_separators)

    highlighter_enabled = bool(settings.get("cursor_word_highlighter_enabled", True))
    case_sensitive = bool(settings.get("cursor_word_highlighter_case_sensitive", True))
    whole_word = bool(settings.get("cursor_word_highlighter_whole_word", True))
    draw_outline = bool(settings.get("cursor_word_highlighter_draw_outlined", True))
    color_scope = str(settings.get("cursor_word_highlighter_color_scope_name", "comment"))
    highlight_on_gutter = bool(settings.get("cursor_word_highlighter_mark_occurrences_on_gutter", False))
    min_active_length = int(cast(int, settings.get("cursor_word_highlighter_min_active_length", 2)))
    min_active_length_persist = int(cast(int, settings.get("cursor_word_highlighter_min_active_length_persist", 1)))

    if highlight_on_gutter:
        gutter_icon_type = str(settings.get("cursor_word_highlighter_icon_type_on_gutter", "dot"))
    else:
        gutter_icon_type = ""

    if not case_sensitive:
        search_flags = sublime.IGNORECASE
    else:
        search_flags = 0

    if not draw_outline:
        draw_flags = sublime.DRAW_NO_OUTLINE
    else:
        draw_flags = sublime.DRAW_NO_FILL


def get_word_by_point(view: sublime.View, pt: int) -> Tuple[sublime.Region, str]:
    word_region_st = view.word(pt)
    word_st = view.substr(word_region_st)

    start_point = word_region_st.begin()
    offset = 0
    for word in jieba.cut(word_st):
        word_len = len(word)
        jieba_word_span = (
            start_point + offset,
            start_point + offset + word_len,
        )

        if jieba_word_span[0] <= pt < jieba_word_span[1]:
            return (sublime.Region(*jieba_word_span), word)

        offset += word_len

    return (sublime.Region(-1, -1), "")


def get_word_regex(word: str, is_whole_word: bool = False) -> str:
    if not word:
        return ""

    if is_whole_word:
        regex_l = "(?<=[\\s{}]|[^\u0001-\u007f])".format(word_separators_re_escaped)
        regex_r = "(?=[\\s{}]|[^\u0001-\u007f])".format(word_separators_re_escaped)
    else:
        regex_l = ""
        regex_r = ""

    if chinese_regex_obj.match(word[0]):
        regex_l = ""

    if chinese_regex_obj.match(word[-1]):
        regex_r = ""

    return regex_l + re.escape(word) + regex_r


class CursorWordHighlighterListener(sublime_plugin.EventListener):
    def on_post_text_command(self, view: sublime.View, command_name: str, args: Optional[Dict[str, Any]]) -> None:
        if not args:
            args = {}

        if not highlighter_enabled:
            view.erase_regions("CursorWordHighlighter")
            return

        is_limited_size = view.size() > file_size_limit

        regions = []  # type: List[sublime.Region]
        processedWords = []
        occurrencesMessage = []
        occurrencesCount = 0
        if (
            command_name == "drag_select"
            or command_name == "move"
            or (command_name == "set_motion" and "move" in args["motion"])
        ):
            for sel in view.sel():
                string = ""

                if sel.empty():
                    string = get_word_by_point(view, sel.b)[1]

                    if not string.strip():
                        break

                    if string not in processedWords:
                        processedWords.append(string)
                        if string and all([c not in word_separators for c in string]):
                            regions = self.find_regions(view, regions, string, is_limited_size)

                else:
                    word = view.word(sel)
                    if word.end() == sel.end() and word.begin() == sel.begin():
                        string = view.substr(word).strip()
                        if string not in processedWords:
                            processedWords.append(string)
                            if string and all([c not in word_separators for c in string]):
                                regions = self.find_regions(view, regions, string, is_limited_size)

                if len(string) < min_active_length:
                    regions = []
                    continue

                occurrences = len(regions) - occurrencesCount
                if occurrences > 0:
                    occurrencesMessage.append(
                        str(occurrences) + " occurrence" + ("s" if occurrences != 1 else "") + ' of "' + string + '"'
                    )
                    occurrencesCount = occurrencesCount + occurrences

            view.erase_regions("CursorWordHighlighter")
            if regions:
                view.add_regions("CursorWordHighlighter", regions, color_scope, gutter_icon_type, draw_flags)
            else:
                view.erase_status("CursorWordHighlighter")

    def find_regions(
        self, view: sublime.View, regions: List[sublime.Region], string: str, limited_size: int
    ) -> List[sublime.Region]:
        search = get_word_regex(string, whole_word)

        if not limited_size:
            regions = view.find_all(search, search_flags)
        else:
            chars = search_limit
            visible_region = view.visible_region()
            begin = 0 if visible_region.begin() - chars < 0 else visible_region.begin() - chars
            end = visible_region.end() + chars
            from_point = begin
            while True:
                region = view.find(search, from_point, search_flags)
                if region:
                    regions.append(region)
                    if region.end() > end:
                        break
                    else:
                        from_point = region.end()
                else:
                    break

        return regions


class PersistentHighlightWordsCommand(sublime_plugin.WindowCommand):
    def get_words(self, text: str) -> List[str]:
        return text.split()

    def run(self) -> None:
        view = self.window.active_view()

        if not view:
            return

        word_list = self.get_words(str(view.settings().get("cursor_word_highlighter_persistant_highlight_text", "")))
        cursor_word = ""
        for sel in view.sel():
            if sel.empty():
                cursor_word = get_word_by_point(view, sel.b)[1].strip()

                if not cursor_word:
                    cursor_word = view.substr(view.word(sel)).strip()
            else:
                cursor_word = view.substr(sel).strip()

            if len(cursor_word) < min_active_length_persist:
                cursor_word = ""
                continue

            if cursor_word in word_list:
                word_list.remove(cursor_word)
            else:
                word_list.append(cursor_word)

            break

        display_list = " ".join(word_list)
        self.highlight(display_list)

    def highlight(self, text: str) -> None:
        self.window.run_command("persistent_unhighlight_words")

        view = self.window.active_view()

        if not view:
            return

        words = self.get_words(text)
        size = 0
        word_set = set()
        for word in words:
            if len(word) < min_active_length or word in word_set:
                continue

            word_set.add(word)

            search = get_word_regex(word, whole_word)
            regions = view.find_all(search, search_flags)
            highlightName = "cursor_word_highlighter_persistant_highlight_word_%d" % size

            view.add_regions(
                highlightName,
                regions,
                color_highlight_scopes[size % len(color_highlight_scopes)],
                "",
                sublime.DRAW_SOLID_UNDERLINE,
            )

            size += 1

        view.settings().set("cursor_word_highlighter_persistant_highlight_size", size)
        view.settings().set("cursor_word_highlighter_persistant_highlight_text", text)


class PersistentUnhighlightWordsCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        view = self.window.active_view()

        if not view:
            return

        size = int(cast(int, view.settings().get("cursor_word_highlighter_persistant_highlight_size", 0)))
        for i in range(0, size):
            view.erase_regions("cursor_word_highlighter_persistant_highlight_word_%d" % i)

        view.settings().set("cursor_word_highlighter_persistant_highlight_size", 0)
        view.settings().erase("cursor_word_highlighter_persistant_highlight_text")
