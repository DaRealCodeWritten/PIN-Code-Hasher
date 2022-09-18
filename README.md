# PIN-Code-Hasher
Generates hashes for a range of PIN codes determined by the user

# How to use MakePINTables.py
Simply launch the file with `python3` and any
launch args you want, if you want to modify the algos
to use, modify the list `libs`

# How to use FindPINTables.py
Make sure you have some hashes generated, then
run the file with `python3`

# Launch args for MakePINTable.py
`--reduced-memory-footprint` Dumps the cache to file more frequently but increases CPU usage
`--reduced-cpu-footprint` Dumps the cache less frequently, more memory usage
