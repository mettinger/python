#%% PARSE BLOCK FROM BLOCKCHAIN.INFO WEBSITE AND LOAD INTO POSTGRESQL

from blockchain import blockexplorer
import psycopg2

#%%

def blockDataToPostgres(blockHeight):
    conn = psycopg2.connect("dbname=mettinger user=postgres")
    cur = conn.cursor()
    
    block = blockexplorer.get_block_height(blockHeight)[0]
    txs = block.transactions
    numTxs = len(txs)
    
    # coinbase transaction?
    
    for i in range(1,numTxs):
        thisTransaction = vars(txs[i])
        
        # process inputs
        inputs = thisTransaction['inputs']
        numInputs = len(inputs)
        for j in range(numInputs):
            thisInput = vars(inputs[j])
            tx_in_n = j
            prev_tx_index = thisInput['tx_index']
            prev_tx_n = thisInput['n']
            tx_index = thisTransaction['tx_index']
            unlocking_script = thisInput['script']
            address = thisInput['address']
            amount = thisInput['value']
            
            query = '''
            INSERT INTO transactions_in (block_height, 
                                          tx_in_n,
                                          prev_tx_index,
                                          prev_tx_n,
                                          tx_index,
                                          unlocking_script,
                                          address,
                                          amount) 
            VALUES (%s, %s, %s, %s, %s, '%s', '%s',%s)
            ''' % (blockHeight, 
                   tx_in_n, 
                   prev_tx_index, 
                   prev_tx_n, 
                   tx_index,
                   unlocking_script,
                   address,
                   amount)
                   
            cur.execute(query)
            
        # process outpouts
        outputs = thisTransaction['outputs']
        numOutputs = len(outputs)
        for j in range(numOutputs):
            thisOutput = vars(outputs[j])
            tx_out_n = thisOutput['n']
            amount = thisOutput['value']
            tx_index = thisTransaction['tx_index']
            script = thisOutput['script']
            address = thisOutput['address']
            
            query = '''
            INSERT INTO transactions_out (block_height, 
                                          tx_out_n,
                                          amount,
                                          tx_index,
                                          script,
                                          address) 
            VALUES (%s, %s, %s, %s,'%s', '%s')
            ''' % (blockHeight, 
                   tx_out_n, 
                   amount,
                   tx_index,
                   script,
                   address)
                   
            cur.execute(query)
            
    conn.commit()
    cur.close()
    conn.close()

# block heights
lowerBlock = 399720
upperBlock = 399820
for thisHeight in range(lowerBlock, upperBlock + 1):
    blockDataToPostgres(thisHeight)


#%%
        
testFlag = 0
if testFlag == 1:
    blocks = blockexplorer.get_block_height(399455)
    block = blocks[0]
    
    txIndex = 10
    tx = vars(block.transactions[txIndex])
    
    allInput = [ vars(i) for i in tx['inputs']]
    allOutput = [ vars(i) for i in tx['outputs']]
        
        
        
        
        