import json
import csv


def main():
    tasks = {}
    submission_dict = {"repo_link": None,
                       "model": {
                                 "model_name": None,
                                 "model_type": None,
                                 "number_params": None,
                                 "data_size": None
                                 },
                       "tasks": tasks,
                       "model_card": None,
                       }
    with open("tasks.tsv") as fin:
        reader = csv.reader(fin, delimiter="\t")
        rows = [x for x in reader][1:]
        for row in rows:
            task = row[0]
            metric = row[4]
            split = row[5]

            split = [x.strip() for x in split.split(",")]
            if "train" in split:
                split.remove("train")
            if "split" in split:
                split.remove("split")
                split.append("test")

            metric = "alpha"
            if task == "sweanalogy":
                metric = "accuracy"
            elif task == "swedn":
                metric = "f1"
            elif task == "swewinogender":
                metric = ("alpha", "parity")

            tasks[task] = {}
            for dt in split:
                tasks[task][dt] = {}
                tasks[task][dt]["other"] = None
                if type(metric) == tuple:
                    for metric_i in metric:
                        tasks[task][dt][metric_i] = None
                else:
                    tasks[task][dt][metric] = None
        with open("new_template.json", "w") as fout:
            json.dump(submission_dict, fout, indent=4)
        return submission_dict




if __name__ == "__main__":
    main()