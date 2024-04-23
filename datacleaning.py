# %%
#read the data from the csv file
df = pd.read_csv('filmtv_movies.csv')
#data cleaning
columns_to_drop = ['filmtv_id', 'total_votes', 'notes', 'humor', 'rhythm', 'effort', 'tension', 'erotism']
df = df.drop(columns = columns_to_drop)
#drop all rows that include movies from countries outside of the United States
df = df[df['country'] == 'United States']
df
df.to_csv('data.csv', index=False)


