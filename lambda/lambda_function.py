from googletrans import Translator

translated = Translator().translate("bonjour", dest="en")

print(translated.text)
