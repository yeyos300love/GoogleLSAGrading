import pandas as pd

def process_csv_upload(path: str):
    '''
    read the CSV file with headers, preserving empty spaces
    returns a list of phone numbers
    '''
    df = pd.read_csv(path, 
                    header=0, 
                    keep_default_na=False, 
                    na_filter=False,
                    usecols=['Customer', 'Job type', 'Location', 'Lead type', 'Charge status', 'Lead received', 'Last activity'])
    
    # filter leads for charged phone calls
    filtered_df = df[(df['Charge status'] == 'Charged') & (df['Lead type'] == 'Phone call')]
    # non-empty customers
    filtered_names_df = filtered_df[filtered_df['Customer'] != '']
    
    # return list of tuples (customer, lead received)
    return list(filtered_names_df[['Customer', 'Lead received']].itertuples(index=False, name=None))
    #return filtered_names_df['Customer'].tolist()