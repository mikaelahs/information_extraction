'''
Last edited: June 22, 2017
@author mhoffmanstapleton@usfca.edu
'''

# This is not a part of the program; it is a separate file showing how I trained a custom ner and custom relationship model. The
# relationship model, called rel_band_classifier.svm, is used in the program. The custom ner model is NOT used in the program. I chose
# to implement the pre-existing ner model in the program, and only use the custom one as an input to the relationship model when
# training it, i.e. in this file. Keep in mind that this file was written long before finalizing the code in the program, and that it
# is hardcoded to run on my computer. I include it simply to give you an idea of how I trained the relationship model.


from bs4 import BeautifulSoup
import re
import sys
sys.path.append('/Users/Mikaela/mitie/MITIE/mitielib')
from mitie import *
from get_html_docs import get_html_docs
reload(sys)
sys.setdefaultencoding('utf8')

ner = named_entity_extractor('/Users/Mikaela/mitie/MITIE/MITIE-models/english/ner_model.dat')
trainer = ner_trainer("/Users/Mikaela/mitie/MITIE/MITIE-models/english/total_word_feature_extractor.dat")
bands = ['10000_Maniacs', 'Belly', 'Black_Star', 'Bob_Marley_and_the_Wailers','The_Breeders', 'Lupe_Fiasco',
         'Run_the_Jewels', 'Talking_Heads', 'Throwing_Muses', 'Tom_Tom_Club']
urls = ['https://en.wikipedia.org/wiki/10,000_Maniacs', 'https://en.wikipedia.org/wiki/Belly_(band)', 'https://en.wikipedia.org/wiki/Black_Star_(rap_duo)',
            'https://en.wikipedia.org/wiki/Bob_Marley_and_the_Wailers', 'https://en.wikipedia.org/wiki/The_Breeders', 'https://en.wikipedia.org/wiki/Lupe_Fiasco',
            'https://en.wikipedia.org/wiki/Run_the_Jewels', 'https://en.wikipedia.org/wiki/Talking_Heads', 'https://en.wikipedia.org/wiki/Throwing_Muses',
            'https://en.wikipedia.org/wiki/Tom_Tom_Club']
get_html_docs = get_html_docs()

def get_terms(filename, band = False, members = None):
    '''
    Given a filename, this function is responsible for extracting relevant terms that can be used to identify entities to train on. If the
    file corresponds to a person, then these terms consist of acts found in the associated acts section in the info box. Otherwise, the 
    list of members created from get_html_docs.py can used, and no scraping is necessary.
    :param filename: the file from which to train on
    :type filename: string
    :param band: whether it's a band or not
    :type band: boolean
    :param members: if it's a band, then this is the list of members
    :type members: None or list
    :return: a list where the first element is the Beautiful Soup object, the second element is the name of the band/person, and the third
     element is the list of members/acts 
    :rtype: list
    '''
    html = open(''.join(['/Users/Mikaela/Desktop/test/', filename]), 'r')
    soup = BeautifulSoup(html, 'html.parser')
    html.close()
    name = re.sub('.html', '', filename)
    # If it's a person then find relevant bands
    if band == False:
        acts = []
        i = 0
        # Grab acts from the associated acts list if possible (more specific set of terms)
        try:
            # Could be under this class
            try:
                for text in soup.find(class_="infobox vcard plainlist").find_all("tr"):
                    if re.search("Associated\sacts", text.text):
                        matches = soup.find(class_="infobox vcard plainlist").find_all("tr")[i].find_all("a")
                        for match in matches:
                            acts.append(re.sub("\s(\(.*\))", "", match['title']))
                    else:
                        i = i + 1
            # But also check under this class
            except:
                for text in soup.find(class_="infobox biography vcard").find_all("tr"):
                    if re.search("Associated\sacts", text.text):
                        matches = soup.find(class_="infobox biography vcard").find_all("tr")[i].find_all("a")
                        for match in matches:
                            acts.append(re.sub("\s(\(.*\))", "", match['title']))
                    else:
                        i = i + 1
        # Otherwise just set acts to the list of ten bands (more general set of terms)
        except:
            pass
        if not acts:
            acts = [re.sub("_", " ", band) for band in bands]
        return soup, name, acts
    # If it's a band then find relevant members (can use names list created in get_html_docs.py)
    else:
        members = [re.sub("_", " ", member) for member in members]
        return soup, name, members


def train_ner(ner, filename, trainer, band = False, members = None):
    '''
    Given a filename, this function is responsible for adding entities found in the text. It uses the pre-existing ner model to flag all
    entities and then searches for ones that correspond to either the band/person of interest or the members/acts associated with them.
    Specifically, it adds a 'person' entity for the person of interest and 'band' entities for associated acts (if it's a person), and
    adds a 'band' entity for the band of interest and 'person' entities for members (if it's a band).
    :param ner: the pre-existing ner model
    :type ner: a mitie object
    :param filename: the file from which to train on
    :type filename: string
    :param trainer: the object that trains the model
    :type trainer: a mitie object
    :param band: whether it's a band or not
    :type band: boolean
    :param members: if it's a band, then this is the list of members
    :type members: None or list
    :return: does not return anything
    '''
    soup, name, search_terms = get_terms(filename, band, members)
    name_together = re.sub("_", " ", name)
    name = name_together.split()
    name.append(name_together)
    search_terms_together = search_terms
    search_terms = [terms.split() for terms in search_terms]
    for i in range(len(search_terms)):
        search_terms[i].append(search_terms_together[i])
    text_list = []
    for text in soup.find(class_="mw-parser-output").find_all("p"):
        text_list.append(text.text)
    tokens = tokenize(' '.join(text_list))
    train_doc = ner_training_instance(tokens)
    entities = ner.extract_entities(tokens)
    locs = [entity[0] for entity in entities]
    text_terms = [[tokens[i].decode() for i in entity[0]] for entity in entities]
    text_terms_together = [' '.join(term) for term in text_terms]
    # Add entity for person/band of interest, making sure to catch all instances of even just part of the name
    for part in name:
        for i in range(len(text_terms_together)):
            if part == text_terms_together[i]:
                # Skip overlapping entities so errors are not thrown
                try:
                    if band == False:
                        train_doc.add_entity(locs[i], "person")
                    else:
                        train_doc.add_entity(locs[i], "band")
                except:
                    pass
    # Add entity for associated bands/members
    for terms in search_terms:
        for term in terms:
            for i in range(len(text_terms_together)):
                if term == text_terms_together[i]:
                    # Skip overlapping entities so errors are not thrown
                    try:
                        if band == False:
                            train_doc.add_entity(locs[i], "band")
                            print "added band for ", text_terms_together[i]
                        else:
                            train_doc.add_entity(locs[i], "person")
                            print "added person for ", text_terms_together[i]
                    except:
                        pass
    trainer.add(train_doc)

def train_relationship_model(new_ner, rel_trainer, filename):
    '''
    Given a filename, this function is responsible for adding positive and negative binary relations. Since it takes the custom ner model
    as an input, this training is relatively straightforward: we know that all tagged entities are bands and people that have the desired 
    relationship, so we only filter for tuples of (band, person) or (person, band), and take all those relations as positive. Those that 
    are filtered out are taken as negative.
    :param new_ner: the custom ner model
    :type new_ner: a mitie object
    :param re_trainer: the object that trains the model
    :type rel_trainer: a mitie object
    :param filename: the file from which to train on
    :type filename: string
    :return: does not return anything
    '''
    html = open(filename, 'r')
    soup = BeautifulSoup(html, 'html.parser')
    html.close()
    text_list = []
    for text in soup.find(class_="mw-parser-output").find_all("p"):
        text_list.append(text.text)
    tokens = tokenize(' '.join(text_list))
    entities = new_ner.extract_entities(tokens)
    # Create tuples of adjacent entities
    adjacent_locs = [(entities[i][0], entities[i + 1][0]) for i in xrange(len(entities) - 1)]
    adjacent_entities = [(entities[i][1], entities[i + 1][1]) for i in xrange(len(entities) - 1)]
    pos_entities = []
    neg_entities = []
    # Check to see whether the tuples consist of the desired format and assign as positive or negative relation based on this
    for i in range(len(adjacent_entities)):
        if (adjacent_entities[i][0] == "person" and adjacent_entities[i][1] == "band") or (adjacent_entities[i][0] == "band" and adjacent_entities[i][1] == "person"):
            pos_entities.append(adjacent_locs[i])
        else:
            neg_entities.append(adjacent_locs[i])
    # Make sure to consider relations of the opposite direction as this will strengthen our model
    pos_entities += [(r, l) for (l, r) in pos_entities]
    neg_entities += [(r, l) for (l, r) in neg_entities]
    for a, b in pos_entities:
        rel_trainer.add_positive_binary_relation(tokens, a, b)
    for a, b in neg_entities:
        rel_trainer.add_negative_binary_relation(tokens, a, b)

# Runs train_ner()
band_list = []
person_list = []
for i in range(len(urls)):
    band, names = get_html_docs.crawl(urls[i], '/Users/Mikaela/Desktop/test/')
    band_list.append(band)
    person_list.append(names)
for i in range(len(band_list)):
    band = band_list[i]
    is_band = True
    members = person_list[i]
    train_ner(ner, '.'.join([band, 'html']), trainer, is_band, members)
for i in range(len(person_list)):
    for person in person_list[i]:
        train_ner(ner, '.'.join([person, 'html']), trainer)
trainer.num_threads = 4
new_ner = trainer.train()
new_ner.save_to_disk("new_ner.dat")


def filelist(root):
    '''
    Given a directory, this function returns a list of files found within the directory.
    :param root: the directory where the html documents are stored
    :type root: string
    :return: the list of searchable html documents
    :rtype: list
    '''
    files = []
    for root, directories, filenames in os.walk(root):
        for filename in filenames:
            # Make sure to avoid weird system files that start with '.'
            if not filename.startswith('.'):
                files.append(os.path.join(root, filename))
    return files

# Runs train_relationship_model()
files = filelist('/Users/Mikaela/Desktop/test')
new_ner = named_entity_extractor('new_ner.dat')
rel_trainer = binary_relation_detector_trainer('people.person.band', new_ner)
for file in files:
    train_relationship_model(new_ner, rel_trainer, file)
rel_trainer.num_threads = 4
rel_detector = rel_trainer.train()
rel_detector.save_to_disk("rel_band_classifier.svm")
