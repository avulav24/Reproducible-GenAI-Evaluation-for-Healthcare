# Third-party library
import pandas as pd

# Built-in library
from typing import  Any
from statistics import mode
import traceback
from typing import Tuple
def generate_publicationMetadata(publication_data:pd.DataFrame) -> pd.DataFrame:
    try:
        required_columns =['query_id','query','source','specialties','speciality_routing','sex_at_birth','age_categories','special_populations','sensitive_topics','query_type']
        query_metadata = publication_data[required_columns]
        query_metadata = query_metadata.drop_duplicates()
        return query_metadata
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None
def generate_queryResponse_reference(query_feedback_data:pd.DataFrame,query_reference_data:pd.DataFrame,publication_queries:pd.DataFrame,query_failed:pd.DataFrame) ->Tuple[pd.DataFrame,pd.DataFrame]:
    try:
        required_columns = ['Query ID','Query','Processed Query','Status','Response ID','Response','Additional Information','Response Time']
        ## include failed responses
        query_failed = query_failed[required_columns]
        query_feedback_data =query_feedback_data._append(query_failed,ignore_index=True)

        #filter the publication queries
        publication_queries = list(publication_queries['query_id'])
        query_feedback_data = query_feedback_data[query_feedback_data['Query ID'].isin(publication_queries)]
        query_reference_data = query_reference_data[query_reference_data['Query ID'].isin(publication_queries)]

        
        query_feedback_data =query_feedback_data[required_columns]

        
        return query_feedback_data,query_reference_data
      
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None
    
def generate_query_status(review_status:pd.DataFrame,query_output:pd.DataFrame,publication:pd.DataFrame)-> pd.DataFrame:
    try:
        ## add failed queries
        reviewed_queries = list(review_status['Query ID'])
        publication_queries = list(publication['query_id'])
        not_in_reviewed = [s for s in publication_queries if not any(sub in s for sub in reviewed_queries)]
        new_data = []
        #check whether its failed resonse query 
        for query in not_in_reviewed:
            output = query_output[query_output['Query ID'] == query]
            if len(output) == 1:
                status =  output.iloc[0]['Status']
                if status != 'Success': # if not sucess , add as failed data
                    new_data.append({'Query ID':query, 'Review status':'Failed response;'+status,'include_exclude':'exclude',
                                        'SMEs_reviewed':'','SMEs_yet_to_review':'','SMEs_unable_to_review':''})
                else:
                    new_data.append({'Query ID':query, 'Review status':'others','include_exclude':'exclude',
                                      'SMEs_reviewed':'','SMEs_yet_to_review':'','SMEs_unable_to_review':''})
            else:
                new_data.append({'Query ID':query, 'Review status':'duplicate data in output file','include_exclude':'exclude',
                                      'SMEs_reviewed':'','SMEs_yet_to_review':'','SMEs_unable_to_review':''})
        new_df = pd.DataFrame(new_data)
        review_status = review_status._append(new_df, ignore_index=True)       

        # add query to existing review status file
        required_columns =['Query ID','Query','Review status','SMEs_reviewed','SMEs_yet_to_review','SMEs_unable_to_review']
        query_status = review_status.merge(query_output, how='left', on='Query ID')
        query_status = query_status[required_columns]
        

        return query_status
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None
def get_full_feedback(full_feedback:pd.DataFrame,publication_queries:pd.DataFrame) -> pd.DataFrame:
    try:
        required_columns = ['SME','Query ID','Query','Response URL','Response','Unable to Review','Overall Answer Helpfulness','Comprehension','Correctness','Completeness','Clinical Harmfulness','Clinical Harmfulness Level','Notes']
        print(full_feedback.columns)
        #filter the publication queries
        publication_queries = list(publication_queries['query_id'])
        full_feedback = full_feedback[full_feedback['Query ID'].isin(publication_queries)]
        full_feedback= full_feedback[required_columns]
        return full_feedback

    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None

def get_transformed_row(review_type,review_status,rater_1:dict[str, Any], rater_2:dict[str,Any],
                        rater_3:dict[str,Any],email_consensus:dict[Any],final:dict[str,Any]) -> dict[str:Any]:
    return {"Query ID":rater_1['Query ID'],
            "review_type":review_type,
            "qa_review_status":review_status,
            
            "overall_rater_1":str(rater_1['Overall Answer Helpfulness']),
            "overall_rater_2":str(rater_2['Overall Answer Helpfulness']),
            "overall_rater_3":str(rater_3['Overall Answer Helpfulness']),
            "overall_email_consensus":str(email_consensus['Overall Answer Helpfulness']),
            "overall_final":str(final['Overall Answer Helpfulness']),
            
            "comprehension_rater_1":str(rater_1['Comprehension']),
            "comprehension_rater_2":str(rater_2['Comprehension']),
            "comprehension_rater_3":str(rater_3['Comprehension']),
            "comprehension_email_consensus":str(email_consensus['Comprehension']),
            "comprehension_final":str(final['Comprehension']),

            "correctness_rater_1":str(rater_1['Correctness']),
            "correctness_rater_2":str(rater_2['Correctness']),
            "correctness_rater_3":str(rater_3['Correctness']),
            "correctness_email_consensus":str(email_consensus['Correctness']),
            "correctness_final":str(final['Correctness']),

            "completeness_rater_1":str(rater_1['Completeness']),
            "completeness_rater_2":str(rater_2['Completeness']),
            "completeness_rater_3":str(rater_3['Completeness']),
            "completeness_email_consensus":str(email_consensus['Completeness']),
            "completeness_final":str(final['Completeness']),

            "harmfulness_rater_1":str(rater_1['Clinical Harmfulness']),
            "harmfulness_rater_2":str(rater_2['Clinical Harmfulness']),
            "harmfulness_rater_3":str(rater_3['Clinical Harmfulness']),
            "harmfulness_email_consensus":str(email_consensus['Clinical Harmfulness']),
            "harmfulness_final":str(final['Clinical Harmfulness']),

            "harmful_level_rater_1":str(rater_1['Clinical Harmfulness Level']),
            "harmful_level_rater_2":str(rater_2['Clinical Harmfulness Level']),
            "harmful_level_rater_3":str(rater_3['Clinical Harmfulness Level']),
            "harmful_level_email_consensus":str(email_consensus['Clinical Harmfulness Level']),
            "harmful_level_final":str(final['Clinical Harmfulness Level'])}
    
def generate_transformed_file(feedback:pd.DataFrame,review_status:pd.DataFrame) -> pd.DataFrame:
    transformed_data =[]
    try:
        required_cols =['SME','Query ID','Overall Answer Helpfulness','Comprehension','Correctness','Completeness','Clinical Harmfulness','Clinical Harmfulness Level']
        feedback =feedback[required_cols]
        empty_dic = {column: 'na' for column in required_cols}
        for index,row in review_status.iterrows():
            if row['include_exclude'] == 'include':
                
                data =''
                df_query = feedback[feedback['Query ID']==row['Query ID']]
                if 'EVAL-consensus' in list(df_query['SME']):
                    email_consensus =(df_query[df_query['SME'] =='EVAL-consensus']).to_dict('records')[0]
                    final = email_consensus
                    
                    sme_rates = df_query[df_query['SME'] !='EVAL-consensus'].head(3).to_dict('records')
                    data = get_transformed_row('Email consensus',row['Review status'],sme_rates[0],sme_rates[1],sme_rates[2],email_consensus,final)
                elif len(df_query) == 2 :
                    sme_rates = df_query.to_dict('records')
                    final = sme_rates[0]
                    data = get_transformed_row('evaluator',row['Review status'],sme_rates[0],sme_rates[1],empty_dic,empty_dic,final)
                
                elif len(df_query) >= 3  and 'mode' in row['Review status']:
                    
                    sme_rates = df_query.to_dict('records')
                    final={}
                    
                    for col in required_cols:
                         
                        
                        v = mode(list(df_query[col]))
                        
                        final[col]=v
                    data = get_transformed_row('evaluator',row['Review status'],sme_rates[0],sme_rates[1],sme_rates[2],empty_dic,final)
                else:
                    sme_rates = df_query.to_dict('records')
                    data = get_transformed_row('evaluator','unknown',sme_rates[0],empty_dic,empty_dic,empty_dic,empty_dic)


               
                transformed_data.append(data)
        transformed_df = pd.DataFrame(transformed_data)
        return transformed_df
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None


