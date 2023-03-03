import json
import argparse

import superlim_evaluate as supeval

TASKS = {
'absabank-imm'                 : supeval.evaluate_absabank_imm,
'argumentation_sentences'      : supeval.evaluate_argumentation_sentences,
'dalaj-ged-superlim'           : supeval.evaluate_dalaj_ged_superlim,
'supersim-superlim-relatedness': supeval.evaluate_supersim_superlim_relatedness,
'supersim-superlim-similarity' : supeval.evaluate_supersim_superlim_similarity,
'sweanalogy'                   : supeval.evaluate_sweanalogy,
'swediagnostics'               : supeval.evaluate_swediagnostics,
'swedn'                        : supeval.evaluate_swedn,
'swefaq'                       : supeval.evaluate_swefaq,
'swemnli'                      : supeval.evaluate_swemnli,
'sweparaphrase'                : supeval.evaluate_paraphrase,
'swesat-synonyms'              : supeval.evaluate_swesat_synonyms,
'swewic'                       : supeval.evaluate_swewic,
'swewinogender'                : supeval.evaluate_swewinogender,
'swewinograd'                  : supeval.evaluate_swewinograd,
}


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment-folder")
    parser.add_argument("--results-file", default="../entry_template.json")
    parser.add_argument("--results-outfile", default="updated_results.json")
    parser.add_argument("--tasks", choices=TASKS.keys(), nargs="+")

    return parser.parse_args()

def main():
    args = get_args()

    if args.results_file:
        with open(args.results_file) as fin:
            results = json.load(fin)
    

    for t in args.tasks:
        print(t)
        t_ = t
        _t = t
        if t == "absabank-imm":
            _t = "ABSAbank-Imm"
        elif t.startswith("supersim-superlim"):
            t_ = "supersim-superlim"
        elif t == "argumentation_sentences":
            t_ = "argumentation-sentences"
            _t = "argumentation-sentences"
        elif t == "swemnli":
            _t = "swenli"
            t_ = "swenli"

        # try:
        if True:
            if t == "sweanalogy" or t == "swedn":
                continue
            if t == "swewinogender":
                print(TASKS[t](f"../../SuperLim-dev/{t_}/{_t}.jsonl", f"../../SuperLim-dev/{t_}/{_t}.jsonl"))
                pred = supeval._read_data_from_jsonl_file(f"../../SuperLim-dev/{t_}/{_t}.jsonl")
                label = pred[0]["label"]
                for x in pred:
                    x["label"] = label
                with open("fake.jsonl", "w") as fout:
                    for line in pred:
                        print(json.dumps(line), file=fout)
                print(TASKS[t](f"../../SuperLim-dev/{t_}/{_t}.jsonl", "fake.jsonl"))
            else:
                print(TASKS[t](f"../../SuperLim-dev/{t_}/{_t}_test.jsonl", f"../../SuperLim-dev/{t_}/{_t}_test.jsonl"))
                pred = supeval._read_data_from_jsonl_file(f"../../SuperLim-dev/{t_}/{_t}_test.jsonl")
                label = pred[0]["label"]
                for x in pred:
                    x["label"] = label
                with open("fake.jsonl", "w") as fout:
                    for line in pred:
                        print(json.dumps(line), file=fout)
                print(TASKS[t](f"../../SuperLim-dev/{t_}/{_t}_test.jsonl", "fake.jsonl"))
        # except Exception as e:
        #     print(t, _t, t_, e)

    with open("updated_results.jsonl", "w") as fout:
        json.dump(results, fout, indent=4)
    


if __name__ == "__main__":
    main()