# DA203-O Course Project
# Authors: Shreyas M (shreyasm@iisc.ac.in) and Mithun TM (mithunt@iisc.ac.in)

# The following code to create a dataframe and remove duplicated rows is always executed and acts as a preamble for your script: 

# dataset = pandas.DataFrame(WEEK_START, Overall Conversion, Search Sessions %, HL Conversion, HM Conversion, SM Conversion, LM Conversion, MC Conversion, CP Conversion, PO Conversion, Logged-in user %)
# dataset = dataset.drop_duplicates()

# Paste or type your script code here:
# Library Imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import matplotlib.ticker as mtick


# Python Class
class RCA():
    def __init__(self, dataframe, week_start, target_metrics, metrics, dependecy_dict):
        '''The __init__() method initialises the variables which are passed when instantiating the class; 
        these variables can be used by the different methods which are within the class scope'''
        self.dependecy_dict = dependecy_dict
        self.week_start = week_start
        self.metrics = metrics
        self.dataframe = dataframe
        self.target_metrics = target_metrics
        self.importances = {}
        self.isAnomaly = {}
    
    def findAnomalousWeeks(self,metric):
        '''Calculates if a metric is anomalous by comparing its trend across previous weeks.
        Uses mean - standard deviation and mean + standard dev to identify anomalies. 
        These thresholds are used based on the criticality of the business metrics, and 
        variations within one standard deviation are required to be examined.'''
        mean = np.mean(self.dataframe[self.dataframe['week_start']<self.week_start][metric])
        stddev = np.sqrt(np.var(self.dataframe[self.dataframe['week_start']<self.week_start][metric]))
        self.dataframe['isOutlier_' + metric] = self.dataframe[metric].apply(lambda x : 1 if x<= mean - 1*stddev or x>= mean + 1*stddev else 0)

    def getAnomalies(self) :
        '''Calls findAnmalousWeeks() method for each of the metrics in the data frame. 
        This would identify if any of the metrics in the data frame is anomalous or not using the mean 
        and standard deviation of that metric in the previous weeks. '''
        for metric in self.metrics:
                self.findAnomalousWeeks(metric)    

    def findFeatureImportance(self, dependentMetric, independentMetrics, dataframe):
        '''For each dependent metric, find the feature importances of the independent metrics using a random forest regressor.'''
        importanceModel = RandomForestRegressor()
        importanceModel.fit(dataframe[independentMetrics], dataframe[dependentMetric])
        importances = dict(zip(independentMetrics,importanceModel.feature_importances_))
        self.importances[dependentMetric] = dict(sorted(importances.items(), key=lambda item: item[1],reverse = True))
        
    def getFeatureImportances(self):
        '''For each dependent metric, find the feature importances of the independent metrics using a random forest regressor.'''
        df = self.dataframe
        for metric in self.target_metrics:                
            if(len(df[(df['week_start'] == self.week_start) & (df['isOutlier_' + metric] ==1)]) == 1):
                print("Metric ", metric, " is anomalous, exploring the anomalous nature of the dependent metrics")
                self.isAnomaly[metric] = 1
                self.findFeatureImportance(metric, self.dependecy_dict[metric], df[df['week_start']<self.week_start])
            else :
                self.isAnomaly[metric] = 0
                self.findFeatureImportance(metric, self.dependecy_dict[metric], df[df['week_start']<self.week_start])
                    
                    
    def isImportantFeaturesAnomalous(self):
        '''For each of the independent features associated with a dependent metric, 
        find if the independent feature was anomalous using getAnomalies() method.'''
        for key1, val1 in self.importances.items():
            for key2, val2 in val1.items():
                df = self.dataframe
                if(len(df[(df['week_start'] == self.week_start) & (df['isOutlier_' + key2]==1)]) ==1):
                    result = " is anomalous"
                    self.isAnomaly[key2] = 1
                    
                else :
                    result = " is not anomalous"
                    self.isAnomaly[key2] = 0
                print("Metric ",key2," with feature importance ", round(val2*100,2),'%', result)
                
    def plot(self):
        '''A chart is plotted with the title displaying the dependent metric’s anomalous nature along with 
        the feature importance and anomalous nature of the independent metrics. 
        This plot is later rendered on a Power BI dashboard.'''
        for metric in self.target_metrics:
            importances = rca1.importances[metric]
            # print(importances)
            
            anomoly_dict = rca1.isAnomaly.copy()
            anomoly_dict.pop('Overall Conversion')
            keys_list = list(anomoly_dict)
            anomoly_dict_filtered = dict(filter(lambda elem: elem[1] == 1, anomoly_dict.items()))
            indices = [keys_list.index(i) for i in anomoly_dict_filtered]

            plt.figure(figsize=(5,5))

            plot_var = plt.bar(list(importances.keys()),list(importances.values()))
            for j in indices:
                plot_var[j].set_color('r')
            plt.xticks(rotation = 90)
            is_anomaly = metric + " " + "is anomalous" if self.isAnomaly[metric]==1 else metric + " " + "is not anomalous"
            plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))

            plt.tight_layout(rect=[0,0,1,0.9])
            plt.title(is_anomaly)
            plt.show()


# Function Calls: 
df = dataset.copy()
cols = list(df.columns)
cols.remove("week_start")
selected_week = df['week_start'].max()
df['pivots'] = 'pivot'


dependentCols =  ['Search Sessions %',
 'HL Conversion',
 'HM Conversion',
 'SM Conversion',
 'LM Conversion',
 'MC Conversion',
 'CP Conversion',
 'PO Conversion',
 'Logged-in user %']

rca1 = RCA(df,selected_week, ["Overall Conversion"], cols, {'Overall Conversion':dependentCols})

rca1.getAnomalies()

rca1.getFeatureImportances()
rca1.isImportantFeaturesAnomalous()
rca1.plot()