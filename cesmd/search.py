# stdlib imports
import zipfile
import io
import os.path
import pathlib

# third party imports
from requests import Session, Request

URL_TEMPLATE = 'https://strongmotioncenter.org/testuser/wserv2/records/query'
RETURN_TYPES = ['dataset', 'metadata']
PROCESS_LEVELS = ['processed', 'raw', 'plots', 'all']
GROUP_OPTIONS = ['station', 'event']

NETWORKS = {"08": "Hokkaido University",
            "AA": "AA - Anchorage Strong Motion Network",
            "AK": "AK - University of Alaska Geophysical Institute",
            "AZ": "AZ - Anza",
            "BG": "BG - Berkeley Geysers Network",
            "BK": "BK - Berkeley Digital Seismic Network",
            "C1": "C1 - Red Sismologica Nacional",
            "CB": "CB - Institute of Geophysics China Earthquake Administration (IGP)",
            "CE": "CE - California Strong Motion Instrumentation Program",
            "CF": "CF - Red Acelerografica Nacional de la Comision Federal de Electr",
            "CI": "CI - California Institute of Technology",
            "CU": "CU - Albuquerque Seismological Laboratory",
            "C_": "C_ - C&GS",
            "EC": "EC - Ecuador Seismic Network",
            "ES": "ES - Spanish Digital Seismic Network",
            "GI": "GI - Red Sismologica Nacional-Guatemala",
            "G_": "G_ - GEOSCOPE",
            "HV": "HV - Hawaiian Volcano Observatory Network",
            "IT": "IT - Italian Strong Motion Network",
            "IU": "IU - GSN - IRIS/USGS",
            "IV": "IV - Istituto Nazionale di Geofisica e Vulcanologia",
            "JP": "JP - BRI",
            "LA": "LA - Los Angeles Basin Seismic Network",
            "MN": "MN - Mediterranean Very Broadband Seismographic Network",
            "NC": "NC - USGS Northern California Regional Network",
            "ND": "ND - New Caledonia Broadband Seismic Network (SismoCal)",
            "NM": "NM - New Madrid Seismic Network",
            "NN": "NN - Nevada Seismic Network",
            "NP": "NP - National Strong Motion Project",
            "NZ": "NZ",
            "OK": "OK - Oklahoma Geological Survey",
            "OV": "OV - Observatorio Vulcanologico y Sismologico de Costa Rica",
            "PA": "PA - Observatorio Sismico del Occidente de Panamá",
            "PG": "PG",
            "PR": "PR - Puerto Rico Strong Motion Program (PRSMP)",
            "TO": "TO - Caltech Tectonic Observatory",
            "TU": "TU - Turkey Strong Motion Network",
            "US": "US - National Earthquake Information Center",
            "UW": "UW - PNSN",
            "WR": "WR - California Department of Water Resources",
            "_C": "_C - Chile"}

STATION_TYPES = {"A": "Array",
                 "G": "Ground",
                 "B": "Building",
                 "Br": "Bridge",
                 "D": "Dam",
                 "T": "Tunnel",
                 "W": "Wharf",
                 "O": "Other", }

FAULT_TYPES = ['NM', 'RS', 'SS']

# for those search parameters where the Python names differ from the ones
# defined by the web API, use this translation table.
KEY_TABLE = {'return_type': 'rettype',
             'process_level': 'download',
             'group_by': 'groupby',
             'min_station_dist': 'minepidist',
             'max_station_dist': 'maxepidist',
             'network': 'netid',
             'station_type': 'sttype',
             'include_inactive': 'abandoned',
             'station_name': 'stname',
             'min_station_latitude': 'minlat',
             'max_station_latitude': 'maxlat',
             'min_station_longitude': 'minlon',
             'max_station_longitude': 'maxlon',
             'station_latitude': 'slat',
             'station_longitude': 'slon',
             'station_radius': 'srad',
             'station_code': 'stcode',
             'event_name': 'evname',
             'fault_type': 'faulttype',
             'min_event_latitude': 'eminlat',
             'max_event_latitude': 'emaxlat',
             'min_event_longitude': 'eminlon',
             'max_event_longitude': 'emaxlon',
             'event_latitude': 'elat',
             'event_longitude': 'elon',
             'event_radius': 'erad',
             }


def get_records(output,
                email,
                unpack=False,
                return_type='dataset',
                process_level='raw',
                group_by='event',
                minpga=None,
                maxpga=None,
                min_station_dist=None,
                max_station_dist=None,
                network=None,
                station_type=None,
                include_inactive=False,
                station_name=None,
                min_station_latitude=None,
                max_station_latitude=None,
                min_station_longitude=None,
                max_station_longitude=None,
                station_latitude=None,
                station_longitude=None,
                radius_km=None,
                station_code=None,
                event_name=None,
                minmag=None,
                maxmag=None,
                fault_type=None,
                startdate=None,
                enddate=None,
                min_event_latitude=None,
                max_event_latitude=None,
                min_event_longitude=None,
                max_event_longitude=None,
                event_latitude=None,
                event_longitude=None,
                event_radius=None,
                eventid=None,
                ):
    """Retrieve strong motion waveform records from CESMD website.

    Args:
        output (str): Filename or directory where downloaded zip data will be written.
        unpack (bool): If True, all zipped files will be unpacked (output will become a directory name.)
        email (str): Email address of requesting user.
        process_level (str): One of 'raw','processed','plots'.
        group_by (str): One of 'event', 'station'
        minpga (float): Minimum PGA value.
        maxpga (float): Maximum PGA value.
        min_station_dist (float): Minimum station distance from epicenter.
        max_station_dist (float): Maximum station distance from epicenter.
        network (str): Source network of strong motion data.
        station_type (str): Type of strong motion station (array, dam, etc.)
        include_inactive (bool): Include results from stations that are no longer active.
        station_name (str): Search only for station matching input name.
        min_station_latitude=None,
        max_station_latitude=None,
        min_station_longitude=None,
        max_station_longitude=None,
        station_latitude=None,
        station_longitude=None,
        radius_km=None,
        station_code=None,
        event_name=None,
        minmag=None,
        maxmag=None,
        fault_type=None,
        start_date=None,
        end_date=None,
        min_event_latitude=None,
        max_event_latitude=None,
        min_event_longitude=None,
        max_event_longitude=None,
        event_latitude=None,
        event_longitude=None,
        event_radius=None,
        eventid=None,
        ...

    """
    # getting the inputargs must be the first line of the method!
    inputargs = locals().copy()
    del inputargs['output']
    del inputargs['unpack']
    if return_type not in RETURN_TYPES:
        fmt = 'Only return types of %s are supported (%s was input)'
        tpl = (','.join(RETURN_TYPES), return_type)
        raise KeyError(fmt % tpl)

    # note: this only supports one of the options or all of them,
    # no other combinations. ??
    if process_level not in PROCESS_LEVELS:
        fmt = 'Only process levels of %s are supported (%s was input)'
        tpl = (','.join(PROCESS_LEVELS), process_level)
        raise KeyError(fmt % tpl)

    if group_by not in GROUP_OPTIONS:
        fmt = 'Only process levels of %s are supported (%s was input)'
        tpl = (','.join(GROUP_OPTIONS), group_by)
        raise KeyError(fmt % tpl)

    # determine which network user wanted
    if network is not None and network not in NETWORKS:
        fmt = 'Network with ID %s not found in list of supported networks.'
        tpl = network
        raise KeyError(fmt % tpl)

    if station_type is not None and station_type not in STATION_TYPES:
        fmt = 'Station type %s not found in list of supported types.'
        tpl = station_type
        raise KeyError(fmt % tpl)

    # check against list of fault types
    if fault_type is not None and fault_type not in FAULT_TYPES:
        fmt = 'Fault type %s not found in supported fault types %s.'
        tpl = (fault_type, ','.join(FAULT_TYPES))
        raise KeyError(fmt % tpl)

    # make sure there is only one method being used to select station geographically
    if min_station_latitude is not None and station_latitude is not None:
        raise Exception(
            'Select stations either by bounding box or by radius, not both.')

    # make sure there is only one method being used to select events geographically
    if min_event_latitude is not None and event_latitude is not None:
        raise Exception(
            'Select events either by bounding box or by radius, not both.')

    # now convert process levels to string webservice expects
    levels = {'processed': 'P',
              'raw': 'R',
              'plots': 'T',
              'all': 'P,R,T'}
    inputargs['process_level'] = levels[process_level]

    # now convert input args to keys of parameters expected by
    params = {}
    for key, value in inputargs.items():
        if key in KEY_TABLE:
            params[KEY_TABLE[key]] = value
        else:
            params[key] = value

    # convert all booleans to strings that are 'true' and 'false'
    for key, value in params.items():
        if isinstance(value, bool):
            if value:
                params[key] = 'true'
            else:
                params[key] = 'false'

    # add in a couple of parameters that seem to be required
    params['orderby'] = 'epidist-asc'
    params['nodata'] = '404'

    session = Session()
    request = Request('GET', URL_TEMPLATE, params=params).prepare()
    url = request.url
    response = session.send(request)

    if not response.status_code == 200:
        fmt = 'Your request returned a status code of %i with message: "%s"'
        raise Exception(fmt % (response.status_code, response.reason))

    if unpack:
        if not os.path.exists(output):
            os.makedirs(output)
        fbytes = io.BytesIO(response.content)
        myzip = zipfile.ZipFile(fbytes, mode='r')
        members = myzip.namelist()
        for member in members:
            finfo = myzip.getinfo(member)
            if finfo.is_dir():
                continue
            print(member)
            if not member.lower().endswith('.zip'):
                fin = myzip.open(member)
                flatfile = member.replace('/', '_')
                outfile = os.path.join(output, flatfile)
                with open(outfile, 'wb') as fout:
                    fout.write(fin.read())
                fin.close()
            else:
                tmpfile = myzip.open(member)
                tmpzip = zipfile.ZipFile(tmpfile, mode='r')
                tmp_members = tmpzip.namelist()
                for tmp_member in tmp_members:
                    if tmp_member.endswith('.zip'):
                        x = 1
                    tfinfo = tmpzip.getinfo(tmp_member)
                    if not tfinfo.is_dir():
                        print(tmp_member)
                        fin = tmpzip.open(tmp_member)
                        flatfile = tmp_member.replace('/', '_')
                        parent, _ = os.path.splitext(member)
                        parent = parent.replace('/', '_')
                        # sometimes the member ends with .zip.zip (??)
                        parent = parent.replace('.zip', '')
                        datadir = os.path.join(output, parent)
                        if not os.path.exists(datadir):
                            os.makedirs(datadir)
                        outfile = os.path.join(datadir, flatfile)
                        if 'zip' in outfile:
                            x = 1
                        with open(outfile, 'wb') as fout:
                            fout.write(fin.read())
                        fin.close()

                tmpzip.close()
                tmpfile.close()
        myzip.close()

        datafiles = []
        for root, fdir, files in os.walk(output):
            for tfile in files:
                if not tfile.endswith('.json'):
                    datafiles.append(tfile)

        return (os.path.abspath(output), datafiles)
    else:
        if not output.endswith('.zip'):
            output += '.zip'
        with open(output, 'wb') as f:
            f.write(response.content)
        return (output, [])
