from pySCM import SimpleClimateModel

fname = 'config/SimpleClimateModelParameterFile.txt'
scm = SimpleClimateModel(fname)
scm.run_model()
scm.plot('CO2', 'temp.png')
