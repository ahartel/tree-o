import hashlib
import json


def photo_size_date(obj):
    """Generate a hash from the file's properties."""
    ext = os.path.splitext(obj.name)[1]
    if ext in ['.jpg', '.jpeg','.png','.cr2']:
        img = PIL.Image.open(obj.path)
        exif_data = img._getexif()
        #print(exif_data)
        #print(obj.stat().st_size)
        metadata = {'size': obj.stat().st_size,
                    'date': exif_data}
        return {'hash': hashlib.sha256(json.dumps(metadata).encode('utf-8')).hexdigest(),
                'type': 'f',
                'content': metadata}
    else:
        raise Exception('not a known image format')


def nothing(obj):
    """"This function gets an os.DirEntry object and just returns a value that has nothing to do with the file's
    content. This function can therefore be used to check if all file names match."""
    return {'hash': 0, 'type': 'f', 'content': 0}


def size_only(obj):
    size = obj.stat().st_size
    return {'hash': size, 'type': 'f', 'content': size}

