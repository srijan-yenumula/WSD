"""Disambiguates between various uses of the word 'line'

Words can have multiple possible uses, a.k.a. word senses.
This program attempts to differentiate between 'line' used in the
sense of 'phone line' versus 'product line'.

Usage:
    To run, specify training and testing datasets, as well as a log file.
    If no redirect is used, all output goes DISPLAY/STDOUT.

    Command-line syntax:
        python decision-list.py [training-file] [test-file] [log]

    Syntax with redirect:
        python decision-list.py [training-file] [test-file] [log] > [result-file]

Input:
    Takes in a dataset to train on as input. Format must be valid XML.

    Example:
        <corpus lang="en">
            <lexelt item="line-n">
                <instance id="line-n.w9_10:6830:">
                    <answer instance="line-n.w9_10:6830:" senseid="phone"/>
                    <context>
                        <s>
                        In contrast, the California economy is booming,
                        with 4.5% access <head>line</head> growth in the past year.
                        </s>
                    </context>
                </instance>
            </lexelt>
        </corpus>

    The XML does not have to be indented as shown to be parsed correctly.

Output:
    The program prints assigned word senses in XML format.

    Example:
        <answer instance="line-n.w8_059:8174:" senseid="product"/>
        <answer instance="line-n.w7_098:12684:" senseid="phone"/>
        <answer instance="line-n.w8_106:13309:" senseid="product"/>

Algorithm:
    - program starts in main()
    - main():
        - open and parse training XML file
        - pass XML DOM to rank_tests()

    - rank_tests():
        - divide text into sense categories
        - sort features based on log_likelihood()
        - log_likelihood():
            - count occurences of feature
            - calculate sense ratio
            - return log of ratio
        - writes ranked feature list decision-list log

    - main() calls assign_senses()
    - assign_senses():
        - open and parse test XML file
        - for each instance of line:
            - finds the first feature in decision list
            - assigns a sense based on the feature
            - prints sense as output

    - program ends when control returns to main()

:name: Srijan Yenumula, Rav Singh
:course: IT-499-002
:date: 18 April 2018
"""

import math
import re
import sys

from bs4 import BeautifulSoup

# file names
TRAINING = sys.argv[1]
TEST = sys.argv[2]
OUTPUT = sys.argv[3]
PHONE = 'phone'
PRODUCT = 'product'


def tests():
    """Feature vector"""

    def telephone_test(line):
        """Feature for 'telephone' in text"""
        return ('telephone' in line, PHONE)
    yield telephone_test

    def sale_test(line):
        """Feature for 'sale(s)' in text"""
        return (re.search(r'sale?', line), PRODUCT)
    yield sale_test

    def sell_test(line):
        """Feature for 'sell(s)' in text"""
        return (re.search(r'sells?', line), PRODUCT)
    yield sell_test

    def call_test(line):
        """Feature for 'call(s)' in text"""
        return (re.search(r'calls?', line), PHONE)
    yield call_test

    def voice_test(line):
        """Feature for 'voice' in text"""
        return ('voice' in line, PHONE)
    yield voice_test

    def market_test(line):
        """Feature for 'market(s)' in text"""
        return (re.search(r'markets?', line), PRODUCT)
    yield market_test

    def service_test(line):
        """Feature for 'service(s)' in text"""
        return (re.search(r'services?', line), PHONE)
    yield service_test

    def food_test(line):
        """Feature for 'food(s)' in text"""
        return (re.search(r'foods?', line), PRODUCT)
    yield food_test


FEATURES = [test for test in tests()]


def rank_tests(soup):
    """Orders tests by log likelihood"""
    text1 = []  # sense1 text
    text2 = []  # sense2 text

    # finds all <s> tags and adds their text to the respective sense
    for instance in soup.find_all('instance'):
        if instance.answer['senseid'] == 'phone':
            for tag in instance.find_all('s'):
                string = tag.string
                text1.append(string)
        else:
            for tag in instance.find_all('s'):
                string = tag.string
                text2.append(string)

    def log_likelihood(feature):
        """Calculates the log likelihood ratio of a feature"""
        count1 = 0  # sense1 count
        count2 = 0  # sense2 count

        sense_text = text1
        other_text = text2

        # swap the current text if the feature indicates a product
        sense = feature('')[1]
        if sense == PRODUCT:
            sense_text = text2
            other_text = text1

        # Count(sense1 feature)
        for line in sense_text:
            if line is not None and feature(line)[0]:
                count1 += 1

        # Count(sense2 feature)
        for line in other_text:
            if line is not None and feature(line)[0]:
                count2 += 1

        total = count1 + count2
        prob1 = count1 / total  # conditional prob of sense1
        prob2 = count2 / total  # probability of sense2

        try:
            ratio = math.log10(prob1 / prob2)
        except ZeroDivisionError:
            ratio = 1

        with open(OUTPUT, 'a+') as output:
            output.write(
                f'{feature.__name__}\t{ratio}\t{sense}\n'
            )

        return ratio

    FEATURES.sort(key=log_likelihood)


def assign_senses(soup):
    """Assigns word senses to test data"""
    sense1_count = len(soup.find_all(senseid="phone"))
    sense2_count = len(soup.find_all(senseid="product"))
    default = PHONE if sense1_count > sense2_count else PRODUCT

    with open(TEST, 'r') as data:
        soup = BeautifulSoup(data, 'xml')

    # generates a sense for each instance tag
    for instance in soup.find_all('instance'):
        text = tuple(
            tag.string for tag in instance.find_all('s')
            if tag.string is not None
        )

        # iterate through decision-list of features
        sense = None
        for line in text:
            for feature in FEATURES:
                test_result = feature(line)
                if test_result[0]:
                    sense = test_result[1]
                    break

        if sense is None:
            sense = default

        id_ = instance['id']
        print(f'<answer instance="{id_}" senseid="{sense}"/>')


def main():
    """Entry point for program"""
    with open(TRAINING, 'r') as data:
        soup = BeautifulSoup(data, 'xml')

    rank_tests(soup)
    assign_senses(soup)


if __name__ == '__main__':
    main()
