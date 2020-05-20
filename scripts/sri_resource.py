r"""
Command to generate the SRI resource integrity hashes and store them in the `config/sri.json` file.

========
Examples
========

Generate an integrity hash for a single file & add it to `config/sri.json`::

>python ./scripts/sri_resource.py "$(publicdist)/main.min.js"

Generate integrity hashes for a bunch of files & add them to `config/sri.json`::

>find $(publicdist)/vendor/*.js -exec python ./scripts/sri_resource.py {} \;
"""

import json
import os
import re
import subprocess
import sys

hash_type = "sha384"

if len(sys.argv) < 2 or not os.path.isfile(sys.argv[1]):
    sys.exit(1)

file_path = os.path.abspath(sys.argv[1])

try:
    sri_hash = subprocess.run(
        f"cat {file_path} | openssl dgst -{hash_type} -binary | openssl base64 -A",
        stdout=subprocess.PIPE,
        shell=True,
    ).stdout.decode("utf-8")
except:
    sys.exit(1)

try:
    data = json.load(open("config/sri.json", "r"))
except:
    data = {}

data[
    re.sub(r"[^a-z0-9]+", "_", os.path.basename(sys.argv[1]))
] = f"{hash_type}-{sri_hash}"

with open("config/sri.json", "w+") as sri:
    sri.write(json.dumps(data))
