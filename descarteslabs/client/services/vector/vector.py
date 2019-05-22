import os
import six
import io
import logging

from descarteslabs.common.property_filtering import GenericProperties
from descarteslabs.client.deprecation import deprecate
from descarteslabs.client.services.service import JsonApiService, ThirdPartyService
from descarteslabs.client.auth import Auth
from descarteslabs.common.dotdict import DotDict


class _SearchFeaturesIterator(object):
    """Private iterator for search_features() that also returns length"""

    def __init__(
        self,
        client,
        product_id,
        geometry,
        query_expr,
        query_limit,
        **kwargs
    ):
        self._client = client
        self._product_id = product_id
        self._geometry = geometry
        self._query_expr = query_expr
        self._query_limit = query_limit
        self._kwargs = kwargs
        self._continuation_token = None
        self._page_offset = 0
        self._page_len = 0

        # updates _continuation_token, _page_offset, _page_len
        self._next_page()
        self._length = self._page.meta.total_results

    def __iter__(self):
        return self

    def __len__(self):
        return self._length

    def __next__(self):
        if self._page_offset >= self._page_len:
            if self._continuation_token is None:
                raise StopIteration()

            self._next_page()

        try:
            return self._page.data[self._page_offset]
        finally:
            self._page_offset += 1

    def _next_page(self):
        self._page = self._client._fetch_feature_page(
            product_id=self._product_id,
            geometry=self._geometry,
            query_expr=self._query_expr,
            query_limit=self._query_limit,
            continuation_token=self._continuation_token,
            **self._kwargs
        )

        self._continuation_token = self._page.meta.continuation_token
        self._page_offset = 0
        self._page_len = len(self._page.data)

    def next(self):
        """Backwards compatibility for Python 2"""
        return self.__next__()


class Vector(JsonApiService):
    """
    Client for storing and querying vector data.

    The Descartes Labs Vector service allows you store vector features
    (points, polygons, etc.) with associated key-value properties, and
    query that data by geometry or by properties.

    It works best at the scale of millions of features. For small amounts
    of vector data that easily fit in memory, working directly with a GeoJSON
    file or similar may be more efficient.

    Concepts:

    * "Feature": a single geometric entity and its associated metadata
      (equivalent to a GeoJSON Feature).
    * "Product": a collection of related Features, with a common id,
      description, and access controls.

    This client currently returns data as dictionaries in
    `JSON API format <http://jsonapi.org/>`_.
    """

    TIMEOUT = (9.5, 60)
    SEARCH_PAGE_SIZE = 1000
    properties = GenericProperties()

    def __init__(self, url=None, auth=None, retries=None):
        """
        :param str url: A HTTP URL pointing to a version of the storage service
            (defaults to current version)
        :param Auth auth: A custom user authentication (defaults to the user
            authenticated locally by token information on disk or by environment
            variables)
        :param urllib3.util.retry.Retry retries: A custom retry configuration
            used for all API requests (defaults to a reasonable amount of retries)
        """

        if auth is None:
            auth = Auth()

        if url is None:
            url = os.environ.get(
                "DESCARTESLABS_VECTOR_URL",
                "https://platform.descarteslabs.com/vector/v2"
            )
        self._gcs_upload_service = ThirdPartyService()

        super(Vector, self).__init__(url, auth=auth, retries=retries)

    def list_products(self, page_size=100, page=1):
        """
        Get all vector products that you have access using JSON API pagination.
        The first page (1) will always succeed but may be empty.
        Subsequent pages may throw :exc:`NotFoundError`.

        :param int page_size: Maximum number of vector products to return per
            page; default is 100.

        :param int page: Which page of results to fetch, if there are more
            results than ``page_size``.

        :rtype: DotDict
        :return: Available vector products and their properties,
            as a JSON API collection.  This dictionary contains the following keys:

            ::

                data:  A list of 'DotDict' instances.  For the keys
                       please see the data key in get_product().
                links: (Optional) A single DotDict instance with the
                       following keys if there is more than one page of products:

                    next: (Optional) A link to the next page of products
                          if available.
                    prev: (Optional) A link to the previous page of products
                          if available.
        """

        params = dict(
            limit=page_size,
            page=page
        )

        # override the json api content type which is default.
        r = self.session.get('/products', params=params, headers={'Content-Type': 'application/json'})
        return DotDict(r.json())

    def get_product(self, product_id):
        """
        Get a product's properties.

        :param str product_id: (Required) The ID of the Vector product to fetch.

        :rtype: DotDict
        :return: The vector product, as a JSON API resource object. The keys are:

            ::

                data: A single 'DotDict' instance with the following keys:

                    id:   The ID of the Vectort product.
                    type: 'product'.
                    meta: A single DotDict instance with the following keys:

                        created: Time that the task was created in ISO-8601 UTC.

                    attributes: A single DotDict instance with the following keys:

                        title:       The title given to this product.
                        description: The description given to this product.
                        owners:      The owners of this product (at a minimum
                                     the organization and the user who created
                                     this product).
                        readers:     The users, groups, or organizations that
                                     can read this product.
                        writers:     The users, groups, or organizations that
                                     can write into this product.
        """
        r = self.session.get('/products/{}'.format(product_id))
        return DotDict(r.json())

    @deprecate(renames={"name": "product_id"})
    def create_product(
        self,
        product_id,
        title,
        description,
        owners=None,
        readers=None,
        writers=None
    ):
        """Add a vector product to your catalog.

        :param str product_id: (Required) A unique name for this Vector product.
            In the created product a namespace consisting of your user id (e.g.
            ``ae60fc891312ggadc94ade8062213b0063335a3c:``) or your organization id (e.g.,
            ``yourcompany:``) will be prefixed to this, if it doesn't already have one,
            in order to make the id globally unique.

        :param str title: (Required) Official product title.

        :param str description: (Required) Information about the product,
            why it exists, and what it provides.

        :param list(str) owners: User, group, or organization IDs that own this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.
            Defaults to [current user, current user's org].

        :param list(str) readers: User, group, or organization IDs that can read
            this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param list(str) writers: User, group, or organization IDs that can edit
            this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :rtype: DotDict
        :return: Created vector product, as a JSON API resource object. For
            a list of keys, please see :meth:`get_product`.
        """

        params = dict(
            title=title,
            description=description,
            owners=owners,
            readers=readers,
            writers=writers
        )

        jsonapi = self.jsonapi_document(type="product", attributes=params, id=product_id)
        r = self.session.post('/products', json=jsonapi)
        return DotDict(r.json())

    @deprecate(required=["product_id", "title", "description"], renames={"name": None})
    def replace_product(
            self,
            product_id=None,
            name=None,
            title=None,
            description=None,
            owners=None,
            readers=None,
            writers=None
    ):
        """Replace a vector product in your catalog.

        :param str product_id: (Required) The ID of the Vector product to update.

        :param str title: (Required) Official product title.

        :param str description: (Required) Information about the product,
            why it exists, and what it provides.

        :param list(str) owners: User, group, or organization IDs that own this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.
            Defaults to [current user, current user's org].

        :param list(str) readers: User, group, or organization IDs that can read
            this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param list(str) writers: User, group, or organization IDs that can edit
            this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param str name: (Deprecated) Will be removed completely in future versions.

        :rtype: DotDict
        :return: Replaced vector product, as a JSON API resource object.  For a
            description of the keys, please see :meth:`get_product`.
        """

        # TODO: fully deprecate `name` and remove from params completely
        params = dict(
            title=title,
            description=description,
            owners=owners,
            readers=readers,
            writers=writers,
        )

        jsonapi = self.jsonapi_document(type="product", attributes=params, id=product_id)
        r = self.session.put('/products/{}'.format(product_id), json=jsonapi)
        return DotDict(r.json())

    @deprecate(renames={"name": None})
    def update_product(
            self,
            product_id,
            name=None,
            title=None,
            description=None,
            owners=None,
            readers=None,
            writers=None
    ):
        """Update a vector product in your catalog using the given parameters.
        If a parameter is not provided, it will not change.  You cannot change the
        ``product_id``.

        :param str product_id: (Required) The ID of the Vector product to update.

        :param str name: (Deprecated) Will be removed completely in future versions.

        :param str title: Official product title.

        :param str description: Information about the product,
            why it exists, and what it provides.

        :param list(str) owners: User, group, or organization IDs that own this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param list(str) readers: User, group, or organization IDs that can read
            this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param list(str) writers: User, group, or organization IDs that can edit
            this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :rtype: DotDict
        :return: Updated vector product, as a JSON API resource object.  For a
            description of the keys please see :meth:`get_product`.

        """

        # TODO: fully deprecate name and remove from params completely
        params = dict(
            title=title,
            description=description,
            owners=owners,
            readers=readers,
            writers=writers,
        )
        params = {k: v for k, v in six.iteritems(params) if v is not None}

        jsonapi = self.jsonapi_document(type="product", attributes=params, id=product_id)
        r = self.session.patch('/products/{}'.format(product_id), json=jsonapi)
        return DotDict(r.json())

    def delete_product(self, product_id):
        """Remove a vector product from the catalog.

        :param str product_id: (Required) The ID of the Vector product to remove.

        :raises NotFoundError: If the product cannot be found.
        """

        self.session.delete('/products/{}'.format(product_id))

    def create_feature(
        self,
        product_id,
        geometry,
        properties=None,
        fix_geometry='accept'
    ):
        """Add a feature to an existing vector product.

        :param str product_id: (Required) The ID of the Vector product to which this
            feature will belong.

        :param dict geometry: (Required) Shape associated with this vector feature.
            This accepts the following types of GeoJSON geometries:

            - Points
            - MultiPoints
            - Polygons
            - MultiPolygons
            - LineStrings
            - MultiLineStrings
            - GeometryCollections

        :param dict properties: Dictionary of arbitrary properties.

        :param str fix_geometry: String specifying how to handle certain problem
            geometries, including those which do not follow counter-clockwise
            winding order (which is required by the GeoJSON spec but not many
            popular tools). Allowed values are ``reject`` (reject invalid
            geometries with an error), ``fix`` (correct invalid geometries if
            possible and use this corrected value when creating the feature),
            and ``accept`` (the default) which will correct the geometry for
            internal use but retain the original geometry in the results.

        :rtype: DotDict
        :return: Created Feature, as a JSON API resource collection.  The keys are:

            ::

                data: A 'DotDict' instance with the following keys:

                    id:        The ID of the feature.
                    type:      'feature'.
                    attributes: A DotDict instance with the following keys:

                        created:    Time that the task was created in ISO-8601 UTC.
                        properties: A DotDict instance.  The keys are user provided.
                                    Supported values are strings, numbers, the
                                    value 'None'.
                        geometry:   A DotDict instance with the following keys:

                            type:       The type of the feature, one of 'Polygon',
                                         'MultiPolygon', 'Point', 'MultiPoint',
                                         'LineString', 'MultiLineString', or
                                         'GeometryCollection'.
                            coordinates: A list of coordinates; the exact structure
                                         of potentially nesting lists depends on
                                         the given type.
        """

        params = dict(
            geometry=geometry,
            properties=properties,
            fix_geometry=fix_geometry
        )

        jsonapi = self.jsonapi_document(type="feature", attributes=params)
        r = self.session.post('/products/{}/features'.format(product_id), json=jsonapi)
        return DotDict(r.json())

    def create_features(self, product_id, features, fix_geometry='accept'):
        """Add multiple features to an existing vector product.

        :param str product_id: (Required) The ID of the Vector product to which these
            features will belong.

        :param list(dict) features: (Required) Each feature must be a dict with a geometry
            and properties field. If you provide more than 100 features,
            they will be batched in
            groups of 100, but consider using :meth:`upload_features()` instead.

        :param str fix_geometry: String specifying how to handle certain problem
            geometries, including those which do not follow counter-clockwise
            winding order (which is required by the GeoJSON spec but not many
            popular tools). Allowed values are ``reject`` (reject invalid geometries
            with an error), ``fix`` (correct invalid geometries if possible and use
            this corrected value when creating the feature), and ``accept``
            (the default) which will correct the geometry for internal use but
            retain the original geometry in the results.

        :rtype: DotDict
        :return: The features as a JSON API resource object. The keys are:

            ::

                data: A list of 'DotDict' instances.  Each instance contains
                      keys as described in create_feature().

        :raises ClientError: A variety of http-related exceptions can
            thrown. If more than 100 features were passed in, some
            of these may have been successfully inserted, others not.
            If this is a problem, then stick with <= 100 features.
        """

        if len(features) > 100:
            logging.warning(
                'create_features: feature collection has more than 100 features,'
                + ' will batch by 100 but consider using upload_features')

        # forcibly pass a zero-length list for appropriate validation error
        for i in range(0, max(len(features), 1), 100):
            attributes = [dict(feat, **{"fix_geometry": fix_geometry}) for feat in features[i:i + 100]]
            jsonapi = self.jsonapi_collection(type="feature", attributes_list=attributes)

            r = self.session.post('/products/{}/features'.format(product_id),
                                  json=jsonapi)
            if i == 0:
                result = DotDict(r.json())
            else:
                result.data.extend(DotDict(r.json()).data)

        return result

    def upload_features(self, file_ish, product_id, max_errors=0, fix_geometry='accept'):
        """
        Asynchonously upload a file or stream of
        `Newline Delimited JSON <https://github.com/ndjson/ndjson-spec>`_
        features.  Note that the file may not contain empty lines or lines containing
        anything but the feature (including e.g. a trailing comma),
        or such lines will cause errors.

        It is recommended that the IOBase object is a byte-oriented (not
        text-oriented) object, although Python 3 allows :class:`io.StringIO` to
        be used.

        This is an asynchronous operation and you can query for the status
        using :meth:`Vector.get_upload_result()` with the upload_id returned by
        this method.

        :type file_ish: str or io.IOBase
        :param file_ish: an open :class:`io.IOBase` object, or a path
            to the file to upload.

        :param str product_id: (Required) The ID of the Vector product to which these
            features will belong.

        :param int max_errors: The maximum number of errors permitted before
            declaring failure.

        :param str fix_geometry: String specifying how to handle certain problem
            geometries, including those which do not follow counter-clockwise
            winding order (which is required by the GeoJSON spec but not many
            popular tools). Allowed values are ``reject`` (reject invalid
            geometries with an error), ``fix`` (correct invalid geometries if
            possible and use this corrected value when creating the feature),
            and ``accept`` (the default) which will correct the geometry for
            internal use but retain the original geometry in the results.

        :rtype: str
        :return: The upload id.
        """

        if isinstance(file_ish, io.IOBase):
            return self._upload_features(file_ish, product_id, max_errors, fix_geometry)
        elif isinstance(file_ish, six.string_types):
            with io.open(file_ish, 'rb') as stream:
                return self._upload_features(stream, product_id, max_errors, fix_geometry)
        else:
            raise Exception('Could not handle file: `{}`; pass a path or open IOBase instance'.format(file_ish))

    def _upload_features(self, iobase, product_id, max_errors, fix_geometry):
        jsonapi = self.jsonapi_document(
            type="features",
            attributes={
                'max_errors': max_errors,
                'fix_geometry': fix_geometry}
        )
        r = self.session.post('/products/{}/features/uploads'.format(product_id), json=jsonapi)
        upload = r.json()
        upload_url = upload['url']
        r = self._gcs_upload_service.session.put(upload_url, data=iobase)
        return upload['upload_id']

    def _fetch_upload_result_page(self, product_id, continuation_token=None, pending=False):
        r = self.session.get(
            '/products/{}/features/uploads'.format(product_id),
            params={'pending': bool(pending), 'continuation_token': continuation_token},
            headers={'Content-Type': 'application/json'},
        )
        return DotDict(r.json())

    def get_upload_results(self, product_id, pending=False):
        """
        Get a list of the uploads submitted to a vector product, and status
        information about each.

        :param str product_id: (Required) The ID of the Vector product for which
            to retrieve the upload results

        :param bool pending: If True, include pending upload jobs in the result.
            Defaults to False.

        :rtype: Iterator of :class:`DotDict` instances
        :return: An iterator over all upload results created with
            :meth:`upload_features`, returning :class:`DotDict` instances with
            the following keys:

            ::

                id:         The ID of the upload task (which is not the upload
                            ID, but you can use it instead of the upload ID).
                type:       'upload'.
                attributes: A 'DotDict' instance with the following keys
                            (note that this contains less information then the
                            information returned by get_upload_result()):

                    created:           Time that the task was created in ISO-8601 UTC.
                    exception_name:    The type of exception, if there is one,
                                       'None' otherwise.
                    failure_type:      'executable_failure' if resource limits are
                                       reached, or 'exception' if an exception was
                                       thrown, 'None' otherwise.
                    peak_memory_usage: The amount of memory used by the task in bytes.
                    runtime:           The number of CPU seconds used by the task.
                    status:            'RUNNING', 'SUCCESS' or 'FAILURE'.
                    labels:            A list of string labels.  The last value is
                                       the upload ID.
        """

        continuation_token = None
        while True:
            page = self._fetch_upload_result_page(product_id, continuation_token=continuation_token, pending=pending)
            for feature in page.data:
                yield feature
            continuation_token = page.meta.continuation_token

            if continuation_token is None:
                break

    def get_upload_result(self, product_id, upload_id, pending=False):
        """
        Get details about a specific upload job. Included information about
        processing error streams, which can help debug failed uploads.

        :param str product_id: (Required) The ID of the product which to retrieve
            the upload result.

        :param str upload_id: (Required) An id pertaining to this requested upload,
            either returned by :meth:`Vector.get_upload_results` or
            :meth:`upload_features`.

        :param bool pending: If True, include pending upload jobs in the result.
            Defaults to False.

        :rtype DotDict:
        :return: The result as a JSON API resource object. The keys are:

            ::

                data: A DotDict instance with the following keys:

                    id:         The ID of the upload task (which is not the upload
                                ID, but you can use it instead of the upload ID).
                    type:       'upload'.
                    attributes: A DotDict instance with the following keys:

                        created:           Time that the task was created in
                                           ISO-8601 UTC.
                        exception_name:    The type of exception, if there is one,
                                           'None' otherwise.
                        failure_type:      'executable_failure' if resource limits
                                           are reached, or 'exception' if an exception
                                           was thrown, 'None' otherwise.
                        peak_memory_usage: The amount of memory used by the task
                                           in bytes.
                        runtime:           The number of CPU seconds used by the task.
                        status:            'RUNNING', 'SUCCESS' or 'FAILURE'.
                        labels:            A list of string labels.  The last value is
                                           the upload ID.
                        load:              A DotDict instance describing the actual
                                           result of the load which continuous
                                           asynchronously after the task itself
                                           has completed (as indicated by the
                                           'RUNNING`` status):

                            errors:      How many errors the load caused.
                            output_rows: The number of actual rows created during the
                                         load (which may differ from the number of rows
                                         given in the upload file).
                            state:       'PENDING', 'RUNNING', or 'DONE'.

                        result: A DotDict instance describing the result of the Upload
                                Task (which pre-processes the data before it's loaded):

                            errors:         A list of errors, potentially empty.
                            input_features: The number of valid rows in the upload file.
                            input_rows:     The number of rows that will be loaded
                                            (unless there are errors, this should be
                                            identical to ``output_rows`` above).
                            job_id:         The internal job ID.
        """

        r = self.session.get(
            '/products/{}/features/uploads/{}'.format(product_id, upload_id),
            params={'pending': bool(pending)},
            headers={'Content-Type': 'application/json'},
        )
        return DotDict(r.json())

    def _fetch_feature_page(
        self,
        product_id,
        geometry,
        query_expr=None,
        query_limit=None,
        continuation_token=None,
        **kwargs
    ):
        """Query vector features within an existing product by page.

        For a detailed explanation of arguments, see :meth:`search_features`.

        :param str continuation_token: Token returned from a previous call
            to this method that can be used to fetch the next page
            of search results. Search parameters must stay consistent
            between calls using a continuation token.

        :rtype: DotDict
        :return: Features satisfying the query, as a JSON API resource
            collection.
        """

        params = {k: v for k, v in dict(
            kwargs,
            geometry=geometry,
            query_expr=(query_expr.serialize() if query_expr is not None else None),
            limit=Vector.SEARCH_PAGE_SIZE,
            query_limit=query_limit,
            continuation_token=continuation_token,
        ).items() if v is not None}

        r = self.session.post('/products/{}/search'.format(product_id), json=params)
        return DotDict(r.json())

    def search_features(
        self,
        product_id,
        geometry=None,
        query_expr=None,
        query_limit=None,
        **kwargs
    ):
        """Iterate over vector features within an existing product.

        At least one of :obj:`geometry`, :obj:`query_expr`, or :obj:`query_limit`
        is required.

        The returned iterator has a length that indicates the size of
        the query.

        :param str product_id: (Required) The ID of the product within which to search.

        :param dict geometry: Search for Features intersecting this shape.
            This accepts the following types of GeoJSON geometries:

            - Points
            - MultiPoints
            - Polygons
            - MultiPolygons
            - LineStrings
            - MultiLineStrings
            - GeometryCollections

        :param `descarteslabs.client.common.filtering.Expression` query_expr:
            A rich query expression generator that represents
            an arbitrary tree of boolean combinations of property
            comparisons.  Using the :data:`properties` filter factory inside
            ``descarteslabs.client.services.vector`` as
            :obj:`p`, you can E.g ``query_expr=(p.temperature >= 50) &
            (p.hour_of_day > 18)``, or even more complicated expressions
            like ``query_expr=(100 > p.temperature >= 50) | ((p.month
            != 10) & (p.day_of_month > 14))`` This expression gets
            serialized and applied to the properties mapping supplied
            with the features in the vector product. If you supply a
            property which doesn't exist as part of the expression that
            comparison will evaluate to False.

        :param int query_limit: Maximum number of features to return for this
            query, defaults to all.

        :rtype: Iterator of :class:`DotDict` instances
        :return: Features satisfying the query, as JSONAPI primary data objects.
            For a description of the keys, please refer to :meth:`create_feature`
            under the ``data`` key.

            :func:`len` can be used on the returned iterator to determine
            the query size.
        """

        return _SearchFeaturesIterator(
            self, product_id, geometry, query_expr, query_limit)

    @deprecate(renames={"name": "new_product_id"})
    def create_product_from_query(
        self,
        new_product_id,
        title,
        description,
        product_id,
        owners=None,
        readers=None,
        writers=None,
        geometry=None,
        query_expr=None,
        query_limit=None
    ):
        """
        Query vector features within an existing product and create a new
        vector product to your catalog from the query result.

        At least one of :obj:`geometry`, :obj:`query_expr`, or :obj:`query_limit`
        is required.

        :param str new_product_id: (Required) A unique name for this product.
            In the created product a namespace consisting of your user id (e.g.
            ``ae60fc891312ggadc94ade8062213b0063335a3c:``) or your organization id
            (e.g., ``yourcompany:``) will be prefixed to this, if it doesn't
            already have one, in order to make the id globally unique.

        :param str title: (Required) Official product title.

        :param str description: (Required) Information about the product,
            why it exists, and what it provides.

        :param str product_id: (Required) The ID of the product within which to search.

        :param list(str) owners: User, group, or organization IDs that own this product.
            Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.
            Defaults to [current user, current user's org].

        :param list(str) readers: User, group, or organization IDs that can read this
            product.  Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param list(str) writers: User, group, or organization IDs that can edit this
            product.  Each ID must be prefixed with ``user:``, ``group:``, or ``org:``.

        :param dict geometry: Search for Features intersecting this shape.
            This accepts the following types of GeoJSON geometries:

            - Points
            - MultiPoints
            - Polygons
            - MultiPolygons
            - LineStrings
            - MultiLineStrings
            - GeometryCollections

        :param descarteslabs.client.common.filtering.Expression query_expr:
            A rich query expression generator that represents
            an arbitrary tree of boolean combinations of property
            comparisons.  Using the :data:`properties` filter factory inside
            :mod:`descarteslabs.client.services.vector` as
            :obj:`p`, you can E.g ``query_expr=(p.temperature >= 50) &
            (p.hour_of_day > 18)``, or even more complicated expressions
            like ``query_expr=(100 > p.temperature >= 50) | ((p.month
            != 10) & (p.day_of_month > 14))`` This expression gets
            serialized and applied to the properties mapping supplied
            with the features in the vector product. If you supply a
            property which doesn't exist as part of the expression that
            comparison will evaluate to False.

        :param int query_limit: Maximum number of features to return for this query,
            defaults to all.

        :rtype: DotDict
        :return: Created vector product, as a JSON API resource object.  For a
            description of the keys, please see :meth:`get_product`.
        """

        product_params = dict(
            id=new_product_id,
            title=title,
            description=description,
            owners=owners,
            readers=readers,
            writers=writers
        )

        query_params = {k: v for k, v in dict(
            geometry=geometry,
            query_expr=(query_expr.serialize() if query_expr is not None else None),
            query_limit=query_limit,
        ).items() if v is not None}

        params = dict(
            product=product_params,
            query=query_params
        )

        r = self.session.post('/products/{}/search/copy'.format(product_id), json=params)
        return DotDict(r.json())

    def get_product_from_query_status(self, product_id):
        """Get the status of the job creating a new product from a query.

        :param str product_id: (Required) The ID of the product for which to
            to check the status.  This ID must have been created
            by a call to :meth:`create_product_from_query`.

        :rtype: DotDict
        :return: A dictionary with information about the status.  The keys are
            ::

                data: A 'DotDict' instance with the following keys:

                    id:         The internal ID for this job.
                    type:       'copy_job'.
                    attributes: A DotDict instance with the following keys:

                        created: Time that the task was created in ISO-8601 UTC.
                        ended:   Time that the task completed in ISO-8601 UTC
                                 (when available).
                        started: Time that the start stared in ISO-8601 UTC
                                 (when available).
                        state:   'PENDING', 'RUNNING', or 'DONE'.
        """

        r = self.session.get("/products/{}/search/copy/status".format(product_id))
        return DotDict(r.json())

    def export_product_from_query(
        self,
        product_id,
        key,
        geometry=None,
        query_expr=None,
        query_limit=None
    ):
        """
        Query vector features within an existing product and export the result
        to DescartesLabs Storage as type ``data`` using the given storage key.

        If none of the :obj:`geometry`, :obj:`query_expr`, or
        :obj:`query_limit` are given, the full product is exported.

        Note that the export is happening asynchronously and can take a
        while depending on the size of the product or query.  You can
        request the status using :meth:`get_export_result()` or
        :meth:`get_export_results()`.

        Once the export is complete, you can download the file from Descartes Labs
        Storage using :meth:`descarteslabs.client.services.storage.Storage.get_file`
        with the given key and a local filename.

        :param str product_id: (Required) The ID of the product within which to search
            or which to copy.

        :param str key: (Required) The name under which the export will be
            available in the Storage service.  The ``storage_type`` will be
            ``data``.  Note that this will overwrite any existing data if
            the key already exists.

        :param dict geometry: Search for Features intersecting this shape.
            This accepts the following types of GeoJSON geometries:

            - Points
            - MultiPoints
            - Polygons
            - MultiPolygons
            - LineStrings
            - MultiLineStrings
            - GeometryCollections

        :param descarteslabs.client.common.filtering.Expression query_expr:
            A rich query expression generator that represents
            an arbitrary tree of boolean combinations of property
            comparisons.  Using the :data:`properties` filter factory inside
            :mod:`descarteslabs.client.services.vector` as
            :obj:`p`, you can E.g ``query_expr=(p.temperature >= 50) &
            (p.hour_of_day > 18)``, or even more complicated expressions
            like ``query_expr=(100 > p.temperature >= 50) | ((p.month
            != 10) & (p.day_of_month > 14))`` This expression gets
            serialized and applied to the properties mapping supplied
            with the features in the vector product. If you supply a
            property which doesn't exist as part of the expression that
            comparison will evaluate to False.

        :param int query_limit: Maximum number of features to return for
            this query, defaults to all.

        :rtype: str
        :return: The export id.
        """

        query_params = {k: v for k, v in dict(
            geometry=geometry,
            query_expr=(query_expr.serialize() if query_expr is not None else None),
            query_limit=query_limit,
        ).items() if v is not None}

        params = dict(
            key=key,
            query=query_params
        )

        r = self.session.post('/products/{}/search/export'.format(product_id), json=params)
        return r.json()['export_id']

    def _fetch_export_result_page(self, product_id, continuation_token=None):
        r = self.session.get(
            '/products/{}/search/export'.format(product_id),
            params={'continuation_token': continuation_token},
            headers={'Content-Type': 'application/json'},
        )

        return DotDict(r.json())

    def get_export_results(self, product_id):
        """
        Get a list of the exports submitted to a vector product, and status
        information about each.  Note that only completed tasks are shown;
        any tasks that are pending or running will not be listed.

        :param str product_id: (Required) The ID of the product to get results for.

        :rtype: Iterator of :class:`DotDict` instances
        :return: An iterator returning :class:`DotDict` instances containing
            information about each completed export task created by
            :meth:`Vector.export_product_from_query`.  See :meth:`get_export_result`
            under ``data`` for an explanation of the information returned.
        """

        continuation_token = None

        while True:
            page = self._fetch_export_result_page(
                product_id,
                continuation_token=continuation_token
            )

            for result in page.data:
                yield result

            continuation_token = page.meta.continuation_token

            if continuation_token is None:
                break

    def get_export_result(self, product_id, export_id):
        """
        Get details about a specific export job. Included information about
        processing error streams, which can help debug failed uploads.
        Note that this information is available once the job completed
        (either successfully or unsuccessfully).

        :param str product_id: (Required) The ID of the product for which to return
            the result.

        :param str export_id: (Required) The export ID for which to return
            the result, as previously returned by
            :meth:`Vector.export_product_from_query`.

        :rtype: DotDict
        :return: The information about the export task once the task has completed.
            The keys are:

            ::

                data: A single 'DotDict' instance with the following keys:

                    id:         The id of the task.
                    type:       export.
                    attributes: A DotDict instance with the following keys:

                        created:           Time that the task was created in
                                           ISO-8601 UTC.
                        exception_name:    The type of exception, if there is one,
                                           'None' otherwise.
                        failure_type:      'executable_failure' if resource limits are
                                           reached, or 'exception' if an exception was
                                           thrown, 'None' otherwise.
                        peak_memory_usage: The amount of memory used by the task in bytes.
                        runtime:           The number of CPU seconds used by the task.
                        status:            'SUCCESS' or 'FAILURE'.
                        labels:            A list of string labels.  The last value is
                                           the key.

        :raises NotFoundError: When the task is either not found or is
            pending or running but has not completed yet.
        """

        r = self.session.get(
            '/products/{}/search/export/{}'.format(product_id, export_id),
            headers={'Content-Type': 'application/json'},
        )

        return DotDict(r.json())

    def delete_features_from_query(self, product_id, geometry=None, query_expr=None, **kwargs):
        """
        Query an existing Vector product and delete features that match
        the query results.

        One of :obj:`geometry` or :obj:`query_expr` is required.

        :param str product_id: (Required) The ID of the product within which to
            search for features to delete.

        :param dict geometry: Search for Features intersecting this shape.
            This accepts the following types of GeoJSON geometries:

            - Points
            - MultiPoints
            - Polygons
            - MultiPolygons
            - LineStrings
            - MultiLineStrings
            - GeometryCollections

        :param descarteslabs.client.common.filtering.Expression query_expr:
            A rich query expression generator that represents
            an arbitrary tree of boolean combinations of property
            comparisons.  Using the :data:`properties` filter factory inside
            :mod:`descarteslabs.client.services.vector` as
            :obj:`p`, you can E.g ``query_expr=(p.temperature >= 50) &
            (p.hour_of_day > 18)``, or even more complicated expressions
            like ``query_expr=(100 > p.temperature >= 50) | ((p.month
            != 10) & (p.day_of_month > 14))`` This expression gets
            serialized and applied to the properties mapping supplied
            with the features in the vector product. If you supply a
            property which doesn't exist as part of the expression that
            comparison will evaluate to False.

        :rtype: DotDict
        :return: Vector product from which the features were deleted, as a JSON API
            resource object. For a list of keys, please see :meth:`get_product`.
        """

        query_params = {k: v for k, v in dict(
            geometry=geometry,
            query_expr=(query_expr.serialize() if query_expr is not None else None)
        ).items() if v is not None}

        r = self.session.delete("/products/{}/search".format(product_id), json=query_params)
        return DotDict(r.json())

    def get_delete_features_status(self, product_id):
        """Get the status of the job deleting features from a query.

        :param str product_id: (Required) The ID of the product to get delete status for.
            the previously initiated deletion using :meth:`create_product` or :meth:`create_product_from_query`.

        :rtype DotDict:
        :return: A dictionary with information about the status.  For a description
            of the keys, please see :meth:`get_product_from_query_status`.
            Note that the ``type`` will be ``u'delete_job``.
        """

        r = self.session.get("/products/{}/search/delete/status".format(product_id))
        return DotDict(r.json())

    def count_features(self, product_id):
        """Get the count of the features in a product.

        :param str product_id: (Required) The ID of the product to count all features for.

        :rtype: int
        :return: The total number of features in a product.
        """
        r = self.session.get("/products/{}/features/count".format(product_id))
        return r.json()
