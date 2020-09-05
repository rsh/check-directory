# check-directory

## checkdir.py

checkdir.py will generate checksum hashes for all of the files in a given directory and write the result in CSV format to either STDOUT (default) or to a CSV file of your choosing.

This is useful to make sure that your files' integrity is intact. You can do this by generating new checksum CSVs periodically and checking for files whose size and date modified have not changed, but the checksum has changed.

Usage:

`python checkdir.py --directory ~/Pictures/ --output out.csv

Which yields:
```
$ cat out.csv
check_time,file,size,time_last_modified,checksum_type,checksum
2020-09-04T17:11:17.142317,wallpapers/classic-mac-os-tile-wallpapers-3.png,30711,1590610980.6488047,SHA-512,2ca74c53a02139cad67caebd02f5af84edae91e0c64e6642b9a29b3b9dd7b50a423da562b900c3dc1429215699acf257a9df8bc1877252bb1e64d89b5a290ceb
2020-09-04T17:11:17.142374,wallpapers/classic-mac-os-tile-wallpapers-6.png,17347,1590611051.2448163,SHA-512,09afe869bc846444183be028a8a1edd121e9156ea2d0f459d13d8404520d0532954a8a04e982e516fc708020f01a7cbc94552637d770ebe2615bb485bb306164
2020-09-04T17:11:17.144436,wallpapers/first-snow-leopard-bg.jpg,1456859,1590611240.6364026,SHA-512,0c6759d4481cc79bf4436ff8c6a26fe9038baae420559e64a38ba69ed0aa4f5aeaca6843503e3a2e9b6b2db377be1e1d023b398bd8545e26a67e9df740faa7b8
```