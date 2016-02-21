#!/usr/bin/python 
import sys 
from blocktools import * 
from block import Block, BlockHeader 

def parse(blockchain): 
        print 'Parsing Block Chain' 
        
        '''
        block = Block(blockchain) 
        return block
        '''
        
        counter = 0 
        while True: 
                print counter 
                block = Block(blockchain) 
                block.toString() 
                print "\n"*10
                counter+=1 
        
        
def main(): 
        if len(sys.argv) < 2: 
                #print 'Usage: blockparser.py filename' 
                blockfile = "/Users/mettinger/Library/Application Support/Bitcoin/blocks/blk00035.dat"
                print "Using default block: " + blockfile
        else: 
                blockfile = sys.argv[1]
                
        with open(blockfile, 'rb') as blockchain: 
                block = parse(blockchain) 
                #block.toString()



if __name__ == '__main__': 
        main()   
