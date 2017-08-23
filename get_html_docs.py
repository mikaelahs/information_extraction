'''
Last edited: June 26, 2017
@author mhoffmanstapleton@usfca.edu
'''

class get_html_docs:
    '''
    This class is responsible for grabbing each band Wikipedia page and the corresponding members' pages. It contains five functions: 
    __init__(), which initializes attributes, fetch(), which actually gets the html and creates a Beautiful Soup object, get_links(),
    which finds urls for members in the band if they exist, crawl(), which manages the previous two functions and writes the html
    documents to a directory of the user's choosing, and get_names() which returns the list of members associated with the band.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.html = None
        self.soup = None
        self.band = None
        self.is_maniacs_or_bob = False
        self.is_lupe = False
        self.links = []
        self.names = []


    def fetch(self, url):
        '''
        Given a url, this function populates self.html and self.soup with the html and corresponding Beautiful Soup object, respectively.
        :param url: the url corresponding to the band or person of interest
        :type url: string
        :return: does not return anything
        '''
        import urllib2
        from bs4 import BeautifulSoup
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        self.html = response.read()
        self.soup = BeautifulSoup(self.html, 'html.parser')


    def get_links(self, url):
        '''
        Given a url, this function populates self.band, self.is_maniacs_or_bob, self.is_lupe, self.links and self.names. It checks the band
        name to see if it's 10,000 Maniacs, Bob Marley and the Wailers, or Lupe Fiasco. These three are special cases as described below.
        Depending on the band, it will scrape different sections of the page to find members and their corresponding links if they exist.
        It also grabs the names of the members with links so we can keep track of people we use in training.
        :param url: the url corresponding to the band or person of interest
        :type url: string
        :return: does not return anything
        '''
        import re
        import string
        remove = string.punctuation
        remove = remove.replace("_", "")
        pattern = r"[{}]".format(remove)
        self.band = re.sub(pattern, "", re.sub("(https://en.wikipedia.org/wiki/)|(_\(.*\))", "", url))
        # Special case, we scrape a different section in order to get touring members not listed in the info box
        if re.search("Maniacs", self.band) or re.search("Bob", self.band):
            self.is_maniacs_or_bob = True
        # Special case, we skip it altogether since there are no members
        elif re.compile("Lupe").search(self.band):
            self.is_lupe = True
        # Scrape the members and past members sections in the info box for links if they exist
        if self.is_lupe == False and self.is_maniacs_or_bob == False:
            i = 0
            for section in self.soup.find(class_="infobox vcard plainlist").find_all("tr"):
                if re.search("Members", section.text):
                    links = self.soup.find(class_="infobox vcard plainlist").find_all("tr")[i]
                    for link in links.find_all("a"):
                        self.links.append(re.sub("/wiki/", "https://en.wikipedia.org/wiki/", link["href"]))
                        self.names.append(re.sub(pattern, "", re.sub("(/wiki/)|(_\(.*\))", "", link["href"])))
                if re.search("Past members", section.text):
                    links = self.soup.find(class_="infobox vcard plainlist").find_all("tr")[i]
                    for link in links.find_all("a"):
                        # Catch an error since one of the so-called urls actually leads to nothing
                        if re.search("index", link['href']):
                            continue
                        self.links.append(re.sub("/wiki/", "https://en.wikipedia.org/wiki/", link["href"]))
                        self.names.append(re.sub(pattern, "", re.sub("(/wiki/)|(_\(.*\))", "", link["href"])))
                else:
                    i = i + 1
        # Otherwise scrape the members section at the bottom of the page for links if they exist
        elif self.is_lupe == False and self.is_maniacs_or_bob == True:
            for link in self.soup.find(class_="multicol").find_all("li"):
                try:
                    address = link.find("a")["href"]
                    self.links.append(re.sub("/wiki/", "https://en.wikipedia.org/wiki/", address))
                    self.names.append(re.sub("[0-9]|(_The_Wailers)", "", re.sub(pattern, "", re.sub("/wiki/", "", address))))
                except:
                    pass


    def crawl(self, url, outputdir):
        '''
        Given a url and directory, this function calls fetch() and get_links(), and then writes the html to a file in the appropriate directory.
        It then calls fetch() for every member link found, and writes the html to a file in the same directory.
        :param url: the url corresponding to the band or person of interest
        :type url: string
        :param outputdir: the path to the directory where the html documents will be stored
        :type outputdir: string
        :return: does not return anything
        '''
        self.fetch(url)
        self.get_links(url)
        # Write the html file for the band
        file = open("/".join([outputdir, "".join([self.band, ".html"])]), 'w')
        file.write(self.html)
        file.close()
        # Write the html files for all members with links to their own page
        for i in range(len(self.links)):
            self.fetch(self.links[i])
            file = open("/".join([outputdir, "".join([self.names[i], ".html"])]), 'w')
            file.write(self.html)
            file.close()


    def get_names(self):
        '''
        This function returns the names of band members that had links to their own Wikipedia page.
        :param: no parameters
        :return: the list of members that had links
        :rtype: list
        '''
        return self.names
