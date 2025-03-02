"""
main.py

Main script for processing feedback data and generating analysis files.
Controls the workflow of data processing and file generation.
"""


# Built-in library
import os
import argparse
import logging
from os import makedirs
import warnings
import traceback

# Custom/User-defined module
import feedback_data
import process_query
import generate_datafiles
import generate_aggregateScore

# Third-party library
import pandas as pd

warnings.filterwarnings('ignore')

def setup_args() -> argparse.ArgumentParser:
    """
    Setup command line arguments.
    """
    parser = argparse.ArgumentParser(description='Assign queries to SMEs.')
    parser.add_argument(
        'feedback_directory', 
        type=str, 
        help='Directory with feedback and disagreement data.'
    )
    parser.add_argument(
        'input_directory', 
        type=str, 
        help='Directory with input data queries_metadata,publication file,query_output and sme_master data.'
    )
    parser.add_argument(
        'out_directory', 
        type=str, 
        help='Directory to store all data files'
    )
    
    return parser
    
def load_sme_master_list(input_directory: str):
    """
    Load SME master list from input directory.

    Args:
        input_directory (str): Directory containing sme_jira_master.xlsx
    Returns:
        tuple: (smes_ready DataFrame, list of SME IDs)
    """
    sme_path = os.path.join(input_directory, 'sme_jira_master.xlsx')
    if os.path.exists(sme_path):
        smes_all = pd.read_excel(sme_path)
        smes_ready = smes_all[smes_all['Status_Ready for Evaluation']=='Yes']
        smes_ready['SME'] = ''
        smes_ready['SME'] = smes_ready.apply(lambda row: f'sme{int(row["Id"]):03d}', axis=1)
        smes_lst = list(smes_ready['SME'])
        print("Loaded %d SMEs (%d ready)", len(smes_all), len(smes_ready))
        print("Available smes: ", smes_lst)
        return smes_ready, smes_lst
    else:
        print(f"Error: SME master list not found at {sme_path}")
        return None, None

def load_all_inputfile(input_directory: str):
    """
    Load all required input files from the specified directory.
    """
    try:
        print("Loading all input data")
        query_metadata = pd.read_excel(input_directory+'/query_metadata_initial.xlsx')
        query_feedback = pd.read_excel(input_directory+'/query_output-initial.xlsx', sheet_name='Queries')
        query_reference = pd.read_excel(input_directory+'/query_output-initial.xlsx', sheet_name='References')
        publication = pd.read_excel(input_directory+'/Publication.xlsx', sheet_name='Publication query list')
        query_failed = pd.read_excel(input_directory+'/query_output-initial-failed.xlsx')
        print("Successfully loaded all data")
        return query_metadata, query_feedback, query_reference, publication, query_failed
    
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None, None, None, None, None
       
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logger = logging.getLogger(__name__)

    # Parse command line arguments
    parser = setup_args()
    args = parser.parse_args()

    # Create output directory
    output_dir = args.out_directory
    makedirs(output_dir, exist_ok=True)
    logging.info('Saving output in %s', output_dir)
   
    # Set directory paths
    feedback_directory = args.feedback_directory
    input_directory = args.input_directory
    out_directory = args.out_directory
    
    # Load all input data
    query_metadata, query_feedback, query_reference, publication, query_failed = load_all_inputfile(input_directory)
    if query_metadata is None:
        logging.error("Failed to load input files")
        exit(1)
    
    # Load SME master list
    sme_ready, sme_list = load_sme_master_list(input_directory)
    if sme_ready is None:
        logging.error("Failed to load SME master list")
        exit(1)
    
    # Load all feedback data from sme_assignments folder
    xlsm_files = feedback_data.get_feedback_files(feedback_directory)
    feedback, reference = feedback_data.load_raw_feedback(xlsm_files)
    
    # Filter only publication data
    publication_queries = list(publication['query_id'])
    feedback = feedback[feedback['Query ID'].isin(publication_queries)]
    feedback.to_excel(os.path.join(feedback_directory, 'raw_feedback.xlsx'))

    # Extract and save unable to review queries
    unable = feedback_data.get_unable_to_review_queries(feedback)
    print(len(unable))
    unable.to_excel(os.path.join(feedback_directory, 'unable.xlsx'))

    # Extract reviewed data alone
    raw_review = feedback_data.get_reviewed_queries(feedback)
    raw_review.to_excel(os.path.join(feedback_directory, 'review.xlsx'))
    print(len(raw_review))

    # Convert the raw feedback to dimension score
    review = feedback_data.convert_to_dimensionscore(raw_review)
    cleaned_feedback = feedback_data.convert_to_dimensionscore(feedback)
    cleaned_feedback.to_excel(os.path.join(feedback_directory, 'cleaned_feedback.xlsx'))
    
    # Assign sme agreement and review status
    review_status, data = process_query.get_review_status(review, sme_ready, cleaned_feedback)
    review_status.to_excel(os.path.join(feedback_directory, 'review_status.xlsx'))

    # Generate data files
    transform_df = generate_datafiles.generate_transformed_file(review, review_status)
    transform_df.to_excel(os.path.join(out_directory, 'transformed.xlsx'), index=False)

    metadata = generate_datafiles.generate_publicationMetadata(publication)
    metadata.to_excel(os.path.join(out_directory, 'Query_metadata.xlsx'), index=False)

    query_feedback, query_reference = generate_datafiles.generate_queryResponse_reference(
        query_feedback, query_reference, publication, query_failed)
    
    with pd.ExcelWriter(os.path.join(out_directory, 'Query_response.xlsx')) as writer:
        query_feedback.to_excel(writer, sheet_name='Feedback', index=False)
        query_reference.to_excel(writer, sheet_name='References', index=False)
    
    query_status = generate_datafiles.generate_query_status(review_status, query_feedback, publication)
    query_status.to_excel(os.path.join(out_directory, 'Query_status.xlsx'), index=False)

    full_feedback = generate_datafiles.get_full_feedback(cleaned_feedback, publication)
    full_feedback.to_excel(os.path.join(out_directory, 'All_results.xlsx'), index=False)

    stats_df = generate_aggregateScore.generate_CIScore(transform_df)
    stats_df.to_excel(os.path.join(out_directory, 'stats.xlsx'), index=False)
