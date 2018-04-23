import os
import sys
import argparse
import mkblob
import pprint
import hashlib
import json


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def hash_tree(tree_root, make_blob):
    """They order in which files and directories are added to the list children might be important for the resulting
    hash value. This could be circumvented by making children a dictionary."""
    hash_subtree = {}
    content_subtree = {}
    for obj in os.scandir(tree_root):
        if obj.is_dir():
            scan = hash_tree(obj.path, make_blob)
            hash_subtree[obj.name] = scan['hash']
            content_subtree[obj.name] = scan
        else:
            try:
                blob = make_blob(obj)
                hash_subtree[obj.name] = blob['hash']
                content_subtree[obj.name] = blob
            except Exception as e:
                print(e)
    # print(tree_root, children)
    return {'hash': hashlib.sha256(json.dumps(hash_subtree).encode('utf-8')).hexdigest(),
            'type': 'd',
            'content': content_subtree}


class Table:
    def __init__(self):
        self.max_name_column_width = 0
        self.max_indentation = 0
        self.rows = []
        self.max_a_column_width = 0

    def append(self, tpl):
        if len(tpl[1])+tpl[0] > self.max_name_column_width:
            self.max_name_column_width = len(tpl[1]) + tpl[0]
        if tpl[0] > self.max_indentation:
            self.max_indentation = tpl[0]
        if len(tpl[4]) > self.max_a_column_width:
            self.max_a_column_width = len(tpl[4])
        self.rows.append(tpl)

    def get_rows(self):
        return self.rows


def compare_trees(a_tree, b_tree, table, level=0):
    """"Spits out a list of tuples (Level, Name, Type, match, a, b)"""
    both = []
    a_only = []
    b_only = []
    for node_name in a_tree.keys():
        if node_name in b_tree.keys():
            if b_tree[node_name]['hash'] == a_tree[node_name]['hash']:
                both.append((node_name, True))
            else:
                both.append((node_name, False))
        else:
            a_only.append(node_name)
    for node in b_tree.keys():
        if node not in a_tree.keys():
            b_only.append(node)

    for node in both:
        if node[1] is True:
            table.append((level, node[0], a_tree[node[0]]['type'], True, '✓', '✓'))
        elif a_tree[node[0]]['type'] == 'd':
            # print("{0}Entering {1}".format(indentation, node[0]))
            table.append((level, node[0], a_tree[node[0]]['type'], False,
                          str(a_tree[node[0]]['hash'])[0:8],
                          str(b_tree[node[0]]['hash'])[0:8]))
            compare_trees(a_tree[node[0]]['content'], b_tree[node[0]]['content'], table, level + 1)
        elif a_tree[node[0]]['type'] == 'f':
            table.append((level, node[0], a_tree[node[0]]['type'], False,
                          str(a_tree[node[0]]['content']),
                          str(b_tree[node[0]]['content'])))
    for node in a_only:
        table.append((level, node, a_tree[node]['type'], False, str(a_tree[node]['hash'])[0:8], 'X'))
    for node in b_only:
        table.append((level, node, b_tree[node]['type'], False, 'X', str(b_tree[node]['hash'])[0:8]))

    return table

# TODO: Move print_table function into the Table class
# TODO: Make colors static members of the Table class as well
def print_table(table):
    indentation = ["".join([" " for _ in range(ind)]) for ind in range(table.max_name_column_width+1)]

    for row in table.get_rows():
        name_spacing = table.max_name_column_width-len(row[1])-row[0]
        a_spacing = table.max_a_column_width-len(row[4])+1
        if row[3]:
            sys.stdout.write(Colors.OKGREEN)
        else:
            sys.stdout.write(Colors.FAIL)
        if row[2] == 'd':
            sys.stdout.write(Colors.OKBLUE)

        print("{0}{1}{2}{3}{4}{5}".format(indentation[row[0]], row[1],
                                          indentation[name_spacing], row[4], indentation[a_spacing], row[5]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a file tree.')
    parser.add_argument('atree',
                        help='The root of the first file tree')
    parser.add_argument('btree',
                        help='The root of the second file tree')
    args = parser.parse_args()

    atree = hash_tree(args.atree, mkblob.size_only)
    # print(ahash[0])
    btree = hash_tree(args.btree, mkblob.size_only)
    # print(bhash[0])

    if atree['hash'] == btree['hash']:
        print("Trees match")
    else:
        tab = Table()
        print_table(compare_trees(atree['content'], btree['content'], tab))
