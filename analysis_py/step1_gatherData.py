# -*- coding: utf-8 -*-
"""
Created on 5/16/2018
V3 contains 1 Repetition of the task-switching task but differ from V1 as there are trialwise feedback during the entire experiment

@author: yc180

This script go through all the log/txt in the folder and extract data to build a "group" DataFrame for later analysis
The output are two files: gpData.pkl & gpSbjInfo.pkl

"""
#%% 
import os
import glob
import pandas as pd
import numpy as np
from copy import copy
#from extractData import extractDataFromCSV

#workingDir = os.path.dirname(os.path.realpath(__file__))
workingDir = "C:\\Users\\yc180\\Documents\\YCCProjects\\TSRC_v3_data\\analysis_py"
os.chdir("..")
# go up one level to the experiment directory

dataDir = os.getcwd() + os.sep + 'data' + os.sep + 'v3_batches' + os.sep  # where the log/txt files are located
csvDir  = os.getcwd() + os.sep + 'data' + os.sep + 'v3_csv' + os.sep

# run the following function to extract missing data from CSV files

#extractDataFromCSV(dataDir, csvDir)


fileList     = glob.glob(dataDir +  "*.log")
infofileList = glob.glob(dataDir +  "*.txt")


gpSbjInfo=pd.DataFrame()

# From trialGen.js outputData function
# output = [this.runId, this.phase, this.stim, this.stimCat, this.task, this.trialType, this.respComp, this.memCond, this.response, this.sbjResp, this.sbjACC, this.sbjRT];
#%% 

colNames=['runId','phase','stim','stimCat','task','trialType','respComp','memCond','response','sbjResp','sbjACC','sbjRT']
gpData = pd.DataFrame(np.empty((0,len(colNames)),dtype=int), columns=colNames)
SCNT=0

for f in range(0,len(fileList),1):
    SCNT=SCNT+1
    D=np.genfromtxt(fileList[f],delimiter=',',dtype=int)
    D=pd.DataFrame(np.transpose(np.reshape(D,(len(colNames),int(D.shape[0]/len(colNames))))),columns=colNames)
    D['sbjId']=SCNT
    
    txtFileName = fileList[f][:-3]+ "txt"
    # read in the corresponding text file and extract SRmapping, etc
    sbjInfo=np.genfromtxt(txtFileName, delimiter=":", dtype=str)
    sbjInfo=pd.DataFrame(np.transpose(sbjInfo))
    sbjInfo.columns = sbjInfo.iloc[0]
    sbjInfo.drop([0],axis=0,inplace=True)    
    # 0 was the index that become header, hasn't reset index, so taking 1
    sbjInfo['sbjId']=SCNT
    sbjInfo.index = sbjInfo.sbjId
    sbjInfo.drop('sbjId',axis=1,inplace=True)
    # 
    D['task1ACC']=0;
    D['stimUnique'] = (D.stimCat*100 + D.stim).astype(int)
    for stimId in D.loc[D.phase==1,'stimUnique'].unique():
        # As there are 2 repetitions, there are two rows... so get MEAN to get the single task id
        D.loc[(D.stimUnique==stimId) & (D.phase==3),'task']     = int(D.loc[(D.stimUnique==stimId) & (D.phase==1),'task'].mean())  # not sure why without int(), it didn't work..       
        D.loc[(D.stimUnique==stimId) & (D.phase==3),'task1ACC'] = int(D.loc[(D.stimUnique==stimId) & (D.phase==1),'sbjACC'].mean())  # not sure why without int(), it didn't work..



    # Replace the 'new' item's respComp condition according to the SRmapping and stimCat,so that calculating FA can be more specific about the stimCat/respComp conditions
    for stimId in D.loc[(D.phase==3) & (D.memCond==5),'stimUnique'].unique():
        newItem_cat = int(D.loc[(D.phase==3) & (D.stimUnique==stimId),'stimCat'])
        stimCat_respComp = int(D.loc[(D.phase==1) & (D.stimCat==newItem_cat),'respComp'].mean())
        D.loc[(D.phase==3) & (D.stimUnique==stimId),'respComp'] = stimCat_respComp
        
    gpSbjInfo = pd.concat([gpSbjInfo,sbjInfo],axis=0)    
    gpData=pd.concat([gpData,D],axis=0)
    
    
#%%
gpData['sbjResp_mem']=copy(gpData['sbjResp'])  # allow sbjResp to have confidence rating info 1(def-new) to 4 (def-old)
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==4),'sbjResp_mem']='defOld'
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==3),'sbjResp_mem']='probOld'
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==2),'sbjResp_mem']='probNew'
gpData.loc[(gpData.phase==3) & (gpData.sbjResp_mem==1),'sbjResp_mem']='defNew'

# no response trials
gpData.loc[gpData.sbjResp==99,'sbjACC'] = 0  
gpData.loc[gpData.sbjResp==99,'sbjRT'] = np.nan
# accuracy for memory task , default accuracy is 0
gpData.loc[(gpData.phase==3) & (gpData.sbjResp>=3) & (gpData.memCond<=4),'sbjACC']=1
gpData.loc[(gpData.phase==3) & (gpData.sbjResp<=2) & (gpData.memCond==5),'sbjACC']=1




# convert codings to categorical variables with meaningful names
gpData['Repetition'] = copy(gpData['runId']) # convert runId into repetition for TaskSw phase
gpData.loc[gpData.runId>=4,'Repetition']=np.nan
gpData.Repetition.replace(0,'Rep1',inplace=True)
gpData.Repetition.replace(1,'Rep1',inplace=True)
gpData.Repetition.replace(2,'Rep2',inplace=True)
gpData.Repetition.replace(3,'Rep2',inplace=True)

# create a new label as old vs. new item for Memory task
gpData['oldNew'] = copy(gpData['response']) 
gpData.oldNew.replace(0,'New', inplace=True)
gpData.oldNew.replace(1,'Old', inplace=True)
gpData.loc[gpData.phase<=2,'oldNew']=np.nan

# preserve the 1,2 task numbering
gpData['taskNum']    = copy(gpData['task'])  

gpData.phase.replace(1,'TaskSw', inplace=True)
gpData.phase.replace(2,'Filler', inplace=True)
gpData.phase.replace(3,'Mem', inplace=True)
gpData.task.replace(1,'animacy', inplace=True)
gpData.task.replace(2,'size', inplace=True)
gpData.trialType.replace(0,'repeat', inplace=True)
gpData.trialType.replace(1,'switch', inplace=True)
gpData.respComp.replace(0,'RC', inplace=True)
gpData.respComp.replace(1,'RIC', inplace=True)

gpData.memCond.replace(1,'old-switch-RIC', inplace=True)
gpData.memCond.replace(2,'old-switch-RC', inplace=True)
gpData.memCond.replace(3,'old-repeat-RIC', inplace=True)
gpData.memCond.replace(4,'old-repeat-RC', inplace=True)
gpData.memCond.replace(5,'new', inplace=True)

gpData.stimCat.replace(1,'Liv-Lg', inplace=True)
gpData.stimCat.replace(2,'Liv-Sm', inplace=True)
gpData.stimCat.replace(3,'NLiv-Lg', inplace=True)
gpData.stimCat.replace(4,'NLiv-Sm', inplace=True)




gpData['respComp']    = pd.Categorical(gpData.respComp, categories=['RC','RIC'], ordered=True)
gpData['memCond']     = pd.Categorical(gpData.memCond, categories=['old-switch-RIC','old-switch-RC','old-repeat-RIC','old-repeat-RC','new'], ordered=True)
gpData['trialType']   = pd.Categorical(gpData.trialType, categories=['switch','repeat'], ordered=True)
gpData['sbjResp_mem'] = pd.Categorical(gpData.sbjResp_mem, categories=['defOld','probOld','probNew','defNew'], ordered=True)
gpData['stimCat']     = pd.Categorical(gpData.stimCat, categories=['Liv-Lg','Liv-Sm','NLiv-Lg','NLiv-Sm'], ordered=True)
gpData['Repetition']  = pd.Categorical(gpData.Repetition, categories=['Rep1','Rep2'], ordered=True)


gpData.reset_index(inplace=True)

#
#%% do a fist pass to exclude subjects with low cued task accuracy
#totalSCNT = len(np.unique(gpData.sbjId))
#goodSbj=[]
#excludeSbj=[]
#for S in np.unique(gpData.sbjId):
#    D = gpData.loc[gpData.sbjId==S]    
#    if D[D.phase=='TaskSw'].sbjACC.mean()*100 > 65:
#        goodSbj.append(S)
#    else:
#        excludeSbj.append(S)
#
#for S in excludeSbj:
#    gpData.drop(gpData[gpData.sbjId==S].index, axis=0, inplace=True)
#%% #%% 

totalSCNT = len(np.unique(gpData.sbjId))
# output DataFrame
os.chdir(workingDir)  # scripts directory
gpData.to_pickle('gpData.pkl')
gpSbjInfo.to_pickle('gpSbjInfo.pkl')
gpData.to_csv('gpData.csv',encoding='utf-8', index=False)
gpSbjInfo.to_csv('gpSbjInfo.csv',encoding='utf-8', index=False)

print(SCNT)