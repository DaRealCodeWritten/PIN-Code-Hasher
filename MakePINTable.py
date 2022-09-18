import hashlib
import threading
from time import time


def hash_generator(algo, start, end, flc):
    """Hash generator that supports threading
    :param algo: Algorithm identifier in string format
    :param start: Number the generator should start at
    :param end: Number the generator should end at
    :param flc: Forced length for the PIN
    """
    counter = start
    while counter < end:
        if len(hashes[algo]) >= 50:
            with open(f"output/pinhashes_{algo}.txt", "a") as out:
                cache = "\n".join(hashes[algo])
                cache = cache+"\n"
                out.write(cache)
                hashes[algo] = []
                print(f"Dumped hashes for {algo}")
        pin = str(counter)
        hasher = hashlib.new(algo)
        string = pin if not flc else f"{counter:0{flc}d}"
        hasher.update(string.encode())
        hashed = hasher.hexdigest()
        hashes[algo].append(string+" | "+hashed)
        counter += 1
    with open(f"output/pinhashes_{algo}.txt", "a") as out:
        out.write("\n".join(hashes[algo]))
        print(f"Dumped remaining hashes for {algo}, stopping...")


alllibs = list(hashlib.algorithms_available)
alllibs.pop(alllibs.index("shake_128"))
alllibs.pop(alllibs.index("shake_256"))
libs = ["sha256", "sha512", "md5"]
threads = {}
hashes = {}
length = int(input("Enter a forced length, or 0 to disable: "))
strt = int(input("Enter the starting number: "))
ended = int(input("Enter the ending number: "))+1
if ended < strt: # End number can't be less than the start!
    raise ValueError("Start number must be less than end number")
if (len(list(str(strt))) > length or len(list(str(ended-1))) > length) and length != 0: 
    """Start or end number was longer than the forced length, if it's enabled"""
    raise ValueError("Start and end number length must not exceed forced length")

starter = time() # Start the clock for timing
for lib in libs: # Init phase, set up the hashes and threads dicts for each algo
    print(f"Initializing algo {lib}")
    hashes[lib] = []
    thread = threading.Thread(name=lib, target=hash_generator, args=(lib,strt,ended,length if length != 0 else False))
    threads[lib] = thread
init_end = time() # Note when init time ended, for timing

for name, thread in threads.items(): # Start each algo's thread
    print(f"Starting algo {name}")
    thread.start()
start_end = time() # Note when start time ended

for name, thread in threads.items(): # Stop time, wait for every thread to close
    print(f"Waiting for algo {name} to stop")
    thread.join()
all_end = time() # Note when all tasks have completed

print("All done!")
print(f"Init took {round(init_end - starter, 3)} seconds")
print(f"Starting took {round(start_end - init_end, 3)} seconds")
print(f"Operation took {round(all_end - start_end, 3)} seconds")
print(f"Script took {round(all_end - starter, 3)} seconds")
