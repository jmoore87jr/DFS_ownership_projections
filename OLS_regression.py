import matplotlib.pyplot as plt
import pandas as pd
import statsmodels.api as sm
from statsmodels.sandbox.regression.predstd import wls_prediction_std

df1 = pd.read_csv('821.csv')
df2 = pd.read_csv('822.csv')
df3 = pd.read_csv('823.csv')
df4 = pd.read_csv('824.csv')

df = pd.concat([df1, df2, df3, df4])
df = df[['Unnamed: 0', 'projected_ownership', 'awesemo_ownership', 'value', 'salary', 'actual_ownership']]
df.columns = ['player', '%_owned_optimal', 'awesemo_ownership', 'value', 'salary', 'actual_ownership']

print(df.info())
print(df.head())

# scatter
x = df['value']
y = df['actual_ownership']
plt.scatter(x, y)
plt.show() # not working
plt.savefig('TEST.png') # working

# OLS regression
X = df[['%_owned_optimal', 'value', 'salary']]
Y = df['actual_ownership']
X = sm.add_constant(X)
model = sm.OLS(Y,X)
results = model.fit()
print(results.summary())


# create new column using regression results
df['predicted_ownership'] = -0.196651 + df['%_owned_optimal']*0.160766 + df['value']*0.048588 + df['salary']*0.000013
print(df)

# mean squared error columns
optimal_MSE = sum((df['%_owned_optimal'] - df['actual_ownership'])**2) / len(df['actual_ownership']) * 100
awesemo_MSE = sum((df['awesemo_ownership'] - df['actual_ownership'])**2) / len(df['actual_ownership']) * 100
predicted_MSE = sum((df['predicted_ownership'] - df['actual_ownership'])**2) / len(df['actual_ownership']) * 100
print("%_optimal MSE * 100: {}".format(optimal_MSE))
print("awesemo MSE * 100: {}".format(awesemo_MSE))
print("predicted MSE * 100: {}".format(predicted_MSE))
df.to_csv('own_predict.csv')

# projecting for a 3 game slate, it seems like my numbers are 25% smaller than they should be because I ran OLS on 4-game slates

# does the high condition number matter? value and optimal_own_% should be highly correlated

# consider adding stdev/$...
# unexciting guys like kleber, horford, adams are being over-projected
# also add pts/$_actual(t-1); players who have done well recently are owned more

# for data collection: 
# download ownership from biggest DK GPP every day, and store in list of dataframes
# to get pts/$_actual(t-1) find each player's most recent slate (for and if) and use that number


