import hashlib
import json
import os
from PIL import Image
from PIL.ExifTags import TAGS

def photo_size_date(obj):
    """Generate a hash from the file's properties."""
    ext = os.path.splitext(obj.name)[1]
    if ext in ['.jpg', '.jpeg','.png','.cr2', '.JPEG', '.JPG']:
        img = Image.open(obj.path)
        exif_data = {TAGS.get(tag): value for tag, value in img._getexif().items()}
        #print(exif_data)
        metadata = {'size': obj.stat().st_size,
                    'date': exif_data['DateTime']}
        #print(["{0}({1}):{2}".format(TAGS.get(tag), tag, value) for tag, value in exif_data.items()])
        return {'hash': hashlib.sha256(json.dumps(metadata).encode('utf-8')).hexdigest(),
                'type': 'f',
                'content': metadata}
    else:
        raise Exception('{0} is not a known image format'.format(ext))


def nothing(obj):
    """"This function gets an os.DirEntry object and just returns a value that has nothing to do with the file's
    content. This function can therefore be used to check if all file names match."""
    return {'hash': 0, 'type': 'f', 'content': 0}


def size_only(obj):
    size = obj.stat().st_size
    return {'hash': size, 'type': 'f', 'content': size}

