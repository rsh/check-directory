import argparse
import csv
from collections import defaultdict

from single_file_tools import read_file

parser = argparse.ArgumentParser()
parser.add_argument("file1", help="a CSV file containing hashes")
parser.add_argument("file2", help="a CSV file containing hashes")
args = parser.parse_args()


file1_loc = args.file1
file2_loc = args.file2


# Example:
# check_time,file,size,time_last_modified,checksum_type,checksum
# 2020-06-07T23:54:07.205353,./.DS_Store,28676,1590431231.0,SHA-512,5173f776f7da47732e0b56dd020d78ee3bb3fccdd797e44f384a428b116e23751c0317c3fe1a700456bd401f78cfc1bbf09a2c4d8e9910f7baea75a2f69a5446


print("Reading file1...", end="")
file1 = read_file(file1_loc)
print("Done")
print("Reading file2...", end="")
file2 = read_file(file2_loc)
print("Done")
print()


print("Files in file1 and not in file2:")
for i in file1['filename_set'] - file2['filename_set']:
    print(i)
    # TODO: Print "None" if none

print()

print("Files in file2 and not in file1:")
for i in file2['filename_set'] - file1['filename_set']:
    print(i)
    # TODO: Print "None" if none

print()

print("Comparing checksums:")
for filename, checksum in file1["filenames_to_checksums"].items():
    if(file2["filenames_to_checksums"][filename] != checksum):
        # TODO: check mod time and size. If the mod time is the same and the checksum is different, there's bit rot
        print(f"ERROR: Checksum is different for file {filename}")
    else:
        print(f"PASS: {filename}")