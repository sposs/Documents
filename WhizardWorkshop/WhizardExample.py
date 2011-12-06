from ILCDIRAC.Interfaces.API.NewInterface.Applications import *
from ILCDIRAC.Interfaces.API.NewInterface.UserJob import *
from ILCDIRAC.Interfaces.API.DiracILC import *
d = DiracILC()
j = UserJob()
wh = Whizard(processlist=d.giveProcessList())
pdict = {'process_input':{'process_id':"h_n1n1","sqrts":3000.,
                          "polarized_beams":"F"},
         "simulation_input":{"n_events":10000}}
wh.setFullParameterDict(pdict)
res = j.append(wh)
if not res['OK']:
    print res['Message']
d.submit(j)
