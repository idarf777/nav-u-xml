import argparse
import sys
import re
import xml.etree.ElementTree as Et
import zipfile


def read_xml(xml: str) -> dict:
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


def convert_geo_t2w(geo: dict) -> dict:
    lat = geo['lat']
    lon = geo['lon']
    return {'lat': lat - 0.00010695*lat + 0.000017464*lon + 0.0046017,
            'lon': lon - 0.000046038*lat - 0.000083043*lon + 0.010040}


# ファイルパスに使えない文字を全角に変換する
PATH_SANITIZER = str.maketrans({
    '\\': '＼',
    '/': '／',
    ':': '：',
    '*': '＊',
    '?': '？',
    '"': '”',
    "<": "＜",
    ">": "＞",
    "|": "｜",
    " ": "　"
})
CSV_SANITIZER = str.maketrans({
    '"': '”'
})


def sanitize(s: str, is_file: bool = True) -> str:
    return re.sub(r'\s', '　', s.translate(PATH_SANITIZER)) if is_file else re.sub(r'\s', ' ', s.translate(CSV_SANITIZER))


def main():
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('-i', '--int-data', type=int, default=0, help='')
    # parser.add_argument('-b', '--bool-data', action='store_true', help='')
    # parser.add_argument('-c', '--counter', type=int, const=50, nargs='?', help='')
    # parser.add_argument('userid', type=int, help='')
    parser.add_argument('-z', '--zipfile', help='NaviConで読み込む用のZIPファイル出力先')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r', encoding = 'utf8'), default=sys.stdin)
    args = parser.parse_args()
    outfile = args.zipfile
    pois = read_xml(args.file.read())
    if outfile:
        with zipfile.ZipFile(outfile, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
            for category, hash_list in iter(sorted(pois.items())):
                with zf.open(f'{sanitize(category)}.csv', 'w') as f:
                    buf = ["タイトル,メモ,URL,コメント"]
                    for h in hash_list:
                        wgs = convert_geo_t2w(h)
                        buf.append('"%s",,"https://www.google.com/maps/search/%.6f,%.6f",' % (sanitize(h['name']), wgs['lat'], wgs['lon']))
                    f.write('\n'.join(buf).encode())
    else:
        print("Category,Latitude,Longitude,Name")
        for category, hash_list in iter(sorted(pois.items())):
            for h in hash_list:
                wgs = convert_geo_t2w(h)
                print('"%s",%f,%f,"%s"' % (sanitize(category, is_file = False), wgs['lat'], wgs['lon'], sanitize(h['name'], is_file = False)))


if __name__ == '__main__':
    main()

