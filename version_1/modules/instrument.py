#!/usr/bin/env python3

import os
from dotenv import load_dotenv

class Instrument:
    name = ""
    values = []

    def __init__(self, name, fx):
        load_dotenv()
        self.name = name
        self.fx = fx
        self.init_clandles()

    def init_clandles(self):
        d = self.fx.get_candles(self.name, period="m1", number=10)
        self.values.insert(0, d)

    def update(self):
        d = self.fx.get_candles(self.name, period=os.getenv("UPDATE_PERIOD"), number=1)
        self.values.insert(0, d)
