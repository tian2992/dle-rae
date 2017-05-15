#!/usr/bin/python3

import dle
import sys

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        print(dle.search(sys.argv[1]))
    else:
        print("Usage:")
        print("  " + sys.argv[0] + " palabra")
