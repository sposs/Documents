'''
User Job class. Used to define (guess what?) user jobs!


@author: Stephane Poss
@author: Remi Ete
@author: Ching Bon Lam
'''

from ILCDIRAC.Interfaces.API.NewInterface.Job import Job
from DIRAC import S_OK,S_ERROR

import string,types

class UserJob(Job):
  def __init__(self, script = None):
    Job.__init__(self, script)
    self.type = 'User'
    
  #############################################################################
  def setInputData( self, lfns ):
    """Helper function.

       Specify input data by Logical File Name (LFN).

       Example usage:

       >>> job = Job()
       >>> job.setInputData(['/ilc/prod/whizard/processlist.cfg'])

       @param lfns: Logical File Names
       @type lfns: Single LFN string or list of LFNs
    """
    if type( lfns ) == list and len( lfns ):
      for i in xrange( len( lfns ) ):
        lfns[i] = lfns[i].replace( 'LFN:', '' )
      inputData = map( lambda x: 'LFN:' + x, lfns )
      inputDataStr = string.join( inputData, ';' )
      description = 'List of input data specified by LFNs'
      self._addParameter( self.workflow, 'InputData', 'JDL', inputDataStr, description )
    elif type( lfns ) == type( ' ' ):  #single LFN
      description = 'Input data specified by LFN'
      self._addParameter( self.workflow, 'InputData', 'JDL', lfns, description )
    else:
      kwargs = {'lfns':lfns}
      return self._reportError( 'Expected lfn string or list of lfns for input data', **kwargs )

    return S_OK()
   
  def setInputSandbox(self,flist):
    """ Mostly inherited from DIRAC.Job
    """
    if type(flist)==type(""):
      flist = [flist]
    if not type(flist)==type([]) :
      return self._reportError("File passed must be either single file or list of files.") 
    self.inputsandbox.extend(flist)
    return S_OK()

  #############################################################################
  def setOutputData(self, lfns, OutputPath='', OutputSE=[]):
    """Helper function, used in preference to Job.setOutputData() for ILC.

       For specifying output data to be registered in Grid storage.  If a list
       of OutputSEs are specified the job wrapper will try each in turn until
       successful.

       Example usage:

       >>> job = Job()
       >>> job.setOutputData(['Ntuple.root'])

       @param lfns: Output data file or files
       @type lfns: Single string or list of strings ['','']
       @param OutputSE: Optional parameter to specify the Storage
       @param OutputPath: Optional parameter to specify the Path in the Storage, postpented to /ilc/user/u/username/
       Element to store data or files, e.g. CERN-tape
       @type OutputSE: string or list
       @type OutputPath: string
    """    
    kwargs = {'lfns':lfns, 'OutputSE':OutputSE, 'OutputPath':OutputPath}
    if type(lfns) == list and len(lfns):
      outputDataStr = string.join(lfns, ';')
      description = 'List of output data files'
      self._addParameter(self.workflow, 'UserOutputData', 'JDL', outputDataStr, description)
    elif type(lfns) == type(" "):
      description = 'Output data file'
      self._addParameter(self.workflow, 'UserOutputData', 'JDL', lfns, description)
    else:
      return self._reportError('Expected file name string or list of file names for output data', **kwargs)

    if OutputSE:
      description = 'User specified Output SE'
      if type(OutputSE) in types.StringTypes:
        OutputSE = [OutputSE]
      elif type(OutputSE) != types.ListType:
        return self._reportError('Expected string or list for OutputSE', **kwargs)
      OutputSE = ';'.join(OutputSE)
      self._addParameter(self.workflow, 'UserOutputSE', 'JDL', OutputSE, description)

    if OutputPath:
      description = 'User specified Output Path'
      if not type(OutputPath) in types.StringTypes:
        return self._reportError('Expected string for OutputPath', **kwargs)
      # Remove leading "/" that might cause problems with os.path.join
      while OutputPath[0] == '/': 
        OutputPath = OutputPath[1:]
      if OutputPath.count("ilc/user"):
        return self._reportError('Output path contains /ilc/user/ which is not what you want', **kwargs)
      self._addParameter(self.workflow, 'UserOutputPath', 'JDL', OutputPath, description)

    return S_OK()
  
  #############################################################################
  def setOutputSandbox( self, files ):
    """Helper function.

       Specify output sandbox files.  If specified files are over 10MB, these
       may be uploaded to Grid storage with a notification returned in the
       output sandbox.

       Example usage:

       >>> job = Job()
       >>> job.setOutputSandbox(['*.log','myfile.slcio'])

       @param files: Output sandbox files
       @type files: Single string or list of strings ['','']

    """
    if type( files ) == list and len( files ):
      fileList = string.join( files, ";" )
      description = 'Output sandbox file list'
      self._addParameter( self.workflow, 'OutputSandbox', 'JDL', fileList, description )
    elif type( files ) == type( " " ):
      description = 'Output sandbox file'
      self._addParameter( self.workflow, 'OutputSandbox', 'JDL', files, description )
    else:
      kwargs = {'files':files}
      return self._reportError( 'Expected file string or list of files for output sandbox contents', **kwargs )

    return S_OK()
