import json

import marshmallow as ma
from marshmallow.fields import Number
from marshmallow.validate import Range
from marshmallow.fields import List, Str, Tuple
from marshmallow.validate import OneOf

from .schema_examples import GEOJSON_MULTI_POLYGON_EXAMPLE


GEOJSON_MULTI_POLYGON_TYPE = 'MultiPolygon'


lon = Number(
    required=True,
    validate=Range(
        min=-180,
        max=180,
        error='Longitude must be between -180, 180'
    )
)

lat = Number(
    required=True,
    validate=Range(
        min=-90,
        max=90,
        error='Latitude must be between -90, 90'
    )
)


class BaseSchema(ma.Schema):

    class Meta:
        render_module = json


class MultiPolygonSchema(BaseSchema):
    type = Str(
        required=True,
        validate=OneOf(
            [GEOJSON_MULTI_POLYGON_TYPE],
            error="Invalid multi polygon type",
        ),
    )

    coordinates = List(
        List(
            List(
                Tuple([lon, lat], required=True),
                required=True,
            ),
            required=True,
        ),
        required=True,
        metadata=dict(example=GEOJSON_MULTI_POLYGON_EXAMPLE["coordinates"]),
    )


def validate_multipolygon(value):
    MultiPolygonSchema().load(value)
