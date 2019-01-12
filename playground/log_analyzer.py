import datetime
import pickle
import binascii
import os

logs_dir = '/home/hkeene/pool/aqualogic/playground/logs/'
log_file = 'log_waterfalls_off'
log_bin = os.path.join(logs_dir, log_file + '.bin')
log_txt = os.path.join(logs_dir, log_file + '.txt')

with open(log_bin, 'rb') as fp:
    items = pickle.load(fp)

items.pop(0) #First element should be a bytearray and not a date

org_time = items[0]

item_range = range(0, len(items)-2, 2)
str_list = list()

for i, el in enumerate(item_range):
    delta_t = str(items[el] - org_time)
    time_since = str(items[item_range[i]] - items[item_range[i-1]])
    bytes = str(binascii.hexlify(items[el+1]))

#    print("{}----{}----{}".format(delta_t, time_since, bytes))
    str_list.append("{}----{}----{}".format(delta_t[5:], time_since[6:], bytes[2:-3]))

str_list.pop(0)
s = "\n".join(str_list)
print(s)

with open(log_txt, "w") as text_file:
    text_file.write(s)
