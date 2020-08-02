import os
import glob

for f in glob.glob('cashbox/*.twenty'):
    os.remove(f)
