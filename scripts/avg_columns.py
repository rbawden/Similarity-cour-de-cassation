#!/usr/bin/python
import sys

# tab-separated line
for line in sys.stdin:
    tabline = [float(x) for x in line.split() if str(x) != 'nan']
    mean = sum(tabline) / len(tabline)
    print(mean)
    
