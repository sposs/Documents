'''
Base application class. All applications inherit this class.

@author: Stephane Poss
@author: Remi Ete
@author: Ching Bon Lam
'''
from DIRAC.Core.Workflow.Module                     import ModuleDefinition
from DIRAC.Core.Workflow.Parameter                  import Parameter

from DIRAC import S_OK,S_ERROR, gLogger
import inspect, sys, string, types, os


####NEED TO CHANGE _IMPORTLOCATION FOR NEW MODULES (CS PARAMETER WOULD BE IDEAL)

class Application(object):
  """ General application definition. Any new application should inherit from this class.
  """
  #need to define slots
  ## __slots__ = []
  def __init__(self, paramdict = None):
    """ Can define the full application by passing a dictionary in the constructor.
    
    >>> app = Application({"Name":"marlin","Version":"v0111Prod",
    ...                    "SteeringFile":"My_file.xml","NbEvts":1000})
    
    @param paramdict: Dictionary of parameters that can be set. Will throw an exception if one of them does not exist.
    @type paramdict: dict
    
    """
    ##Would be cool to have the possibility to pass a dictionary to set the parameters, a bit like the current interface
    
    #application nane (executable)
    self.appname = ""
    #application version
    self.version = ""
    #Number of evetns to process
    self.nbevts = 0
    #Steering file (duh!)
    self.steeringfile = ""
    #Input sandbox: steering file automatically added to SB
    self.inputSB = []
    #Input file
    self.inputfile = ""
    self.forget_about_Input = False
    #Output file
    self.outputFile = ""
    self.outputPath = ""
    self.outputDstFile = ''
    self.outputDstPath = ''
    self.outputRecFile = ''
    self.outputRecPath = ''    
    self.outputSE = ''
    self._listofoutput = []
    #Log file
    self.logfile = ""
    #Energy to use (duh! again)
    self.energy = 0
    #Detector type (ILD or SID)
    self.detectortype = ""
    #Data type : gen, SIM, REC, DST
    self.datatype = ""
    
    ##Debug mode
    self.debug = False
    
    #Prod Parameters: things that appear on the prod details
    self.prodparameters = {}
        
    #Module name and description: Not to be set by the users, internal call only, used to get the Module objects
    self._modulename = ''
    self._moduledescription = ''
    self._importLocation = "ILCDIRAC.Workflow.Modules"
        
    #System Configuration: comes from Job definition
    self._systemconfig = ''
    
    #Internal member: hold the list of the job's application set before self: used when using getInputFromApp
    self._jobapps = []
    self._jobsteps = []
    self._jobtype = ''
    #input application: will link the OutputFile of the guys in there with the InputFile of the self 
    self._inputapp = []
    #Needed to link the parameters.
    self._inputappstep = None
    
    #flag set to true in Job.append
    self.addedtojob = False
    ####Following are needed for error report
    self._log = gLogger.getSubLogger(self.__class__.__name__)
    self._errorDict = {}
    
    ### Next is to use the setattr method.
    self._setparams(paramdict)
  
  def __repr__(self):
    str  = "%s"%self.appname
    if self.version:
      str += " %s"%self.version
    return str
  
  def _setparams(self,params):
    if not params:
      return S_OK()
    for param,value in params.items():
      if type(value) in types.StringTypes:
        value = "'%s'"%value
      try:
        exec "self.set%s(%s)"%(param,str(value))
      except:
        self._log.error("The %s class does not have a set%s method."%(self.__class__.__name__,param))
    return S_OK()  
    
    
  def setName(self,name):
    """ Define name of application
    
    @param name: Name of the application. Normally, every application defines its own, so no need to call that one
    @type name: string 
    """
    self._checkArgs({ 'name' : types.StringTypes } )
    self.appname = name
    return S_OK()  
    
  def setVersion(self,version):
    """ Define version to use
    
    @param version: Version of the application to use
    @type version: string
    """
    self._checkArgs({ 'version' : types.StringTypes } )
    self.version = version
    return S_OK()  
    
  def setSteeringFile(self,steeringfile):
    """ Set the steering file, and add it to sandbox
    
    @param steeringfile: Steering file to use. Can be any type: whizard.in, mokka.steer, slic.mac, marlin.xml, lcsim.lcsim, etc.
    @type steeringfile: string
    """
    self._checkArgs({ 'steeringfile' : types.StringTypes } )
    self.steeringfile = steeringfile
    if os.path.exists(steeringfile) or steeringfile.lower().count("lfn:"):
      self.inputSB.append(steeringfile) 
    return S_OK()  
    
  def setLogFile(self,logfile):
    """ Define application log file
    
    @param logfile: Log file to use. Set by default if not set.
    @type logfile: string
    """
    self._checkArgs({ 'logfile' : types.StringTypes } )
    self.logfile = logfile
    return S_OK()  
  
  def setNbEvts(self,nbevts):
    """ Set the number of events to process
    
    @param nbevts: Number of events to process (or generate)
    @type nbevts: int
    """
    self._checkArgs({ 'nbevts' : types.IntType })
    self.nbevts = nbevts  
    return S_OK()  

  def setNumberOfEvents(self,nbevts):
    """ Set the number of events to process, alias to setNbEvts
    """
    return self.setNbEvts(nbevts)
    
  def setEnergy(self,energy):
    """ Set the energy to use
    
    @param energy: Energy used in GeV
    @type energy: float
    """
    if not type(energy)==type(1.1):
      energy = float(energy)
    self._checkArgs({ 'energy' : types.FloatType })
    self.energy = energy
    return S_OK()  
    
  def setOutputFile(self,ofile, path = None):
    """ Set the output file
    
    @param ofile: Output file name. Will overwrite the default. This is necessary when linking applications (when using L{getInputFromApp})
    @type ofile: string
    @param path: Set the output path for the output file to go. Will not do anything in a UserJob. Use setOutputData of the job for that functionality.
    @type path: string
    """
    self._checkArgs({ 'ofile' : types.StringTypes } )
    
    self.outputFile = ofile
    self.prodparameters[ofile]={}
    if self.detectortype:
      self.prodparameters[ofile]['detectortype'] = self.detectortype
    if self.datatype:
      self.prodparameters[ofile]['datatype']= self.datatype
    
    if path:
      self._checkArgs({ 'path' : types.StringTypes } )
      self.outputPath = path
      
    return S_OK()  
  
  def setOutputSE(self,se):
    """ Set the output storage element for all files produced by this application.
    
    @param se: Storage element name. Example CERN-SRM, IN2P3-SRM, RAL-SRM, IMPERIAL-SRM
    @type se: string
  
    """
    self._checkArgs({ 'se' : types.StringTypes } )
    self.outputSE = se
    return S_OK()
  
  def setInputFile(self,inputfile):
    """ Set the input file to use: stdhep, slcio, root, whatever
    
    @param inputfile: Input file (data, not steering) to pass to the application. Can be local file of LFN:
    @type inputfile: string or list
    """
    kwargs = {"inputfile":inputfile}
    if not type(inputfile) in types.StringTypes and not type(inputfile)==type([]):
      return self._reportError("InputFile must be string or list of strings",__name__,**kwargs)
    if not type(inputfile)==type([]):
      inputfile = [inputfile]
    for f in inputfile:
      if os.path.exists(f) or f.lower().count("lfn:"):
        self.inputSB.append(f)
        
    self.inputfile = string.join(inputfile,";")

    return S_OK()
  
  def setForgetAboutInput(self):
    """ Do not overwrite the input set in the SteeringFile
    """
    
    self.forget_about_Input = True
    
    return S_OK()
  
  def getInputFromApp(self,application):
    """ Called to link applications
    
    >>> mokka = Mokka()
    >>> marlin = Marlin()
    >>> marlin.getInputFromApp(mokka)
    
    @param application: Application to link against.
    @type application: application
    """
    self._inputapp.append(application)
    return S_OK()  

  def setDebug(self,debug = True):
    """ Set the applciation to debug mode
    
    >>> app = Application()
    >>> app.setDebug()
    
    @param debug: Set the applciation to debug mode. Default is True when called. If not, then it's false.
    @type debug: bool
    """
    self._checkArgs({ "debug": types.BooleanType} )
    self.debug = debug
    return S_OK()

  def listAttributes(self):
    """ Method to list attributes for users. Doesn't list any private or semi-private attributes
    """
    print 'Attribute list :'
    for key,val in self.__dict__.items():
      if not key[0]=="_":
        if not val:
          val = "Not defined"
        print "  ",key,":",val


########################################################################################
#    More private methods: called by the applications of the jobs, but not by the users
#    Please, do not touch when you don't know what you are doing.
#                           / \  //\
#            |\___/|      /   \//  \\
#            /0  0  \__  /    //  | \ \    
#           /     /  \/_/    //   |  \  \  
#           @_^_@'/   \/_   //    |   \   \ 
#           //_^_/     \/_ //     |    \    \
#        ( //) |        \///      |     \     \
#      ( / /) _|_ /   )  //       |      \     _\
#    ( // /) '/,_ _ _/  ( ; -.    |    _ _\.-~        .-~~~^-.
#  (( / / )) ,-{        _      `-.|.-~-.           .~         `.
# (( // / ))  '/\      /                 ~-. _ .-~      .-~^-.  \
# (( /// ))      `.   {            }                   /      \  \
#  (( / ))     .----~-.\        \-'                 .~         \  `. \^-.
#             ///.----..>        \             _ -~             `.  ^-`  ^-_
#               ///-._ _ _ _ _ _ _}^ - - - - ~                     ~-- ,.-~
#                                                                  /.-~
########################################################################################

  def _setApplicationModuleAndParameters(self,stepdefinition) :
    """Create Application Module, add it to a Step and set values to Module. Called in every applications 
    """
    m1 = self._applicationModule()
    stepdefinition.addModule(m1)
    m1i = stepdefinition.createModuleInstance(m1.getType(),stepdefinition.getType())
    self._applicationModuleValues(m1i)
    return S_OK()
  
  def _setUserJobFinalization(self,stepdefinition) :
    """ Create UserOutputDataModule and add it to Step. 
    Called after the private method setApplicationModuleAndParameters in some user job applications
    """
    m2 = self._getUserOutputDataModule()
    stepdefinition.addModule(m2)
    stepdefinition.createModuleInstance(m2.getType(),stepdefinition.getType())
    return S_OK()
  
  def _setOutputComputeDataList(self, stepdefinition) :
    """ Create ComputeOutputDataListModule and add it to Step. 
    Called after the private method setApplicationModuleAndParameters in some production job applications
    """
    m2 = self._getComputeOutputDataListModule()
    stepdefinition.addModule(m2)
    stepdefinition.createModuleInstance(m2.getType(),stepdefinition.getType())
    return S_OK()
    
  def _createModuleDefinition(self):
    """ Create Module definition. As it's generic code, all apps will use this.
    """
    moduledefinition = ModuleDefinition(self._modulename)
    moduledefinition.setDescription(self._moduledescription)
    body = 'from %s.%s import %s\n' % (self._importLocation, self._modulename, self._modulename)
    moduledefinition.setBody(body)
    return moduledefinition
  
  def _getUserOutputDataModule(self):
    """ This is separated as not all applications require user specific output data (i.e. GetSRMFile and Overlay). Only used in UserJobs.
    
    The UserJobFinalization only runs last. It's called every step, but is running only if last.
    """
    moduledefinition = ModuleDefinition('UserJobFinalization')
    moduledefinition.setDescription('Uploads user output data files with specific policies.')
    body = 'from %s.%s import %s\n' % (self._importLocation, 'UserJobFinalization', 'UserJobFinalization')
    moduledefinition.setBody(body)
    return moduledefinition
  
  def _getComputeOutputDataListModule(self):
    """ This is separated from the applications as this is used in production jobs only.
    """
    moduledefinition = ModuleDefinition("ComputeOutputDataList")
    moduledefinition.setDescription("Compute the output data list to be treated by the last finalization")
    body = 'from %s.%s import %s\n' % (self._importLocation, "ComputeOutputDataList", "ComputeOutputDataList" )
    moduledefinition.setBody(body)
    return moduledefinition
  
  def _applicationModule(self):
    """ Create the module for the application, and add the parameters to it. Overloaded by every application class.
    """
    return None
  
  def _applicationModuleValues(self,moduleinstance):
    """ Set the values for the modules parameters. Needs to be overloaded for each application.
    """
    pass

  def _userjobmodules(self,stepdefinition):
    """ Method used to return the needed module for UserJobs. It's different from the ProductionJobs (userJobFinalization for instance)
    """
    self._log.error("This application does not implement the modules, you get an empty list")
    return S_ERROR('Not implemented')
  
  def _prodjobmodules(self,stepdefinition):
    """ Same as above, but the other way around.
    """
    self._log.error("This application does not implement the modules, you get an empty list")
    return S_ERROR('Not implemented')
  
  def _checkConsistency(self):
    """ Called from Job Class, overloaded by every class. Used to check that everything is fine, in particular that all required parameters are defined.
    Should also call L{_checkRequiredApp} when needed.
    """
    return S_OK()
  
  def _checkFinalConsistency(self):
    """ Called from Job Class, overloaded by every class. Used to check that everything is fine, in particular that all required parameters are defined.
    Some info are passed from the job to the applications: this is then used to check that it makes the app valid 
    """
    return S_OK()

  def _checkRequiredApp(self):
    """ Called by L{_checkConsistency} when relevant
    """
    if self._inputapp:
      for app in self._inputapp:
        if not app in self._jobapps:
          return S_ERROR("job order not correct: If this app uses some input coming from an other app, the app in question must be passed to job.append() before.")
        else:
          idx = self._jobapps.index(app)
          self._inputappstep = self._jobsteps[idx]
    return S_OK()
  
  def _addBaseParameters(self,stepdefinition):
    """ Add to step the default parameters: appname, version, steeringfile, (nbevts, Energy), LogFile, InputFile, OutputFile, OutputPath
    """
    stepdefinition.addParameter(Parameter("applicationName",   "", "string", "", "", False, False, "Application Name"))
    stepdefinition.addParameter(Parameter("applicationVersion","", "string", "", "", False, False, "Application Version"))
    stepdefinition.addParameter(Parameter("SteeringFile",      "", "string", "", "", False, False, "Steering File"))
    stepdefinition.addParameter(Parameter("applicationLog",    "", "string", "", "", False, False, "Log File"))
    stepdefinition.addParameter(Parameter("InputFile",         "", "string", "", "",  True, False, "Input File"))
    stepdefinition.addParameter(Parameter("ForgetInput",    False,"boolean", "", "", False, False, "Do not overwrite input steering"))
    if len(self.outputFile):
      stepdefinition.addParameter(Parameter("OutputFile",      "", "string", "", "", False,  False, "Output File"))
    if len(self.outputDstFile):
      stepdefinition.addParameter(Parameter("outputDST",       "", "string", "", "", False,  False, "Output DST File"))
    if len(self.outputRecFile):
      stepdefinition.addParameter(Parameter("outputREC",      "", "string", "", "",  False,  False, "Output REC File"))
      
    stepdefinition.addParameter(Parameter("OutputPath",        "", "string", "", "",  True, False, "Output File path on the grid"))
    stepdefinition.addParameter(Parameter("outputPathREC",     "", "string", "", "",  True, False, "Output REC File path on the grid"))
    stepdefinition.addParameter(Parameter("outputPathDST",     "", "string", "", "",  True, False, "Output DST File path on the grid"))
    stepdefinition.addParameter(Parameter("OutputSE",          "", "string", "", "",  True, False, "Output File storage element"))
    stepdefinition.addParameter(Parameter('listoutput',        [],   "list", "", "", False, False, "list of output file name"))
    #Following should be workflow parameters
    #stepdefinition.addParameter(Parameter("NbOfEvents",         0,    "int", "", "", False, False, "Number of events to process"))
    #stepdefinition.addParameter(Parameter("Energy",             0,    "int", "", "", False, False, "Energy"))
    return S_OK()
  
  def _setBaseStepParametersValues(self,stepinstance):
    """ Set the values for the basic step parameters
    """
        
    stepinstance.setValue("applicationName",    self.appname)
    stepinstance.setValue("applicationVersion", self.version)
    stepinstance.setValue("applicationLog",     self.logfile)
    stepinstance.setValue("SteeringFile",       self.steeringfile)
    if not self._inputapp:
      stepinstance.setValue("InputFile",        self.inputfile)
    stepinstance.setValue( "ForgetInput",       self.forget_about_Input)
    if len(self.outputFile):  
      stepinstance.setValue("OutputFile",       self.outputFile)
    if len(self.outputRecFile):  
      stepinstance.setValue("outputREC",        self.outputRecFile)
    if len(self.outputDstFile):  
      stepinstance.setValue("outputDST",        self.outputDstFile)
    stepinstance.setValue("OutputPath",         self.outputPath)
    stepinstance.setValue("outputPathREC",      self.outputRecPath)
    stepinstance.setValue("outputPathDST",      self.outputDstPath)
    stepinstance.setValue("OutputSE",           self.outputSE)
    stepinstance.setValue('listoutput',         self._listofoutput)
    return S_OK()
      
      
  def _addParametersToStep(self,stepdefinition):
    """ Method to be overloaded by every application. Add the parameters to the given step. Should call L{_addBaseParameters}.
    Called from Job
    """
    return self._addBaseParameters(stepdefinition)
  
  def _setStepParametersValues(self,stepinstance):
    """ Method to be overloaded by every application. For all parameters that are not to be linked, set the values in the step instance
    Called from Job
    """
    return self._setBaseStepParametersValues(stepinstance)

  def _resolveLinkedStepParameters(self,stepinstance):
    """ Method to be overloaded by every application that resolve what are the linked parameters (e.g. OuputFile and InputFile). See L{StdhepCut} for example.
    Called from Job.
    """
    return S_OK()

  def _analyseJob(self,job):
    """ Called from Job, only gives the application the knowledge of the Job (application, step, system config)
    """
    self._job = job
    
    self._systemconfig = job.systemConfig
    
    self._jobapps      = job.applicationlist
    
    self._jobsteps     = job.steps
    
    self._jobtype      = job.type
    
    return S_OK()

  def _addedtojob(self):
    """ Called from Job to tell the application that it is added to job and the parameter values are set.
    
    Prevents the user from thinking he can change the values after the app was added to job.
    """
    self.addedtojob = True
  
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

  #############################################################################
  def _reportError( self, message, name = '', **kwargs ):
    """Internal Function. Gets caller method name and arguments, formats the 
       information and adds an error to the global error dictionary to be 
       returned to the user. 
       Stolen from DIRAC Job Class
    """
    className = name
    if not name:
      className = __name__
    methodName = sys._getframe( 1 ).f_code.co_name
    arguments = []
    for key in kwargs:
      if kwargs[key]:
        arguments.append( '%s = %s ( %s )' % ( key, kwargs[key], type( kwargs[key] ) ) )
    finalReport = 'Problem with %s.%s() call:\nArguments: %s\nMessage: %s\n' % ( className, methodName, string.join( arguments, ', ' ), message )
    if self._errorDict.has_key( methodName ):
      tmp = self._errorDict[methodName]
      tmp.append( finalReport )
      self._errorDict[methodName] = tmp
    else:
      self._errorDict[methodName] = [finalReport]
    self._log.error( finalReport )
    return S_ERROR( finalReport )
