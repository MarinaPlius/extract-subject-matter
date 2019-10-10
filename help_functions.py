import requests
from bs4 import BeautifulSoup
import re
from nltk import tokenize, FreqDist, pos_tag, ne_chunk, tree
#import pickle
#import nltk
#from trigram_tagger import SubjectTrigramTagger
import spacy
#import textacy.extract
import semistructured_statements

nltk.data.path.append('nltk_data/')

#download stop word list
file = open("stopwords.txt", "r")
stop_words = file.read().split()
file.close()

NOUNS = ['NN', 'NNS', 'NNP', 'NNPS']
VERBS = ['VB', 'VBG', 'VBD', 'VBN', 'VBP', 'VBZ']


def text_from_url(url):
    """extracts text from an url"""
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        title = soup.find('title').get_text()
    except: 
        pass
    document = ' '.join([p.get_text() for p in soup.find_all('p')])
    document1 = ' '.join([p.get_text() for p in soup.find_all('div')])
    return  title + document + document1

def clean(text):
    """removes enronious characters, extra whitespace and stop words"""
    text = re.sub('[^A-Za-z .-]+', ' ', text)
    text = ' '.join([i for i in text.split() if i not in stop_words])
    return text

def freq_words(text):
    """chooses the most frequent nouns"""
    tokens = tokenize.word_tokenize(text)
    words = [word.lower() for word in tokens if word.isalnum() and not word.lower() in stop_words]
    fdist = FreqDist(words)
    most_freq_words = [w for w, c in fdist.most_common(15) if pos_tag([w], tagset='universal')[0][1] == "NOUN"]
    return most_freq_words

def get_entities(text):
    """returns list of most common Named Entities using NLTK Chunking"""
    entities = []
    sentences = tokenize.sent_tokenize(text)
    sentences = [tokenize.word_tokenize(sent) for sent in sentences]

    # Part of Speech Tagging
    sentences = [pos_tag(sent) for sent in sentences]
    for tagged_sentence in sentences:
        for chunk in ne_chunk(tagged_sentence):
            if type(chunk) == tree.Tree:
                entities.append(' '.join([c[0] for c in chunk]).lower())

    #Choosing the most common
    freq_ent = [w for w, c in FreqDist(entities).most_common(50)]
    return freq_ent

def subject(text, keywords):
    """returns a subject of a text: frequent words intersected with named entities"""
    entities = get_entities(text)
    subject = []
    subject_short = []
    for entity in entities:
        for ent in entity.split():
            if ent in keywords:
                subject.append(entity)
                subject_short.append(ent)
    return subject[0], subject_short[0]

"""def trained_tagger(existing=False):


    if existing:
        trigram_tagger = pickle.load(open('trained_tagger.pkl', 'rb'))
        return trigram_tagger

    # Aggregate trained sentences for N-Gram Taggers
    train_sents = nltk.corpus.brown.tagged_sents()
    train_sents += nltk.corpus.conll2000.tagged_sents()
    train_sents += nltk.corpus.treebank.tagged_sents()

    # Create instance of SubjectTrigramTagger and persist instance of it
    trigram_tagger = SubjectTrigramTagger(train_sents)
    pickle.dump(trigram_tagger, open('trained_tagger.pkl', 'wb'))

    return trigram_tagger"""


"""def get_svo(sentence, subject):

    subject_idx = next((i for i, v in enumerate(sentence)
                    if v[0].lower() == subject), None)
    data = {'subject': subject}
    for i in range(subject_idx, len(sentence)):
        found_action = False
        for j, (token, tag) in enumerate(sentence[i+1:]):
            if tag in VERBS:
                data['action'] = token
                found_action = True
            if tag in NOUNS and found_action == True:
                data['object'] = token
                data['phrase'] = sentence[i: i+j+2]
                return data
    return {}"""

"""def get_phrase(text, subject, subject_short):

    trigram_tagger = trained_tagger(existing=True)
    sentences = tokenize.sent_tokenize(text)
    sentences = [tokenize.word_tokenize(sent) for sent in sentences]
    sentences = [sentence for sentence in sentences if subject_short in [word.lower() for word in sentence]]
    tagged_sents = [trigram_tagger.tag(sent) for sent in sentences]
    svos = [get_svo(sentence, subject_short) for sentence in tagged_sents]
    phrase = []
    return svos """

def extract_facts(text, subject):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    #statements = textacy.extract.semistructured_statements(doc, subject)
    statements = semistructured_statements.semistructured_statements(doc, subject)
    facts = []
    for statement in statements:
        subject, verb, fact = statement
        facts.append((str(fact)).strip())
    facts = list(set(facts))
    return facts















