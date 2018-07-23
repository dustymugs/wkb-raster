from inspect import isclass
import numpy as np
from struct import pack
import sys

__all__ = [
    'POSTGIS_PIXEL_TYPES',
    'write'
]

class POSTGIS_PIXEL_TYPES(object):

    class BOOL(object):

        pixtype = 0 
        size = 1
        struct = '?'
        numpy = np.bool_

    class UINT2(object):

        pixtype = 1
        size = 1
        struct = 'B'
        numpy = np.uint8

    class UINT4(object):

        pixtype = 2 
        size = 1
        struct = 'B'
        numpy = np.uint8

    class INT8(object):

        pixtype = 3 
        size = 1
        struct = 'b'
        numpy = np.int8

    class UINT8(object):

        pixtype = 4
        size = 1
        struct = 'B'
        numpy = np.uint8

    class INT16(object):

        pixtype = 5
        size = 2
        struct = 'h'
        numpy = np.int16

    class UINT16(object):

        pixtype =  6
        size = 2
        struct = 'H'
        numpy = np.uint16

    class INT32(object):

        pixtype = 7
        size = 4
        struct = 'i'
        numpy = np.int32

    class UINT32(object):

        pixtype = 8
        size = 4
        struct = 'I'
        numpy = np.uint32

    class FLOAT32(object):

        pixtype = 10
        size = 4
        struct = 'f'
        numpy = np.float32

    class FLOAT64(object):

        pixtype = 11
        size = 8
        struct = 'd'
        numpy = np.float64

    RANKED = [
        FLOAT64,
        FLOAT32,
        UINT32,
        INT32,
        UINT16,
        INT16,
        UINT8,
        INT8,
        BOOL,
        UINT4,
        UINT2,
    ]

    @staticmethod
    def get_by(pixtype=None, size=None, struct=None, numpy=None, best_match=True):

        matches = tuple((
            v
            for v in POSTGIS_PIXEL_TYPES.children
            if (
                (pixtype is not None and v.pixtype == pixtype) or
                (size is not None and v.size == size) or
                (struct is not None and v.struct == struct) or
                (numpy is not None and v.numpy == numpy)
            )
        ))

        if best_match:

            if len(matches) == 1:
                return matches[0]

            for rank in ranked:
                if rank in matches:
                    return rank

        return matches

POSTGIS_PIXEL_TYPES.children = tuple((
    v
    for k, v in POSTGIS_PIXEL_TYPES.__dict__.items()
    if isclass(v)
))

def write(rast_dict):
    '''
    Provided a dictionary matching the return of wkb_raster.read, returns
    a WKB file-like objecto

    Based off the RFC:

        https://trac.osgeo.org/postgis/browser/trunk/raster/doc/RFC2-WellKnownBinaryFormat

    rast_dict expected to have this format:

        {
            'version': int,
            'scaleX': float,
            'scaleY': float,
            'ipX': float,
            'ipY': float,
            'skewX': float,
            'skewY': float,
            'srid': int,
            'width': int,
            'height': int,
            'bands': [
                {
                    'isOffline': bool,
                    'hasNodataValue': bool,
                    'isNodataValue': bool,
                    'pixtype': int,
                    'nodata': bool|int|float,

                    # if out-db band

                    'bandNumber': int (1-based) of raster file's band index,
                    'path': string to physical path of file,

                    # if in-db band

                    'ndarray': numpy.ndarray((width, height), bool|int|float)
                },
                ...
            ]
        }

    : rast_dict: dictionary to be serialized into WKB
    : returns: WKB binary string
    '''

    rast_bstr = b''

    # raster endian
    #
    # +---------------+-------------+------------------------------+
    # | endiannes     | byte        | 1:ndr/little endian          |
    # |               |             | 0:xdr/big endian             |
    # +---------------+-------------+------------------------------+
    endian = '>' if sys.byteorder != 'little' else '<'
    rast_bstr += pack(
        endian + 'b',
        0 if endian == '>' else 1
    )

    # raster header data
    #
    # +---------------+-------------+------------------------------+
    # | version       | uint16      | format version (0 for this   |
    # |               |             | structure)                   |
    # +---------------+-------------+------------------------------+
    # | nBands        | uint16      | Number of bands              |
    # +---------------+-------------+------------------------------+
    # | scaleX        | float64     | pixel width                  |
    # |               |             | in geographical units        |
    # +---------------+-------------+------------------------------+
    # | scaleY        | float64     | pixel height                 |
    # |               |             | in geographical units        |
    # +---------------+-------------+------------------------------+
    # | ipX           | float64     | X ordinate of upper-left     |
    # |               |             | pixel's upper-left corner    |
    # |               |             | in geographical units        |
    # +---------------+-------------+------------------------------+
    # | ipY           | float64     | Y ordinate of upper-left     |
    # |               |             | pixel's upper-left corner    |
    # |               |             | in geographical units        |
    # +---------------+-------------+------------------------------+
    # | skewX         | float64     | rotation about Y-axis        |
    # +---------------+-------------+------------------------------+
    # | skewY         | float64     | rotation about X-axis        |
    # +---------------+-------------+------------------------------+
    # | srid          | int32       | Spatial reference id         |
    # +---------------+-------------+------------------------------+
    # | width         | uint16      | number of pixel columns      |
    # +---------------+-------------+------------------------------+
    # | height        | uint16      | number of pixel rows         |
    # +---------------+-------------+------------------------------+
    rast_bstr += pack(
        endian + 'HHddddddIHH',
        rast_dict['version'],
        len(rast_dict['bands']),
        rast_dict['scaleX'],
        rast_dict['scaleY'],
        rast_dict['ipX'],
        rast_dict['ipY'],
        rast_dict['skewX'],
        rast_dict['skewY'],
        rast_dict['srid'],
        rast_dict['width'],
        rast_dict['height']
    )

    for band_dict in rast_dict['bands']:

        band_bstr = b''

        # band header data
        #
        # +---------------+--------------+-----------------------------------+
        # | isOffline     | 1bit         | If true, data is to be found      |
        # |               |              | on the filesystem, trought the    |
        # |               |              | path specified in RASTERDATA      |
        # +---------------+--------------+-----------------------------------+
        # | hasNodataValue| 1bit         | If true, stored nodata value is   |
        # |               |              | a true nodata value. Otherwise    |
        # |               |              | the value stored as a nodata      |
        # |               |              | value should be ignored.          |
        # +---------------+--------------+-----------------------------------+
        # | isNodataValue | 1bit         | If true, all the values of the    |
        # |               |              | band are expected to be nodata    |
        # |               |              | values. This is a dirty flag.     |
        # |               |              | To set the flag to its real value |
        # |               |              | the function st_bandisnodata must |
        # |               |              | must be called for the band with  |
        # |               |              | 'TRUE' as last argument.          |
        # +---------------+--------------+-----------------------------------+
        # | reserved      | 1bit         | unused in this version            |
        # +---------------+--------------+-----------------------------------+
        # | pixtype       | 4bits        | 0: 1-bit boolean                  |
        # |               |              | 1: 2-bit unsigned integer         |
        # |               |              | 2: 4-bit unsigned integer         |
        # |               |              | 3: 8-bit signed integer           |
        # |               |              | 4: 8-bit unsigned integer         |
        # |               |              | 5: 16-bit signed integer          |
        # |               |              | 6: 16-bit unsigned signed integer |
        # |               |              | 7: 32-bit signed integer          |
        # |               |              | 8: 32-bit unsigned signed integer |
        # |               |              | 10: 32-bit float                  |
        # |               |              | 11: 64-bit float                  |
        # +---------------+--------------+-----------------------------------+

        # extract pixel info for numpy array
        pixel_class = POSTGIS_PIXEL_TYPES.get_by(pixtype=band_dict['pixtype'])

        band_bstr += pack(
            endian + 'B',
            (
                (int(band_dict['isOffline']) << 7) +
                (int(band_dict['hasNodataValue']) << 6) +
                (int(band_dict['isNodataValue']) << 5) +
                (0 << 4) +
                pixel_class.pixtype
            )
        )

        # nodata value
        # +---------------+--------------+-----------------------------------+
        # | nodata        | 1 to 8 bytes | Nodata value                      |
        # |               | depending on |                                   |
        # |               | pixtype [1]  |                                   |
        # +---------------+--------------+-----------------------------------+
        band_bstr += pack(
            endian + pixel_class.struct,
            band_dict['nodata']
        )

        if band_dict['isOffline']:

            # out-db metadata
            #
            # +-------------+-------------+-----------------------------------+
            # | bandNumber  | uint8       | 0-based band number to use from   |
            # |             |             | the set available in the external |
            # |             |             | file                              |
            # +-------------+-------------+-----------------------------------+
            # | path        | string      | null-terminated path to data file |
            # +-------------+-------------+-----------------------------------+

            # offline bands are 0-based, convert from 1-based due to user consumption
            band_bstr += pack(
                endian + 'B',
                band_dict['bandNumber'] - 1
            )

            path = band_dict['path'].encode()
            band_bstr += pack(
                '{}{}s'.format(endian, len(path)),
                path
            )
            band_bstr += b'\x00' # NULL value denoting end of string

        else:

            # pixel values: width * height * size
            #
            # +------------+--------------+-----------------------------------+
            # | pix[w*h]   | 1 to 8 bytes | Pixels values, row after row,     |
            # |            | depending on | so pix[0] is upper-left, pix[w-1] |
            # |            | pixtype [1]  | is upper-right.                   |
            # |            |              |                                   |
            # |            |              | As for endiannes, it is specified |
            # |            |              | at the start of WKB, and implicit |
            # |            |              | up to 8bits (bit-order is most    |
            # |            |              | significant first)                |
            # |            |              |                                   |
            # +------------+--------------+-----------------------------------+

            band_bstr += pack(
                endian + ''.join(
                    [pixel_class.struct] *
                    (rast_dict['width'] * rast_dict['height'])
                ),
                *(band_dict['ndarray'].flatten().tolist())
            )

        rast_bstr += band_bstr

    return rast_bstr
