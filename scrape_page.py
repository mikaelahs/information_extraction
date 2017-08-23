'''
Last edited: June 26, 2017
@author mhoffmanstapleton@usfca.edu
'''

class scrape_page():
    '''
    This class is responsible for scraping an html document to find the names of band members or associated acts. It contains seven functions: 
    __init__(), which initializes attributes, populate_soup(), which creates a Beautiful Soup object, populate_members(), which grabs the 
    names of members from the info box, populate_acts(), which grabs the names of associated acts from the info box, and three functions to 
    return each of these. This class was necessary in addition to get_html_documents.py because the way we go about scraping in this file 
    is different from before. We are no longer looking for links, but looking for the actual text that corresponds to members (more names 
    will be grabbed since we are not limiting to only those that have links) and associated acts (this was not scraped at all before).
    '''

    def __init__(self, file):
        '''
        Constructor
        '''
        self.file = file
        self.soup = None
        self.members = []
        self.acts = []


    def populate_soup(self):
        '''
        This function reads the html and creates a Beautiful Soup object, which is stored in self.soup.
        :param: no parameters
        :return: does not return anything
        '''
        from bs4 import BeautifulSoup
        f = open(self.file, 'r')
        html = f.read()
        f.close()
        self.soup = BeautifulSoup(html, 'html.parser')


    def populate_members(self):
        '''
        This function searches for a members section in the info box and, if found, parses the text to create a list of members, which is
        stored in self.members. This is repeated for a past members section and appends any results to self.members.
        :param: no parameters
        :return: does not return anything
        '''
        import re
        i = 0
        # Catch any errors since there might not be an info box
        try:
            for section in self.soup.find(class_="infobox vcard plainlist").find_all("tr"):
                # Search for a members section
                if re.search("Members", section.text):
                    matches = self.soup.find(class_="infobox vcard plainlist").find_all("tr")[i].text.split('\n')
                    for match in matches:
                        if match != '' and match != 'Members':
                            self.members.append(re.sub("(\(.*\))", "", match))
                # Repeat search, but this time look for a past members section
                if re.search("Past members", section.text):
                    matches = self.soup.find(class_="infobox vcard plainlist").find_all("tr")[i].text.split('\n')
                    for match in matches:
                        if match != '' and match != 'Past members':
                            self.members.append(re.sub("(\(.*\))", "", match))
                else:
                    i = i + 1
        except:
            pass


    def populate_acts(self):
        '''
          This function searches for an associated acts section in the info box and, if found, parses the text to create a list of acts, 
          which is stored in self.acts. 
          :param: no parameters
          :return: does not return anything
        '''
        import re
        # Special case, this info box has an associated acts section that separates acts by just a space
        if re.search("Aston_Barrett", self.file):
            matches = self.soup.find(class_="infobox vcard plainlist").find_all("tr")[10].find_all("a")
            for match in matches:
                self.acts.append(re.sub("\s(\(.*\))", "", match['title']))
        # This is for all other cases since the acts are separated by either a newline character or comma
        else:
            i = 0
            # Catch any errors since there might not be an info box
            try:
                # First check to see if there's an info box labelled by 'infobox vcard plainlist'
                for section in self.soup.find(class_="infobox vcard plainlist").find_all("tr"):
                    if re.search("Associated acts", section.text):
                        matches = self.soup.find(class_="infobox vcard plainlist").find_all("tr")[i].text
                        if re.search(", ", matches):
                            matches = re.sub("(Associated acts)|(\n)|( Has also toured.*)", "", matches).split(", ")
                        else:
                            matches = matches.split("\n")
                        for match in matches:
                            if match != '' and match != 'Associated acts':
                                self.acts.append(match)
                    else:
                        i = i + 1
            except:
                pass
            try:
                # Otherwise check to see if there's an info box labelled by 'infobox biography vcard'
                for section in self.soup.find(class_="infobox biography vcard").find_all("tr"):
                    if re.search("Associated acts", section.text):
                        matches = self.soup.find(class_="infobox biography vcard").find_all("tr")[i].text
                        if re.search(",", matches):
                            matches = re.sub("(Associated acts)|(\n)|( Has also toured.*)", "", matches).split(", ")
                        else:
                            matches = matches.split("\n")
                        for match in matches:
                            if match != '' and match != 'Associated acts':
                                self.acts.append(match)
                    else:
                        i = i + 1
            except:
                pass


    def get_soup(self):
        '''
          This function returns the Beautiful Soup object, which is returned in order to pass it as a parameter in extract_info.py.
          :param: no parameters
          :return: the Beautiful Soup object created from the html document
          :rtype: Beautiful Soup object
        '''
        return self.soup


    def get_members(self):
        '''
          This function returns the list of members. If it is not empty, i.e. the list was successfully scraped, then this list is used in
          extract_info.py to match extracted relationships to known ones.
          :param: no parameters
          :return: the list of members scraped from the info box section
          :rtype: list
        '''
        return self.members


    def get_acts(self):
        '''
          This function returns the list of associated acts. If it is not empty, i.e. the list was successfully scraped, then this list 
          is used in extract_info.py to match extracted relationships to known ones.
          :param: no parameters
          :return: the list of associated acts scraped from the info box section
          :rtype: list
        '''
        return self.acts
