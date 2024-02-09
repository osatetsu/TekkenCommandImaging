# 鉄拳コマンドの画像化ツール

Tekken game command imager.

English version is [README_en](README_en.md).

このツールは格闘ゲームの鉄拳シリーズで使用されるコマンド表記を、背景透過の png 画像にするものです。

鉄拳初心者のみなさんが電卓表記されても分からないということで、その一助になればと思い作成しています。
生成した画像は動画やブログ、SNSなどでもご利用いただけます。

## インストール

特にインストール作業はありませんが、事前準備が必要です。
事前準備が終われば、ダウンロードした python スクリプトを実行することになります。

### 事前準備(1)

事前に python 3.12 以上の実行環境を用意してください。
おそらく、3.6 以降であれば動作するとは思いますが、私の動作環境は 3.12 で、それより前については未確認です。

もし、Windows 10/11 を使用中の場合は、Microsoft store からインストール可能です。

### 事前準備(2)

このツールで使用している外部モジュールをダウンロード、インストールします。
下記コマンドを実行してください。

```.sh
pip install -r requirements.txt
```

## 使い方

コマンドラインで実行します。
Windows であれば、コマンドプロンプト、あるいは、Power Shell や Terminal から下記のように実行してください。

```.sh
python tekken_command_image.py -o 出力ファイル名 'コマンド'
```

機能

 * コマンド自体は、日本で主体のテンキー表記が使用可能です。
    * 方向は、1234n6789
    * ボタンは、LP, RP, WP, LK, RK, WK
    * 大文字、小文字はどちらも使用可能で、混在してもOK
    * スライド表記は `[ ]` の間に記述
    * コマンドの区切りは、 `>` または `,`
    * 方向、および、ボタンの境目を見やすくするために ` ` (半角スペース)を使用可能

方向キーとボタンの関係

```
 7 8 9   LP RP (両パンチ 'WP')
 4 n 6 
 1 2 3   LK RK (両キック 'WK')
```
![方向とボタン](images/dir-button.png)

### 例: 風神拳

ニュートラルがあるコマンドの例として。

```.sh
python tekken_command_image.py -o images/fujinken.png '6n23RK'
```

![風神拳](images/fujinken.png)

### 例: 箭疾歩(ぜんしっぽ) - Tekken 7

スライド入力(素早く攻撃ボタンを連続で押す)の例として。
パンチやキック表記は小文字でも表記可能です。

```.sh
python tekken_command_image.py -o images/zenshippo.png '6[lklp]'
```

![箭疾歩](images/zenshippo.png)

### 例: ニーナ空中コンボ

コマンドが長大な例として。

```.sh
python tekken_command_image.py -o output.png '3RP > 9RK > 9LK > 3LKRP1RP > 66 > 3LKRP4RK > 66 > 236RKLKWP' 
```

![Nina combo](images/nina_combo.png)


## 制限

 1. 現状、ボタンの同時押し表記(例: `LP+RK`)は、未対応です。

## ライセンス

ソースコード、および、ドキュメントは GPLv3 です。

## 最後に

 * 機能追加のご要望、あるいは、不具合報告は [Issues](https://github.com/osatetsu/TekkenCommandImaging/issues) へしていただければと思います。
 * ko-fi にてご寄付いただけると、活動の励みになります。

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/E1E1U0BU1)
