analysis = AnalysisInterface(connection)
query = {"temperature": {">=": 270}, 
         "simu_type": "sewlab"}
res = analysis.get_run_by_parameter_query(query)
for run in res:
    pdict = analysis.get_parameters_for_run(run)
    print pdict
