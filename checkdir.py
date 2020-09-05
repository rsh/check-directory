import argparse
import csv
import hashlib
import os
from datetime import datetime

import logging



# Goals: check for bit rot, either by recalculating checksums periodically, or by comparing a directory to
#        its backup copy.
#   - Can be verified without knowing anything about the program that generated it.
#   - Human Readable

# TODO: offer options other than SHA256? BLAKE2?
# TODO: check for getmtime() precision variation by OS / FS.

# TODO: take an input CSV file that contains already calculated hashes. If the hashes are "recent enough"
#       and the date modified matches, then copy the row from the old file to the new one. Do not modify the
#       input file. "Recent enough" will be defined on the command line.


# TODO: Provide option to print a log file that contains
#   - Symlink Info:
#       - a list of files skipped because they were symlinks
#       - where that symlink pointed to
#       - whether or not that place was a valid file
#       - if that place is under our root_dir
#       - (is all of that necessary?)
#   - General stats
#       - How long each stage took
#       - Total running time
#       - How many files were checksummed
#       - How many files were skipped
#   - Write a summary to the log, which contains:
#       - Number of files found
#         - How many were checksummed
#         - How many were skipped, and for what reason
#             - symlink, filenotfound, etc

# TODO: Provide option to specify a "debug csv out" that contains: filename, how long each file took, size in bytes

# TODO: Don't overwrite output file.. error and exit.

# TODO: send error messages to stderr, change exit code to error value

# TODO: exclude the file we're writing to.

# TODO: The output lists files in the topmost directory as "./foo.txt" but files that are further down the tree are
#       listed as "baz/foo.txt" (no leading "./"). They should be consistent. 

# TODO: Move to external file.

from libs.convert_size import convert_size

parser = argparse.ArgumentParser()
parser.add_argument("--directory", help="The directory that contains the files that you want to checksum")

# TODO: should this be removed, eventually? Once we're writing to a log file, we can send the csv output to STDOUT instead.
parser.add_argument("-o", "--output", required=True, help="Output file (csv)")

args = parser.parse_args()
logger = logging.getLogger('checkdir')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('checkdir.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(process)d - [%(levelname)s] - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

root_dir = args.directory
file_list = []

logger.info("Gathering list of files to checksum...")

if not os.path.isdir(root_dir):
    logger.info("Error - value provided for 'directory' is not a valid directory: '{}'".format(root_dir))
    exit(1)


num_files_checksummed = 0
num_files_symlink = 0
num_files_error = 0

for dir_, _, files in os.walk(root_dir):
    for file_name in files:

        # assuming the command was run with DIRECTORY set to "/Users/foo/"
        # and we are currently on /Users/foo/mystuff/Pictures/photo.jpg

        #   dir_ will be: /Users/foo/mystuff/Pictures
        #   file_name will be: photo.jpg

        rel_dir = os.path.relpath(dir_, root_dir)       # e.g. mystuff/Pictures
        rel_file = os.path.join(rel_dir, file_name)     # e.g. mystuff/Pictures/photo.jpg
        full_path = os.path.join(dir_, file_name)       # e.g. /Users/foo/mystuff/Pictures/photo.jpg

        if(os.path.islink(full_path)):
            logger.info("Skipping file because it is a symlink: '{}'".format(full_path))
            num_files_symlink += 1
        elif(os.path.isfile(full_path)):
            file_list.append(rel_file)
            logger.info("Files found so far: {}".format(len(file_list))) if(len(file_list) % 1000 == 0) else None
        else:
            # TODO: Print to stderr? Raise exception?
            logger.error("ERROR: Skipping file because it is somehow 'not a file' but also 'not a symlink' (that's weird): '{}')".format(full_path))

logger.info("Done gathering list of files. Total files found: {}".format(len(file_list)))

# TODO: along with percentages and num files left, count num files / second and rolling average last 10 files size / processing time
logger.info("Sorting the list of files...")
file_list.sort()
logger.info("Done sorting the list of files")

fieldnames = ["check_time", "file", "size", "time_last_modified", "checksum_type", "checksum"]


with open(args.output, 'w', newline='') as csvfile: # TODO: Should the file be opened and closed only to write a new line? What's idiomatic?

    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    # TODO: Catch KeyboardInterrupt, finish writing to the file, close the file, and exit.

    files_checked = 0
    for rel_file in file_list:
        full_path = os.path.join(root_dir, rel_file)

        row = {}
        row["file"] = rel_file

        start = datetime.now()
        try:
            row["time_last_modified"] = str(os.path.getmtime(full_path))
            file_size = os.path.getsize(full_path)
            row["size"] = str(file_size)

            sha512_hash = hashlib.sha512()
            BLOCK_SIZE = 32768
            CHECKSUM_PROGRESS_UPDATE_INTERVAL = 32 * 1000000
            MIN_SIZE_FOR_PRINTING_PROGRESS = 32 * 1000000
            with open(full_path, "rb") as f:
                size_processed_so_far = 0
                for byte_block in iter(lambda: f.read(BLOCK_SIZE),b""):
                    sha512_hash.update(byte_block)
                    size_processed_so_far += BLOCK_SIZE

                    if(file_size >  MIN_SIZE_FOR_PRINTING_PROGRESS):
                        if(size_processed_so_far % CHECKSUM_PROGRESS_UPDATE_INTERVAL == 0):
                            logger.info("Processing large file:\t" +
                                "{:.2%}".format(size_processed_so_far/file_size) +
                                "\t({}/{})".format(convert_size(size_processed_so_far),convert_size(file_size)) +
                                "\t{}/{}".format(files_checked,len(file_list)))
                            logger.info("\t\t{}".format(rel_file))

                row["checksum"] = sha512_hash.hexdigest()
                row["checksum_type"] = "SHA-512"
                row["check_time"] = datetime.now().isoformat()

                if row["time_last_modified"] != str(os.path.getmtime(full_path)):
                    logger.error("Error: File {} was modified during checking. The checksum might not reflect the file's current state.".format(row["file"]))
                    num_files_error += 1
                    break

            writer.writerow(row)
            num_files_checksummed += 1
        except OSError as e:
            logger.error("OSError on file: {}".format(row['file']))
            logger.error("Message: {}".format(e))
            num_files_error += 1

        files_checked += 1
        if(files_checked % 10 == 0):
            logger.info("{}%\t {}/{}".format('%.2f' % round(files_checked/len(file_list) * 100, 2),files_checked,len(file_list)))

 # TODO: Summary should include how many were checksummed, how many were imported from
 #       external file, how many were rejected from external file for being stale,
 #       how many had errors.
logger.info("Attempted to checksum {} files. Exiting".format(files_checked))