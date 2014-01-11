# -*- coding: utf-8 -*-
import sys
sys.path.append('../')

import zoro

def test_version():
    assert zoro.__version__ is not None
