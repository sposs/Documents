modifiers = {"temperature": 300}
proj = simudb.add_simulation_project("ProjectName", "Some description", "stephanep", commit=True)
simu = simudb.add_simulation("SimulationName", proj, commit=True)
name = "A_group_%s" % str(datetime.datetime.now()).replace(" ", "_")
group = simudb.add_simugroup(name, "sewlab", simu, designId, commit=True)
run = simudb.add_run("sewlab", group, pdict=modifiers, version="1.0", commit=True)
analyis.set_parameter_value(run.id, {"temperature": 300})
