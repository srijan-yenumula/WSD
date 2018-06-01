#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 21 22:55:45 2018
    Scores output from decision-list.py by comparing against a key
        
        This program will compare the "my-line-answers.txt" (output of decision-list.py) with a given
        key "line-answers.txt" file and calculates the accuracy and provide the
        confusion matrix for the same.
        
        Libraries Used: nltk, pandas, sys, scikit learn, scipy
        
        Usage:
        The program requires two files --
        1. the output generated file from decision-list.py which is my-line-answers.txt in this case
        2. the given key which is line-answers.txt
        
        The program should be run from command prompt/ terminal, once the path of the python file is specified
        the below line should be typed:
        
        python
        scorer.py my-line-answers.txt line-answers.txt > wsd_report.txt
        
        once the above command is run, a text file wsd_report.txt is created in the
        directory location. This file will contain accuracy and confusion matrix computed for
        the above comparisons.
        
        
        Algorithm:
        
        Step 1: Program starts in main()
        
        Step 2: Read the output file and create a dictionary separating the line and senseID
        
        Step 3: Reading the line number as key and senseID as our value
        
        Step 4: For a particular key match the values
        
        Step 5: Find the accuracy of the model by dividing the count of matched words with the len of the model out file.
        
        Step 6: Create a confusion matrix by comparing the predicted and   ground truth answers
        Step 7: END
        
        :author name: Srijan Yenumula, Rav Singh
        :class: AIT-590, IT-499-002P
        :date: 19-MAR-2018
        
"""

import sys
import nltk
import pandas as pd
import scipy
from sklearn.metrics import confusion_matrix


def main():
    """Program entry point"""

    actual_result_file = sys.argv[1]
    groundtruth_file = sys.argv[2]
    
    with open(actual_result_file) as myfile:
        mylist = [line.rstrip('\n') for line in myfile]
        
        new_key= [i.split(':"', 1) for i in mylist] 
     
        new_key_dict = {}

    for a in range (1,len(new_key)):
        key=new_key[a][0]
        value=new_key[a][1]
        new_key_dict[key]=value
    
    with open(groundtruth_file) as myfile1:
        mylist1 = [line.rstrip('\n') for line in myfile1]

    new_key_1= [i.split(':"', 1) for i in mylist1] 
     
    model_key_dict = {}

    for a in range (1,len(new_key_1)):
        key=new_key_1[a][0]
        value=new_key_1[a][1]
        model_key_dict[key]=value

    count = 0 

    for key in new_key_dict:
        if ( new_key_dict[key]== model_key_dict[key]):
            count= count+1

    accuracy = (count/ len(model_key_dict))*100
    outvalue = "Model Accuracy is {}".format(accuracy)

    key_list=[]
    for v in new_key_dict:
        key_list.append(new_key_dict[v])
    

    model_list=[]
    for v in model_key_dict:
        model_list.append(model_key_dict[v])



    df1 = pd.Series( (v for v in key_list) )
    df2 = pd.Series( (v for v in model_list) )
    
    df_confusion = pd.crosstab(df1, df2) 

    print(
        "The baseline accuracy is 42.8%",
        outvalue,
        '\n',
        'Confusion Matrix: ',
        str(df_confusion),
        sep='\n',
    )
if __name__ == '__main__':
    main()
