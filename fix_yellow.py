
content = open("src/agentbox/ui/styles.py").read()

# Restore text selections and check colors to explicitly be yellow
content = content.replace("color: #8af050;", "color: #FACC15;") # Yellow for selected text/buttons
content = content.replace("border: 1px solid #3B6B22;", "border: 1px solid #4ADE80;") # Green border for active states
content = content.replace("background-color: #1D2A1C;", "background-color: #16221A;") # Dark green background for active states

# Gradient for primary buttons (Yellow to Green)
content = content.replace(
    "stop:0 #8af050, stop:1 #76e648",
    "stop:0 #FACC15, stop:1 #4ADE80"
)
content = content.replace(
    "border: 1px solid #b4f026;",
    "border: 1px solid #FACC15;"
)

# Gradient hover
content = content.replace(
    "stop:0 #b4f026, stop:1 #9df026",
    "stop:0 #FDE047, stop:1 #86EFAC"
)
content = content.replace(
    "border-color: #c8f048;",
    "border-color: #FEF08A;"
)

open("src/agentbox/ui/styles.py", "w").write(content)
