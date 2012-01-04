#####################################################
# $HeadURL: svn+ssh://svn.cern.ch/reps/dirac/ILCDIRAC/trunk/ILCDIRAC/Workflow/Modules/ModuleBase.py $
#####################################################
""" ModuleBase - base class for ILC workflow modules. 
Stolen by S. Poss from LHCbSystem.Workflow.Modules

"""

__RCSID__ = "$Id: ModuleBase.py 45427 2011-11-25 08:29:02Z sposs $"

from DIRAC  import S_OK, S_ERROR, gLogger, gConfig
from DIRAC.DataManagementSystem.Client.ReplicaManager import ReplicaManager
from DIRAC.Core.DISET.RPCClient import RPCClient
from DIRAC.RequestManagementSystem.Client.DISETSubRequest import DISETSubRequest
from DIRAC.Core.Security.ProxyInfo import getProxyInfoAsString
from DIRAC.Resources.Catalog.PoolXMLFile import getGUID
from DIRAC.Core.Utilities.Adler import fileAdler
from DIRAC.TransformationSystem.Client.FileReport import FileReport
from DIRAC.Core.Utilities.File import makeGuid
import DIRAC
import os,string,sys,re

class ModuleBase(object):

  #############################################################################
  def __init__(self):
    """ Initialization of module base.
    """
    self.log = gLogger.getSubLogger('ModuleBase')
    # FIXME: do we need to do this for every module?
    result = getProxyInfoAsString()
    if not result['OK']:
      self.log.error('Could not obtain proxy information in module environment with message:\n', result['Message'])
    else:
      self.log.info('Payload proxy information:\n', result['Value'])

    self.systemConfig = ''
    self.applicationLog = ''
    self.applicationVersion=''
    self.applicationName = ''
    self.InputData = ''
    self.SteeringFile = ''
    self.energy = 0
    self.NumberOfEvents = 0
    self.result = S_ERROR()
    self.InputFile = ''
    self.ignoremissingInput = False
    self.OutputFile = ''
    self.jobType = ''
    self.stdError = ''
    self.debug = False
    self.jobID = None
    if os.environ.has_key('JOBID'):
      self.jobID = os.environ['JOBID']
    self.eventstring = ''
    self.ignoreapperrors = False

  #############################################################################
  def setApplicationStatus(self,status, sendFlag=True):
    """Wraps around setJobApplicationStatus of state update client
    """
    if not self.jobID:
      return S_OK('JobID not defined') # e.g. running locally prior to submission

    self.log.verbose('setJobApplicationStatus(%s,%s)' %(self.jobID,status))

    if self.workflow_commons.has_key('JobReport'):
      self.jobReport  = self.workflow_commons['JobReport']

    if not self.jobReport:
      return S_OK('No reporting tool given')
    jobStatus = self.jobReport.setApplicationStatus(status,sendFlag)
    if not jobStatus['OK']:
      self.log.warn(jobStatus['Message'])

    return jobStatus

  #############################################################################
  def sendStoredStatusInfo(self):
    """Wraps around sendStoredStatusInfo of state update client
    """
    if not self.jobID:
      return S_OK('JobID not defined') # e.g. running locally prior to submission

    if self.workflow_commons.has_key('JobReport'):
      self.jobReport  = self.workflow_commons['JobReport']

    if not self.jobReport:
      return S_OK('No reporting tool given')

    sendStatus = self.jobReport.sendStoredStatusInfo()
    if not sendStatus['OK']:
      self.log.error(sendStatus['Message'])

    return sendStatus

  #############################################################################
  def setJobParameter(self,name,value, sendFlag = True):
    """Wraps around setJobParameter of state update client
    @param name: job parameter 
    @param value: value of the job parameter
    @param sendFlag: passed to setJobParameter
    @return: S_OK(), S_ERROR()
    """
    if not self.jobID:
      return S_OK('JobID not defined') # e.g. running locally prior to submission

    self.log.verbose('setJobParameter(%s,%s,%s)' %(self.jobID,name,value))

    if self.workflow_commons.has_key('JobReport'):
      self.jobReport  = self.workflow_commons['JobReport']

    if not self.jobReport:
      return S_OK('No reporting tool given')
    jobParam = self.jobReport.setJobParameter(str(name),str(value),sendFlag)
    if not jobParam['OK']:
      self.log.warn(jobParam['Message'])

    return jobParam

  #############################################################################
  def sendStoredJobParameters(self):
    """Wraps around sendStoredJobParameters of state update client
    """
    if not self.jobID:
      return S_OK('JobID not defined') # e.g. running locally prior to submission

    if self.workflow_commons.has_key('JobReport'):
      self.jobReport  = self.workflow_commons['JobReport']

    if not self.jobReport:
      return S_OK('No reporting tool given')

    sendStatus = self.jobReport.sendStoredJobParameters()
    if not sendStatus['OK']:
      self.log.error(sendStatus['Message'])

    return sendStatus

  #############################################################################
  def setFileStatus(self,production,lfn,status):
    """ Set the file status for the given production in the Production Database
    
    @param production: production ID
    @param lfn: logical file name of the file that needs status change
    @param status: status to set
    @return: S_OK(), S_ERROR()
    """
    self.log.verbose('setFileStatus(%s,%s,%s)' %(production,lfn,status))

    if not self.workflow_commons.has_key('FileReport'):
      fileReport =  FileReport('Transformation/TransformationManager')
      self.workflow_commons['FileReport'] = fileReport

    fileReport = self.workflow_commons['FileReport']
    result = fileReport.setFileStatus(production,lfn,status)
    if not result['OK']:
      self.log.warn(result['Message'])

    self.workflow_commons['FileReport']=fileReport

    return result

  #############################################################################
  def setReplicaProblematic(self,lfn,se,pfn='',reason='Access failure'):
    """ Set replica status to Problematic in the File Catalog
    @param lfn: lfn of the problematic file
    @param se: storage element
    @param pfn: physical file name
    @param reason: as name suggests...
    @return: S_OK()
    """

    rm = ReplicaManager()
    source = "Job %d at %s" % (self.jobID,DIRAC.siteName())
    result = rm.setReplicaProblematic((lfn,pfn,se,reason),source)
    if not result['OK'] or result['Value']['Failed']:
      # We have failed the report, let's attempt the Integrity DB faiover
      integrityDB = RPCClient('DataManagement/DataIntegrity',timeout=120)
      fileMetadata = {'Prognosis':reason,'LFN':lfn,'PFN':pfn,'StorageElement':se}
      result = integrityDB.insertProblematic(source,fileMetadata)
      if not result['OK']:
        # Add it to the request
        if self.workflow_commons.has_key('Request'):
          request  = self.workflow_commons['Request']
          subrequest = DISETSubRequest(result['rpcStub']).getDictionary()
          request.addSubRequest(subrequest,'integrity')

    return S_OK()

  #############################################################################
  def getCandidateFiles(self,outputList,outputLFNs,fileMask):
    """ Returns list of candidate files to upload, check if some outputs are missing.
        
      @param outputList: has the following structure:
      [ ('outputDataType':'','outputDataSE':'','outputDataName':'') , (...) ] 
          
      @param outputLFNs: list of output LFNs for the job
        
      @param fileMask:  output file extensions to restrict the outputs to
        
      @return: dictionary containing type, SE and LFN for files restricted by mask
    """
    fileInfo = {}
    for outputFile in outputList:
      if outputFile.has_key('outputFile') and outputFile.has_key('outputDataSE') and outputFile.has_key('outputPath'):
        fname = outputFile['outputFile']
        fileSE = outputFile['outputDataSE']
        filePath= outputFile['outputPath']
        fileInfo[fname] = {'path':filePath,'workflowSE':fileSE}
      else:
        self.log.error('Ignoring malformed output data specification',str(outputFile))

    for lfn in outputLFNs:
      if os.path.basename(lfn) in fileInfo.keys():
        fileInfo[os.path.basename(lfn)]['lfn']=lfn
        self.log.verbose('Found LFN %s for file %s' %(lfn,os.path.basename(lfn)))
        if len(os.path.basename(lfn))>127:
          self.log.error('Your file name is WAAAY too long for the FileCatalog. Cannot proceed to upload.')
          return S_ERROR('Filename too long')
        if len(lfn)>256+127:
          self.log.error('Your LFN is WAAAAY too long for the FileCatalog. Cannot proceed to upload.')
          return S_ERROR('LFN too long')
        
    #Check that the list of output files were produced
    for fileName,metadata in fileInfo.items():
      if not os.path.exists(fileName):
        self.log.error('Output data file %s does not exist locally' %fileName)
        if not self.ignoreapperrors:
          return S_ERROR('Output Data Not Found')
        del fileInfo[fileName]
    #Check the list of files against the output file mask (if it exists)
    #candidateFiles = {}
    #if fileMask:
      ##nothing to do yet, as FileMask is not used
      #for fileName,metadata in fileInfo.items():
      #  if metadata['type'].lower() in fileMask or fileName.split('.')[-1] in fileMask:
      #    candidateFiles[fileName]=metadata
      #  else:
      #    self.log.info('Output file %s was produced but will not be treated (outputDataFileMask is %s)' %(fileName,string.join(self.outputDataFileMask,', ')))

      #if not candidateFiles.keys():
      #  return S_OK({}) #nothing to do
    #  candidateFiles = fileInfo
    #else:
      #do not apply mask to files
      
    candidateFiles = fileInfo
    #Sanity check all final candidate metadata keys are present (return S_ERROR if not)
    mandatoryKeys = ['path','workflowSE','lfn'] #filedict is used for requests
    for fileName,metadata in candidateFiles.items():
      for key in mandatoryKeys:
        if not metadata.has_key(key):
          return S_ERROR('File %s has missing %s' %(fileName,key))
    
    return S_OK(candidateFiles)  

  #############################################################################
  def getFileMetadata(self,candidateFiles):
    """Returns the candidate file dictionary with associated metadata.
    
    @param candidateFiles: The input candidate files dictionary has the structure:
    {'lfn':'','path':'','workflowSE':''}
       
    This also assumes the files are in the current working directory.
    @return: File Metadata
    """
    #Retrieve the POOL File GUID(s) for any final output files
    self.log.info('Will search for POOL GUIDs for: %s' %(string.join(candidateFiles.keys(),', ')))
    pfnGUIDs = {}
    generated = []
    for fname in candidateFiles.keys():
      guid = makeGuid(fname)
      pfnGUIDs[fname]=guid
      generated.append(fname)
    pfnGUID = S_OK(pfnGUIDs)
    pfnGUID['generated']=generated
    #pfnGUID = getGUID(candidateFiles.keys())
    #if not pfnGUID['OK']:
    #  self.log.error('PoolXMLFile failed to determine POOL GUID(s) for output file list, these will be generated by the ReplicaManager',pfnGUID['Message'])
    #  for fileName in candidateFiles.keys():
    #    candidateFiles[fileName]['guid']=''
    #if pfnGUID['generated']:
    self.log.debug('Generated GUID(s) for the following files ',string.join(pfnGUID['generated'],', '))
    #else:
    #  self.log.info('GUIDs found for all specified POOL files: %s' %(string.join(candidateFiles.keys(),', ')))

    for pfn,guid in pfnGUID['Value'].items():
      candidateFiles[pfn]['guid']=guid

    #Get all additional metadata about the file necessary for requests
    final = {}
    for fileName,metadata in candidateFiles.items():
      fileDict = {}
      fileDict['LFN'] = metadata['lfn']
      fileDict['Size'] = os.path.getsize(fileName)
      fileDict['Addler'] = fileAdler(fileName)
      fileDict['GUID'] = metadata['guid']
      fileDict['Status'] = "Waiting"   
      
      final[fileName]=metadata
      final[fileName]['filedict']=fileDict
      final[fileName]['localpath'] = '%s/%s' %(os.getcwd(),fileName)  

    #Sanity check all final candidate metadata keys are present (return S_ERROR if not)
    mandatoryKeys = ['guid','filedict'] #filedict is used for requests (this method adds guid and filedict)
    for fileName,metadata in final.items():
      for key in mandatoryKeys:
        if not metadata.has_key(key):
          return S_ERROR('File %s has missing %s' %(fileName,key))

    return S_OK(final)
  
  def resolveInputVariables(self):
    if self.workflow_commons.has_key('SystemConfig'):
      self.systemConfig = self.workflow_commons['SystemConfig']
    if self.workflow_commons.has_key('IgnoreAppError'):
      self.ignoreapperrors = self.workflow_commons['IgnoreAppError']
    if self.step_commons.has_key('applicationName'):
      self.applicationName = self.step_commons['applicationName']      
    if self.step_commons.has_key('applicationVersion'):
      self.applicationVersion = self.step_commons['applicationVersion']
    if self.step_commons.has_key('applicationLog'):
      self.applicationLog = self.step_commons['applicationLog']
    
    if self.step_commons.has_key('SteeringFile'):
      self.SteeringFile = self.step_commons['SteeringFile']
      
    if self.workflow_commons.has_key('JobType'):
      self.jobType = self.workflow_commons['JobType']
      
    if self.workflow_commons.has_key('Energy'):
      self.energy = self.workflow_commons['Energy']

    if self.workflow_commons.has_key('NbOfEvts'):
      self.NumberOfEvents = self.workflow_commons['NbOfEvts']
      self.workflow_commons['NbOfEvents'] = self.NumberOfEvents

    if self.step_commons.has_key('InputFile'):
      self.InputFile = self.step_commons['InputFile']
    
    if self.step_commons.has_key('ForgetInput'):
      self.ignoremissingInput = self.step_commons['ForgetInput']
            
    if self.workflow_commons.has_key('InputData'):
      self.InputData = self.workflow_commons['InputData']
      
    if self.workflow_commons.has_key('ParametricInputData'):
      self.InputData += ";"+self.workflow_commons['ParametricInputData']
    self.InputData = self.InputData.rstrip(";")
    if self.InputData==";":
      self.InputData = ''

    if not self.OutputFile:
      #this is to keep compatibility with old interface, where step param is with o  
      if self.step_commons.has_key("outputFile"):
        self.OutputFile = self.step_commons["outputFile"]
      #this is for new interface where step param has O  
      if self.step_commons.has_key("OutputFile"):
        self.OutputFile = self.step_commons["OutputFile"]

    #Next is also a module parameter, should be already set
    if self.step_commons.has_key('debug'):
      self.debug =  self.step_commons['debug']

          
    res = self.applicationSpecificInputs()
    if not res['OK']:
      return res
    return S_OK('Parameters resolved')
  
  def applicationSpecificInputs(self):
    return S_OK()

  def finalStatusReport(self,status):
    message = '%s %s Successful' %(self.applicationName,self.applicationVersion)
    if status:
      self.log.error( "==================================\n StdError:\n" )
      self.log.error( self.stdError )
      message = '%s exited With Status %s' %(self.applicationName,status)
      self.setApplicationStatus(message)
      self.log.error(message)
      if not self.ignoreapperrors:
        return S_ERROR(message)
    else: 
      self.setApplicationStatus('%s %s Successful' %(self.applicationName,self.applicationVersion))
    return S_OK(message)    

  def redirectLogOutput(self, fd, message):
    """Catch the output from the application
    """
    sys.stdout.flush()
    if message:
      if self.eventstring:
        if re.search(self.eventstring,message):
          print message
      else:
        print message
      if self.applicationLog:
        log = open(self.applicationLog,'a')
        log.write(message+'\n')
        log.close()
      else:
        self.log.error("Application Log file not defined")
    if fd == 1:
      self.stdError += message
        