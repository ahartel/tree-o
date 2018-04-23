import os
import argparse
import mkblob

def list_tree(tree_root):
    """Put all files together with the content returned by make_blob into a list."""

    tree_list = []
    for obj in os.scandir(tree_root):
        if obj.is_dir():
            subtree_list = list_tree(obj.path)
            tree_list.extend(subtree_list)
        else:
            try:
                blob = mkblob.photo_size_date(obj)
                data = [obj.name,
                        blob['content']['size'],
                        blob['content']['date'],
                        tree_root,
                        blob['hash']]
                tree_list.append(data)
            except Exception as e:
                print(e)
    # print(tree_root, children)
    return tree_list


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a file tree.')
    parser.add_argument('tree',
                        help='The root of the file tree')

    args = parser.parse_args()

    tree = sorted(list_tree(args.tree), key=lambda photo: photo[2])
    for photo in tree:
        print(photo)
