import serpent
from pyethereum import tester, utils, abi

serpent_code = '''
def multiply(a):
return(a*2)
'''

s = tester.state()
c = s.abi_contract(serpent_code)
o = c.multiply(5)
print(str(o))
