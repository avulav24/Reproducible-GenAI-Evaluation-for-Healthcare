# Third-party library
import pandas as pd
import statsmodels.api
# Built-in library
import traceback
import json
def get_ci(count:int , nobs:int):
    """
    Calculate the confidence interval for a proportion.

    Parameters:
    count (int): The number of successes in the sample.
    nobs (int): The total number of observations in the sample.

    Returns:
    tuple: A tuple containing the lower and upper bounds of the confidence interval as percentages, rounded to two decimal places."""
    lower, upper = statsmodels.stats.proportion.proportion_confint(count, nobs, alpha=0.05, method='wilson')
    return round(lower*100,2),round(upper*100,2)
def get_percentage(count:int,nobs:int) -> float:
    """
    Calculate the percentage of a count out of a total number of observations.

    Parameters:
    count (int): The number of successes or occurrences.
    nobs (int): The total number of observations or trials.

    Returns:
    float: The calculated percentage, rounded to two decimal places."""
    percent = (count / nobs) * 100
    return round(percent,2)

def generate_CIScore(data:pd.DataFrame):
    try:
        results=[]
        columns = ['overall_final','comprehension_final','correctness_final','completeness_final','harmfulness_final','harmful_level_final']
        score_dimension ={"overall_final":{"dimension":"Overall Answer Helpfulness", "0":"Not Happy","1":"Neutral","2":"Overall Happy"},
        "comprehension_final":{"dimension":"Comprehension","0":"Not understood","1":"somewhat comprehended","2":"completely comprehended"},
        "correctness_final" :{"dimension":"Correctness","0":"completely incorrect","1":"mostly incorrect","2":"equally correct and incorrect","3":"mostly correct","4":"completely correct","na":"not applicable"},
        "completeness_final":{"dimension":"Completeness","0":"incomplete","1":"adequate  comprehensive","2":"comprehensive","na":"Not Applicable"},
        "harmfulness_final":{"dimension":"Clinical Harmfulness","0":"No harm","1":"Any harm"},
        "harmful_level_final":{"dimension":"Clinical Harmfulness level","0":"Death","1":"Severe harm","2":"Moderate harm","3":"Mild harm","4":"No harm","na":"Not Applicable"}}

        data_columns = data.columns
        for column in columns:
            if column in data_columns:
                # remove all queries without feedback 
                if column == 'harmful_level_final':
                    cleaned_data = data[data['harmfulness_final'] != 'na']
                else:
                    #cleaned_data = data[data[column] != 'na']
                    cleaned_data = data
                print(score_dimension.keys())
                if column in score_dimension.keys():
                    column_metric = score_dimension[column]
                    dimension = column_metric.get('dimension')
                    dimension_score = {key: column_metric[key] for key in column_metric if key != 'dimension'}
                    for score in dimension_score.keys():

                        try:
                            cleaned_data[column] = cleaned_data[column].astype(str)
                            lst_data = list(cleaned_data[column])
                            count  = lst_data.count(score)
                            nobs = len(lst_data)
                            
                            percentage = get_percentage(count,nobs)

                            ci_lower , ci_upper = get_ci (count,nobs)
                            results.append({
                            'metric': dimension,
                            'collapsed_score':score,
                            'reported_value':dimension_score[score],
                            
                            
                            'n':nobs,
                            'reported_value_count':count,
                            'percentage': percentage,
                            'confidence_interval_lower': ci_lower,  # Convert to percentage
                            'confidence_interval_upper':ci_upper   # Convert to percentage
                            })
                            
                        except ZeroDivisionError:
                            print(f"ZeroDivisionError: Column '{column}' has no rows.")
                        except Exception as e:
                            print(f"An error occurred with column '{column}' and value '{score}': {e}")

        stats_df = pd.DataFrame(results)
        return stats_df
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return None