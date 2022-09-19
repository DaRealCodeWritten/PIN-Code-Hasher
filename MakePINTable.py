import hashlib
import threading
from tqdm import trange
from time import time, sleep
import sys


def hash_generator(algo, start, end, flc, split):
    """Hash generator that supports threading
    :param algo: Algorithm identifier in string format
    :param start: Number the generator should start at
    :param end: Number the generator should end at
    :param flc: Forced length for the PIN
    :param split: Number representing how often to dump hashes
    """
    for counter in range(start, end):
        if len(hashes[algo]) >= split:
            with open(f"output/pinhashes_{algo}.txt", "a") as out:
                cache = "\n".join(hashes[algo])
                cache = cache+"\n"
                out.write(cache)
                hashes[algo] = []
        pin = str(counter)
        hasher = hashlib.new(algo)
        string = pin if not flc else f"{counter:0{flc}d}"
        hasher.update(string.encode())
        hashed = hasher.hexdigest()
        hashes[algo].append(string+" | "+hashed)
    with open(f"output/pinhashes_{algo}.txt", "a") as out:
        out.write("\n".join(hashes[algo]))


if "--reduced-memory-footprint" in sys.argv:
    split = 25
elif "--reduced-cpu-footprint" in sys.argv:
    split = 100
else:
    split = 50
alllibs = list(hashlib.algorithms_available)
alllibs.pop(alllibs.index("shake_128"))
alllibs.pop(alllibs.index("shake_256"))
#libs = ["sha256", "sha512", "md5"]
libs = alllibs
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
    print(f"Initializing algo {lib}", flush=True)
    hashes[lib] = []
    thread = threading.Thread(name=lib, target=hash_generator, args=(lib,strt,ended,length if length != 0 else False, split))
    threads[lib] = thread
init_end = time() # Note when init time ended, for timing

print("All threads initialized, starting", flush=True)
for name, thread in threads.items(): # Start each algo's thread
    thread.start()
start_end = time() # Note when start time ended

for name, thread in threads.items(): # Stop time, wait for every thread to close
    thread.join()
all_end = time() # Note when all tasks have completed

print("All done!", flush=True)
print(f"Init took {round(init_end - starter, 3)} seconds")
print(f"Starting took {round(start_end - init_end, 3)} seconds")
print(f"Operation took {round(all_end - start_end, 3)} seconds")
print(f"Script took {round(all_end - starter, 3)} seconds")
