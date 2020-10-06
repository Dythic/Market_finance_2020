#!/usr/bin/env python3

import fxcmpy
import sys
import re
import os
from modules.instrument import Instrument
from dotenv import load_dotenv

_instruments = []

def main():
    load_dotenv()
    fx = fxcmpy.fxcmpy(access_token=os.getenv("FXCM_API_KEY"), log_level="error")
    print("Connection to FXCM etablished")
    instruments = fx.get_instruments()
    for i in instruments:
        if re.compile("[A-Z]{3}\/[A-Z]{3}").match(i):
            d = Instrument(i, fx)
            _instruments.append(d)
            print('Succesfully init class for {}'.format(i))
    fx.close()

if __name__ == '__main__':
    main()
 