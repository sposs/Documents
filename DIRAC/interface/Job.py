'''
New Job class, for the new interface. This job class should not be used to create jobs. Use L{UserJob} or L{ProductionJob}.

@author: Stephane Poss
@author: Remi Ete
@author: Ching Bon Lam
'''

from DIRAC.Interfaces.API.Job                          import Job as DiracJob
from ILCDIRAC.Interfaces.API.NewInterface.Application  import Application
from DIRAC.Core.Workflow.Step                          import StepDefinition
from DIRAC.Core.Workflow.Parameter                     import Parameter 
from DIRAC import S_ERROR,S_OK,gLogger
import string, inspect


class Job(DiracJob):
  """ ILCDIRAC job class
  
  Inherit most functionality from DIRAC Job class
  """
  def __init__(self, script = None):
    DiracJob.__init__(self, script)
    self.log = gLogger.getSubLogger("ILCJob")
    self.applicationlist = []
    self.inputsandbox = []
    self.outputsandbox = []
    self.check = True
    self.systemConfig = ''
    self.stepnumber = 0
    self.steps = []
    self.nbevts = 0
    self.energy = 0
    self.setSystemConfig('x86_64-slc5-gcc43-opt')
    
  def setInputData(self, lfns):
    """ Overload method to cancel it
    """
    return self._reportError('%s does not implement setInputData'%self.__name__)
  def setInputSandbox(self, files):
    """ Overload method to cancel it
    """
    return self._reportError('This job class does not implement setInputSandbox')
  def setOuputData(self, lfns, OutputSE = [], OutputPath = '' ):
    """ Overload method to cancel it
    """
    return self._reportError('This job class does not implement setOutputData')
  def setOutputSandbox(self, files):
    """ Overload method to cancel it
    """
    return self._reportError('This job class does not implement setOutputSandbox')
  
  def setIgnoreApplicationErrors(self):
    """ Helper function
    
    Set a flag for all applications that they should not care about errors
    """
    self._addParameter(self.workflow, 'IgnoreAppError', 'JDL', True, 'To ignore application errors')
    return S_OK()
  
  def dontPromptMe(self):
    """ Helper function
    
    Called by users to remove checking of job.
    """
    self.check = False
    return S_OK()
      
  def _askUser(self):
    """ Private function
    
    Called from DiracILC class to prompt the user
    """
    if not self.check:
      return S_OK()
    for app in self.applicationlist:
      print app
      app.listAttributes()
      print "\n"
    answer = raw_input('Proceed and submit job(s)? (Y/N): ')
    if not answer.lower() in ('y', 'yes'):
      return S_ERROR("User did not validate")
    else:
      # no more debug output in further loops
      self.check = False
    return S_OK()
  
  def append(self,application):
    """ Helper function
    
    This is the main part: call for every application
    @param application: Application instance
    
    """
    #Start by defining step number
    self.stepnumber = len(self.steps) + 1
    

    res = application._analyseJob(self)
    if not res['OK']:
      return res
    
    res = application._checkConsistency()
    if not res['OK']:
      self.log.error("%s failed to check its consistency: %s"%(application,res['Message']))
      return S_ERROR("%s failed to check its consistency: %s"%(application,res['Message']))
    
    res = self._jobSpecificParams(application)
    if not res['OK']:
      self.log.error("%s failed job specific checks: %s"%(application,res['Message']))
      return S_ERROR("%s failed job specific checks: %s"%(application,res['Message']))

    res = application._checkFinalConsistency()
    if not res['OK']:
      self.log.error("%s failed to check its consistency: %s"%(application,res['Message']))
      return S_ERROR("%s failed to check its consistency: %s"%(application,res['Message']))
    
    ### Once the consistency has been checked, we can add the application to the list of apps.
    self.applicationlist.append(application)
    ##Get the application's sandbox and add it to the job's
    for isb in application.inputSB:
      if not isb in self.inputsandbox:
        self.inputsandbox.append(isb)
    #self.inputsandbox.extend(application.inputSB)

    ##Now we can create the step and add it to the workflow
    #First we need a unique name, let's use the application name and step number
    stepname = "%s_step_%s"%(application.appname,self.stepnumber)
    stepdefinition = StepDefinition(stepname)
    self.steps.append(stepdefinition)

    ##Set the modules needed by the application
    res = self._jobSpecificModules(application,stepdefinition)
    if not res['OK']:
      self.log.error("Failed to add modules: %s"%res['Message'])
      return S_ERROR("Failed to add modules: %s"%res['Message'])
  
    ### add the parameters to  the step
    res = application._addParametersToStep(stepdefinition)
    if not res['OK']:
      self.log.error("Failed to add parameters: %s"%res['Message'])   
      return S_ERROR("Failed to add parameters: %s"%res['Message'])   
      
    ##Now the step is defined, let's add it to the workflow
    self.workflow.addStep(stepdefinition)
    
    ###Now we need to get a step instance object to set the parameters' values
    stepInstance = self.workflow.createStepInstance(stepdefinition.getType(),stepname)

    ##Set the parameters values to the step instance
    res = application._setStepParametersValues(stepInstance)
    if not res['OK']:
      self.log.error("Failed to resolve parameters values: %s"%res['Message']) 
      return S_ERROR("Failed to resolve parameters values: %s"%res['Message'])   
    
    ##stepInstance.setLink("InputFile",here lies the step name of the linked step, maybe get it from the application,"OutputFile")
    res = application._resolveLinkedStepParameters(stepInstance)
    if not res['OK']:
      self.log.error("Failed to resolve linked parameters: %s"%res['Message'])
      return S_ERROR("Failed to resolve linked parameters: %s"%res['Message'])
    #Now prevent overwriting of parameter values.
    application._addedtojob()
  
    self._addParameter(self.workflow, 'TotalSteps', 'String', self.stepnumber, 'Total number of steps')
    if application.nbevts:
      self._addParameter(self.workflow, 'NbOfEvts', 'int', application.nbevts, "Number of events to process")
  
    ##Finally, add the software packages if needed
    if application.appname and application.version:
      self._addSoftware(application.appname, application.version)
      
    return S_OK()
  
  def _jobSpecificModules(self,application,step):
    """ Returns the list of the job specific modules for the passed application. Is overloaded in ProductionJob class. UserJob uses the default.
    """
    return application._userjobmodules(step)

  def _jobSpecificParams(self,application):
    """ Every type of job has to reimplement this method. By default, just set the log file if not provided and the energy.
    """
    if not application.logfile:      
      logf = application.appname
      if application.version:
        logf += "_"+application.version
      logf += "_Step_%s.log"%self.stepnumber  
      application.setLogFile(logf)
    
    if self.energy:
      if not application.energy:
        application.setEnergy(self.energy)
      elif application.energy != self.energy:
        return S_ERROR("You have to use always the same energy per job.")
    else:
      if application.energy:
        self.energy = application.energy
      else:
        self.log.warn("Energy not set for this step")
      #  return S_ERROR("Energy must be set somewhere.")
     
    if self.energy:
      self._addParameter(self.workflow, "Energy", "float", self.energy, "Energy used")
    return S_OK()

  def _addSoftware( self, appName, appVersion ):
    """ Private method
    """

    currentApp  = "%s.%s" % ( appName.lower(), appVersion )
    swPackages  = 'SoftwarePackages'
    description = 'ILC Software Packages to be installed'

    if not self.workflow.findParameter( swPackages ):
      self._addParameter( self.workflow, swPackages, 'JDL', currentApp, description )
    else:
      apps = self.workflow.findParameter( swPackages ).getValue()

      if not currentApp in string.split( apps, ';' ):
        apps += ';' + currentApp

      self._addParameter( self.workflow, swPackages, 'JDL', apps, description )

  def _checkArgs( self, argNamesAndTypes ):
    """ Private method to check the validity of the parameters
    """

    # inspect.stack()[1][0] returns the frame object ([0]) of the caller
    # function (stack()[1]).
    # The frame object is required for getargvalues. Getargvalues returns
    # a tuple with four items. The fourth item ([3]) contains the local
    # variables in a dict.

    args = inspect.getargvalues( inspect.stack()[ 1 ][ 0 ] )[ 3 ]

    #

    for argName, argType in argNamesAndTypes.iteritems():

      if not args.has_key(argName):
        self._reportError(
          'Method does not contain argument \'%s\'' % argName,
          __name__,
          **self._getArgsDict( 1 )
        )

      if not isinstance( args[argName], argType):
        self._reportError(
          'Argument \'%s\' is not of type %s' % ( argName, argType ),
          __name__,
          **self._getArgsDict( 1 )
        )

  def _getArgsDict( self, level = 0 ):
    """ Private method
    """

    # Add one to stack level such that we take the caller function as the
    # reference point for 'level'

    level += 1

    #

    args = inspect.getargvalues( inspect.stack()[ level ][ 0 ] )
    dict = {}

    for arg in args[0]:

      if arg == "self":
        continue

      # args[3] contains the 'local' variables

      dict[arg] = args[3][arg]

    return dict
