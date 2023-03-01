import json
from fix_format import fix_data_size


tasks = {"ABSA": "absabank-imm",
         "": "argumentation_sentences",
         "DaLAJ": "dalaj-ged-superlim",
         "SuperSim": "supersim-superlim-relatedness",
         "": "supersim-superlim-similarity",
         "Swedish Analogy": "sweanalogy",
         "SweDiagnostics": "swediagnostics",
         "": "swedn",
         "Swedish FAQ": "swefaq",
         "SweMNLI": "swemnli",
         "SweParaphrase": "sweparaphrase",
         "SweSAT": "swesat-synonyms",
         "SweWiC": "swewic",
         "SweWinogender": "swewinogender",
         "SweWinograd": "swewinograd",
         }


def read_md_table(fin):
    categories = None
    table = {}
    for line in fin:
        if line.startswith("|"):
            line = [x.strip() for x in line.split("|") if x.strip()]
            if categories is None:
                categories = line
                for c in categories:
                    table[c] = []
            elif not line[0].startswith("-"):
                for x, c in zip(line, categories):
                    try:
                        x = float(x)
                    except ValueError:
                        x = "_".join(x.split())
                        pass
                    table[c].append(x)
    return table


def main():
    with open("dev.md") as dev_in:
        dev = read_md_table(dev_in)
    with open("test.md") as test_in:
        test = read_md_table(test_in)
    with open("winogender.md") as winogender_in:
        winogender = read_md_table(winogender_in)
    
    for i, model in enumerate(dev["Model"]):
        with open("entry_template.json") as fin:
            results = json.load(fin)
        old_name = model.replace("_", " ").replace("/", "-")
        with open(f"model_deliverables/{old_name}.json") as fin:
            old_results = json.load(fin)
        for task in filter(lambda x: x != "Model", dev.keys()):
            if task in tasks:
                proper_name = tasks[task]
                dev_val = dev[task][i]
                test_val = test[task][i]
                try:
                    results["tasks"][proper_name]["dev"]["alpha"] = dev_val
                    results["tasks"][proper_name]["test"]["alpha"] = test_val
                except Exception as e:
                    print(task, proper_name, results["tasks"][proper_name])
        results["repo_link"] = old_results["repo_link"]
        results["model"] = old_results["model"]
        results["model_card"] = old_results["model_card"]
        if model in winogender["Model"]:
            for i, _model in enumerate(winogender["Model"]):
                if _model == model:
                    results["tasks"]["swewinogender"]["test"]["alpha"] = winogender["SweWinogender (Alpha)"][i]
                    results["tasks"]["swewinogender"]["test"]["parity"] = winogender["SweWinogender (Parity)"][i]
        model = model.replace("/", "-")
        results = fix_data_size(results) 
        with open(f"submissions/{model}.json", "w") as fout:
            json.dump(results, fout, indent=4)

    
               

if __name__ == "__main__":
    main()
            