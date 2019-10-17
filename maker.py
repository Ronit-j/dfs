# import distutils.dir_util
# path = "abc/pqr/"
# distutils.dir_util.mkpath(path)

# RW = "w"

# if RW == "a+" or RW == "w":
#     with open(path+"file1.txt", RW) as f:        # write to the cached file
#         f.write("write_client_input")
# else:
#     with open(path+"file1.txt", "r") as f:        # read from the cached file
#         # print_breaker()
#         print(f.read())
#         # print_breaker()
import os
from time import gmtime, strftime
import sys
curr_path = os.path.dirname(os.path.realpath(sys.argv[0]))
print(curr_path)
client_id = strftime("%Y%m%d%H%M%S", gmtime())
print(os.path.join(curr_path, "client_cache", client_id))