import pandas as pd
import re




def dwellRegressionOnRelevantElements(dwells,grouper):

   
    #keep only dwells on relevant Elements
    dwells = dwells[dwells.apply(lambda x: x["element_"] in x["Relevant elements names"], axis=1)]
    
    #compute revisits
    dwells = dwells.groupby(['participant','currentQuestion','tabName','element_']+grouper,as_index=False).agg(visits=('id','count'))
    #calculate revisits
    dwells["revisits"] = dwells["visits"]-1    
    

    return dwells

def timeInterval(x):
    return x.iloc[-1]-x.iloc[0]

def periodCalculation(allData):
    
    #goup by participant, currentQuestion and Typ1, Type2 and Type3, Phase
    #Grouping by currentQuestion allows us to compute timeInterval() by substracting the last timestamp for the question from the first one
    #Grouping by 'Type1','Type2','Type3', Phase is done just to keep track of these attributes for further grouping. The grouping by questionID is already at the most fine-grained question level
    allData = allData.groupby(['currentQuestion','participant','Type1','Type2','Type3','Phase'],as_index=False).agg(timeInterval=('Timestamp', timeInterval))

    return allData

def scanPathPrecision(allData,grouper):


    #label fixations on relevant Elements
    allData["relevant"] = allData.apply(lambda x: 1 if x["element"] in x["Relevant elements names"] else 0, axis=1)
    
    allData = allData.groupby(['participant','currentQuestion']+grouper, as_index=False).agg(scan_path_precision=('relevant','mean'),timeInterval=('Timestamp', timeInterval),timestamp=('timestamp_formatted', 'first') )
    
    return allData


def averageFixationDuration(fixationData,grouper):
    return fixationData.groupby(['participant','currentQuestion']+grouper, as_index=False).agg(Average_Fixation_Duration=('Fixation Duration','mean'),timestamp=('timestamp_formatted', 'first'))

def averageSaccadeAmplitudeForPhases(phases,data,grouper):
    
    phases["RelAttrMerge"] = phases['participant'].astype(str) +";"+phases['currentQuestion'].astype(str) +";"+phases['Timestamp'].astype(str)
    return phases.groupby(grouper,as_index=False).agg(avSaccadeAmplitude=('RelAttrMerge', (lambda x: asaIntimeInterval(x,data))),timestamp=('timestamp_formatted', 'first'))



def asaIntimeInterval(x,data):
    
    #print("--------------")

    #extracing relevant attributes
    participant = x.iloc[0].split(";")[0]
    currentQuestion = int(x.iloc[0].split(";")[1])
    
    startTime = float(x.iloc[0].split(";")[2])
    endTime = float(x.iloc[-1].split(";")[2])
    
    #print(participant,currentQuestion,startTime,endTime)
    
    #select all saccades between startTime and EndTime for specific participant and task
    saccadeData = data.loc[(data['participant']==participant) & (data['currentQuestion']==currentQuestion)  & (data['Timestamp']>=startTime) & (data['Timestamp']<endTime)].copy(deep=True)
      
    #return average saccade amplitude
    return saccadeData['Saccade Amplitude'].mean()





def fixationProportionThresholdAnalysis(allData,grouper):


    #groupby participant, currentQuestion and grouper
    fixationData = allData.groupby(['participant','currentQuestion']+grouper, as_index=False).agg(
        shortFixationsProp=('Fixation Duration',lambda x: ((x <= 250)*1).sum()/x.count()),
        longFixationsProp=('Fixation Duration',lambda x: ((x > 500)*1).sum()/x.count()),
        timestamp=('timestamp_formatted', 'first')
    )
   

    return fixationData


#Test: OK
def phaseDetection(fixationData,questions):
   
    #keep only local or global tasks
    #fixationData = fixationData.loc[fixationData['Type1']==level]
    #label relevent elements
    fixationData["relevant"] = fixationData.apply(lambda x: 1 if x["element"] in x["Relevant elements names"] else 0, axis=1)
    
    
    out = None
    for participant in fixationData["participant"].unique():
        for task in fixationData["currentQuestion"].unique():
            
            #print("------")
            #print(participant)
            #print(task)
            
            #inits  
            endOfPhase1 = -1 #End of Phase 1 denotes the time when the participant locates the first relevant activity 
            endOfPhase2 = -1 #End of Phase 2 denotes the time wehn the participant locates all relevant activity
            
            #get question ids
            keys = [item['id'] for item in questions]
            new_dict = dict(zip(keys, questions)) 
            
            #dict with key=element, value=0
            checks = { element:0 for element in new_dict[task]["Relevant elements names"]}
            
            #print(checks)
            
            #select participant and task data
            rData = fixationData.loc[(fixationData['participant']==participant) &  (fixationData['currentQuestion']==task)].copy(deep=True)
            #reset index
            rData = rData.reset_index(drop=True)
            
            
            #find index of end of Phase 1 (if the participants ever finds the first relevant activity)
            endOfPhase1 = rData.index[rData['relevant'] == 1].tolist()[0] if len(rData.index[rData['relevant'] == 1].tolist())>0 else -1
            
            #print("endOfPhase1",endOfPhase1)
        
            #if end of Phase 1 detected
            if endOfPhase1!=-1:
                
                #set fixated element as checked
                checks[rData.iloc[endOfPhase1]['element']] = 1
                
                #print("checked updated (1)",checks)
                
                for i,(index,row) in enumerate(rData.iterrows()):
                    # skip rows before endOfPhase1
                    if i < endOfPhase1: 
                        continue 
                    # check if row['relevant']== 1 i.e., a relevant element was fixated 
                    if row['relevant']==1:
                        if checks[row['element']]==0:
                            # set checks[row['element']]=1 if not already set to 1
                            checks[row['element']] = 1
                            
                            #print("checked updated (2)",checks)
                    
                    # check if all relevant elements were fixated
                    if all(value == 1 for value in checks.values()):
                        #if so set endOfPhase2
                        endOfPhase2 = index
                        #print("all relevant elements fixated")
                        #print(f'endOfPhase2: {endOfPhase2}')
                        break
                
            #the phases are reduced to search and inference but could be more detailed    
            rData["Phase"] = rData.apply(lambda x: "N/A" if endOfPhase1== -1 or endOfPhase2== -1
                                         #x: 99999 if endOfPhase1== -1 or endOfPhase2== -1 
                                         #else 1 if x.name<endOfPhase1  
                                         #else 2 if x.name<endOfPhase2
                                         #else 3
                                         else "search" if x.name<endOfPhase2
                                         else "inference"
                                         ,axis=1)
            
            out = pd.concat([out,rData],axis=0)
            
    out = out.reset_index(drop=True)
    return out    


def addQuestionInfo(allData,questions):
    
    #change the type of questionID to integer
    allData['currentQuestion'] = allData['currentQuestion'].astype('int')
    
    #extend the columns of questionnaireData with those in DataFrame(questions) based the common question ID
    allData = allData.merge(pd.DataFrame(questions), left_on=['currentQuestion'], right_on=['id'])
    
    return allData

