"""
Experimentation views
"""


from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from edx_rest_framework_extensions.auth.session.authentication import SessionAuthenticationAllowInactiveUser
from rest_framework import permissions, viewsets

from experiments import filters, serializers
from experiments.models import ExperimentData, ExperimentKeyValue
from experiments.permissions import IsStaffOrOwner, IsStaffOrReadOnly
from openedx.core.djangoapps.cors_csrf.authentication import SessionAuthenticationCrossDomainCsrf

User = get_user_model()  # pylint: disable=invalid-name


class ExperimentCrossDomainSessionAuth(SessionAuthenticationAllowInactiveUser, SessionAuthenticationCrossDomainCsrf):
    """Session authentication that allows inactive users and cross-domain requests. """
    pass


class ExperimentDataViewSet(viewsets.ModelViewSet):
    authentication_classes = (JwtAuthentication, ExperimentCrossDomainSessionAuth,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ExperimentDataFilter
    permission_classes = (permissions.IsAuthenticated, IsStaffOrOwner,)
    queryset = ExperimentData.objects.all()
    serializer_class = serializers.ExperimentDataSerializer
    _cached_users = {}

    def filter_queryset(self, queryset):
        queryset = queryset.filter(user=self.request.user)
        return super(ExperimentDataViewSet, self).filter_queryset(queryset)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ExperimentDataCreateSerializer
        return serializers.ExperimentDataSerializer

    def create_or_update(self, request, *args, **kwargs):
        # If we have a primary key, treat this as a regular update request
        if self.kwargs.get('pk'):
            return self.update(request, *args, **kwargs)

        # If we only have data, check to see if an instance exists in the database. If so, update it.
        # Otherwise, create a new instance.
        experiment_id = request.data.get('experiment_id')
        key = request.data.get('key')

        if experiment_id and key:
            try:
                obj = self.get_queryset().get(user=self.request.user, experiment_id=experiment_id, key=key)
                self.kwargs['pk'] = obj.pk
                return self.update(request, *args, **kwargs)
            except ExperimentData.DoesNotExist:
                pass

        self.action = 'create'
        return self.create(request, *args, **kwargs)

    def _cache_users(self, usernames):
        users = User.objects.filter(username__in=usernames)
        self._cached_users = {user.username: user for user in users}

    def _get_user(self, username):
        user = self._cached_users.get(username)

        if not user:
            user = User.objects.get(username=username)
            self._cached_users[username] = user

        return user


class ExperimentKeyValueViewSet(viewsets.ModelViewSet):
    authentication_classes = (JwtAuthentication, ExperimentCrossDomainSessionAuth,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = filters.ExperimentKeyValueFilter
    permission_classes = (IsStaffOrReadOnly,)
    queryset = ExperimentKeyValue.objects.all()
    serializer_class = serializers.ExperimentKeyValueSerializer
