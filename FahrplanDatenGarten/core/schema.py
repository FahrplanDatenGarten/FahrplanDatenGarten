import graphene
from graphene import ObjectType
from graphene.relay.node import Node, Field
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import *


class ProviderNode(DjangoObjectType):
    class Meta:
        model = Provider
        filter_fields = (
            'friendly_name',
            'internal_name',
        )
        interfaces = (Node, )


class SourceNode(DjangoObjectType):
    class Meta:
        model = Source
        filter_fields = (
            'friendly_name',
            'internal_name',
            'provider',
        )
        interfaces = (Node, )


class StopNode(DjangoObjectType):
    class Meta:
        model = Stop
        filter_fields = (
            'name',
            'ifopt',
            'country',
            'latitude',
            'longitude',
            'provider',
            'has_long_distance_traffic',
        )
        interfaces = (Node, )


class StopIDKindNode(DjangoObjectType):
    class Meta:
        model = StopIDKind
        filter_fields = (
            'name',
            'provider',
        )
        interfaces = (Node, )


class StopIDNode(DjangoObjectType):
    class Meta:
        model = StopID
        filter_fields = (
            'external_id',
            'source',
            'kind',
        )
        interfaces = (Node, )


class JourneyNode(DjangoObjectType):
    class Meta:
        model = Journey
        filter_fields = (
            'name',
            'stop',
            'date',
            'journey_id',
            'source',
            'cancelled',
        )
        interfaces = (Node, )


class JourneyStopNode(DjangoObjectType):
    actual_arrival_time = graphene.DateTime()
    actual_departure_time = graphene.DateTime()

    actual_arrival_delay = graphene.String()    # TODO: Maybe find a nicer way here...
    actual_departure_delay = graphene.String()  # TODO: See https://github.com/graphql-python/graphene-django/issues/348

    class Meta:
        model = JourneyStop
        filter_fields = (
            'stop',
            'journey',
            'planned_arrival_time',
            'planned_departure_time',
            'actual_arrival_delay',
            'actual_departure_delay',
            'cancelled',
        )
        interfaces = (Node, )

    def resolve_actual_arrival_time(self, info, **kwargs):
        return self.get_actual_arrival_time()

    def resolve_actual_departure_time(self, info, **kwargs):
        return self.get_actual_departure_time()


class Query(ObjectType):
    provider = Field(ProviderNode)
    providers = DjangoFilterConnectionField(ProviderNode)
    source = Field(SourceNode)
    sources = DjangoFilterConnectionField(SourceNode)
    stop = Field(StopNode)
    stops = DjangoFilterConnectionField(StopNode)
    stopidkind = Field(StopIDKindNode)
    stopidkinds = DjangoFilterConnectionField(StopIDKindNode)
    stopid = Field(StopIDNode)
    stopids = DjangoFilterConnectionField(StopIDNode)
    journey = Field(JourneyNode)
    journeys = DjangoFilterConnectionField(JourneyNode)
    journey_stop = Field(JourneyStopNode)
    journey_stops = DjangoFilterConnectionField(JourneyStopNode)
