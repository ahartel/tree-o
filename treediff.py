import hashlib
import PIL.Image
import json
import os
import argparse
import mkblob
import pprint


def scan_tree(tree_root, make_blob):
    """They order in which files and directories are added to the list children might be important for the resulting
    hash value. This could be circumvented by making children a dictionary."""
    children = {}
    subtree = {}
    for obj in os.scandir(tree_root):
        if obj.is_dir():
            scan = scan_tree(obj.path, make_blob)
            children[obj.name] = scan[0]
            subtree[obj.name] = scan
        else:
            try:
                blob = make_blob(obj)
                children[obj.name] = blob
                subtree[obj.name] = blob
            except Exception as e:
                print(e)
    #print(tree_root, children)
    return hashlib.sha256(json.dumps(children).encode('utf-8')).hexdigest(), subtree


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a file tree.')
    parser.add_argument('atree',
                        help='The root of the first file tree')
    parser.add_argument('btree',
                        help='The root of the second file tree')
    args = parser.parse_args()

    ahash = scan_tree(args.atree, mkblob.size_only)
    print(ahash[0])
    pprint.pprint(ahash[1])
    bhash = scan_tree(args.btree, mkblob.size_only)
    print(bhash[0])
    pprint.pprint(bhash[1])
