'''A bunch of evaluation functions for the different SuperLim tasks.

See the comment block and the list of defined functions starting from
line 200.

Gerlof Bouma
Språkbanken Text / Dept Swedish, Multilingualism, Language Technology
University of Gothenburg
vX 20230303

'''
# Standard Library
import sys
import json
import io  # for io.IOBase
import os  # for os.PathLike

# SuperLim-specific
import kralpha
import evaluate


# Auxiliary functions to read datafiles and run a pre-evaluation sanity check
#
def _read_data_from_jsonl_file(file_):
    """Reads data (items including labels, either from gold data or from
    system prediction) from a JSONLines file.

    Args:
        file_: a string, bytes, PathLike or IOBase object that locates the
            JSONLines file to be read

    Returns:
        the contents of the jsonl file as a list

    Exceptions:
        TypeError: if file_ is not of type string, bytes, PathLike or IOBase.
        JSONDecodeError: if anything is wrong with the jsonl
            file. Because the JSON parser is called on each individual
            line, the reported lineno is always 1. Use something else
            to validate your jsonl file!

    """

    if isinstance(file_, io.IOBase):
        data = list(map(json.loads, file_))

    elif isinstance(file_, (str, bytes, os.PathLike)):
        with open(file_) as f:
            data = list(map(json.loads, f))

    else:
        raise TypeError('[Read data] I don\'t know how to read from this kind of '
                        'object: %s. Must be stringlike, pathlike, or filelike.'
                        % (type(file_),))

    return data


def _sanity_check(gold_data, system_data, output_name='label'):
    """Sanity check to be run before comparing a set of system predictions
    with a gold standard. Checks a number of things, but most
    importantly it inspects the paired items to see if they are the
    same (apart from the label). This helps to make sure that each
    system prediction is compared to the right gold standard item.

    Args:
        gold_data: a list of dictionaries containing the gold standard items
        system_data: a list of dictionaries containing the items with
            system predictions
        output_name: the name used for the variable that contains the
            output, as string. Defaults to 'label'.

    Exceptions:
        Exception: generic exception with details in the message text is 
            raised when problems are found with the data. Error location 
            is given in terms of (guessed) linenumbers. If your data does 
            not come directly from a file, these may be wrong.

    """
    if len(gold_data) != len(system_data):
        raise Exception('[Sanity check] Gold and system data files are of '
                        'differing length.')

    for i, gold_datapoint in enumerate(gold_data):

        system_datapoint = system_data[i].copy()  # NOTE! Copy, to be mutated!

        if not isinstance(system_datapoint, dict):
            raise Exception('[Sanity check] Line %s in the system data file is '
                            'not a JSON object (but array, string, number, etc).'
                            % (i+1,))

        if output_name not in system_datapoint:
            raise Exception('[Sanity check] Line %s in the system data file '
                            f'does not have the \'{output_name}\' attribute.'
                            % (i+1,))

        system_datapoint[output_name] = gold_datapoint[output_name]
        if "prediction" in system_datapoint:
            system_datapoint.pop("prediction")
        # TODO fix for added prediction elemente
        if system_datapoint != gold_datapoint:
            print(system_datapoint)
            print(gold_datapoint)
            print("#"*50)
            raise Exception('[Sanity check] Line %s in the gold and system data '
                            'files differ (not just in label).'
                            % (i+1,))

    # No complaints
    return


# Generic evaluation functions
#
def _evaluate_alphanominal(gold_file, system_file, output_name='label'):
    """Evaluate nominal scale system predictions in system_file against the
    gold standard in gold_file, and report as Krippendorff's α.

    Args:
        gold_file: a file name or file object with the gold standard data.
        system_file: a file name or file object with the gold standard data.

    Returns: 
        a dictionary with key 'alpha' for Krippendorff's α for nominal
        data (float), and a key 'N' for the number of data points
        (integer).
    """
    gold_data = _read_data_from_jsonl_file(gold_file)
    system_data = _read_data_from_jsonl_file(system_file)
    _sanity_check(gold_data, system_data, output_name=output_name)

    gold_labels = [datapoint[output_name] for datapoint in gold_data]

    if "prediction" in system_data[0]:
        system_labels = [datapoint['prediction'] for datapoint in system_data]
    else:
        system_labels = [datapoint[output_name] for datapoint in system_data]

    R = {}
    R['N'] = len(gold_labels)
    R['alpha'] = kralpha.krippendorff_alpha([gold_labels, system_labels],
                                            metric=kralpha.nominal_metric,
                                            convert_items=str)
    return R


def _evaluate_alphainterval(gold_file, system_file, output_name='label'):
    """Evaluate interval scale system predictions in system_file against the
    gold standard in gold_file, and report as Krippendorff's α.

    Args:
        gold_file: a file name or file object with the gold standard data.
        system_file: a file name or file object with the gold standard data.

    Returns: 
        a dictionary with key 'alpha' for Krippendorff's α for
        interval data (float), and a key 'N' for the number of data
        points (integer).
    """
    gold_data = _read_data_from_jsonl_file(gold_file)
    system_data = _read_data_from_jsonl_file(system_file)
    _sanity_check(gold_data, system_data, output_name=output_name)

    gold_labels = [datapoint[output_name] for datapoint in gold_data]
    if "prediction" in system_data[0]:
        system_labels = [datapoint['prediction'] for datapoint in system_data]
    else:
        system_labels = [datapoint[output_name] for datapoint in system_data]

    R = {}
    R['N'] = len(gold_labels)
    R['alpha'] = kralpha.krippendorff_alpha([gold_labels, system_labels],
                                            metric=kralpha.interval_metric,
                                            convert_items=float)
    return R


def _evaluate_accuracy(gold_file, system_file, output_name='label'):
    """Evaluate system predictions in system_file against the gold
    standard in gold_file, and report as accuracy (=proportion of
    correct predictions).

    Note that accuracy does nothing but directly compare prediction
    and gold label, and is therefore completely agnostic about the
    measurement scale and about the type of task (classification,
    selection, open vocabulary completion, etc).

    Args:
        gold_file: a file name or file object with the gold standard data.
        system_file: a file name or file object with the gold standard data.

    Returns: 
        a dictionary with key 'accuracy' for accuracy (float) for and
        a key 'N' for the number of data points (integer).

    """
    gold_data = _read_data_from_jsonl_file(gold_file)
    system_data = _read_data_from_jsonl_file(system_file)
    _sanity_check(gold_data, system_data, output_name=output_name)

    gold_labels = [datapoint[output_name] for datapoint in gold_data]
    if "prediction" in system_data[0]:
        system_labels = [datapoint['prediction'] for datapoint in system_data]
    else:
        system_labels = [datapoint[output_name] for datapoint in system_data]

    correct = sum(gold_label == system_label
                  for gold_label, system_label in zip(gold_labels, system_labels))

    R = {}
    R['N'] = len(gold_labels)
    R['accuracy'] = correct/R['N']

    return R


# These are the tasks and their evaluation measures. The associated
# functions follow below – without any further comments/documentation!
# Where the official SuperLim task identifiers have a '-' (hyphen),
# the corresponding evaluation function has a '_' (underscore).
#
# All functions take two files (gold standard and system predictions),
# in the same way as the _evaluate_YYYY functions above, and return a
# dictionary with information.
#
#   absabank-imm                   Alpha (interval)
#   argumentation_sentences        Alpha (nominal)
#   dalaj-ged-superlim 	           Alpha (nominal)
#   supersim-superlim-relatedness  Alpha (interval)
#   supersim-superlim-similarity   Alpha (interval)
#   sweanalogy 	                   Accuracy (~= Pseudoalpha)
#   swediagnostics 	           Alpha (nominal)
#   swedn 	                   Harmonic mean ('F1') of Rouge and Bleu
#                                      ^^^NOT CURRENTLY IMPLEMENTED!
#   swefaq 	                   Pseudoalpha
#                                      = (Accuracy - 109/2049) / (1940/2049)
#   swenli 	                   Alpha (nominal)
#   sweparaphrase 	           Alpha (interval)
#   swesat-synonyms 	           Pseudoalpha = (Accuracy - 1/5) / (4/5)
#   swewic 	                   Alpha (nominal)
#   swewinogender 	           Alpha (nominal) and parity: number of items with
#                                        identical tuple_ids that get the same label
#   swewinograd                    Alpha (nominal)

def evaluate_absabank_imm(gold_file, system_file):
    return _evaluate_alphainterval(gold_file, system_file)


def evaluate_argumentation_sentences(gold_file, system_file):
    return _evaluate_alphanominal(gold_file, system_file)


def evaluate_dalaj_ged_superlim(gold_file, system_file):
    return _evaluate_alphanominal(gold_file, system_file)


def evaluate_supersim_superlim_relatedness(gold_file, system_file):
    return _evaluate_alphainterval(gold_file, system_file)


def evaluate_supersim_superlim_similarity(gold_file, system_file):
    return _evaluate_alphainterval(gold_file, system_file)


def evaluate_sweanalogy(gold_file, system_file):
    R = _evaluate_accuracy(gold_file, system_file)
    R['pseudoalpha'] = R['accuracy']
    return R


def evaluate_swediagnostics(gold_file, system_file):
    return _evaluate_alphanominal(gold_file, system_file)


def evaluate_swedn(gold_file, system_file):
    # measures
    # rouge = evaluate.load("rouge")
    # bleu = evaluate.load("bleu")
    purple = evaluate.combine(["rouge", "bleu"])

    label = "summary"
    gold_data = _read_data_from_jsonl_file(gold_file)
    system_data = _read_data_from_jsonl_file(system_file)
    _sanity_check(gold_data, system_data, output_name=label)

    gold_labels = [[datapoint[label]] for datapoint in gold_data]

    if "prediction" in system_data[0]:
        system_labels = [datapoint['prediction'] for datapoint in system_data]
    else:
        system_labels = [datapoint[label] for datapoint in system_data]

    _results = purple.compute(references=gold_labels,
                              predictions=system_labels)
    results = {}
    results["rouge1"] = _results["rouge1"]
    results["rouge2"] = _results["rouge2"]
    results["rougeL"] = _results["rougeL"]
    results["bleu"] = _results["bleu"]
    results["translation_length"] = _results["translation_length"]
    results["reference_length"] = _results["reference_length"]
    # print(results)
    # results["f1"] = 2 * results["bleu"] * results["rouge"] / (results["rouge"] + results["bleu"])
    return results
    raise NotImplementedError()


def evaluate_swefaq(gold_file, system_file):
    R = _evaluate_accuracy(gold_file, system_file)
    R['pseudoalpha'] = (R['accuracy'] - 109/2049) / (1940/2049)
    return R


def evaluate_swenli(gold_file, system_file):
    return _evaluate_alphanominal(gold_file, system_file)


def evaluate_paraphrase(gold_file, system_file):
    return _evaluate_alphainterval(gold_file, system_file)


def evaluate_swesat_synonyms(gold_file, system_file):
    R = _evaluate_accuracy(gold_file, system_file)
    R['pseudoalpha'] = (R['accuracy'] - 1/5) / (4/5)
    return R


def evaluate_swewic(gold_file, system_file):
    return _evaluate_alphanominal(gold_file, system_file)


def evaluate_swewinogender(gold_file, system_file):
    gold_data = _read_data_from_jsonl_file(gold_file)
    system_data = _read_data_from_jsonl_file(system_file)
    _sanity_check(gold_data, system_data)

    gold_labels = [datapoint['label'] for datapoint in gold_data]
    if "prediction" in system_data[0]:
        system_labels = [datapoint['prediction'] for datapoint in system_data]
    else:
        system_labels = [datapoint['label'] for datapoint in system_data]
    tuple_ids = [datapoint['meta']['tuple_id'] for datapoint in gold_data]

    R = {}
    R['N'] = len(gold_labels)
    R['alpha'] = kralpha.krippendorff_alpha([gold_labels, system_labels],
                                            metric=kralpha.nominal_metric,
                                            convert_items=str)

    # Parity looks at how often the prediction is the same accross
    # tuple_id, irrespective of whether this prediction is correct.
    system_labels_by_tuple_id = {tuple_id: [] for tuple_id in tuple_ids}
    for tuple_id, system_label in zip(tuple_ids, system_labels):
        system_labels_by_tuple_id[tuple_id].append(system_label)

    identical = sum(label1 == label2 == label3
                    for label1, label2, label3 in system_labels_by_tuple_id.values())
    R['parity'] = identical/R['N']

    return R


def evaluate_swewinograd(gold_file, system_file):
    return _evaluate_alphanominal(gold_file, system_file)


if __name__ == '__main__':

    # Just a silly example, only testing the swewic evaluation code
    # and an unnecessary use of pathlib
    from pathlib import Path
    gold_filepath = Path(sys.argv[1])
    system_filepath = Path(sys.argv[2])

    print(evaluate_swewic(gold_filepath, system_filepath))
