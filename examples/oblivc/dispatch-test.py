import conclave.lang as sal
from conclave.utils import *
from conclave import workflow


def protocol():
    """
    Define inputs and operations to be performed between them.
    """

    """
    Define input datasets
    """
    cols_in_a = [
        defCol('a', 'INTEGER', [1]),
        defCol('b', 'INTEGER', [1]),
    ]
    cols_in_b = [
        defCol('a', 'INTEGER', [2]),
        defCol('b', 'INTEGER', [2]),
    ]

    """
    Create input relations.
    """
    in1 = sal.create("in1", cols_in_a, {1})   ## input file should be at {{{input_path}}}/in1.csv
    in2 = sal.create("in2", cols_in_b, {2})

    """
    Specify relations (docs at conclave/lang.py)
    """
    cc1 = sal.concat([in1, in2], 'cc1', ['a', 'b'])

    agg1 = sal.aggregate(cc1, 'agg1', ['b'], 'a', '+', 'b')

    sal.collect(agg1, 1)

    return {in1, in2}


if __name__ == "__main__":
    workflow.run(protocol)
