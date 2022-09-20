import hashlib
import threading
from tqdm import trange
from json import dump, load
from time import time, sleep
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import sys


class StateManager:
    def __init__(self):
        self.state = {
            "cache": {}
        }
    def update_state(self, new_state):
        self.state.update(new_state)
    def dump_state(self):
        with open("state.json", "w") as file:
            dump(self.state, file)
    def load_state(self):
        with open("state.json", "r") as file:
            self.state = load(file)
    def resume(self):
        stop_no = self.state["end-number"]
        force_len = self.state["force-length"]
        skip_no = self.state["dump-frequency"]
        cache = self.state["cache"]
        for algo in cache.keys():
            hashes[algo] = cache[algo]["hashes"]
        with ThreadPoolExecutor(len(hashes.keys())) as exe:
            for lib in cache.keys():
                start_no = cache[lib]["ended"]
                future = exe.submit(hash_generator, lib, start_no, stop_no, force_len, skip_no)
                futures.append(future)


def hash_generator(algo, start, end, flc, split):
    """Hash generator that supports threading
    :param algo: Algorithm identifier in string format
    :param start: Number the generator should start at
    :param end: Number the generator should end at
    :param flc: Forced length for the PIN
    :param split: Number representing how often to dump hashes
    """
    for counter in range(start, end):
        if stop_code == 1:
            global stater
            stater.state["cache"][algo] = {
                "ended": counter,
                "hashes": hashes[algo]
            }
            print(f"Successfully updated state, {algo} thread closed")
            return
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


def loading_screen(): # Loading screen while the hashing runs
    while 1:
        try:
            for sym in ["/", "-", "\\", "|"]:
                global stop_code
                if stop_code == 1:
                    print(f"{sym} finished")
                    return
                global starter
                print(f"{sym} working... {int(time()-starter)}s elapsed", end="\r")
                sleep(0.5)
        except: pass

if "--reduced-memory-footprint" in sys.argv:
    split = 25 # Dump the cache more frequently
elif "--reduced-cpu-footprint" in sys.argv:
    split = 100 # Dump the cache less frequently
else:
    split = 50
stop_code = 0
hashes = {} # Dictionary of algorithms and cached hashes
futures = [] # List of running futures
stater = StateManager()
if "--resume" in sys.argv: # Try to resume from state.json
    print("Resuming...")
    stater.load_state()
    print("Loaded state, running...")
    stater.resume()
    print("Finished")
    while not all(future.done() for future in futures):
        continue
    exit()

alllibs = list(hashlib.algorithms_available)
alllibs.pop(alllibs.index("shake_128")) # These 2 algorithms
alllibs.pop(alllibs.index("shake_256")) # require a length arg for hexdigest
libs = ["sha256", "sha512", "md5"]
#libs = alllibs # DONT USE THIS UNLESS YOU KNOW WHAT YOU'RE DOING
length = int(input("Enter a forced length, or 0 to disable: "))
strt = int(input("Enter the starting number: "))
ended = int(input("Enter the ending number: "))+1
cur = {
    "end-number": ended,
    "force-length": length,
    "dump-frequency": split
}
stater.update_state(cur) # Save initial values for later resumption if needed

if ended < strt: # End number can't be less than the start!
    raise ValueError("Start number must be less than end number")
if (len(list(str(strt))) > length or len(list(str(ended-1))) > length) and length != 0: 
    """Start or end number was longer than the forced length, if it's enabled"""
    raise ValueError("Start and end number length must not exceed forced length")

starter = time() # Start the clock for timing

for lib in libs: # Init phase, set up the hashes and threads dicts for each algo
    print(f"Initializing algo {lib}", flush=True)
    hashes[lib] = []
init_end = time() # Note when init time ended, for timing

print("All threads initialized, starting", flush=True)

try:
    with ThreadPoolExecutor(len(hashes.keys())) as executor:
        for lib in hashes.keys():
            future = executor.submit(hash_generator, lib, strt, ended, length, split)
            futures.append(future)

except KeyboardInterrupt:
    print("Received SIGINT or Ctrl+C, shutting down")
    stop_code = 1 # Signal all threads to stop
    for future in futures: # Wait for all futures to stop
        future.result()
    stater.dump_state() # Dump the current program state for later resumption

try:
    for future in futures: # Check to make  sure no children were running
       if future.running(): raise TimeoutError()

except TimeoutError as e: # Script tried to exit while child thread was running
    raise RuntimeError("Main thread destroyed while child is running") from e

all_end = time() # Note when all tasks have completed
print("All done!", flush=True)
print(f"Init took {round(init_end - starter, 3)} seconds")
print(f"Operation took {round(all_end - init_end, 3)} seconds")
print(f"Script took {round(all_end - starter, 3)} seconds")
