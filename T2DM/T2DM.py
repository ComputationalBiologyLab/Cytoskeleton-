# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 01:00:19 2022

@author: Lenovo
"""


import pandas as pd
import sklearn
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
import os 
from matplotlib import pyplot as plt
from sklearn.feature_selection import RFECV
from sklearn.datasets import make_classification
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
import warnings  
from matplotlib.axes import Axes
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.feature_selection import SelectFromModel
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE
from sklearn.pipeline import make_pipeline
from collections import Counter
import time
import itertools
from sklearn.model_selection import GridSearchCV
warnings.filterwarnings('ignore')
from sklearn.model_selection import cross_val_predict
from sklearn.metrics import auc
from sklearn.metrics import plot_roc_curve
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.pipeline import Pipeline

from sklearn.metrics import balanced_accuracy_score


os.chdir("D:/cytoskeleton/diabetes")


# read_the_data
file_name= "D:/cytoskeleton/diabetes/cyto_counts.csv"
# index_col=0 to consider the first coloum as row names
data= pd.read_csv(file_name ,index_col= 0)
print(data.shape)
print(data.head())

# integer encode
label_encoder = LabelEncoder()
# fit and transform the data
data['group']= label_encoder.fit_transform(data['group'])
print(data['group'])
#split_the_data
X = data.iloc[: ,:-1]
y= data.iloc[: ,-1:]
print(y.head(5))
''''''''''''''''''''
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

print('Train', X_train.shape, y_train.shape)
print('Test', X_test.shape, y_test.shape)

# test_multiple_classifiers
classifiers = [
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    KNeighborsClassifier(),
    SVC(kernel="linear"),
    GaussianNB()
    ]
# Naive Train Accuracy
algo = []
scores = []
for clf in classifiers:
    algo.append(clf.__class__.__name__)
    scores.append(cross_val_score(clf,X,y, cv=5, scoring="accuracy").mean() * 100)
warnings.filterwarnings('ignore')
Naivescore_df_Train = pd.DataFrame({'Algorithm': algo, 'Score': scores}).set_index('Algorithm')

Naivescore_df_Train
#suport_vector_machine
param_grid = {'C': [0.1, 1, 10, 100, 1000],
              'gamma': [1, 0.1, 0.01, 0.001, 0.0001],
              'kernel': ["rbf"]}

grid = GridSearchCV(SVC(), param_grid, refit =True, verbose =3)

# fitting the model for grid search
grid.fit(X_train, y_train)

# print best parameter after tuning
print(grid.best_params_)

# print how our model looks after hyper-parameter tuning
print(grid.best_estimator_)
#cross_validation_to_validate_the_accuracy

clf= SVC(kernel='linear', C=0.1,gamma=1, random_state=42, probability=True)
#for_classification_report
results = []
names = []

for score in ["roc_auc", "f1", "precision", "recall", "accuracy"]:
   cvs = cross_val_score(clf, X, y, scoring=score, cv=5).mean()
   print(score + " : "+ str(cvs))
   print('\n')

clf.fit(X_train, y_train) 
y_pred = clf.predict(X_test)
balanced_accuracy_score(y_test, y_pred)

#ROC_curve_before_RFE
X = X.to_numpy()
y=y.to_numpy()
# #############################################################################
# Run classifier with cross-validation and plot ROC curves
cv = StratifiedKFold(n_splits=5)
tprs = []
aucs = []
mean_fpr = np.linspace(0, 1, 100)

fig, ax = plt.subplots()
for i, (train, test) in enumerate(cv.split(X, y)):
    clf.fit(X[train], y[train])
    viz = plot_roc_curve(clf, X[test], y[test],
                         name='ROC fold {}'.format(i),
                         alpha=0.3, lw=1, ax=ax)
    interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
    interp_tpr[0] = 0.0
    tprs.append(interp_tpr)
    aucs.append(viz.roc_auc)

ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
        label='Chance', alpha=.8)

mean_tpr = np.mean(tprs, axis=0)
mean_tpr[-1] = 1.0
mean_auc = auc(mean_fpr, mean_tpr)
std_auc = np.std(aucs)
ax.plot(mean_fpr, mean_tpr, color='b',
        label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
        lw=2, alpha=.8)

std_tpr = np.std(tprs, axis=0)
tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                label=r'$\pm$ 1 std. dev.')

ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05],
       title="Receiver operating ")
ax.legend(loc="lower right")
plt.show()
#feature_selection_REF

#choose_the_optimal_number
Model= SVC(kernel='linear', random_state=42, probability=True)
rfecv = RFECV(estimator=Model, step=1,cv=StratifiedKFold(5),scoring='accuracy')
rfetrain=rfecv.fit(X_train, y_train)
print('Optimal number of features :', rfecv.n_features_)
min_features_to_select = 1
print('Optimal number of features :', rfecv.n_features_)
n_scores = len(rfecv.cv_results_["mean_test_score"])
plt.figure()
plt.xlabel("Number of features selected")
plt.ylabel("Mean test accuracy")
plt.errorbar(
    range(min_features_to_select, n_scores + min_features_to_select),
    rfecv.cv_results_["mean_test_score"],color="#00FFFF")
plt.title("Recursive Feature Elimination \nwith correlated features")
plt.figtext(.6, .6, "Optimal number of features=25")
plt.show()
#Apply_the_model_with_the_selected_features
rfe = RFE(estimator=Model, n_features_to_select=rfecv.n_features_, step=1)
rfe = rfe.fit(X_train, y_train)
rfe_train=X_train.loc[:, rfe.get_support()]
rfe_test=X_test.loc[:, rfe.get_support()]
rfe_data=X.loc[:, rfe.get_support()]
# Checking the Accuracy after rfe
#classification_report
results = []
names = []

for score in ["roc_auc", "f1", "precision", "recall", "accuracy"]:
   cvs = cross_val_score(clf, rfe_data, y, scoring=score, cv=5).mean()*100
   print(score + " : "+ str(cvs))
   print('\n')

clf.fit(rfe_train, y_train)
y_pred = clf.predict(rfe_test)
balanced_accuracy_score(y_test, y_pred)

#roc_curve_After_feature_selection 
rfe_data=rfe_data.to_numpy()
y=y.to_numpy()
# Run classifier with cross-validation and plot ROC curves
cv = StratifiedKFold(n_splits=5)
tprs = []
aucs = []
mean_fpr = np.linspace(0, 1, 100)

fig, ax = plt.subplots()
for i, (train, test) in enumerate(cv.split(rfe_data, y)):
    clf.fit(rfe_data[train], y[train])
    viz = plot_roc_curve(clf, rfe_data[test], y[test],
                         name='ROC fold {}'.format(i),
                         alpha=0.3, lw=1, ax=ax)
    interp_tpr = np.interp(mean_fpr, viz.fpr, viz.tpr)
    interp_tpr[0] = 0.0
    tprs.append(interp_tpr)
    aucs.append(viz.roc_auc)

ax.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r',
        label='Chance', alpha=.8)

mean_tpr = np.mean(tprs, axis=0)
mean_tpr[-1] = 1.0
mean_auc = auc(mean_fpr, mean_tpr)
std_auc = np.std(aucs)
ax.plot(mean_fpr, mean_tpr, color='b',
        label=r'Mean ROC (AUC = %0.2f $\pm$ %0.2f)' % (mean_auc, std_auc),
        lw=2, alpha=.8)

std_tpr = np.std(tprs, axis=0)
tprs_upper = np.minimum(mean_tpr + std_tpr, 1)
tprs_lower = np.maximum(mean_tpr - std_tpr, 0)
ax.fill_between(mean_fpr, tprs_lower, tprs_upper, color='grey', alpha=.2,
                label=r'$\pm$ 1 std. dev.')

ax.set(xlim=[-0.05, 1.05], ylim=[-0.05, 1.05],
       title="Receiver operating ")
ax.legend(loc="lower right")
plt.show()
rfe_train.to_csv("feature.csv")

