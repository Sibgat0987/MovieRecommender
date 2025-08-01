import json

with open("Movie-recommender-system.ipynb", "r", encoding="utf-8") as f:
    notebook = json.load(f)

with open("movie_recommender.py", "w", encoding="utf-8") as f:
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            f.write("# --------- Cell ---------\n")
            f.writelines(cell["source"])
            f.write("\n\n")
