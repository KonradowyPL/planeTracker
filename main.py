#!/usr/bin/python3
import sys
from src.main import run


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        delta = 0
    else:
        delta = int(sys.argv[1])
    run(delta=delta)
