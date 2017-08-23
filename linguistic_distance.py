'''
Last edited: May 25, 2017
@author mhoffmanstapleton@usfca.edu
'''

class linguistic_distance:
    '''
    This class is responsible for calculating the levenshtein distance between two words. It contains two functions: 
    __init__(), which initializes attributes, and levenshtein(), which returns the distance.
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.distance = None

    def levenshtein(self, first_word, sec_word):
        '''
        Given two words, this function returns the levenshtein distance between the two words. It uses a list of lists 
        to create a matrix, and assigns values to the entries of the matrix according to the rules outlined in class. The
        levenshtein distance is the last entry in the matrix.
        :param first_word: the first word (order does not matter)
        :type first_word: string
        :param sec_word: the second word (order does not matter)
        :type sec_word: string
        :return: the distance between the words
        :rtype: integer
        '''
        # Create a matrix of the appropriate size and fill with 0s
        matrix = [[0 for j in range(len(sec_word) + 1)] for i in range(len(first_word) + 1)]
        # Replace the first row and column with their appropriate values
        for i in range(len(matrix)):
            matrix[i][0] = i
        matrix[0] = range(0, len(sec_word) + 1)
        # Replace the rest of the entries with the minimum of the calculated options
        for i in range(1, len(first_word) + 1):
            for j in range(1, len(sec_word) + 1):
                first_choice = matrix[i - 1][j] + 1
                sec_choice = matrix[i][j - 1] + 1
                if first_word[i - 1] == sec_word[j - 1]:
                    third_choice = matrix[i - 1][j - 1]
                else:
                    third_choice = matrix[i - 1][j - 1] + 2
                matrix[i][j] = min(first_choice, sec_choice, third_choice)
        # Return the last entry since this is what the levenshtein distance is defined as
        return matrix[-1][-1]
