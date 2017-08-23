'''
Last edited: June 26, 2017
@author mhoffmanstapleton@usfca.edu
'''

class user_interface:
    '''
    This class is responsible for prompting the user for search terms and handling any errors that may arise from user input. It contains 
    five functions: __init__(), which initializes attributes, manager(), which figures out attributes of the search term and calls the 
    appropriate function in extract_info.py, filelist(), which returns the list of searchable html documents, find_doc() which matches the
    search term with the corresponding html document, and prompt(), which prompts the user and handles all the different cases.
    '''

    def __init__(self, mitie_dir, mitie_ner, file_dir, training_bands, training_people):
        '''
        Constructor
        '''
        self.mitie_dir = mitie_dir
        self.mitie_ner = mitie_ner
        self.file_dir = file_dir
        self.training_bands = training_bands
        self.training_people = training_people
        self.quit = False
        self.is_band = False
        self.in_training = False
        self.has_members_or_acts = False
        self.members = None
        self.acts = None


    def manager(self, file, name, command):
        '''
        Given the file, name of the entity, and command the user entered, this function figures out whether the search term is a band or
        person, was in the training or outside of it, and whether it has a members or associated acts section in the info box. If the
        entity has members or associated acts, it grabs those names. Depending on this set of attributes, it calls the appropriate function
        in extract_info.py. This is necessary in order for the program to adequately filter extracted relationships and match them based on
        known results when possible.
        :param file: the pathname to the file of interest
        :type file: string
        :param name: the name of the entity of interest
        :type name: string
        :param command: the first word of input, which is either 'person' or 'band'
        "type command: string
        :return: does not return anything
        '''
        from scrape_page import scrape_page
        from extract_info import extract_info
        scrape_page = scrape_page(file)
        scrape_page.populate_soup()
        soup = scrape_page.get_soup()
        # Figure out three attributes: person or band, in training or outside of it, and whether there is a members or associated acts section
        if command == 'band':
            self.is_band = True
            scrape_page.populate_members()
            if name in self.training_bands:
                self.in_training = True
                # Populate a list of members if that section exists in the info box
                self.members = scrape_page.get_members()
                if self.members:
                    self.has_members_or_acts = True
            else:
                self.members = scrape_page.get_members()
                if self.members:
                    self.has_members_or_acts = True
        else:
            scrape_page.populate_acts()
            if name in self.training_people:
                self.in_training = True
                # Populate a list of associated acts if that section exists in the info box
                self.acts = scrape_page.get_acts()
                if self.acts:
                    self.has_members_or_acts = True
            else:
                self.acts = scrape_page.get_acts()
                if self.acts:
                    self.has_members_or_acts = True
        # Special case, populate associated acts with known list of potential bands if the search term was a person in training without acts
        if self.is_band == False and self.in_training == True and self.has_members_or_acts == False:
            self.acts = self.training_bands
        # Make an instance for extract_info.py and use the ner model to flag entities
        extract_info = extract_info(name, self.mitie_dir, self.mitie_ner, soup, self.is_band, self.members, self.acts)
        extract_info.populate_entities()
        # Depending on the search term attributes, call different functions in extract_info.py. These filter the extracted relationships
        # differently, using known information to get better results when possible
        if (self.is_band == True and self.has_members_or_acts == True) or (self.is_band == True and self.in_training == True and self.has_members_or_acts == False):
            extract_info.filter_entities_by_score()
            extract_info.band_in_or_outside_training_with_members()
        elif (self.is_band == False and self.has_members_or_acts == True) or (self.is_band == False and self.has_members_or_acts == True):
            extract_info.filter_entities_by_score()
            extract_info.person_in_or_outside_training_with_acts()
        elif (self.is_band == False and self.in_training == True and self.has_members_or_acts == False):
            extract_info.filter_entities_by_score()
            extract_info.person_in_training_without_acts()
        elif (self.is_band == True and self.in_training == False and self.has_members_or_acts == False):
            extract_info.filter_entities_by_search()
            extract_info.band_outside_training_without_members()
        else:
            extract_info.filter_entities_by_search()
            extract_info.person_outside_training_without_acts()


    def filelist(self, root):
        '''
        Given a directory, this function returns a list of files found within the directory.
        :param root: the directory where the html documents are stored
        :type root: string
        :return: the list of searchable html documents
        :rtype: list
        '''
        import os
        files = []
        for root, directories, filenames in os.walk(root):
            for filename in filenames:
                # Make sure to avoid weird system files that start with '.'
                if not filename.startswith('.'):
                    files.append(os.path.join(root, filename))
        return files


    def find_doc(self, input, command):
        '''
        Given the user input and command associated with that input, this function matches the search term with the corresponding html
        document from the directory of searchable files. If there is no match, it handles this gracefully and asks the user to try again.
        If there is a match, then it calls manager() and goes on to the next step.
        :param input: the entire user input, including the command (below) and entity of interest
        :type input: string
        :param command: the first word of input, which is either 'person' or 'band'
        :type command: string
        :return: does not return anything
        '''
        import re
        import string
        remove = string.punctuation
        remove = remove.replace("_", "")
        pattern = r"[{}]".format(remove)
        # Handles search terms with multiple words
        if len(input) > 2:
            name = '_'.join(input[1:len(input)])
        else:
            name = input[1]
        file = "/".join([self.file_dir, '.'.join([re.sub(pattern, "", name), 'html'])])
        files = self.filelist(self.file_dir)
        # If the file exists, move on to the next step
        if file in files:
            self.manager(file, re.sub("_", " ", re.sub(pattern, "", name)), command)
        else:
            print "Error: HTML document not found. Either the search term was misspelled or it is not in the set of HTML documents. Please try again."


    def prompt(self):
        '''
        This function prompts the user and handles all the different cases, including any errors that arise. If the user quits, it exits the
        program gracefully. Otherwise, it continuously prompts the user after any search term printing results.
        :param no parameters
        :return: does not return anything
        '''
        print "Please enter either 'person', 'band', or 'quit'. If choosing 'person' or 'band', then on the same line enter a space followed by the name of the entity you wish to find. Note that capitalization is important."
        while self.quit == False:
            # Need to reset these with every new search term since we do not actually create a new instance
            self.is_band = False
            self.in_training = False
            self.has_members_or_acts = False
            self.members = None
            self.acts = None
            input = raw_input('Find: ').split()
            try:
                command = input[0]
            except:
                print "You have not entered anything."
            # If they quit, exit gracefully
            if command == 'quit':
                self.quit = True
                print 'You have successfully quit.'
            # Otherwise, search for the entity in the list of searchable documents
            elif (command == 'person' or command == 'band') and len(input) > 1:
                self.find_doc(input, command)
            else:
                print 'An error has occurred. Please check that you have entered input that is correctly formatted.'
