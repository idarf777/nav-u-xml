import argparse
import sys
import re
import xml.etree.ElementTree as Et


def read_xml(xml) -> dict:
    result = {}
    root = Et.fromstring(xml)
    for gpoi in root.iter('gpoi'):
        pos = gpoi.find(".//pos")
        lat = float(pos.find('./lat').text)
        lon = float(pos.find('./lon').text)
        name = gpoi.find('.//name/nb').text
        category = gpoi.find('./category').text
        rem = re.match(r'\A\d+:(.+)\Z', category)
        if rem:
            category = rem.group(1)
        # print("%f %f %s %s" % (lat, lon, name, category))
        result.setdefault(category, [])
        result[category].append({'lat': lat, 'lon': lon, 'name': name})

    return result


def convert_geo_t2w(geo) -> dict:
    lat = geo['lat']
    lon = geo['lon']
    return {'lat': lat - 0.00010695*lat + 0.000017464*lon + 0.0046017,
            'lon': lon - 0.000046038*lat - 0.000083043*lon + 0.010040}


def main():
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('-i', '--int-data', type=int, default=0, help='')
    # parser.add_argument('-b', '--bool-data', action='store_true', help='')
    # parser.add_argument('-c', '--counter', type=int, const=50, nargs='?', help='')
    # parser.add_argument('userid', type=int, help='')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r', encoding = 'utf8'), default=sys.stdin)
    args = parser.parse_args()

    pois = read_xml(args.file.read())
    print("Category,Latitude,Longitude,Name")
    for k,v in iter(sorted(pois.items())):
        for h in v:
            wgs = convert_geo_t2w(h)
            print("%s,%f,%f,%s" % (k, wgs['lat'], wgs['lon'], h['name']))


if __name__ == '__main__':
    main()

