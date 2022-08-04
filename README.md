# nav-u-xml

## Overview
SONYボータブルナビnav-uシリーズ(NV-U75VT, etc)のユーザ登録地点をCSVに変換して出力する。

[NaviCon](https://play.google.com/store/apps/details?id=jp.co.denso.navicon.view)で取り込む用のZIPファイルを出力可能なので、Android端末があればNaviCon経由でnav-uから別のナビに登録地点を転送できる。

### Requirements

- python 3.x

## Getting Started

### ユーザ登録地点のエクスポート

1. nav-uでメモリースティックduoに登録地点をエクスポートする。
2. PCでメモリースティックduoを読み込み、mark_export.xmlをPCのローカルドライブにコピーする。

### 単一のCSVに出力

````
python ./main.py mark_export.xml
````

次のような出力を得る。緯度経度は世界測地系である。

```
Category,Latitude,Longitude,Name
"買い物",34.605316,138.224303,"海鮮なぶら市場"
"買い物",35.118235,138.839977,"ららぽーと沼津"
```


### NaviCon用ZIPファイルに出力

````
python ./main.py mark_export.xml -zip out.zip
````

#### ZIPファイルの取り込み

1. ZIPファイルを端末に転送

   - Bluetooth転送やgoogleドライブ等を経由してAndroid端末にout.zipを転送する。

2. NaviConにZIPを取り込む

   - [File](https://play.google.com/store/apps/details?id=com.google.android.apps.nbu.files)等のファイラーアプリでout.zipを「共有」し、共有先にNaviConを選択する。


**Warning**
ここではNaviConおよびその操作方法については関知いたしません。


## Author

[twitter](https://twitter.com/idarf777)

## License

[GPL3](./LICENSE)