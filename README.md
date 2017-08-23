# information_extraction
This is an information extraction system that finds relationships between musical bands, the music produced by those bands, and the people who make up the musical bands. This was an assignment completed for an NLP class that was part of the MSAN program. My version of this assignment received the highest grade in the class.

The program requires three parameters:

(1) pathname to mitielib
Example: /Users/Mikaela/mitie/MITIE/mitielib

(2) pathname to ner_model.dat
Example: /Users/Mikaela/mitie/MITIE/MITIE-models/english/ner_model.dat

(3) pathname to directory you wish to store HTML documents
Example: /Users/Mikaela/Desktop/test

You would run the program from the command line by entering:
python a2.py /Users/Mikaela/mitie/MITIE/mitielib /Users/Mikaela/mitie/MITIE/MITIE-models/english/ner_model.dat /Users/Mikaela/Desktop/test

Some notes:

- Upon starting the program, it will automatically go and grab the HTML from Wikipedia for each of the ten bands and their
members and write files to the directory specified in (3).

- When entering search terms, capitalization is important.
Example: Entering "band Run the Jewels" is correct and will match the document, while entering "band Run The Jewels" is
incorrect and will not match the document.

- The program uses the pre-existing NER model and a custom relationship model called rel_band_classifier.svm. This file
is included and should be stored in the same directory where you run the code. The training for this model was done
beforehand and is not a part of the program. I do, however, include a file called train_models.py, which includes code
that trained the model. I include this file simply to give you an idea of how I trained the relationship model.

- My program assumes the equivalence of bands and people in the context of associated acts.
Example: If the search term is person, say John Lennon, then I want to find all "bands" associated with John Lennon. This
might return The Beatles (as expected), but it might also return Elton John since they collaborated on stuff. This fits the
requirement for being "in" Elton John, even though Elton John is a person. Since this assignment does not directly address
the issue of "bands" titled by a person's name, I chose to interpret it in this way.
