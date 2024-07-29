#!/bin/sh

echo 'FORMATTING PYTHON FILES'
# this makes eligible files PEP8 compliant automatically
yapf --recursive -i accounts notifications
echo 'FORMATTING PYTHON FILES: COMPLETED'

echo '------------------------------------------------------------'

echo 'RUNNING PYTHON LINTER'
# this shows us which files are not PEP8 compliant
flake8 accounts localcontexts
echo 'RUNNING PYTHON LINTER: COMPLETED'
