'''
Last edited: June 26, 2017
@author mhoffmanstapleton@usfca.edu
'''

# This is the file that runs everything

urls = ['https://en.wikipedia.org/wiki/10,000_Maniacs', 'https://en.wikipedia.org/wiki/Belly_(band)', 'https://en.wikipedia.org/wiki/Black_Star_(rap_duo)',
            'https://en.wikipedia.org/wiki/Bob_Marley_and_the_Wailers', 'https://en.wikipedia.org/wiki/The_Breeders', 'https://en.wikipedia.org/wiki/Lupe_Fiasco',
            'https://en.wikipedia.org/wiki/Run_the_Jewels', 'https://en.wikipedia.org/wiki/Talking_Heads', 'https://en.wikipedia.org/wiki/Throwing_Muses',
            'https://en.wikipedia.org/wiki/Tom_Tom_Club']

if __name__ == '__main__':
    import sys
    import re
    import string
    from get_html_docs import get_html_docs
    from user_interface import user_interface

    args = sys.argv
    if len(args) != 4:
        print "Error: incorrect number of parameters. The first parameter is the pathname for mitielib. The second parameter is the pathname for ner_model.dat. The third parameter is the pathname for where the HTML documents are stored."

    remove = string.punctuation
    remove = remove.replace("_", "")
    pattern = r"[{}]".format(remove)
    training_bands = []
    training_people = []
    # Grab the html documents and make a list of training bands and members
    for url in urls:
        doc = get_html_docs()
        doc.crawl(url, args[3])
        names = [re.sub("_", " ", name) for name in doc.get_names()]
        for name in names:
            training_people.append(name)
        training_bands.append(re.sub("_", " ", re.sub(pattern, "", re.sub("(https://en.wikipedia.org/wiki/)|(_\(.*\))", "", url))))

    # This keeps looping until the user quits
    user_interface = user_interface(args[1], args[2], args[3], training_bands, training_people)
    user_interface.prompt()
