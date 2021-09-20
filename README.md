# WeatherDataScraper

## 概要
気象庁の"過去の気象データ検索"ページから天気情報をスクレーピングしDBに保存するプログラムです。  
[気象庁|過去の気象データ検索](http://www.data.jma.go.jp/obd/stats/etrn/index.php)  

以下の3つのモジュールから構成されています。

1. 全国159の観測地点情報を取得し、DBに保存するプログラム
1. 指定した年のデータを取得し、CSVファイルに保存するプログラム
1. 保存したCSVをDBに保存するプログラム

データを一旦CSVに落とすのは、スクレーピングのためのデータが一部欠けていたりするためです。  
スクレーピングは時間がかかる処理のため、失敗した部分だけ再トライできるようにする必要がありました。

## 準備
- 開発環境は以下の通りです。
	- Windows 10
	- Python 3.8

※ 実行にはvenvを作成することをお勧めします  
`py -m venv myvenv`  
必要なモジュールもインストールしてください  
`py -m pip install -r requirements.text`

## 観測地点情報の取得
コマンド
`py scrape_statins.py`  
実行したファルダの下に"data/weather.sqlite3"というファイルが作成されます。  

## 過去データの取得
コマンド  
`py scrape_past_weather.py [year] [code]`  

year: 取得する年を指定します。
- 単年の場合 → year:2021
- 複数年の指定場合 → year:2021,2020,2019  
- 複数年をレンジで指定 → year:2021-2010

code: 特定の観測地点のデータを取得する場合に指定します。
- 全て → 指定しない
- 単独の観測地点 → code:47401
- 複数の観測地点 → code:47402, 47403  
※codeはstationsテーブルの'code'を参照してください。  
※codeは連続しているものでは無いので、レンジ指定はできません

例：`py scrape_past_weather.py year:2021,2020 code:47401`

実行するとdataフォルダの下にcsvファイルが作成されます。  
例. data/weather_2011.csv

## データの取り込み
作成したCSVファイルをDBに取り込みます

コマンド  
`py import_weather_data.py [year]`  

year: インポートする年を指定します。  
- 指定の仕方はscrape_past_weatherと同じです。
- data/weather_[year].csvファイルの内容をDBに書き込みます  
※ データ登録時に当該年度のデータを一旦消すため、重複登録はされません

例：`py import_weather_data.py year:2021,2020`