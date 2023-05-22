import pandas as pd

df = pd.read_csv('all_combinations_1.csv')
df.to_csv('all_combinations_1.csv', header=['State', 'Rto', 'Fuel Type', 'Model'], index=False)


a = 10