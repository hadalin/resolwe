"""Data viewset."""
from rest_framework import exceptions, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from resolwe.flow.filters import DataFilter
from resolwe.flow.models import Data, Process
from resolwe.flow.models.utils import fill_with_defaults
from resolwe.flow.serializers import DataSerializer
from resolwe.flow.utils import get_data_checksum
from resolwe.permissions.loader import get_permissions_class
from resolwe.permissions.mixins import ResolwePermissionsMixin
from resolwe.permissions.shortcuts import get_objects_for_user

from .mixins import (
    ParametersMixin,
    ResolweCheckSlugMixin,
    ResolweCreateModelMixin,
    ResolweUpdateModelMixin,
)


class DataViewSet(
    ResolweCreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    ResolweUpdateModelMixin,
    mixins.DestroyModelMixin,
    ResolwePermissionsMixin,
    ResolweCheckSlugMixin,
    ParametersMixin,
    viewsets.GenericViewSet,
):
    """API view for :class:`Data` objects."""

    queryset = Data.objects.all().prefetch_related(
        "process", "descriptor_schema", "contributor", "collection", "entity"
    )
    serializer_class = DataSerializer
    filter_class = DataFilter
    permission_classes = (get_permissions_class(),)

    ordering_fields = (
        "contributor",
        "created",
        "finished",
        "id",
        "modified",
        "name",
        "process_name",
        "process_type",
        "started",
        "type",
    )
    ordering = "-created"

    @action(detail=False, methods=["post"])
    def duplicate(self, request, *args, **kwargs):
        """Duplicate (make copy of) ``Data`` objects."""
        if not request.user.is_authenticated:
            raise exceptions.NotFound

        ids = self.get_ids(request.data)
        queryset = get_objects_for_user(
            request.user, "view_data", Data.objects.filter(id__in=ids)
        )
        actual_ids = queryset.values_list("id", flat=True)
        missing_ids = list(set(ids) - set(actual_ids))
        if missing_ids:
            raise exceptions.ParseError(
                "Data objects with the following ids not found: {}".format(
                    ", ".join(map(str, missing_ids))
                )
            )

        # TODO support ``inherit_collection``
        duplicated = queryset.duplicate(contributor=request.user)

        serializer = self.get_serializer(duplicated, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def get_or_create(self, request, *args, **kwargs):
        """Get ``Data`` object if similar already exists, otherwise create it."""
        response = self.perform_get_or_create(request, *args, **kwargs)
        if response:
            return response

        return super().create(request, *args, **kwargs)

    def perform_get_or_create(self, request, *args, **kwargs):
        """Perform "get_or_create" - return existing object if found."""
        self.define_contributor(request)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        process = serializer.validated_data.get("process")
        process_input = request.data.get("input", {})

        fill_with_defaults(process_input, process.input_schema)

        checksum = get_data_checksum(process_input, process.slug, process.version)
        data_qs = Data.objects.filter(
            checksum=checksum,
            process__persistence__in=[
                Process.PERSISTENCE_CACHED,
                Process.PERSISTENCE_TEMP,
            ],
        )
        data_qs = get_objects_for_user(request.user, "view_data", data_qs)
        if data_qs.exists():
            data = data_qs.order_by("created").last()
            serializer = self.get_serializer(data)
            return Response(serializer.data)

    def _parents_children(self, request, queryset):
        """Process given queryset and return serialized objects."""
        queryset = get_objects_for_user(request.user, "view_data", queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def parents(self, request, pk=None):
        """Return parents of the current data object."""
        return self._parents_children(request, self.get_object().parents)

    @action(detail=True)
    def children(self, request, pk=None):
        """Return children of the current data object."""
        return self._parents_children(request, self.get_object().children)
