'''
Last edited: June 26, 2017
@author mhoffmanstapleton@usfca.edu
'''

class extract_info:
    '''
    This class is responsible for flagging entities and extracting relationships between them. We designate different functions to handle 
    the extraction process based on known information in order to optimize search results. This class contains nine functions: __init__(), 
    which initializes attributes, populate_entities(), which uses the ner model to flag entities, filter_entities_by_score(), which uses the
    relationship model to score the relationships and filters them according to score, filter_entities_by_search(), which filters the 
    relationships by search term and entity format, band_in_or_outside_training_with_members(), which matches entities in selected 
    relationships to known members, person_in_or_outside_training_with_acts(), which is analogous to the previous function but for people,
    person_in_training_without_acts(), which matches entities in selected relationships to the original list of ten bands, band_outside_
    training_without_members(), which removes duplicate members and prints results, and person_outside_training_without_acts(), which is 
    analogous to the previous function but for people.
    '''

    def __init__(self, name, mitie_dir, mitie_ner, soup, is_band, members, acts):
        '''
        Constructor
        '''
        self.name = name
        self.mitie_dir = mitie_dir
        self.mitie_ner = mitie_ner
        self.soup = soup
        self.is_band = is_band
        self.members = members
        self.acts = acts
        self.ner = None
        self.tokens = None
        self.entities = None
        self.adjacent_entities = []
        self.a_list = []
        self.b_list = []


    def populate_entities(self):
        '''
          This function populates self.ner, self.tokens, self.entities, and self.adjacent_entities. It first takes all text within <p> tags
          and breaks it into tokens. It then uses the pre-existing ner model in mitie to flag entities as person, organization, location, 
          or misc. It then creates tuples of adjacent entities and makes sure to append switched around tuples to account for relationships
          going the opposite way.
          :param: no parameters
          :return: does not return anything
        '''
        import sys
        sys.path.append(self.mitie_dir)
        from mitie import named_entity_extractor, tokenize
        # Use the pre-existing ner model
        self.ner = named_entity_extractor(self.mitie_ner)
        # Only grab text within <p> tags to avoid javascript and text not contained within a sentence
        text_list = []
        for text in self.soup.find_all("p"):
           text_list.append(text.text)
        # Tokenize the text, flag entities, and create tuples of adjacent entities
        self.tokens = tokenize(' '.join(text_list))
        # self.tokens = tokenize(self.soup.text)
        self.entities = self.ner.extract_entities(self.tokens)
        self.adjacent_entities = [(self.entities[i][0], self.entities[i + 1][0]) for i in xrange(len(self.entities) - 1)]
        self.adjacent_entities += [(r, l) for (l, r) in self.adjacent_entities]


    def filter_entities_by_score(self):
        '''
          This function extracts relationships between adjacent entities and assigns scores to those relationships. It uses a custom
          relationship model, called rel_band_classifier.svm, to score the relationships. Relationships with negative scores are filtered
          out and those with positive scores are kept. These are appended to lists, which are used in the functions below to figure out
          whether we can match the kept entities to known aliases.
          :param: no parameters
          :return: does not return anything
        '''
        import sys
        sys.path.append(self.mitie_dir)
        from mitie import binary_relation_detector
        # Use a custom relationship model
        rel_detector = binary_relation_detector("rel_band_classifier.svm")
        # Extract relationships between adjacent entities and assign scores to each relationship
        for a, b in self.adjacent_entities:
            a_name = ' '.join(self.tokens[i].decode('ascii', 'ignore') for i in a)
            b_name = ' '.join(self.tokens[i].decode('ascii', 'ignore') for i in b)
            relation = self.ner.extract_binary_relation(self.tokens, a, b)
            score = rel_detector(relation)
            # Only keep those relationships which have a positive score
            if score > 0:
                self.a_list.append(a_name)
                self.b_list.append(b_name)


    def filter_entities_by_search(self):
        '''
          This function is analogous to the one above, but uses an entirely different process to choose which relationships to keep. This 
          function is only used when it is searching unseen data, and there are no members or acts to match entities to. It splits the name 
          of the entity of interest into different parts (words) and searches the flagged entities to see whether these parts appear. Any 
          matches are checked to make sure that the opposite entity is flagged as the appropriate thing (either person or organization). 
          Assuming the relationship fits this criteria, the entities are appended to lists similar to before.
          :param: no parameters
          :return: does not return anything
        '''
        import re
        # Set the classification term to what is desired depending on whether the entity of interest is a band or person
        if self.is_band == True:
            classification = "PERSON"
        else:
            classification = "ORGANIZATION"
        name_parts = self.name.split()
        for a, b in self.adjacent_entities:
            a_name = ' '.join(self.tokens[i].decode('ascii', 'ignore') for i in a)
            b_name = ' '.join(self.tokens[i].decode('ascii', 'ignore') for i in b)
            # Check to see whether part of the name is in either of the entities
            for part in name_parts:
                if re.search(part, a_name) and not re.search(part, b_name):
                    # If a match is found, use the location of the match to figure out what the entity was classified as
                    for entity in self.entities:
                        if entity[0] == b:
                            # Only keep the relationship if it is classified as what is desired
                            if entity[1] == classification:
                                self.a_list.append(a_name)
                                self.b_list.append(b_name)
                elif re.search(part, b_name) and not re.search(part, a_name):
                    # If a match is found, use the location of the match to figure out what the entity was classified as
                    for entity in self.entities:
                        if entity[0] == a:
                            # Only keep the relationship if it is classified as what is desired
                            if entity[1] == classification:
                                self.a_list.append(a_name)
                                self.b_list.append(b_name)


    def band_in_or_outside_training_with_members(self):
        '''
          This function is called when we have a set of members to match our selected entities to. It assumes that each relationship, which
          has already been filtered by score, is comprised of the entity of interest along with one of the members or acts found in the 
          info box. Naturally, we use levenshtein distance to match the entity to its appropriate full-length alias. This function is also
          responsible for printing the results.
          :param: no parameters
          :return: does not return anything
        '''
        # This catches Lupe Fiasco, which has no members
        if self.members:
            from linguistic_distance import linguistic_distance
            linguistic_distance = linguistic_distance()
            matched_members = []
            # Cycle through each relationship that passed our standards for scoring
            for i in range(len(self.a_list)):
                # Figure out which entity corresponds to the entity of interest by calculating levenshtein distances
                a_distance = linguistic_distance.levenshtein(self.a_list[i], self.name)
                b_distance = linguistic_distance.levenshtein(self.b_list[i], self.name)
                distance = []
                # Cycle through each member to match the non entity of interest with its appropriate member
                for member in self.members:
                    if a_distance < b_distance:
                        # Special case, otherwise the minimized levenshtein distance will point to something else
                        if self.b_list[i] == 'Marley':
                            self.b_list[i] = 'Bob Marley & The Wailers'
                        distance.append(linguistic_distance.levenshtein(self.b_list[i], member))
                    else:
                        # Special case, otherwise the minimized levenshtein distance will point to something else
                        if self.a_list[i] == 'Marley':
                            self.a_list[i] = 'Bob Marley & The Wailers'
                        distance.append(linguistic_distance.levenshtein(self.a_list[i], member))
                    match_index = distance.index(min(distance))
                    matched_members.append(self.members[match_index])
            # Print the results and make sure not to print duplicates
            already_printed = []
            for i in range(len(self.a_list)):
                if matched_members[i] not in already_printed:
                    print matched_members[i], "was in", self.name
                    already_printed.append(matched_members[i])
            if not already_printed:
                print "None found."
        else:
            print "None found."


    def person_in_or_outside_training_with_acts(self):
        '''
          This function is analogous to the function above and treats everything in similar ways. See that description for more detail. We
          chose to keep separate functions since it was conceptually easier to keep band and person separate from each other and because we
          have different lists for members and acts. There are also enough small coding differences to support this choice.
          :param: no parameters
          :return: does not return anything
        '''
        from linguistic_distance import linguistic_distance
        linguistic_distance = linguistic_distance()
        matched_acts = []
        # Cycle through each relationship that passed our standards for scoring
        for i in range(len(self.a_list)):
            # Figure out which entity corresponds to the entity of interest by calculating levenshtein distances
            a_distance = linguistic_distance.levenshtein(self.a_list[i], self.name)
            b_distance = linguistic_distance.levenshtein(self.b_list[i], self.name)
            distance = []
            # Cycle through each act to match the non entity of interest with its appropriate act
            for act in self.acts:
                if a_distance < b_distance:
                    # Special case, otherwise minimized levenshtein distance will point to something else
                    if self.b_list[i] == 'Marley':
                        self.b_list[i] = 'Bob Marley & The Wailers'
                    distance.append(linguistic_distance.levenshtein(self.b_list[i], act))
                else:
                    # Special case, otherwise minimized levenshtein distance will point to something else
                    if self.a_list[i] == 'Marley':
                        self.a_list[i] = 'Bob Marley & The Wailers'
                    distance.append(linguistic_distance.levenshtein(self.a_list[i], act))
            match_index = distance.index(min(distance))
            matched_acts.append(self.acts[match_index])
        # Print the results and make sure not to print duplicates
        already_printed = []
        for i in range(len(self.a_list)):
            if matched_acts[i] not in already_printed:
                print self.name, "was associated with", matched_acts[i]
                already_printed.append(matched_acts[i])
        if not already_printed:
            print "None found."


    def person_in_training_without_acts(self):
        '''
        This function is called under special circumstances when the entity of interest is a person within the training, but does not have
        any associated acts. We use what we do know about the person, which is the knowledge that they were in one of the ten original bands,
        to match the entities, which have already been filtered by score, to one of these bands. This makes sense since the fact that they
        don't have an associated acts section means they probably weren't in multiple bands anyway. 
        :param: no parameters
        :return: does not return anything
        '''
        import re
        from linguistic_distance import linguistic_distance
        linguistic_distance = linguistic_distance()
        matched_acts = []
        # Cycle through each relationship that passed our standards for scoring
        for i in range(len(self.a_list)):
            # Figure out which entity corresponds to the entity of interest by calculating levenshtein distances
            a_distance = linguistic_distance.levenshtein(self.a_list[i], self.name)
            b_distance = linguistic_distance.levenshtein(self.b_list[i], self.name)
            # Cycle through each act to match the non entity of interest with its appropriate act
            # The difference here is that the list of acts was not scraped from their page, but is instead just the list of ten original bands
            for act in self.acts:
                if a_distance < b_distance:
                    if re.search(self.b_list[i], act):
                        matched_acts.append(act)
                else:
                    if re.search(self.a_list[i], act):
                        matched_acts.append(act)
        matched_acts = list(set(matched_acts))
        # Print the results and make sure not to print duplicates
        already_printed = []
        for i in range(len(matched_acts)):
            if matched_acts[i] not in already_printed:
                print self.name, "was associated with", matched_acts[i]
                already_printed.append(matched_acts[i])
        if not already_printed:
            print "None found."


    def band_outside_training_without_members(self):
        '''
        This function is called when we do NOT have a set of members to match our selected entities to. In this case, we can only use 
        levenshtein distance to figure out which of the entities corresponds to the entity of interest. We cannot, however, use this method
        to match the other entity, so we simply leave it as is and hope that the filtering algorithm did an ok job. This function removes
        duplicates and prints the results.
          :param: no parameters
          :return: does not return anything
        '''
        from linguistic_distance import linguistic_distance
        linguistic_distance = linguistic_distance()
        members = []
        # Cycle through each relationship that passed our standards (in this case, we used the search algorithm)
        for i in range(len(self.a_list)):
            # Figure out which entity corresponds to the entity of interest by calculating levenshtein distances
            a_distance = linguistic_distance.levenshtein(self.a_list[i], self.name)
            b_distance = linguistic_distance.levenshtein(self.b_list[i], self.name)
            if a_distance < b_distance:
                members.append(self.b_list[i])
            else:
                members.append(self.a_list[i])
        # Remove duplicates; there may be multiple aliases for the same thing, but this won't catch that since we have nothing to compare it to
        members = list(set(members))
        # Print the results
        for i in range(len(members)):
            print members[i], "was in", self.name
        if not members:
            print "None found."


    def person_outside_training_without_acts(self):
        '''
          This function is analogous to the function above and treats everything in similar ways. See that description for more detail. We
          chose to keep separate functions since it was conceptually easier to keep band and person separate from each other and because we
          have different lists for members and acts. There are also enough small coding differences to support this choice.
          :param: no parameters
          :return: does not return anything
        '''
        from linguistic_distance import linguistic_distance
        linguistic_distance = linguistic_distance()
        acts = []
        # Cycle through each relationship that passed our standards (in this case, we used the search algorithm)
        for i in range(len(self.a_list)):
            # Figure out which entity corresponds to the entity of interest by calculating levenshtein distances
            a_distance = linguistic_distance.levenshtein(self.a_list[i], self.name)
            b_distance = linguistic_distance.levenshtein(self.b_list[i], self.name)
            if a_distance < b_distance:
                acts.append(self.b_list[i])
            else:
                acts.append(self.a_list[i])
        # Remove duplicates; there may be multiple aliases for the same thing, but this won't catch that since we have nothing to compare it to
        acts = list(set(acts))
        # Print the results
        for i in range(len(acts)):
            print self.name, "was associated with", acts[i]
        if not acts:
            print "None found."
