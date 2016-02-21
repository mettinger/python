#%%

from blockchain import blockexplorer

#%%

block = blockexplorer.get_block('000000052e9213e6856d9644525f9cda367b4d50fa7150204dd970')


#%%
blocks = blockexplorer.get_block_height(399455)
block = blocks[0]


