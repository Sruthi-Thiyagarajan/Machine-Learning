# -*- coding: utf-8 -*-
"""Sruthi_Diamond_Prediction.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rdIEvyLC6jAs99jJODI30IftAptBiVdb
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline
from sklearn import preprocessing
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error
from sklearn import metrics
from pprint import pprint
from sklearn.model_selection import RandomizedSearchCV
from sklearn.model_selection import learning_curve
#!pip install dtreeviz
#from dtreeviz.trees import dtreeviz
from sklearn import tree
#!git clone https://github.com/ajayarunachalam/RegressorMetricGraphPlot.git
#cd RegressorMetricGraphPlot/
#from regressioncomparemetricplot import CompareModels
#import scikitplot as skplt
import warnings
def warn(*args, **kwargs):
    pass
warnings.warn = warn

"""Reading dataset from csv file. There is a column named "Unnamed" containing the indices. Removing it from the dataset.

9 columns forms the 'x' and price column is the 'y'. "Cut, Color, Clarity, Carat' is main 4C's in determining the price. The "x,y,z" represents the dimensions of the diamond. Depth is given by the calculation: z/mean(x,y). The table represents the width (flat facet of the diamond,responsible for reflecting the light).
"""

df = pd.read_csv("diamonds.csv")
display(df.head(3))
df.drop("Unnamed: 0", axis=1, inplace=True)
display(df.head(6))
df.info()
df_original=df.copy()

"""Data Preprocessing step

Checking for null values and any invalid datatype
"""

df.isnull().sum()
df.info()

df.describe()

"""The minimum values of x,y,z is shown as 0. This represents dimensionless diamonds or faulty data points. Removing the faulty datapoints. The shape command shows 20 faulty datapoints have been removed. """

df = df.drop(df[df["x"]==0].index)
df = df.drop(df[df["y"]==0].index)
df = df.drop(df[df["z"]==0].index)
df.shape

"""Pairplot to visualise the data correlation and to identify the outliers"""

# plot price vs. carat
#sns.set(style="ticks", color_codes=True)
#p=sns.color_palette('bright')
#sns.palplot(p)

sns.pairplot(df, x_vars=["carat"], y_vars=["price"], markers=["D","+"], palette="bright")
plt.show()

"""Plotting carat parameter vs other C's (Cut, Color, Clarity). Using hue in pairplot"""

shade=["#00FF00","#FFBF00","#FF0000","#800080","#000000"]
#ax = sns.pairplot(df, hue="carat", x_vars=['cut', 'clarity', 'color'], y_vars = ['carat'],palette="bright")
sns.pairplot(df, x_vars=['cut', 'clarity', 'color'], y_vars = ['carat'])
sns.pairplot(df, x_vars=['cut', 'clarity', 'color'], y_vars = ['price'])
plt.tight_layout()
plt.subplots_adjust(bottom=0.5)
plt.show()

"""most bigger diamonds (higher carat) fall in Fair cut, I1 clarity and H-I color. These are poor (commercial grade) diamonds.

histplot to see the distribution and to identify the outliers. We are considering continuous variable for histplot.
"""

def histplot(df, listvar):
 fig, axes = plt.subplots(nrows=1, ncols=len(listvar), figsize=(20, 4))
 counter=0
 for ax in axes:
  df.hist(column=listvar[counter], bins=20, ax=axes[counter])
  plt.xlabel(listvar[counter])
  counter = counter+1
 fig.tight_layout()
 plt.show()

#Selecting continuous variables
continuous_vars = df.select_dtypes(include=[np.number]).columns
display(list(continuous_vars))
histplot(df,continuous_vars)

"""From the above graphs, we can predict that there are some outliers. To visualise the outliers, boxplot is used."""

def dfboxplot(df, listvar):
 fig, axes = plt.subplots(nrows=1, ncols=len(listvar), figsize=(20, 3))
 counter=0
 for ax in axes:
  df.boxplot(column=listvar[counter], ax=axes[counter])
  plt.xlabel(listvar[counter])
  counter = counter+1
 plt.tight_layout()
 plt.show()

dfboxplot(df, continuous_vars)
#Features=df['carat','depth','table','price','x','y','z']
#dfbox=df[["price","Features"]]
#dfbox=pd.DataFrame(dfbox)
#ns.boxplot(y='price', x='Features',data=dfbox)
#plt.xticks(rotation=90)
#plt.ylabel("Price")

def removeoutliers(df, listvars, z):
    from scipy import stats
    for var in listvars:
        df1 = df[np.abs(stats.zscore(df[var])) < z]
    return df1
#df = removeoutliers(df, continuous_vars,2)
#df.shape

#Outliers removal using IQR
def remove_outlier(df_in, col_name):
  q1 = df_in[col_name].quantile(0.25)
  q3 = df_in[col_name].quantile(0.75)
  iqr = q3-q1 #Interquartile range
  fence_low  = q1-1.5*iqr
  fence_high = q3+1.5*iqr
  df_out = df_in.loc[(df_in[col_name] > fence_low) & (df_in[col_name] < fence_high)]
  return df_out

for c_vars in list(continuous_vars):
  if c_vars != "price":
   df = remove_outlier(df, c_vars)

dfboxplot(df, continuous_vars)

#Dropping the outliers. 
#df  = df[(df["depth"]<75)&(df["depth"]>45)]
#df  = df[(df["table"]<80)&(df["table"]>40)]
#df = df[(df["x"]<30)]
#df = df[(df["y"]<30)]
#df = df[(df["z"]<30)&(df["z"]>2)]
#df.shape



"""Log Transform"""

#def log_transform(df, listvars):
#   for var in listvars:
#      df[var] = np.log(df[var])
#log_transform(df, continuous_vars)
#histplot(df, continuous_vars)

"""Label Encoding of the categorical variables."""

s = (df.dtypes =="object")
object_cols = list(s[s].index)
print("Categorical variables:", end=" ")
print(object_cols)

# Make copy to avoid changing original data 
#label_data = df.copy()

# Apply label encoder to each column with categorical data
label_encoder = LabelEncoder()
for col in object_cols:
    df[col] = label_encoder.fit_transform(df[col])
#To visualise the values given to the labels.
#The index of the label represents the value given to the label
    print("Values of the label_encoder for {}: ".format(col), end=" ")
    print(label_encoder.classes_)
df.head(5)

print(df.shape)
df.describe()

"""Correlation Matrix : To know the relationship between the attributes and variables in a dataset. To be precise, how one variable is related to another in a dataset."""

cmap = sns.diverging_palette(240, 10, n=9, as_cmap=True)
corrmat= df.corr()
f, ax = plt.subplots(figsize=(12,12))
sns.heatmap(corrmat,cmap=cmap,annot=True, )

"""Creating feature set and target set. "X" and "Y"
"""

# Assigning the featurs as X and trarget as y
y= df["price"]
X= df.drop(["price"],axis =1)
X_train, X_test, y_train, y_test = train_test_split(X, y,test_size=0.25, random_state=7)
#print(X_test.shape[1])

"""Building pipelins of standard scaler and model for various regressors."""

#Normalizing the data only numerical using StandardScaler.
continuous_vars = list(continuous_vars)
print(continuous_vars)
features = df[continuous_vars]
scaler = StandardScaler().fit(features.values)
features = scaler.transform(features.values)
df[continuous_vars] = features
df.head(5)

dt = DecisionTreeRegressor(random_state=0)
rf = RandomForestRegressor(random_state = 0)
xgb = XGBRegressor(random_state =0,verbosity = 0, silent = True)

# List of all the regressors
regressors = [dt, rf, xgb]

# Dictionary of pipelines and model types for ease of reference
regressor_dict = {0:"DecisionTree", 1:"RandomForest", 2:"XGBRegressor"}

# Fit the pipelines
for model in regressors:
    model.fit(X_train, y_train)

"""Cross validation"""

print("{:<30} {:<35} {:<35}".format("Model","RMSE","R2"))
for i, model in enumerate(regressors):
    cv_score_NRMSE = cross_val_score(model, X_train,y_train,scoring="neg_root_mean_squared_error", cv=10)
    cv_score_R2 = cross_val_score(model, X_train,y_train,scoring="r2", cv=10)
    print("{:30s} {:<35} {:<35}".format(regressor_dict[i], -1*cv_score_NRMSE.mean(), cv_score_R2.mean()))

"""Considering RandomForest and XGBRegressor to predict the values"""

pred_random = rf.predict(X_test)
pred_XGB = xgb.predict(X_test)
pred_dt = dt.predict(X_test)

predicted_list = [pred_dt,pred_random,pred_XGB]

# Model Evaluation
rmse=[None]*3
mse=[None]*3
mae=[None]*3
ar2 = [None]*3
r2=[None]*3
print("{:<30} {:<35} {:<35} {:<35} {:<35} {:<35}".format("Model","RMSE","MSE","MAE","Adjusted R2","R2"))
for i, model in enumerate(predicted_list):
  rmse[i] = np.sqrt(metrics.mean_squared_error(y_test, predicted_list[i]))
  mse[i] = metrics.mean_squared_error(y_test, predicted_list[i])
  mae[i] = metrics.mean_absolute_error(y_test, predicted_list[i])
  r2[i] = metrics.r2_score(y_test, predicted_list[i])
  ar2[i] = 1-(1-r2[i])*(len(y_test)-1)/(len(y_test)-X_test.shape[1]-1)
  print("{:30s} {:<35} {:<35} {:<35} {:<35} {:<35}".format(regressor_dict[i], rmse[i],mse[i],mae[i],ar2[i],r2[i]))

print("==============================================================================")
print("Graph Observations")
fig, ax = plt.subplots()
ax.scatter(pred_dt, y_test, edgecolors='yellow')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
plt.title('Diamond Price Prediction (Decision Tree Regression)')
plt.show()

fig, ax = plt.subplots()
ax.scatter(pred_random, y_test, edgecolors='orange')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
plt.title('Diamond Price Prediction (Random Forest Regression)')
plt.show()

fig, ax = plt.subplots()
ax.scatter(pred_XGB, y_test, edgecolors='cyan')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
plt.title('Diamond Price Prediction (XGBoost Regression)')
plt.show()
print("================================================================================")

#Printing the predicted and actual values given by random forest
comparison_df = pd.DataFrame({'Real Values':y_test, 'Predicted Values':pred_random})
comparison_df.head(15)

#Random Forest Regressor
print(X_train.shape)
print(y_train.shape)
rf = RandomForestRegressor(random_state = 35)
# Look at parameters used by our current forest
print('Parameters currently in use:\n')
pprint(rf.get_params())

"""Random Forest Hyperparameter Tuning Considerations
n_estimators = number of trees in the foreset
max_features = max number of features considered for splitting a node
max_depth = max number of levels in each decision tree
min_samples_split = min number of data points placed in a node before the node is split
min_samples_leaf = min number of data points allowed in a leaf node
bootstrap = method for sampling data points (with or without replacement)

Creating a grid to select the appropriate hyperparameters.
On each iteration, the algorithm will choose a difference combination of the features. Hence, there are 2 * 12 * 2 * 3 * 3 * 10 = 4320 settings/combinations.
"""

# Number of trees in random forest
n_estimators = [int(x) for x in np.linspace(start = 200, stop = 2000, num = 10)]
# Number of features to consider at every split
max_features = ['auto', 'sqrt']
# Maximum number of levels in tree
max_depth = [int(x) for x in np.linspace(10, 110, num = 11)]
max_depth.append(None)
# Minimum number of samples required to split a node
min_samples_split = [2, 5, 10]
# Minimum number of samples required at each leaf node
min_samples_leaf = [1, 2, 4]
# Method of selecting samples for training each tree
bootstrap = [True, False]
# Create the random grid
random_grid = {'n_estimators': n_estimators,
               'max_features': max_features,
               'max_depth': max_depth,
               'min_samples_split': min_samples_split,
               'min_samples_leaf': min_samples_leaf,
               'bootstrap': bootstrap}
pprint(random_grid)

"""Random Search Training to determine the best hyperparameters"""

# Use the random grid to search for best hyperparameters
# First create the base model to tune
rf = RandomForestRegressor(random_state = 35)
# Random search of parameters, using 3 fold cross validation, 
# search across 100 different combinations, and use all available cores
rf_random = RandomizedSearchCV(estimator = rf, param_distributions = random_grid, n_iter = 10, cv = 3, verbose=2, random_state=35, n_jobs = -1)
# Fit the random search model
rf_random.fit(X_train, y_train)

rf_random.best_params_

#Predict and calculate the metrics with best fit params
best_random = rf_random.best_estimator_
pred_best_random= best_random.predict(X_test)

# Model Evaluation with tuned hyperparameters
print("==============================================================================")
print("Random Forest")
print("R^2:",metrics.r2_score(y_test, pred_best_random))
print("Adjusted R^2:",1 - (1-metrics.r2_score(y_test, pred_best_random))*(len(y_test)-1)/(len(y_test)-X_test.shape[1]-1))
print("MAE:",metrics.mean_absolute_error(y_test, pred_best_random))
print("MSE:",metrics.mean_squared_error(y_test, pred_best_random))
print("RMSE:",np.sqrt(metrics.mean_squared_error(y_test, pred_best_random)))

fig, ax = plt.subplots()
ax.scatter(pred_best_random, y_test, edgecolors='yellow')
ax.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=3)
ax.set_xlabel('Predicted')
ax.set_ylabel('Actual')
plt.title('Diamond Price Prediction (Hyperparameter Tuned Random Forest Regression)')
plt.show()

print("===============================================================================")