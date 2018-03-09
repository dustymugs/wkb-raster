## WKB Raster

Read WKB rasters to Numpy arrays.

### Docs

```python
wkb_raster.read(wkb)
```

__Parameters__

- __wkb__ - file-like object. Binary raster in WKB format.

__Returns__

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
        'bands': [{
            'nodata': bool|int|float,
            'isOffline': bool,
            'hasNodataValue': bool,
            'isNodataValue': bool,
            'ndarray': numpy.ndarray((width, height), bool|int|float)
        }, ...]
    }

__Usage__

With a binary WKB file:

```python
import wkb_raster

with open('img.wkb') as f:
    raster = wkb_raster.read(f)
    raster['bands'][0]
```

With WKB from PostGIS Raster. Use [ST_AsWKB](http://postgis.net/docs/manual-dev/RT_ST_AsBinary.html)
to return the WKB representation of the raster.

```sql
SELECT ST_AsWKB(rast) FROM rasters;
```

Wrap the binary buffer in `cStringIO.StringIO`:

```python
from cStringIO import StringIO
import wkb_raster

raster = wkb_raster.read(StringIO(buf))
raster['bands'][0]
```

### Links

- [Raster WKB RFC](http://trac.osgeo.org/postgis/browser/trunk/raster/doc/RFC2-WellKnownBinaryFormat)
