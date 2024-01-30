# !/bin/sh

echo -e 'FORMATTING PYTHON FILES'
# this makes eligible files PEP8 compliant automatically
yapf --recursive -i .
echo -e 'FORMATTING PYTHON FILES: COMPLETED\n\n'

echo -e 'RUNNING PYTHON LINTER\n'
# this shows us which files are not PEP8 compliant
flake8
echo -e '\n\nRUNNING PYTHON LINTER: COMPLETED'