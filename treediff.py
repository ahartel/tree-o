import os
import argparse
import mkblob
import pprint
import hashlib
import json


def scan_tree(tree_root, make_blob):
    """They order in which files and directories are added to the list children might be important for the resulting
    hash value. This could be circumvented by making children a dictionary."""
    hash_subtree = {}
    content_subtree = {}
    for obj in os.scandir(tree_root):
        if obj.is_dir():
            scan = scan_tree(obj.path, make_blob)
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


def compare_trees(a_tree, b_tree, level=0):

    indentation = "".join([" " for _ in range(level)])

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
            print("{0}{1}\t{2}\t{3}".format(indentation, node[0], '✓', '✓'))
        elif a_tree[node[0]]['type'] == 'd':
            print("{0}Entering {1}".format(indentation, node[0]))
            compare_trees(a_tree[node[0]]['content'], b_tree[node[0]]['content'], level + 1)
        elif a_tree[node[0]]['type'] == 'f':
            print("{0}{1}\t{2}\t{3}".format(indentation,
                                            node[0],
                                            a_tree[node[0]]['content'],
                                            b_tree[node[0]]['content']))

    for node in a_only:
        print("{0}{1}\t{2}\t{3}".format(indentation, node, a_tree[node]['hash'], 'X'))
    for node in b_only:
        print("{0}{1}\t{2}\t{3}".format(indentation, node, 'X', b_tree[node]['hash']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a file tree.')
    parser.add_argument('atree',
                        help='The root of the first file tree')
    parser.add_argument('btree',
                        help='The root of the second file tree')
    args = parser.parse_args()

    atree = scan_tree(args.atree, mkblob.size_only)
    # print(ahash[0])
    btree = scan_tree(args.btree, mkblob.size_only)
    # print(bhash[0])

    if atree['hash'] == btree['hash']:
        print("Trees match")
    else:
        compare_trees(atree['content'], btree['content'])
