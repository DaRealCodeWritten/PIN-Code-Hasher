import os


print("PIN Hash Finder v1")
print("Please input the directory to the hash files, or leave blank")
print("to default to the ./output folder")
directory = input("Directory: ")
finder = input("Input a hash to find: ")
if directory == "":
    directory = "output/"
files = []
print("Indexing files...")
for filename in os.listdir(directory):
    if not filename.startswith("pinhashes_"):
        continue
    files.append(directory+filename)
print(f"Indexed {len(files)} files")

print("Searching, this may take a while...")
found = False
for file in files:
    print(f"Considering {file}")
    try:
        with open(file) as stream:
            for line in stream:
                broken = line.split(" | ")
                if broken[1].strip("\n") == finder:
                    found = True
                    algo = file.split("_", 1)[1].strip(".txt")
                    print(f"Hit: Hash matches PIN {broken[0]} using {algo}")
                    raise StopIteration() # We're done, break out of the loop
    except StopIteration:
        break

if not found:
    print("Couldn't find the PIN corresponding to the hash, exiting...")
    exit()
print("All done!")
