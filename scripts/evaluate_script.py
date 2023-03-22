import json
import argparse
import random
import os
import evaluate
from collections import defaultdict

import superlim_evaluate as supeval

TASKS = {
    'absabank-imm': supeval.evaluate_absabank_imm,
    'argumentation-sentences': supeval.evaluate_argumentation_sentences,
    'dalaj-ged-superlim': supeval.evaluate_dalaj_ged_superlim,
    'supersim-superlim-relatedness': supeval.evaluate_supersim_superlim_relatedness,
    'supersim-superlim-similarity': supeval.evaluate_supersim_superlim_similarity,
    'sweanalogy': supeval.evaluate_sweanalogy,
    'swediagnostics': supeval.evaluate_swediagnostics,
    'swedn': supeval.evaluate_swedn,
    'swefaq': supeval.evaluate_swefaq,
    'swenli': supeval.evaluate_swenli,
    'sweparaphrase': supeval.evaluate_paraphrase,
    'swesat-synonyms': supeval.evaluate_swesat_synonyms,
    'swewic': supeval.evaluate_swewic,
    'swewinogender': supeval.evaluate_swewinogender,
    'swewinograd': supeval.evaluate_swewinograd,
}
ONLY_TEST = ["swewinogender", "supersim-superlim-relatedness",
             "supersim-superlim-similarity", "sweanalogy", "swediagnostics", "swesat-synonyms"]
CLASS_TASK = ['argumentation-sentences', 'dalaj-ged-superlim',
              'swediagnostics', 'swenli', 'swewic', 'swewinogender', 'swewinograd']


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-folder")
    parser.add_argument("--reference-folder")
    parser.add_argument("--results-file", default="../entry_template.json")
    parser.add_argument("--results-outfile", default="updated_results.json")
    parser.add_argument(
        "--tasks", choices=list(TASKS.keys()) + ["all"], nargs="+")

    return parser.parse_args()


def main():

    # acc_f1 = evaluate.combine(["accuracy", "f1"])
    acc = evaluate.load("accuracy")
    f1 = evaluate.load("f1")
    spear_pear = evaluate.combine(["spearmanr", "pearsonr"])

    args = get_args()

    if args.results_file:
        with open(args.results_file) as fin:
            results = json.load(fin)

    if "all" in args.tasks:
        args.tasks = TASKS.keys()

    # results["tasks"] = {}
    for t in args.tasks:
        if t not in os.listdir(args.experiment_folder):
            continue
        # This is mainly to make swedn work unless the key gets changed
        label = "label"
        prediction = "prediction"
        if t == "swedn":
            label = "summary"
            prediction = "prediction"

        results["tasks"][t] = {}
        for devtest in ["dev", "test"]:
            if t in ONLY_TEST and devtest == "dev":
                continue

            results["tasks"][t][devtest] = {}

            if t.startswith("supersim"):
                gold_file = os.path.join(
                    args.reference_folder, "supersim-superlim", f"{t}_{devtest}.jsonl")
            else:
                gold_file = os.path.join(
                    args.reference_folder, t, f"{t}_{devtest}.jsonl")
            pred_file = os.path.join(
                args.experiment_folder, t, f"{devtest}.jsonl")

            r = TASKS[t](gold_file, pred_file)

            l2i = defaultdict(lambda: len(l2i))
            gold = []
            with open(gold_file) as fin:
                for line in fin:
                    jline = json.loads(line)
                    if type(jline[label]) == str:
                        gold.append(l2i[jline[label]])
                    else:
                        gold.append(jline[label])

            pred = []
            with open(pred_file) as fin:
                for line in fin:
                    jline = json.loads(line)
                    if type(jline[label]) == str:
                        pred.append(l2i[jline[prediction]])
                    else:
                        pred.append(jline[prediction])
            measure = acc if type(gold[0]) == int else spear_pear
            r.update(measure.compute(references=gold, predictions=pred))
            if t in CLASS_TASK:
                r.update(f1.compute(references=gold,
                         predictions=pred, average="macro"))
            results["tasks"][t][devtest] = r

    with open(args.results_outfile, "w") as fout:
        json.dump(results, fout, indent=4)

    return


if __name__ == "__main__":
    main()
