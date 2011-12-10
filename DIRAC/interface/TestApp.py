from Application import *

class TestApp(Application):
    def __init__(self,paramdict = None):
        self.something = ""
        self.somethingelse = ''
        Application.__init__(self, paramdict)

        self._modulename = "MyTestModule"
        self.appname = self._modulename
        self._moduledescription = 'Some test module'
    
        
    def setSomething(self,something):
        self._checkArgs( {
            'something' : types.StringTypes
        } )
        self.something = something

    def setSomethingElse(self,somethingelse):
        self._checkArgs( {
            'somethingelse' : types.StringTypes
        } )
        self.somethingelse = somethingelse

    #### Below are the module/step objects definitions
    def _applicationModule(self):
        m1 = self._createModuleDefinition()
        m1.addParameter(Parameter("something",      "", "string", "", "", False, False, "Something"))
        m1.addParameter(Parameter("somethingelse",   "", "string", "", "", False, False, "Something else"))
        return m1
  
    def _applicationModuleValues(self,moduleinstance):
        moduleinstance.setValue("something",self.something)
        moduleinstance.setValue('somethingelse',self.somethingelse)
  
    def _userjobmodules(self,stepdefinition):
        res1 = self._setApplicationModuleAndParameters(stepdefinition)
        #res2 = self._setUserJobFinalization(stepdefinition) #This could be needed later
        #if not res1["OK"] or not res2["OK"] :
        #    return S_ERROR('userjobmodules failed')
        if not res1['OK']:
            return S_ERROR('userjobmodules failed')
        return S_OK()
    
    def _addParametersToStep(self,stepdefinition):
        res = self._addBaseParameters(stepdefinition)
        if not res["OK"]:
            return S_ERROR("Failed to set base parameters")
        return S_OK()
  
    def _setStepParametersValues(self, instance):
        self._setBaseStepParametersValues(instance)
        #for depn,depv in self.dependencies.items():
        #    self._job._addSoftware(depn,depv)
        return S_OK()
      
    def _checkConsistency(self):
        """ Checks that script and dependencies are set.
        """
        if not self.something:
            return S_ERROR("Something not defined")
      
        return S_OK()  
