"""Script to extract prior knowledge based on state files.

Example
-------

> python python scripts/get_prior_knowledge.py

or

> python scripts/get_prior_knowledge.py  -s output/tables/example.csv

Authors
-------
- De Bruin, Jonathan
"""

import argparse

from pathlib import Path

from asreview import ASReviewData
from asreview.state import open_state

import pandas as pd


def get_prior_from_state(state):
    """Get prior knowledge from state file."""
    with open_state(state) as s:

        prior_knowledge = s.get("label_idx", 0)
        labels = s.get("labels", 0)

        df = pd.DataFrame({
            "row_number": prior_knowledge,
            "label": labels[prior_knowledge]
        })

        return df


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Merge prior knowledge of states files into single table."
    )
    parser.add_argument(
        '-d',
        type=str,
        default="data",
        help='Dataset folder or glob.')
    parser.add_argument(
        "-o",
        type=str,
        default="output/tables/overview_prior_knowledge.csv",
        help="Output table location")
    args = parser.parse_args()

    # load states
    if Path(args.d).is_dir():
        datasets = Path(args.d).glob("*")
    else:
        datasets = Path(args.d).glob()

    subsets = []
    print("datasets found:")
    for dataset in datasets:
        print(dataset)
        states = Path("output", "simulation", dataset.stem,
                      "state_files").glob("*")

        df_data = ASReviewData.from_file(dataset).df

        print("states found:")
        for state in states:
            print(state)

            # get prior info
            s = get_prior_from_state(state)
            s["dataset_name"] = dataset
            s["state_name"] = state

            # add the title of the paper
            s["title"] = df_data \
                .iloc[s["row_number"].tolist()]["title"].tolist()
            # add titles
            subsets.append(s)

    # export the file to table
    result = pd.concat(subsets, axis=0)

    Path(args.o).parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(Path(args.o), index=False)
    result.to_excel(Path(args.o).with_suffix('.xlsx'), index=False)