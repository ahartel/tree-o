"""This software can generate a merkle tree of a certain toplevel directory.
It scans a file tree recursively and generates blob hashes of all image files where only the meta data of the file enters the hash.
Here, we use the date of capture and the file size as metadata. Later, we should add tags.
For each directory, the relative file names will be stored with the blob hashes in a dictionary which will then be hashed for the directory.
The hashes of the individual files and directories will be stored in a flat file for later lookup.
It might be a good idea to store them alphabetically by hash to allow fast lookup if a given image (hash) is already in the file tree.

There will then be an additional visualization tool that can compare two such generated trees.
Another tool will be able to automatically insert all pictures from a camera folder into the file tree and it will make use of the existing merkle tree to check for duplicates.
This copy-from-camera tool shall have an ignore option which lets the user define a tag that is used to mark pictures as don't copy."""

import hashlib
import PIL.Image
import json
import os
import argparse

def print_file(arg, dirname, names):
    print(dirname)
    for name in names:
        print(" {0}".format(name))

def makeblob(obj):
    """Generate a hash from the file's properties."""
    ext = os.path.splitext(obj.name)[1]
    if ext in ['.jpg', '.jpeg','.png','.cr2']:
        img = PIL.Image.open(obj.path)
        exif_data = img._getexif()
        #print(exif_data)
        #print(obj.stat().st_size)
        metadata = {'size': obj.stat().st_size,
                    'date': exif_data}
        return hashlib.sha256(json.dumps(metadata).encode('utf-8')).hexdigest()
    else:
        raise Exception('not a known image format')

def scantree(root):
    """They order in which files and directories are added to the list children might be important for the resulting
    hash value. This could be circumvented by making children a dictionary."""
    children = {}
    for obj in os.scandir(root):
        if obj.is_dir():
            children[obj.name] = scantree(obj.path)
        else:
            try:
                children[obj.name] = makeblob(obj)
            except Exception as e:
                pass
    print(root,children)
    return hashlib.sha256(json.dumps(children).encode('utf-8')).hexdigest()

parser = argparse.ArgumentParser(description='Process a photo file tree.')
parser.add_argument('root',
                    help='The root of the file tree')
args = parser.parse_args()
root = args.root

#walker = os.walk(root)
#for obj in os.scandir(root):
#    print(obj.is_dir())
#for i, tup in enumerate(walker):
#    print(tup)
#    print(hashlib.sha256(tup[0].encode('utf-8')).hexdigest())
#    if i > 10:
#        break

scantree(root)
