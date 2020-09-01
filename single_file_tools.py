import csv
from collections import defaultdict

def find_duplicates(file_dictionary, min_size = 0):

    
    EMPTY_FILE_SHA512_CHECKSUM = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
    for checksum, filenames in file_dictionary['checksums_to_filenames'].items():
        size = int(file_dictionary['checksums_to_sizes'][checksum])

        if(checksum == EMPTY_FILE_SHA512_CHECKSUM): # TODO: Sanity check: check the file size and make sure it's 0 too?
            print(f"Skipping {len(filenames)} files with a checksum the same as the empty checksum")
        
        elif(size < min_size):
            print(f"Skipping {len(filenames)} files with size {size}")


        elif(len(filenames) > 1):
            print(f"Multiple files found for checksum: {checksum}")
            for f in filenames:
                print(f)
            print()


# Example:
# check_time,file,size,time_last_modified,checksum_type,checksum
# 2020-06-07T23:54:07.205353,./.DS_Store,28676,1590431231.0,SHA-512,5173f776f7da47732e0b56dd020d78ee3bb3fccdd797e44f384a428b116e23751c0317c3fe1a700456bd401f78cfc1bbf09a2c4d8e9910f7baea75a2f69a5446

def read_file(filename):
    file_handle = open(filename)
    input_file = csv.DictReader(file_handle)

    checksums_to_filenames = defaultdict(list)
    filenames_to_checksums = {}

    checksums_to_sizes = {}

    checksum_set = set()
    filename_set = set()

    for row in input_file:
        checksums_to_filenames[row['checksum']].append(row['file'])
        filenames_to_checksums[row['file']] = row['checksum']

        if(row['checksum'] in checksums_to_sizes and
           row['size'] != checksums_to_sizes[row['checksum']]):
           print(f"ERROR: multiple sizes for checksum: {row['checksum']}")
        checksums_to_sizes[row['checksum']] = row['size']

        checksum_set.add(row['checksum'])
        filename_set.add(row['file'])
    file_handle.close()

    # This seems wasteful. Can we make this use space more efficiently? Is it necessary?
    return {
        "checksums_to_filenames": checksums_to_filenames,
        "filenames_to_checksums": filenames_to_checksums,
        "checksums_to_sizes": checksums_to_sizes,
        "filename_set": filename_set,
        "checksum_set": checksum_set
    }
