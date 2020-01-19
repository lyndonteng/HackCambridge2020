from googletrans import Translator
translator = Translator()

### put this in the logic for handling input.
result = translator.translate(input_string, dest='en')