import datetime
import pickle
import binascii

with open('log.bin', 'rb') as fp:
    items = pickle.load(fp)
"""
for item in items:
    if isinstance(item, datetime.time):
        print (item)
    else:
        print (binascii.hexlify(item))
"""

dates = list()
for i, item in enumerate(items):
    if isinstance(item, datetime.time):
        dates.append(i)

print(dates[0])
print(items[dates[0]])
