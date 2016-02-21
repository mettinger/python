
from ethereum import tester as t
s = t.state()
c = s.abi_contract('mul2.se')
print c.double(42)
