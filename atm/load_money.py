import sys
from uuid import uuid4
from pathlib import Path

amount = int(sys.argv[1])
count = amount / 20
count_int = int(count)
if count == count_int:
    for _ in range(count_int):
        Path(f'cashbox/{uuid4()}.twenty').touch()
else:
    print('Amount must be a multiple of 20.')
