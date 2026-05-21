import os
path = 'core/migrations'
print(f"Files in {path}:")
for f in os.listdir(path):
    print(f" - {f}")
