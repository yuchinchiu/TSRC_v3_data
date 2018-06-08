# -*- coding: utf-8 -*-
"""

@author: yc180

Ideally, participants will submit data to our server right after run_task_v1.html.
However, sometimes that did not happen and data are transferred back to the Main.html and then submitted to AMT server.
In that case, data shows up in the csv file for each batch.
Thus, this function/script is to salvage those data.
The script cross reference existing log/txt and data in the csv.
If data in the csv is not in the log/txt folder, then output log/txt files.

"""

def extractDataFromCSV(dataDir, csvDir):
    
    from glob import glob
    import pandas as pd
    import numpy as np
    
    csvList = glob(csvDir  + '*.csv')
    txtList = glob(dataDir + '*.txt')
    existingId=['']  # using pd.Series.str.match require at least one element, so create an empty subjId
    
    
    for f in range(0,len(txtList),1):
        sbjInfo=np.genfromtxt(txtList[f], delimiter=":", dtype=str)
        sbjInfo=pd.DataFrame(np.transpose(sbjInfo))
        sbjInfo.columns = sbjInfo.iloc[0]
        sbjInfo.drop([0],axis=0,inplace=True)
        sbjInfo.reset_index(drop=True,inplace=True)
        existingId.append(sbjInfo.loc[0,'workerId'])
    
    existingId = pd.Series(existingId) # in order to use str match method
    SCNT=0
    for f in range(0,len(csvList),1):
        df = pd.read_csv(csvList[f])
        for S in range(0,len(df),1):        
            SCNT=SCNT+1
            a = 'Answer.RTs' in df.columns
            if a:
                RT = str(df.loc[S,'Answer.RTs'])
                if RT!='nan':
                    #  print('contain data, check if already-exist or not...')
                    wkid = str(df.loc[S,'WorkerId'])
                    if sum(existingId.str.match(wkid))==0: # no existing txt/log
                        fileName = dataDir + df.loc[S,'AssignmentId'] + '.log'
                        with open(fileName, "w") as log_file:
                            log_file.write("%s" % RT)       
                            # need to print a txt file as well
                            sbjInfo['confirmation number']=''  #
                            sbjInfo['workerId']= wkid
                            sbjInfo['assignmentId']= df.loc[S,'AssignmentId']                    
                            sbjInfo['age']=''
                            sbjInfo['gender']=''
                            sbjInfo['ethnicity']=''
                            sbjInfo['race']=''                
                            fileName = dataDir + df.loc[S,'AssignmentId'] + '.txt'
                            with open(fileName, "w") as text_file:
                                for r in sbjInfo.columns:   
                                    string1 = r + ":"
                                    text_file.write("%s" % string1)
                                    if r=='Finish':
                                        text_file.write("%s" % sbjInfo.loc[0,r])
                                    else:
                                        text_file.write("%s\n" % sbjInfo.loc[0,r])

                    else:
                        print('log/txt already exist. No output file.')
            else:
                print('no data in csv')


