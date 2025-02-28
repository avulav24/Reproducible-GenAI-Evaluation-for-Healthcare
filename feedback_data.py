# Third-party library
import pandas as pd
import openpyxl as xl
import numpy as np

# Built-in library
import re
import os
import glob
import traceback
from typing import Tuple


def get_feedback_files(main_directory):
    # Use glob to find all .xlsm files in the main directory and subdirectories
    pattern = os.path.join(main_directory, '**', '*.xlsm')
    xlsm_files = glob.glob(pattern, recursive=True)
    feedback_xlsm_files = [file for file in xlsm_files if os.path.basename(file).startswith('feedback')]
    return feedback_xlsm_files

def extract_sme_code(filename):
    pattern = r'EVAL-(?:consensus|\d+)'
    match = re.search(pattern, filename)
    if match:
        return match.group()
    else:
        return None
    
def dimension_index(x):
    if x =='' or pd.isna(x):
        return 'na'
    elif x == 'n/a':
            return 'na'
    else:
        
        return x.split('--')[0].strip() 

def load_raw_feedback(datapathlist : list) -> Tuple[pd.DataFrame, pd.DataFrame]:
    try:
        combined_QAdata = pd.DataFrame()
        combined_refdata = pd.DataFrame()
        for path in datapathlist:
            smeName = extract_sme_code(path)
            book = xl.load_workbook(path) 
            sheets = book.sheetnames
            if 'Feedback' in sheets: 
                df_QAdata = pd.read_excel(path,sheet_name='Feedback')
                headers = df_QAdata.iloc[0]
                df_QAdata  = pd.DataFrame(df_QAdata.values[1:], columns=headers)
                df_QAdata['SME'] = smeName
                df_QAdata = df_QAdata.dropna(subset=['Query ID'])
                combined_QAdata  = combined_QAdata._append(df_QAdata, ignore_index=True)
            if 'References' in sheets:
                df_refdata = pd.read_excel(path,sheet_name='References')
                df_refdata['SME'] = smeName
                df_refdata = df_refdata.dropna(subset=['Query ID'])
                combined_refdata = combined_refdata._append(df_refdata,ignore_index=True)
        return combined_QAdata,combined_refdata
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None,None


def get_reviewed_queries(feedback:pd.DataFrame) -> pd.DataFrame:
    try:
        feedback =feedback[feedback['Unable to Review'] != 'X']
        feedback = feedback.dropna(subset=['Overall Answer Helpfulness','Comprehension','Clinical Harmfulness'])
        comprehend =feedback[feedback['Comprehension'] != '0']
        na_correct = list(comprehend[comprehend['Correctness'] == 'na']['Query ID'])
        na_complete= list(comprehend[comprehend['Completeness'] == 'na']['Query ID'])
        na_correct.extend(na_complete)
        na_correct = set(na_correct)
        feedback = feedback[~feedback['Query ID'].isin(na_correct)]
        return feedback
    
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def get_unable_to_review_queries(feedback:pd.DataFrame) -> pd.DataFrame:
    try:
        feedback =feedback[feedback['Unable to Review'] == 'X']
        return feedback
    
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None
  
def convert_to_dimensionscore(feedback:pd.DataFrame)->pd.DataFrame:
    try:
        feedback['Overall Answer Helpfulness'] = np.where(
        feedback['Overall Answer Helpfulness']==' 🙁', 0, np.where(
            feedback['Overall Answer Helpfulness']==' 😐', 1, np.where(
                feedback['Overall Answer Helpfulness']==' 😀', 2, feedback['Overall Answer Helpfulness']
            )
        )
    )

        feedback['Comprehension'] = feedback['Comprehension'].apply(lambda x: dimension_index(x))
        feedback['Correctness'] =  feedback['Correctness'].apply(lambda x: dimension_index(x))
        feedback['Completeness'] =  feedback['Completeness'].apply(lambda x: dimension_index(x))
        feedback['Clinical Harmfulness'] =  feedback['Clinical Harmfulness'].apply(lambda x: dimension_index(x))
        feedback['Clinical Harmfulness Level'] = feedback['Clinical Harmfulness Level'].apply(lambda x: dimension_index(x))
        return feedback
    except Exception as e:
        
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

