from DIRAC.TransformationSystem.Client.Transformation import Transformation
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from DIRAC.Interfaces.API.Job import Job

j = Job()
tc = TransformationClient()

t = Transformation()
t.setTransformationName("Un exemple") #<- unique
t.setTransformationGroup("Un groupe") #<- for monitoring
t.setType("MCSimulation")#type must be among known types
t.setDescription("Ceci est un exemple")
t.setLongDescription("C'est un bel exemple")
t.setBody(j.workflow._toXML())
t.setGroupSize(1)
t.setPlugin("Standard")
t.addTransformation() #<-- transformation is created here
t.setStatus("Active") #<-- make it start
t.setAgentType("Automatic") #<-- should be by default
transfid = t.getTransformationID()['Value'] #<- unique
tc.createTransformationInputDataQuery(transfid, 
                                      {'meta1':val1,"meta2":{">":34}})
