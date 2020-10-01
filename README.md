# Sublime Text: Cursor Word Highlighter

A Word Highlighter plug-in.

![CursorWordHighlighter][screenshot]

## Introduction

With this plugin you will have automatically word highlighted with cursor,
you don't need any hotkey and it works on Vim mode, non-Vim mode and mouse selecting.
It also supports persistent keyword highlight with hotkey assigned
(by default `Alt+Enter` to highlight/unhighlight and `Alt+Shift+Enter` to unhighlight all).

## Installation

1. This plugin is not published on the official Package Control.
   To install, add a custom repository for Package Control with steps described
   [here](https://github.com/jfcherng-sublime/ST-my-package-control/blob/master/README.md#usage).
1. Install `CursorWordHighlighter` via Package Control.

## Options

- `"cursor_word_highlighter_enabled" : true`

  Enable or disable this plugin

- `"cursor_word_highlighter_case_sensitive" : true`

  Case sensitive or not

- `"cursor_word_highlighter_draw_outlined" : true`

  2 sytle of highlight has been provided, with draw outlined,
  plugin will only draw a outline instead of filling the words, vice versa.

- `"cursor_word_highlighter_color_scope_name" : "comment"`

  This decide the color of highlight, options are`comment`, `string`,`invalid`, etc.
  You can reach them in your .tmTheme file.

- `"cursor_word_highlighter_mark_occurrences_on_gutter" : false`

  If this comes true, it also marks all occurrences of highlighted words on the gutter bar.
  To customize the icons, the property `cursor_word_highlighter_icon_type_on_gutter` is helpful.

- `"cursor_word_highlighter_icon_type_on_gutter" : dot`

  4 valid types: dot, circle, bookmark and cross.

- `"cursor_word_highlighter_min_active_length" : 2`

  It's very likely that you don't want to highlight short words, such as a "word" which has only one character.
  In that case, we have this constrain which requires the word is at least 2-char.

- `"cursor_word_highlighter_min_active_length_persist" : 1`

  Like `cursor_word_highlighter_min_active_length` but for persistent highlighting.

## Acknowledgment

Official `WordHighlight` plugin seems to do the similar job,
but I couldn't get it work on mine, neither ST2 nor ST3, so I read its code and make this plugin.

You might also wanna check [WordHighlight][2], and the idea of persistent highlight came from [HighlightWords][3],
even some bit of code from his project, thanks [Sean Liang][4].
Actually all what I've done is combining 2 plugins together in my preferable way.

I also wrote a [blog][5] for this, but it's in Chinese, check it out if you are interested.

[screenshot]: https://raw.githubusercontent.com/jfcherng-sublime/ST-CursorWordHighlighter/chinese/docs/images/screenshot.png
[2]: https://github.com/SublimeText/WordHighlight
[3]: https://github.com/seanliang/HighlightWords
[4]: http://weibo.com/seanliang
[5]: http://www.ownself.org/blog/2014/cursor-word-highlighter-for-sublime-text.html
