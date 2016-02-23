#%% PARSE BLOCK FROM BLOCKCHAIN.INFO WEBSITE

from blockchain import blockexplorer
import psycopg2

#%%

def blockDataToPostgres(blockHeight):
    conn = psycopg2.connect("dbname=mettinger user=postgres")
    cur = conn.cursor()
    
    block = blockexplorer.get_block_height(blockHeight)[0]
    txs = block.transactions
    numTxs = len(txs)
    for i in range(1,numTxs):
        thisTransaction = vars(txs[i])
        inputs = thisTransaction['inputs']
        numInputs = len(inputs)
        for j in range(numInputs):
            thisInput = vars(inputs[j])
            tx_in_n = j
            prev_tx_index = thisInput['tx_index']
            prev_tx_n = thisInput['n']
            tx_index = thisTransaction['tx_index']
            unlocking_script = thisInput['script']
            
            
            query = '''
            INSERT INTO transactions_in (block_height, 
                                          tx_in_n,
                                          prev_tx_index,
                                          prev_tx_n,
                                          tx_index,
                                          unlocking_script) 
            VALUES (%s, %s, %s, %s, %s, '%s')
            ''' % (blockHeight, 
                   tx_in_n, 
                   prev_tx_index, 
                   prev_tx_n, 
                   tx_index,
                   unlocking_script)
                   
            cur.execute(query)
    
    conn.commit()
    cur.close()
    conn.close()
        
        
thisHeight = 399455
blockDataToPostgres(thisHeight)


#%%
        
blocks = blockexplorer.get_block_height(399455)
block = blocks[0]

txIndex = 10
tx = vars(block.transactions[txIndex])

inputIndex = 0
txInput = vars(tx['inputs'][inputIndex])

outputIndex = 0
txOutput = vars(tx['outputs'][outputIndex])
        
        
        
        
        