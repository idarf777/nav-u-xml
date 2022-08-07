import argparse
import sys
import re
import traceback
import xml.etree.ElementTree as Et
import zipfile
from pprint import pprint

from mapfan_api import MapfanApi


def read_xml(xml: str, s_category: str|None, s_max: int) -> dict:
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
        if (s_category is not None) & (s_category != sanitize(category, is_file = False)):
            continue
        # print("%f %f %s %s" % (lat, lon, name, category))
        result.setdefault(category, [])
        if (s_max < 0) | (len(result[category]) < s_max):
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


def proc_mapfan(loginid: str, password: str, pois: dict):
    api = MapfanApi()
    try:
        print("Status: authorizing MapFan...", file = sys.stderr)
        api.authorize(loginid, password)
        for category, hash_list in iter(sorted(pois.items())):
            for h in hash_list:
                wgs = convert_geo_t2w(h)
                addr = api.get_address(wgs['lat'], wgs['lon'])
                bookmark = api.post_bookmark(wgs['lat'], wgs['lon'], sanitize(h['name']), sanitize(re.sub(r'\s', '', addr.get('address'))))
                print(f"Status: posted {bookmark['name']}", file = sys.stderr)
    except Exception as e:
        print(f"Error: {traceback.format_exception_only(type(e), e)}", file = sys.stderr)


def proc_zipfile(outfile: str, pois: dict):
    with zipfile.ZipFile(outfile, 'w', compression = zipfile.ZIP_DEFLATED) as zf:
        for category, hash_list in iter(sorted(pois.items())):
            with zf.open(f'{sanitize(category)}.csv', 'w') as f:
                buf = ["タイトル,メモ,URL,コメント"]
                for h in hash_list:
                    wgs = convert_geo_t2w(h)
                    buf.append('"%s",,"https://www.google.com/maps/search/%.6f,%.6f",' % (sanitize(h['name']), wgs['lat'], wgs['lon']))
                f.write('\n'.join(buf).encode())


def proc_csv(pois: dict):
    print("Category,Latitude,Longitude,Name")
    for category, hash_list in iter(sorted(pois.items())):
        for h in hash_list:
            wgs = convert_geo_t2w(h)
            print('"%s",%f,%f,"%s"' % (sanitize(category, is_file = False), wgs['lat'], wgs['lon'], sanitize(h['name'], is_file = False)))


def main():
    parser = argparse.ArgumentParser(description = __doc__, formatter_class = argparse.RawDescriptionHelpFormatter)
    # parser.add_argument('-i', '--int-data', type=int, default=0, help='')
    # parser.add_argument('-b', '--bool-data', action='store_true', help='')
    # parser.add_argument('-c', '--counter', type=int, const=50, nargs='?', help='')
    parser.add_argument('--mapfan', help='MapFanのブックマークを登録する (MapFan会員ID,パスワードをカンマ区切りで指定する)')
    parser.add_argument('--category', help='特定のカテゴリ名だけを対象にする')
    parser.add_argument('--zipfile', help='NaviConで読み込む用のZIPファイルを生成する (ファイルパスを指定する)')
    parser.add_argument('--csv', action='store_true', help='CSVをstdoutに出力する')
    parser.add_argument('--max', type=int, default=-1, help='カテゴリ内の最大出力件数')
    parser.add_argument('file', nargs='?', type=argparse.FileType('r', encoding = 'utf8'), default=sys.stdin)
    args = parser.parse_args()
    pois = read_xml(args.file.read(), sanitize(args.category, is_file = False) if args.category else None, args.max)

    if (args.mapfan is None) & (args.zipfile is None) & (args.csv is None):
        print("Error: いずれかの出力指定が必要です。", file = sys.stderr)
        exit(1)

    if args.mapfan:
        acc = args.mapfan.split(',')
        if len(acc) != 2 | len(acc[0]) == 0 | len(acc[1]) == 0:
            print("Error: MapFan会員IDまたはパスワードが不正です。", file = sys.stderr)
            exit(2)
        proc_mapfan(acc[0], acc[1], pois)

    if args.zipfile:
        proc_zipfile(args.zipfile, pois)

    if args.csv:
        proc_csv(pois)


if __name__ == '__main__':
    main()

