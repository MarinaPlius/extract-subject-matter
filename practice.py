import help_functions
from nltk import tokenize


"""file = open("little prince.txt", "r")
text = file.read()
file.close()"""

url = "https://en.wikipedia.org/wiki/Melania_Trump"
text = help_functions.text_from_url(url)

text_clean = help_functions.clean(text)
ent = help_functions.get_entities(text_clean)
print(ent)
key_words = help_functions.freq_words(text_clean)
subject, subject_short = help_functions.subject(text_clean, key_words)
phrase = help_functions.get_phrase(text_clean, subject, subject_short)
facts = help_functions.extract_facts(text, subject)



