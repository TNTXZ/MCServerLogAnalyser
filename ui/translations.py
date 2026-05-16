import json
import locale
import os


def _detect_system_language(available_languages):
    try:
        sys_lang, _ = locale.getdefaultlocale()
        if sys_lang:
            lang_code = sys_lang[:2]
            if lang_code in available_languages:
                return lang_code
    except Exception:
        pass

    try:
        lc = os.environ.get("LANG") or os.environ.get("LC_ALL") or ""
        if lc:
            lang_code = lc[:2]
            if lang_code in available_languages:
                return lang_code
    except Exception:
        pass

    return "en"


class Translator:
    def __init__(self, json_path=None):
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), "translations.json")

        with open(json_path, encoding="utf-8") as f:
            self._tr = json.load(f)

        detected = _detect_system_language(self._tr.keys())
        self._current_lang = detected if detected in self._tr else "en"

    @property
    def languages(self):
        return list(self._tr.keys())

    def set_language(self, lang):
        if lang in self._tr:
            self._current_lang = lang

    def get(self, key):
        return self._tr[self._current_lang].get(key, key)

    @property
    def lang(self):
        return self._current_lang
