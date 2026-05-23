content = open("src/agentbox/ui/styles.py").read()

replacements = {
    "#42D392": "#8af050",
    "#3BC47E": "#76e648",
    "#5EDFA4": "#b4f026",
    "#4DD898": "#9df026",
    "#7EEABD": "#c8f048",
    "#2B5E42": "#3B6B22",
    "#1C2A24": "#1D2A1C",
    "#D9FFE9": "#EAFFD9",
}

for old, new in replacements.items():
    content = content.replace(old, new)

open("src/agentbox/ui/styles.py", "w").write(content)
