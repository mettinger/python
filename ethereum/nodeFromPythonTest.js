Web3 = require('web3')

web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

var transaction = web3.eth.getTransaction("0x3147c1f1e223dfed619a288d49b4b32a64fb0b7436d3436b22e98f91fb079749");

console.log(transaction)

