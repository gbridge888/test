#!/hds/eda/virtualenv/3.7.4/venv/bin/python

import chardet
import os

for root, dirs, names in os.walk('.'):
    print root
    for n in names:
    print '%s => %s (%s)' % (n, chardet.detect(n)['encoding'], chardet.detect(n)['confidence'])
