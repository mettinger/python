#%%

from subprocess import call, check_output

#%%

script = "/Users/mettinger/Github/python/ethereum/nodeFromPythonTest.js"
result = check_output(["/usr/local/bin/node", script])