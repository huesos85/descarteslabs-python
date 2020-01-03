from ... import env
from ...cereal import serializable
from ..core import typecheck_promote
from ..primitives import Str, Int, Float, Bool
from ..containers import List, Struct, CollectionMixin
from .feature import Feature

FeatureCollectionStruct = Struct[{"features": List[Feature]}]


@serializable(is_named_concrete_type=True)
class FeatureCollection(FeatureCollectionStruct, CollectionMixin):
    "Proxy FeatureCollection constructed from a sequence of Features."

    _constructor = "FeatureCollection.create"
    _element_type = Feature

    @typecheck_promote(List[Feature])
    def __init__(self, features):
        "Construct a FeatureCollection from a sequence of Features."
        super(FeatureCollection, self).__init__(features=features)

    @classmethod
    @typecheck_promote(Str)
    def from_vector_id(cls, id):
        """
        Construct a Workflows FeatureCollection from a vector ID.

        The FeatureCollection will contain all `Feature`s within the `GeoContext` used in the computation.

        Parameters
        ----------
        id: Str
            An ID of a product in the Descartes Labs Vector service.

        Returns
        -------
        ~descarteslabs.workflows.FeatureCollection
        """
        return cls._from_apply(
            "FeatureCollection.from_vector",
            id,
            geocontext=env.geoctx,
            __token__=env._token,
        )

    @classmethod
    def from_geojson(cls, geojson):
        """
        Construct a Workflows FeatureCollection from a GeoJSON mapping.

        Note that the GeoJSON must be relatively small (under 10MiB of serialized JSON).

        Parameters
        ----------
        geojson: Dict

        Returns
        -------
        ~descarteslabs.workflows.FeatureCollection
        """
        try:
            if geojson["type"].lower() != "featurecollection":
                raise ValueError(
                    "Expected a GeoJSON FeatureCollection type, "
                    "not {!r}".format(geojson["type"])
                )

            # Embed the JSON directly in the graft
            # Note this bypasses any validation in Feature, Geometry, etc.
            return cls._from_apply(cls._constructor, geojson["features"])
        except KeyError:
            raise ValueError(
                "Expected a GeoJSON mapping containing the field 'type' and 'features', "
                "but got {}".format(geojson)
            )

    @classmethod
    def _promote(cls, obj):
        if isinstance(obj, dict):
            return cls.from_geojson(obj)
        return super(FeatureCollection, cls)._promote(obj)

    @typecheck_promote(
        value=(Int, Float, Str), default_value=(Int, Float), merge_algorithm=Str
    )
    def rasterize(self, value=1, default_value=1, merge_algorithm="add"):
        """
        Rasterize all Features into one `~.geospatial.Image`

        Parameters
        ----------
        value: Int, Float, Str, default=1
            Fill enclosed pixels with this value.
            Pixels outside the `FeatureCollection` will be masked, and set to 0.

            If a string, it will look up that key in the properties of each `Feature`;
            the value there must be a number.
        default_value: Int, Float, default=1
            Value to use if ``value`` is a string and the key does
            not exist in the properties of a `Feature`.
        merge_algorithm: Str, default="add"
            How to combine values where Features overlap. Options are
            ``"add"``, to sum the values, or ``"replace"``, to use the value
            from the `Feature` that comes last in the `FeatureCollection`.

        Notes
        -----
        Rasterization happens according to the `~.workflows.types.geospatial.GeoContext`
        of the `.Job`, so the geometry is projected into and rasterized at
        that CRS and resolution.

        Returns
        -------
        rasterized: ~.geospatial.Image
            An Image with 1 band named ``"features"``, and empty properties and bandinfo.
        """
        from .image import Image

        return Image._from_apply(
            "rasterize",
            self,
            value,
            env.geoctx,
            default_value=default_value,
            merge_algorithm=merge_algorithm,
        )

    @typecheck_promote(None, reverse=Bool)
    def sorted(self, key, reverse=False):
        """
        Copy of this `~.geospatial.FeatureCollection`, sorted by a key function.

        Parameters
        ----------
        key: Function
            Function which takes an `Feature` and returns a value to sort by.
        reverse: Bool, default False
            Sorts in ascending order if False (default), descending if True.

        Returns
        -------
        sorted: ~.geospatial.FeatureCollection
        """
        key = self._make_sort_key(key)
        return self._from_apply("sorted", self, key, reverse=reverse)
        # NOTE(gabe): `key` is a required arg for the "sorted" function when given an FeatureCollection,
        # hence why we don't give it as a kwarg like we do for Collection.sorted
