from pySCM import SimpleClimateModel

fname = 'SimpleClimateModelParameterFile.txt'
scm = SimpleClimateModel(fname)
scm.run_model()
scm.plot('CO2', 'temp.png')
