content = open('src/agentbox/catalog.py').read()
# Find the line "# ── Catalog singleton"
parts = content.split("# ── Catalog singleton ─────────────────────────────────────────────────────────────")
top_part = parts[0]
bottom_part = parts[1]

# Split bottom_part at "_GENERAL_README = "
sub_parts = bottom_part.split("_GENERAL_README = \"\"\"\\")
singleton_and_store = "# ── Catalog singleton ─────────────────────────────────────────────────────────────" + sub_parts[0]
constants_part = "_GENERAL_README = \"\"\"\\" + sub_parts[1]

# Reassemble: top_part + constants_part + singleton_and_store
new_content = top_part + constants_part + "\n" + singleton_and_store

# Fix imports
new_content = new_content.replace("import json\nfrom pathlib import Path\n", "")
new_content = new_content.replace("from dataclasses import dataclass", "import json\nfrom dataclasses import dataclass\nfrom pathlib import Path")

open('src/agentbox/catalog.py', 'w').write(new_content)
