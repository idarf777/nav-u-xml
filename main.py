import argparse
import sys
import re
import xml.etree.ElementTree as Et
import zipfile


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


def sanitize(s: str) -> str:
    return re.sub('[",\n\r]', ' ', s)


def main():
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('-i', '--int-data', type=int, default=0, help='')
    # parser.add_argument('-b', '--bool-data', action='store_true', help='')
    # parser.add_argument('-c', '--counter', type=int, const=50, nargs='?', help='')
    # parser.add_argument('userid', type=int, help='')
    parser.add_argument('-g', '--googlemapsurl', action='store_true', help='google mapsのURLを出力する')
    parser.add_argument('-z', '--zip', help='zipファイルパス')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r', encoding = 'utf8'), default=sys.stdin)
    args = parser.parse_args()
    is_url = args.googlemapsurl
    zipout = args.zip

    buf = []
    pois = read_xml(args.file.read())
    if is_url:
        buf.append("タイトル,メモ,URL")
    else:
        buf.append("Category,Latitude,Longitude,Name")
    for k,v in iter(sorted(pois.items())):
        for h in v:
            wgs = convert_geo_t2w(h)
            if is_url:
                buf.append("%s,,https://www.google.com/maps/@%.6f,%.6f,20z" % (sanitize(h['name']), wgs['lat'], wgs['lon']))
            else:
                buf.append("%s,%f,%f,%s" % (sanitize(k), wgs['lat'], wgs['lon'], sanitize(h['name'])))

    if zipout:
        with zipfile.ZipFile(zipout, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            with zf.open('imported_nav-u.csv', 'w') as f:
                f.write('\n'.join(buf).encode())
    else:
        print('\n'.join(buf))


if __name__ == '__main__':
    main()

