"""
This file is to help generate range inputs to copy 
for the scroll volume download scripts.
The motivating use case is to sample every nth volume 
to get a representative sample of the scroll to then 
create the masked cube .csv files for scrolls 2 & 4
"""
scrollZAxis = 14427 #scroll 2 length 14427, scroll 4 length ...
step = 100 #every nth volume to sample, 500 choosen as it lines up with vol cubes

output = "["
for i in range(0, scrollZAxis, step):
    output += f"{i},"

output = output[:-1] + "]"
print(output)

#Example output: [0,500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,
# 6000,6500,7000,7500,8000,8500,9000,9500,10000,10500,11000,11500,12000,12500,
# 13000,13500,14000]
# This output can be used as input to the scroll volume download scripts 
# to download every 500th volume