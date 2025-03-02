"""
process_query.py

This module handles the processing of queries and their review status,
including SME agreement checks and review status generation.
"""

# Third-party library
import pandas as pd


# Built-in library
import traceback
import itertools
from typing import Tuple

def check_sme_md(query_sme: pd.DataFrame, sme_data: pd.DataFrame) -> bool:
    """
    Check if any SME in the query has MD or DO credentials.

    Args:
        query_sme: DataFrame containing SME information for a query
        sme_data: DataFrame containing all SME data

    Returns:
        bool: True if MD/DO credentials exist, False otherwise
    """
    try:
        sme_list = list(query_sme['SME'])
        merged_df = sme_data[sme_data['ID'].isin(sme_list)]
        credentials = list(merged_df['Please specify your clinical credentials'])
        return 'MD' in credentials or 'DO' in credentials
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def check_sme_agree(df_query) -> str:
    """
    Check agreement level between SMEs for a query.

    Args:
        df_query: DataFrame containing query reviews from multiple SMEs

    Returns:
        str: Agreement status string with inclusion decision
    """
    try:
        columns_to_compare = [
            'Overall Answer Helpfulness',
            'Comprehension',
            'Correctness',
            'Completeness',
            'Clinical Harmfulness',
            'Clinical Harmfulness Level'
        ]
        
        sme_disagree = []
        if len(df_query) == 2:
            for col in columns_to_compare:
                if len(set(df_query[col])) == 2:
                    sme_disagree.append(col)
            return '2 SMEs disagree~exclude' if sme_disagree else '2 SMEs agree~include'
  
        elif len(df_query) == 3:
            agree = []
            disagree = []
            three = []
            for col in columns_to_compare:
                unique_values = len(set(df_query[col]))
                if unique_values == 1:
                    agree.append(col)
                elif unique_values == 2:
                    disagree.append(col)
                elif unique_values == 3:
                    three.append(col)
                    
            if len(three) > 0:
                return '3 SMEs disagree~exclude'
            elif len(disagree) > 0 and len(three) == 0:
                return '3 SMEs mode agree~include'
            else:
                return '3 SMEs agree~include'
        
        elif len(df_query) >= 3:
            return 'more than 3 SMEs~include'
            
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def collapsed_score(data: pd.DataFrame) -> pd.DataFrame:
    """
    Group scores into collapsed categories.

    Args:
        data: DataFrame containing review scores

    Returns:
        DataFrame with additional grouped score columns
    """
    try:
        columns = [
            'Overall Answer Helpfulness',
            'Comprehension',
            'Correctness',
            'Completeness',
            'Clinical Harmfulness',
            'Clinical Harmfulness Level'
        ]
        
        for col in columns:
            data[col] = data[col].astype(str)
            
        # Q3 change - raw value are same as grouped value
        data['overall_grouped'] = data['Overall Answer Helpfulness']
        data['comprehension_grouped'] = data['Comprehension']
        data['correctness_grouped'] = data['Correctness']
        data['completeness_grouped'] = data['Completeness']
        data['harmfulness'] = data['Clinical Harmfulness']
        data['harmful_level_grouped'] = data['Clinical Harmfulness Level']
        
        return data
        
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def check_collapsed_score(df_query, columns, count):
    """
    Check agreement between SMEs based on collapsed scores.

    Args:
        df_query: DataFrame containing query reviews
        columns: List of columns to check
        count: Number of SMEs

    Returns:
        str: Agreement status with inclusion decision
    """
    agree = []
    disagree = []
    columns = [
        'overall_grouped',
        'comprehension_grouped',
        'correctness_grouped',
        'completeness_grouped',
        'harmfulness',
        'harmful_level_grouped'
    ]
    
    if count == 2:    
        for col in columns:
            if len(set(df_query[col])) == 1:
                agree.append(col)
            elif len(set(df_query[col])) >= 1:
                disagree.append(col)
        return 'Collapsed disagree~exclude' if disagree else 'Collapsed agree~include'
        
    elif count == 3:  
        data_dic = df_query.to_dict('records')
        for r1, r2 in itertools.combinations(data_dic, 2):
            agree = all((r1[dim] == r2[dim] for dim in columns))
            if agree:
                return '3 SMEs - Collapsed agree~include'
        return '3 SMEs - Collapsed disagree~exclude'

def add_not_reviwed_smes(assigned_smes: list, reviewed_smes: list, unable_to_review: list) -> str:
    """
    Get list of SMEs who haven't reviewed the query yet.

    Args:
        assigned_smes: List of all assigned SMEs
        reviewed_smes: List of SMEs who completed review
        unable_to_review: List of SMEs unable to review

    Returns:
        str: Comma-separated string of SMEs yet to review
    """
    try:
        filtered_list = [s for s in assigned_smes if not any(sub in s for sub in reviewed_smes)]
        filtered_list = [s for s in filtered_list if not any(sub in s for sub in unable_to_review)]
        return ",".join(filtered_list)

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None   

def get_review_status(feedback: pd.DataFrame, sme_data: pd.DataFrame, master_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate review status for all queries.

    Args:
        feedback: DataFrame containing review feedback
        sme_data: DataFrame containing SME information
        master_df: DataFrame containing master data

    Returns:
        Tuple containing review status DataFrame and processed data DataFrame
    """
    QA_final = []
    
    try:
        data = collapsed_score(feedback)
        query_list = set(data['Query ID'])
        full_queries = set(master_df['Query ID'])
        imcomplete = [s for s in full_queries if not any(sub in s for sub in query_list)]
        
        for query in query_list:
            # Get all SMEs assigned to the query
            assigned_smes = list(master_df[master_df['Query ID'] == query]['SME'])
            # Unable to review SMEs
            unable_to_review_smes = list(master_df[(master_df['Query ID'] == query) & 
                                                 (master_df['Unable to Review'] == 'X')]['SME'])
            df_query = data[data['Query ID'] == query]
            # Get all SMEs who reviewed the query completely
            reviewed_smes = list(df_query['SME'])
            not_reviewed = add_not_reviwed_smes(assigned_smes, reviewed_smes, unable_to_review_smes)
            
            # Check for only sme reviewed queries
            if 'EVAL-consensus' not in reviewed_smes:
                # If reviewed by "2 SMEs"
                if len(df_query) >= 2:
                    # Check for any MD or DO credential SME
                    sme_md_pass = check_sme_md(df_query, sme_data)
                    # Query with one MD or DO
                    if sme_md_pass:
                        sme_agree = check_sme_agree(df_query)
                        QA_final.append([
                            query,
                            sme_agree.split('~')[0],
                            sme_agree.split('~')[1],
                            ",".join(reviewed_smes),
                            not_reviewed,
                            ",".join(unable_to_review_smes)
                        ])
                    else:
                        QA_final.append([
                            query,
                            'Missing SME - MD,DO',
                            "exclude",
                            ",".join(reviewed_smes),
                            not_reviewed,
                            ",".join(unable_to_review_smes)
                        ])
                elif len(df_query) == 1:
                    QA_final.append([
                        query,
                        '1 SME review',
                        "exclude",
                        ",".join(reviewed_smes),
                        not_reviewed,
                        ",".join(unable_to_review_smes)
                    ])
            # Check for email consensus
            elif 'EVAL-consensus' in reviewed_smes:
                QA_final.append([
                    query,
                    'Email consensus agreed',
                    "include",
                    ",".join(reviewed_smes),
                    not_reviewed,
                    ",".join(unable_to_review_smes)
                ])

        review_df = pd.DataFrame(QA_final, columns=[
            'Query ID', 'Review status', 'include_exclude',
            'SMEs_reviewed', 'SMEs_yet_to_review', 'SMEs_unable_to_review'
        ])
        
        # Add non reviewed data
        data_incompleted = []
        for q in imcomplete:
            assign_smes = list(master_df[master_df['Query ID'] == q]['SME'])
            unable_smes = list(master_df[(master_df['Query ID'] == q) & 
                                       (master_df['Unable to Review'] == 'X')]['SME'])
            review_smes = []
            not_reviewed = add_not_reviwed_smes(assign_smes, review_smes, unable_smes)
            data_incompleted.append({
                'Query ID': q,
                'Review status': 'incomplete',
                'include_exclude': 'exclude',
                'SMEs_reviewed': review_smes,
                'SMEs_yet_to_review': not_reviewed,
                'SMEs_unable_to_review': unable_smes
            }) 
            
        new_df = pd.DataFrame(data_incompleted)
        review_df = pd.concat([review_df, new_df], ignore_index=True)
        
        return review_df, data
        
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None, None
