from DIRAC.Core.Base import Script
Script.parseCommandLine()
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import UserJob
from ILCDIRAC.Interfaces.API.NewInterface.Applications import Marlin
from ILCDIRAC.Interfaces.API.DiracILC import DiracILC
d = DiracILC()                            # Provides job checking utilities
j = UserJob()                             # You are running a user job
m = Marlin()                              # Get an application instance
m.setVersion("v0116")                     # Define the version to use
m.setSteeringFile("clic_ild_cdr_steering.xml") #What the app should do
m.setInputFile("LFN:/ilc/prod/clic/3tev/ee_h_bb/ILD/DST/00000375/000/\
ee_h_bb_dst_375_999.slcio")               # Add some input
m.setGearFile("clic_ilc_cdr.gear")        # Application specific field
res = j.append(m)                         # Add the application to the job
if not res['OK']:
  print res['Message']                    # Catch any error
j.submit(d)                               # Submit the job
#Not shown here: metadata queries, chaining of applications
