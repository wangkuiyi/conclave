from salmon.codegen import CodeGen
from salmon.dag import *
import os, pystache


def op_to_sum(op):
    if op == "+":
        return "sum"


def split_datatypes(cols):
    integers = []
    floats = []

    for i in range(len(cols)):
        if cols[i].typeStr == "INTEGER":
            integers.append(i)
        elif cols[i].typeStr == "STRING":
            # assume elements are stored as strings by default
            pass
        elif cols[i].typeStr == "FLOAT":
            floats.append(i)
        else:
            print("Unknown datatype: {0}".format(cols[i].typeStr))

    return [integers, floats]


class SparkCodeGen(CodeGen):
    def __init__(self, dag, template_directory="{}/templates/spark".format(os.path.dirname(os.path.realpath(__file__)))):
        super(SparkCodeGen, self).__init__(dag)
        self.template_directory = template_directory

    def _generateJob(self, job_name, op_code):

        template = open("{}/job.tmpl".format(self.template_directory), 'r').read()
        data = { 'JOB_NAME': job_name,
                 'SPARK_MASTER': 'local',  # XXX(malte): make configurable
                 'OP_CODE': op_code }

        return pystache.render(template, data)

    def _generateAggregate(self, agg_op):

        aggregator = agg_op.aggregator

        agg_type = 'agg_' + op_to_sum(aggregator)

        template = open("{0}/{1}.tmpl".format(self.template_directory, agg_type), 'r').read()

        data = {
            'KEYCOL': agg_op.keyCol.idx,
            'AGGCOL': agg_op.aggCol.idx,
            'INREL': agg_op.getInRel().name,
            'OUTREL': agg_op.outRel.name
        }

        return pystache.render(template, data)

    def _generateConcat(self, concat_op):

        template = open("{0}/{1}.tmpl".format(self.template_directory, 'concat'), 'r').read()

        data = {
            'INRELS': [rel.name for rel in concat_op.getInRels()],
            'OUTREL': concat_op.outRel.name
        }

        return pystache.render(template, data)

    def _generateCreate(self, create_op):

        template = open("{}/create.tmpl".format(self.template_directory), 'r').read()

        type_lists = split_datatypes(create_op.outRel.columns)

        data = {
                'RELATION_NAME': create_op.outRel.name,
                'INPUT_PATH': "/tmp",  # XXX(malte): make configurable
                'INT_COLS': [i for i in type_lists[0]],
                'FLOAT_COLS': [j for j in type_lists[1]]
               }

        return pystache.render(template, data)

    def _generateJoin(self, join_op):

        leftName = join_op.getLeftInRel().name
        rightName = join_op.getRightInRel().name

        # spark code supports multiple join cols, only need to modify
        # data variables in the future for multiple join cols
        leftJoinCol, rightJoinCol = join_op.leftJoinCol, join_op.rightJoinCol

        template = open("{0}/{1}.tmpl".format(self.template_directory, 'join'), 'r').read()

        data = {
            'LEFT_PARENT': leftName,
            'RIGHT_PARENT': rightName,
            'LEFT_COL': leftJoinCol.idx,
            'RIGHT_COL': rightJoinCol.idx,
            'OUTREL': join_op.outRel.name
        }

        return pystache.render(template, data)

    def _generateProject(self, project_op):

        cols = project_op.selectedCols

        template = open("{0}/{1}.tmpl".format(self.template_directory, 'project'), 'r').read()

        data = {
            'COL_IDS': [c.idx for c in cols],
            'INREL': project_op.getInRel().name,
            'OUTREL': project_op.outRel.name
        }
        return pystache.render(template, data)

    def _generateMultiply(self, mult_op):

        op_cols = mult_op.operands

        if hasattr(op_cols[1], 'idx'):
            scalar = False
            operand = op_cols[1].idx
        else:
            scalar = True
            operand = op_cols[1]

        template = open("{0}/{1}.tmpl".format(self.template_directory, 'multiply'), 'r').read()

        data = {
            'OPERAND': operand,
            'SCALAR': scalar,
            'TARGET_ID': mult_op.targetCol.idx,
            'INREL': mult_op.getInRel().name,
            'OUTREL': mult_op.outRel.name
        }

        return pystache.render(template, data)

    def _generateStore(self, store_op):

        template = open("{}/store.tmpl".format(self.template_directory), 'r').read()
        data = {
                'RELATION_NAME': store_op.outRel.name,
                'OUTPUT_PATH': "/tmp"  # XXX(malte): make configurable
               }

        return pystache.render(template, data)

    def _writeCode(self, code, output_directory, job_name):
        # write code to a file
        outfile = open("{}/{}.py".format(output_directory, job_name), 'w')
        outfile.write(code)