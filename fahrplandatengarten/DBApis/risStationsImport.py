import functools
from decimal import Decimal

from fahrplandatengarten.DBApis.risApi import RisApiSession
from fahrplandatengarten.core.models import StopIDKind, Provider, Source, Stop, StopID


@functools.lru_cache
def get_id_kind(id_type):
    id_type = id_type.lower()
    kind = StopIDKind.objects.filter(name=id_type, provider__internal_name__startswith='db_')
    if not kind:
        provider, _ = Provider.objects.get_or_create(
            internal_name='db', friendly_name='Deutsche Bahn')
        kind, _ = StopIDKind.objects.get_or_create(
            name=id_type,
            provider=provider
        )
    return kind


def import_by_eva(eva_id):
    ris_stations = RisApiSession('stations')

    resp = ris_stations.get(f'v1/stop-places/{eva_id}')
    resp.raise_for_status()
    data = resp.json()['stopPlaces'][0]

    resp = ris_stations.get(f'v1/stop-places/{eva_id}/keys')
    resp.raise_for_status()
    keys = {key['type']: key['key'] for key in resp.json()['keys']}

    provider, _ = Provider.objects.get_or_create(
        internal_name='db', friendly_name='Deutsche Bahn')
    source, _ = Source.objects.get_or_create(
        internal_name='db_ris_stations',
        friendly_name='Deutsche Bahn RIS::Stations',
        provider=provider)

    transports = set(data['availableTransports'] + data['availablePhysicalTransports'])

    data = {
        'country': data['countryCode'],
        'latitude': Decimal(data['position']['latitude']),
        'longitude': Decimal(data['position']['longitude']),
        'name': data['names']['DE']['nameLong'],
        'has_long_distance_traffic': 'INTERCITY_TRAIN' in transports or 'HIGH_SPEED_TRAIN' in transports,
    }

    stop = Stop.objects.filter(
        stopid__external_id=eva_id,
        stopid__kind=get_id_kind('eva'),
    ).first()
    if stop is None or stop.provider == provider:
        if stop is None:
            stop = Stop.objects.create(
                provider=provider,
                ifopt=keys.get('IFOPT'),
                **data
            )
            StopID.objects.get_or_create(
                stop=stop,
                external_id=eva_id,
                source=source,
                kind=get_id_kind('eva')
            )
        else:
            for k, v in data.items():
                stop.__setattr__(k, v)
            stop.save()

        for k, v in keys.items():
            if k in ['IFOPT', 'EVA']:
                continue
            StopID.objects.get_or_create(
                stop=stop,
                external_id=v,
                source=source,
                kind=get_id_kind(k)
            )
    return stop


class RisStationImportError(Exception):
    pass
