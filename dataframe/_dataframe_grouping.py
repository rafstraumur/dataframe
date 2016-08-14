# @author = 'Simon Dirmeier'
# @email = 'rafstraumur@simon-dirmeier.net'
import numpy
from prettytable import PrettyTable
import dataframe

from ._dataframe_group import DataFrameGroup


class DataFrameGrouping:
    """
    Class that holds information o how every row in a data frame is grouped into subsets.
    """

    def __init__(self, obj, *args):
        self.__dataframe = obj
        # the indexes of the columns of the original table that are used for grouping
        self.__grouping_col_idx = obj.which_colnames(*args)
        # the column names of the original table that are used for grouping
        self.__grouping_col_names = args
        # the array if values that produces a group ( e.g. 0 -> [0,1], 1 -> [1,0], etc.)
        self.__grouping_values = {}
        # indexing tree for logarithmic lookup of group index
        self.__search_tree = dataframe.SearchTree()
        # array of group indexes for every row, i.e. every element is the group index the row belongs to
        self.__group_idxs = numpy.zeros(obj.nrow()).astype(int)
        # groups: maps from grp index to group object
        self.__groups = dict()
        self.__group_by()

    def __iter__(self):
        for k, v in self.__groups.items():
            yield k, v

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.__groups[item]

    def __str__(self):
        pt = PrettyTable(self.__dataframe.colnames())
        for i, group in enumerate(self.__groups.values()):
            if i > 1:
                break
            for j, row in enumerate(group):
                if j < 5:
                    pt.add_row(row.values())
            if i == 0:
                pt.add_row(["---"] * len(self.__dataframe.colnames()))
        return pt.__str__()

    def grouping_colnames(self):
        return self.__grouping_col_names

    def groups(self):
        """
        Getter the values of the group dictionary, i.e. the Group objects

        :return: returns the groupings of the rows
        :rtype: list(DataFrameGroup)
        """
        return self.__groups.values()

    def ungroup(self):
        """
        Getter for the normal DataFrame object without grouping information.

        :return: returns the ungrouped DataFrame
        :rtype: DataFrame
        """
        return self.__dataframe

    def __group_by(self):
        self.__set_grp_idxs()
        self.__set_groups()

    def __set_grp_idxs(self):
        # iterate over all rows from the dataframe and assign each row a group index
        for row in self.__dataframe:
            els = [row[x] for x in self.__grouping_col_idx]
            grp_idx = self.__search_tree.find(*els)
            self.__group_idxs[row.idx()] = grp_idx
            self.__grouping_values[str(grp_idx)] = els

    def __set_groups(self):
        # iterate over the array of group assignments
        # add each row of the original DataFrame to the specific group
        # get unique group indexes
        for grp_idx in numpy.unique(self.__group_idxs):
            # get the row indexes of the original data frame that belong to group 'grp_idx' and cast to list
            row_idxs = list(numpy.where(self.__group_idxs == grp_idx)[0])
            # get the columns with the respective indexes from the dataframe
            group_columns = {x: self.__dataframe[x][row_idxs] for x in self.__dataframe.colnames()}
            # add the rows to a new group
            self.__groups[str(grp_idx)] = DataFrameGroup(grp_idx,
                                                         row_idxs,
                                                         self.__grouping_values[str(grp_idx)],
                                                         self.__grouping_col_names,
                                                         **group_columns)
