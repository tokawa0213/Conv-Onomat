#!/usr/bin/python3.3
# -*- coding:utf-8 -*-
r""" 「小説家になろう」のWebページを解析し、青空文庫形式TEXTっぽいファイルをカレントパスに作る.


使い方
・起動パラメータにNコードを指定する (複数指定可)
・--aozoraオプションで青空文庫形式TEXTのファイルを生成する
・--epub3オプションでEPUB 3.0形式のファイルを生成する
・-l --localオプションで取得済みのローカルデータからファイルを生成する
・-s 更新の有無だけを取得し表示する

# コンパイルしておく場合
#python3 -m compileall narouTo.py

# 更新の有無だけを取得し表示する (ダウンロードをしない)
$ narouTo.py N9669BK N4251CR N6316BN
　　or
$ narouTo.py N9669BK N4251CR N6316BN --aozora -s

# ダウンロードをして、青空文庫形式TEXTファイルを生成する場合
$ narouTo.py N9669BK N4251CR N6316BN --aozora

# ダウンロードをせず、取得済みのローカルデータから青空文庫形式TEXTファイルを生成する場合
$ narouTo.py N9669BK N4251CR N6316BN --aozora --local

# ダウンロードをせず、取得済みのローカルデータからEPUB 3.0形式ファイルを生成する場合
$ narouTo.py N9669BK N4251CR N6316BN --epub3 --local


注意
・HTML文書からテキストを抜き出している
・WebサイトのHTML文書の構造が変わったら、プログラムの対応が必要
・出力するテキストファイルのエンコードはUTF-8
・ルビ対応済み (各小説の作者独自のルビ？には未対応)
・代替表現はビューアーによって対応状況が違うので適当に手抜き
・挿絵対応 (pngのオリジナル画像を挿し絵として扱う)
・エラー処理は殆ど入れていない
・サーバー側の負荷を考えて1部取得毎にディレイ(1秒)を設定する.
・1つの小説につき9999部まで


取得対象Webサイト：小説家になろう
　小説情報ページ(Nコード／あらすじ／作者名／掲載日／最終話掲載日など)
　http://ncode.syosetu.com/novelview/infotop/ncode/$Nコード$/

　目次ページ(章の一覧)
　http://ncode.syosetu.com/$Nコード$/

　小説本文
　http://ncode.syosetu.com/$Nコード$/$章番号$/

　挿し絵(原本)　＊外部サイト：みてみん
　http://$作者ID$.mitemin.net/userpageimage/viewimagebig/icode/$icode$/


使用している青空文庫のタグ
［＃大見出し］$見出し1$［＃大見出し終わり］
［＃中見出し］$見出し2$［＃中見出し終わり］
［＃改ページ］
｜$名称$《$ルビ$》
［＃（$画像ファイルのパス$）入る］


EPUB 3.0
　日本電子書籍出版社協会
　http://ebpaj.jp/

　電書協 EPUB 3 制作ガイド
　http://ebpaj.jp/counsel/guide

　「電書協 EPUB 3 制作ガイド ver.1.1.3 2015年1月1日版」
　http://ebpaj.jp/images/ebpaj_epub3guide_ver1.1.3-150101.zip

　「電書協 EPUB 3 制作ガイド ver.1.1.3」追加サンプルファイル
　http://ebpaj.jp/cmspage/wp/wp-content/uploads/2012/12/ebpaj-viewsamples-201511011.zip


動作に必要なもの
　Python Ver 3.3以降
　Beautiful Soup 4
　  https://www.crummy.com/software/BeautifulSoup/
　  $ sudo apt-get install python3-bs4
      または
    $ pip install beautifulsoup4

開発環境
　Python 3.4.3 / Ubuntu 14.04
　Python 3.6.4 / Android 5.1


更新履歴　(__PROGRAM_VERSIONも書き換えること)
2016-11-02  新規作成
2016-11-18　前書きと後書きの挿し絵に対応
2016-12-01　EPUB 3にて文中の'&', '<', '>'をHTMLの特殊文字に変換
2017-10-23　章情報ページの掲載日付の書式変更に対応(YYYY年 MM月 DD日→YYYY/MM/DD)
          　本文ページの画像URLの変更に対応(miteminのURLの先頭が//となった)
2018-01-15　長編作品対応(本文ファイル名の部数の桁数を3桁→4桁)
          　Nコード大文字化
          　＊＊ローカルデータを削除して取り直して下さい
          　＊＊またはファイル名の先頭3桁をゼロ詰め4桁にリネームして下さい
2018-02-18　Beautiful Soup 4.4.x対応
          　ファイル名文字数制限(小章タイトルを30、大章タイトルを30)
"""
import os
import sys
import re
import argparse
import textwrap
import time
import zipfile
import urllib.request
from bs4 import BeautifulSoup

# ------------------------------------------------------------------------------
# 定数の定義　(非公開)
# ------------------------------------------------------------------------------

# バージョン番号
__PROGRAM_VERSION = "20180218"

# 差分ファイルの格納先
# 　os.getcwd()              カレント (Win/Linux)
# 　os.path.expanduser('~')  ホームディレクトリ(Win/Linux)
__PATH_WORK = os.path.join(os.getcwd(), "narouTo4")

# アーカイブファイルの格納先
__PATH_ARCHIVE = os.getcwd()


# ------------------------------------------------------------------------------
# 定数の定義　(公開)
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 変数の定義　(非公開)
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# 変数の定義　(公開)
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# クラスの定義　(非公開)
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# クラスの定義　(公開)
# ------------------------------------------------------------------------------

class Downloader(object):
    r"""
    クラス名　なろうダウンローダー

    「小説家になろう」のWebサイトを解析し小説をダウンロードする。
    本クラスはユーティリティー的なクラスなため、インスタンス化はしない。

    公開メソッド
    def getNovel( ncode, oPath ):
    """
    # --------------------------------------------------------------------------
    # クラス定数の定義　(非公開)
    # --------------------------------------------------------------------------

    # 連載有無文字
    __NOVELTYPE_END = "完結済"
    __NOVELTYPE_NOTEND = "連載中"

    # 小説情報ページのURL
    # 　{0}  Nコード
    __URL_HEADER = "http://ncode.syosetu.com/novelview/infotop/ncode/{0}/"

    # 章情報ページ(トップページ)のURL
    # 　{0}  Nコード
    __URL_RECORD = "http://ncode.syosetu.com/{0}/"

    # 本文ページのURL
    # 　{0}  Nコード
    # 　{1}  章の番号
    __URL_BODY = "http://ncode.syosetu.com/{0}/{1}/"

    # Webページ取得遅延時間 (Webサーバーの負荷にならないように注意する)
    __HTTP_WAIT = 1.0  # 1000ms

    # 本文ファイル名
    # 　{0}  Nコード
    # 　{1}  章番号
    # 　{2}  小章の名称
    # 　{3}  大章の名称
    # 　{4}  掲載日付(YYYYMMDD)
    __OUTPUT_FNAME_BODY = "{1:0>4}_{4}_「{3} {2}」"

    # --------------------------------------------------------------------------
    # クラス定数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(非公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    __RE_RUBY_TAG = re.compile(r'<ruby>.*?</ruby>')
    __RE_RUBY_CLEAR = re.compile(r'<[^>]*?>')

    @staticmethod
    def __changeRuby(html):
        r""" HTMLルビを青空文庫ルビに置換する.

        Args:
            html HTMLテキスト
        Returns:
            置換後のHTMLテキスト
        Raises:
            None
        """
        html = html.replace("《", "≪")
        html = html.replace("》", "≫")
        html = html.replace("｜", "|")
        match = __class__.__RE_RUBY_TAG.search(html)
        while match:
            submatch = match.group()

            tmp = __class__.__RE_RUBY_CLEAR.sub('', submatch)
            tmp = tmp.replace("(", "《").replace("（", "《")
            tmp = tmp.replace(")", "》").replace("）", "》")
            tmp = tmp.replace("≪", "《")
            tmp = tmp.replace("≫", "》")
            tmp = r"｜" + tmp

            html = html.replace(submatch, tmp)
            match = __class__.__RE_RUBY_TAG.search(html)

        return html

    @staticmethod
    def __getHeader(ncode):
        r""" 小説情報取得.

        「小説家になろう」の小説情報ページを解析し、小説の情報を取得する。

        Args:
            ncode Nコード
        Returns:
            小説情報 (ディクショナリ型)

              ncode      1 Nコード
              title      1 小説タイトル
              noveltype  1 '完結済' OR '連載中'
              ex         1 あらすじ
              writer     1 作者名
              date1      1 掲載日 (YYYY-MM-DD)
              date2      1 最終話掲載日 (YYYY-MM-DD)
        Raises:
            None
        """
        url = __class__.__URL_HEADER.format(ncode);
        with urllib.request.urlopen(url) as response:
            html = response.read()

        soup = BeautifulSoup(
            __class__.__changeRuby(html.decode('utf-8')), 'html.parser')

        header = {}

        # Nコード
        header['ncode'] = soup.find(id='ncode').string.strip()

        # 小説タイトル
        header['title'] = soup.h1.string.rstrip()

        # 連載状況
        # 　完結済　'noveltype'
        # 　連載中　'noveltype_notend'
        if soup.find(id='noveltype'):
            header['noveltype'] = __class__.__NOVELTYPE_END

        else:
            header['noveltype'] = __class__.__NOVELTYPE_NOTEND

        # あらすじ
        # 作者名
        cols = soup.find(id='noveltable1').findAll('td')
        header['ex'] = cols[0].get_text().rstrip()
        header['writer'] = cols[1].get_text().rstrip()

        # 掲載日
        # 最終話掲載日
        cols = soup.find(id='noveltable2').findAll('td')
        header['date1'] = cols[0].get_text().rstrip()
        header['date2'] = cols[1].get_text().rstrip()

        header['date1'] = "{0}-{1}-{2} {3}:{4}:00".format(
            header['date1'][0:4]
            , header['date1'][6:-11]
            , header['date1'][9:-8]
            , header['date1'][13:-4]
            , header['date1'][16:-1])

        header['date2'] = "{0}-{1}-{2} {3}:{4}:00".format(
            header['date2'][0:4]
            , header['date2'][6:-11]
            , header['date2'][9:-8]
            , header['date2'][13:-4]
            , header['date2'][16:-1])

        return header

    #    __RE_RECORD_DATE = re.compile( r'(\d\d\d\d)年 (\d\d)月 (\d\d)日' )
    __RE_RECORD_DATE = re.compile(r'(\d{4})/(\d{1,2})/(\d{1,2})')
    __RE_RECORD_ID = re.compile(r'^.*\/(.*)\/$')

    @staticmethod
    def __getRecords(ncode):
        r""" 章情報取得.

        「小説家になろう」の小説のトップページを解析し、章の情報を取得する。

        各章(本文)の公開順の通し番号っぽいが、抜けの有無が不明なため数字ではなくIDとして扱う。

        Args:
            ncode Nコード
        Returns:
        　　章情報リスト (リスト型)
              0..*  章情報 (ディクショナリ型)
                id              1    章の番号
                novel_sublist2  1    小章の名称
                chapter_title   0..1 大章の名称
                long_update     1    掲載日付(YYYYMMDD)
                flagChap        1    章内で先頭の見出しを表す(True/False)
        Raises:
            None
        """
        url = __class__.__URL_RECORD.format(ncode)
        with urllib.request.urlopen(url) as response:
            html = response.read()

        soup = BeautifulSoup(html.decode('utf-8'), 'html.parser')

        records = []
        tags = soup.find(class_='index_box').findAll(['div', 'dl'])
        chapName = None
        flagChap = False
        for tag in tags:
            if 'div' == tag.name and 'chapter_title' == tag['class'][0]:

                tmp = tag.getText().rstrip()
                if tmp != chapName:
                    flagChap = True

                chapName = tmp

            elif 'dl' == tag.name and 'novel_sublist2' == tag['class'][0]:
                tagA = tag.dd.a

                record = {}
                record['id'] = \
                    __class__.__RE_RECORD_ID.match(tagA['href']).group(1)
                record['novel_sublist2'] = tagA.getText().rstrip()
                record['chapter_title'] = ""
                if chapName:
                    record['chapter_title'] = chapName

                tmp = tag.dt.getText()
                if tag.dt.span:
                    tmp = tag.dt.span['title']
                tmp.strip()

                match = __class__.__RE_RECORD_DATE.search(tmp)
                record['long_update'] = "{}{}{}".format(
                    match.group(1), match.group(2), match.group(3))
                record['flagChap'] = flagChap

                records.append(record)

                flagChap = False

        return records

    __RE_BODY_IMAGETAG = re.compile(r'[ \t\u3000]*__IMAGE_(.*?)_IMAGE__')
    __RE_BODY_BLANKLINE1 = re.compile(r'[ \t\u3000]+\n')
    __RE_BODY_BLANKLINE2 = re.compile(r'\n\n\n\n+')

    @staticmethod
    def __getBody(ncode, id, oPath):
        r""" 本文情報取得.

        「小説家になろう」の本文ページを解析し、前書き／本文／後書きのテキストを取得する。

        Args:
            ncode  Nコード
            id     章の番号
            oPath  出力先パス
        Returns:
            本文情報 (ディクショナリ型)
              bef    0..1 前書きのテキスト (HTMLのタグは除去済み)
              aft    0..1 後書きのテキスト (HTMLのタグは除去済み)
              body   1    本文のテキスト (HTMLのタグは除去済み)
        Raises:
            None
        """
        url = __class__.__URL_BODY.format(ncode, id)
        with urllib.request.urlopen(url) as response:
            html = response.read()

        body = {}
        body['body'] = ""
        body['bef'] = ""
        body['aft'] = ""

        soup = BeautifulSoup(
            __class__.__changeRuby(html.decode('utf-8')), 'html.parser')

        # 前書き
        tmp = BeautifulSoup(
            __class__.__getImage(
                str(soup.find(id='novel_p')), ncode, True, oPath), 'html.parser')
        tmp = tmp.find(id='novel_p')
        if tmp:
            body['bef'] = tmp.getText()

        # 後書き
        tmp = BeautifulSoup(
            __class__.__getImage(
                str(soup.find(id='novel_a')), ncode, True, oPath), 'html.parser')
        tmp = tmp.find(id='novel_a')
        if tmp:
            body['aft'] = tmp.getText()

        # 本文
        soup = BeautifulSoup(
            __class__.__getImage(
                str(soup.find(id='novel_honbun')), ncode, True, oPath), 'html.parser')
        body['body'] = soup.find(id='novel_honbun').getText()

        # 一時的な代替タグを青空文庫のタグに変換
        for key in ['bef', 'aft', 'body']:
            match = __class__.__RE_BODY_IMAGETAG.search(body[key])
            while match:
                submatch = match.group()
                urlImage = match.group(1)
                body[key] = body[key].replace(
                    submatch, "［＃（{}）入る］".format(urlImage))

                match = __class__.__RE_BODY_IMAGETAG.search(body[key])

        # 空行圧縮 (3行以上を2行にする)
        for key in ['bef', 'aft', 'body']:
            body[key] = \
                __class__.__RE_BODY_BLANKLINE1.sub(r'\n', body[key])
            body[key] = \
                __class__.__RE_BODY_BLANKLINE2.sub(r'\n\n\n', body[key])

            body[key] = body[key].rstrip()

        return body

    __RE_IMAGE_A = re.compile(r'<a.*?</a>')
    __RE_IMAGE_ICODE = re.compile(r'icode\/(.*)\/$')

    @staticmethod
    def __getImage(html, ncode, bOrg, oPath):
        r""" 挿し絵を取得する.

        本文中の挿し絵をダウンロードする。
        挿し絵の<a><img></a>を一時待避用のタグに置換する。

        Args:
            html   HTMLテキスト(本文)
            ncode  Nコード
            bOrg   True  作者が投稿したオリジナル画像を取得する
                   False 本文中に表示されている画像を取得する
            oPath  出力先パス
        Returns:
            置換後のHTMLテキスト
        Raises:
            None
        """
        oPath = os.path.join(oPath, "img")
        match = __class__.__RE_IMAGE_A.search(html)
        if match and not os.path.exists(oPath):
            os.mkdir(oPath)

        while match:
            submatch = match.group()

            a = BeautifulSoup(submatch, 'html.parser').a
            url = a.img['src']

            # ICODEを抜き出す
            icode = __class__.__RE_IMAGE_ICODE.search(url).group(1)

            # 画像のURLを取得
            # 　a.href     作者が投稿した実際の画像が表示されるWebページ
            #   a.img.src  本文中に表示されている縮小画像
            if bOrg:
                url = a['href']
                localImagePath = None

                if "//" == url[0:2]:
                    url = "http:" + url

                try:
                    with urllib.request.urlopen(url) as response:
                        soup = BeautifulSoup(
                            response.read().decode('utf-8'), 'html.parser')

                        url = soup.find(class_='imageview').a['href']

                except Exception as e:
                    print("\r", end="", file=sys.stderr, flush=True)
                    print("{0:<10}ERROR:{1}[{2}]".format(
                        ncode
                        , "Webページの構造が変わった可能性があます。"
                          "画像の取得に失敗しました。"
                        , url))

            filename = "{0}_{1}".format(ncode, icode)
            localImagePath = \
                __class__.__downloadImage(url, os.path.join(oPath, filename))

            # 一時的に代替タグへ置換
            # 　画像ファイルへのパスは本文ファイルからの相対パス
            if localImagePath:
                filename = os.path.basename(localImagePath)
                newImageTag = "__IMAGE_{}_IMAGE__".format(
                    os.path.join("img", filename))

            else:
                newImageTag = "画像({})".format(url)

            html = html.replace(submatch, newImageTag)
            match = __class__.__RE_IMAGE_A.search(html)

        return html

    @staticmethod
    def __downloadImage(url, oPath):
        r""" 画像をダウンロードする.

        Args:
            url   ダウンロード対象の画像のURL
            oPath 出力先画像パス(ファイル名には拡張子は含まない)
        Returns:
            ダウンロードした画像へのパス(ファイル名に拡張子を含む)
        Raises:
            None
        """
        with urllib.request.urlopen(url) as response:
            if response.code != 200:
                return None

            ext = ""
            tmp = response.info()['Content-Type']
            if "image/jpeg" == tmp:
                ext = ".jpg"

            elif "image/png" == tmp:
                ext = ".png"

            elif "image/gif" == tmp:
                ext = ".gif"

            else:
                return None

            newPath = oPath + ext
            with open(newPath, 'wb') as of:
                of.write(response.read())

        return newPath

    @staticmethod
    def __outputHeaderPage(filename, header, records, oPath):
        r""" 小説情報の青空文庫形式ファイル作成.

        青空文庫形式TEXTっぽいファイルを作り、表紙のファイルとして出力する。


     　「小説家になろう」WebサイトがUTF-8であり、文字コード変換の問題が面倒なので生成するテキストもUTF-8にしておく。

        Args:
            filename    ファイル名 (拡張子なし)
            header      小説情報
            record      章情報
            oPath       出力先パス
        Returns:
            ファイル名 (拡張子あり)
        Raises:
            None

        """
        filename += ".txt"

        # 表紙
        buf = []
        buf.append(header['title'])
        buf.append("\n")
        buf.append(header['writer'])
        buf.append("\n\n\n掲載元")
        buf.append("\n「小説家になろう」")
        buf.append("\n　Ｎコード　　　")
        buf.append(header['ncode'])
        buf.append("\n　掲載日　　　　")
        buf.append(header['date1'][0:16])
        buf.append("\n　最終話掲載日　")
        buf.append(header['date2'][0:16])
        buf.append("　")
        buf.append(header['noveltype'])

        # あらすじ
        buf.append("\n［＃改ページ］\n")
        buf.append("［＃大見出し］あらすじ［＃大見出し終わり］\n\n\n")
        buf.append(header['ex'])

        # 目次
        buf.append("\n［＃改ページ］\n")
        buf.append("［＃大見出し］目次［＃大見出し終わり］\n\n")
        for record in records:
            if record['flagChap']:
                buf.append("\n")

                buf.append(record['chapter_title'])
                buf.append("\n\n")

            buf.append("　")
            buf.append(record['novel_sublist2'])
            buf.append("\n")

        # ファイルへ出力
        path = os.path.join(oPath, filename)
        with open(path, 'wt', encoding='utf-8') as fs:
            fs.write(''.join(buf))

        return filename

    @staticmethod
    def __outputBodyFile(filename, header, record, body, oPath):
        r""" 章情報(小説の本文)の青空文庫形式ファイル作成.

        青空文庫形式TEXTっぽいファイルを作り、本文のみのファイルとして出力する。


     　「小説家になろう」WebサイトがUTF-8であり、文字コード変換の問題が面倒なので生成するテキストもUTF-8にしておく。

        Args:
            filename    ファイル名 (拡張子なし)
            header      小説情報
            record      章情報
            oPath       出力先パス
        Returns:
            ファイル名 (拡張子あり)
        Raises:
            None

        """
        filename += ".txt"
        buf = []

        # 大章タイトル
        if record['flagChap']:
            buf.append("［＃大見出し］{0}［＃大見出し終わり］\n\n".format(
                record['chapter_title']))

        # 小章タイトル
        buf.append("［＃中見出し］{0}［＃中見出し終わり］\n\n\n".format(
            record['novel_sublist2']))

        # 前書き
        if body['bef']:
            buf.append("（前書き）\n\n")

            buf.append(body['bef'])
            buf.append("\n")
            buf.append("［＃改ページ］\n")

        # 本文
        buf.append(body['body'])
        buf.append("\n")

        # 後書き
        if body['aft']:
            buf.append("［＃改ページ］\n")

            buf.append("（後書き）\n\n")

            buf.append(body['aft'])
            buf.append("\n")

        # ファイルへ出力
        path = os.path.join(oPath, filename)
        with open(path, 'wt', encoding='utf-8') as fs:
            fs.write(''.join(buf))

        return filename

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    @staticmethod
    def getNovel(ncode, oPath, flagS):
        r""" 小説取得処理.

        指定されたNコードの小説をWebサーバーから取得し、テキストファイルとしてローカルに保存する。

        Args:
            ncode   Nコード
            oPath   出力先パス
            flagS   True  小説本文のダウンロードをしない
                    False 小説本文のダウンロードをする
        Returns:
            True    データの取得に成功
            False   データの取得に失敗
        Raises:
            None
        """
        # データ格納用ディレクトリを生成
        if not os.path.exists(oPath):
            os.makedirs(oPath)

        # 小説情報を取得
        header = None
        try:
            print("\r", end="", file=sys.stderr, flush=True)
            print("{0:<10}小説情報を取得中".format(ncode)
                  , end="", file=sys.stderr, flush=True)

            header = __class__.__getHeader(ncode)

        except urllib.error.HTTPError as e:
            print("\r", end="", file=sys.stderr, flush=True)
            print("{0:<10}ERROR:{1}{2}".format(
                ncode
                , "「小説家になろう」のWebサイトに接続できませんでした。"
                , e.reason))
            return False

        except urllib.error.URLError as e:
            print("\r", end="", file=sys.stderr, flush=True)
            print("{0:<10}ERROR:{1}{2}".format(
                ncode
                , "「小説家になろう」のWebサイトに接続できませんでした。"
                , e.reason))
            return False

        except AttributeError as e:
            print("\r", end="", file=sys.stderr, flush=True)
            print("{0:<10}ERROR:{1}{2}".format(
                ncode
                , "Webページの構造が変わった可能性があり、"
                  "本バージョンでは小説を取得することが出来ません。"
                , e))
            return False

        finally:
            time.sleep(__class__.__HTTP_WAIT)

        # 目次を取得
        try:
            records = []
            if header:
                print("\r\033[K{0:<10}目次を取得中".format(ncode)
                      , end="", file=sys.stderr, flush=True)

                records = __class__.__getRecords(ncode)
                header['RecordMax'] = len(records)

            else:
                print("\r\033[K", end="", file=sys.stderr, flush=True)
                return False
        except:
            pass

        # 更新チェック
        # 　新規投稿または掲載日が異なるもの(改稿)を対象とする
        try:

            print("\r\033[K{0:<10}更新状況をチェック".format(ncode)
                  , end="", file=sys.stderr, flush=True)

            newRecords = records[:]
            files = [f for f in os.listdir(oPath)]
            for file in files:
                tmp = file.split('_')
                if 2 > len(tmp):
                    continue

                id = tmp[0]
                timestamp = tmp[1]

                for record in newRecords:
                    id_ = record['id'].zfill(4)
                    if id_ != id:
                        continue

                    if record['long_update'] == timestamp:
                        newRecords.remove(record)
                        break

                    elif record['long_update'] != timestamp:
                        os.remove(os.path.join(oPath, file))
                        break

            print("\r", end="", file=sys.stderr, flush=True)
            print("{0:<10}{5} {2}  最終話掲載日 {4}  全{3:>4}部  {1}".format(
                ncode
                , header['title']
                , header['noveltype']
                , header['RecordMax']
                , header['date2'][:-3]
                , "UPD" if newRecords else "---"), flush=True)

            time.sleep(__class__.__HTTP_WAIT)
        except:
            pass

        # 表紙ファイル出力
        try:
            if not flagS and newRecords:
                __class__.__outputHeaderPage(
                    "0000_表紙", header, records, oPath)
            else:
                print("\r\033[K", end="", file=sys.stderr, flush=True)
                return False
        except:
            pass

        try:
            # 各章の本文を取得＆テキストファイル出力
            imax = len(newRecords)
            i = 1
            chapName = ""
            for record in newRecords:
                p = 1.0 * i / imax
                pos = int(25 * p)
                temp = "{2:.2f}% [{0}{1}]".format("#" * pos, "-" * (25 - pos), p * 100)

                temp = "\r\033[K    本文を取得中  {0} / {1}部  {2}".format(
                    str(i), str(imax), temp)

                print(temp, end="", file=sys.stderr, flush=True)

                body = __class__.__getBody(header['ncode'], record['id'], oPath)

                fileName = __class__.__OUTPUT_FNAME_BODY.format(
                    ncode
                    , record['id']
                    , record['novel_sublist2'][:30]
                    , record['chapter_title'][:30]
                    , record['long_update'])
                fileName = _escapeFileName(fileName)

                __class__.__outputBodyFile(fileName, header, record, body, oPath)

                i = i + 1

                time.sleep(__class__.__HTTP_WAIT)

            print("\r\033[K", end="", file=sys.stderr, flush=True)
            return True if newRecords else False
        except:
            # TODO
            pass

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------


#    @classmethod
#    def __class_method(cls):
#        pass

# --------------------------------------------------------------------------
# クラスメソッドの定義　(公開)
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# 特殊メソッドの定義
# --------------------------------------------------------------------------

#    def __init__(self):

# ----------------------------------------------------------------------
# インスタンス変数の定義 (非公開)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# インスタンス変数の定義 (公開)
# ----------------------------------------------------------------------

# --------------------------------------------------------------------------
# プロパティーの定義
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# インスタンスメソッドの定義　(非公開)
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# インスタンスメソッドの定義　(公開)
# --------------------------------------------------------------------------

class NovelGenerator(object):
    r"""
    クラス名　小説生成

    Downloaderで生成された差分ファイルから小説の情報を収拾しファイルを生成する。
    派生先で_generateFileをオーバーライドして使う。

    公開関数
    def generate( self, iPath, arcPath ):
    def _generateFile( self, iPath, arcPath, header, bodys ):
    """

    # --------------------------------------------------------------------------
    # クラス定数の定義　(非公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス定数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(非公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    @staticmethod
    def __getHeader(iPath):
        r""" 小説情報取得.

        ローカルに保存されている小説のデータを解析し、小説の情報を取得する。

        Args:
            iPath  差分ファイル格納パス
        Returns:
            小説情報 (ディクショナリ型)

              ncode      1 Nコード
              title      1 小説タイトル
              flag       1 '完結済' OR '連載中'
              summary    1 あらすじ
              writer     1 作者名
              date1      1 掲載日 (YYYY-MM-DD)
              date2      1 最終話掲載日 (YYYY-MM-DD)
        Raises:
            None
        """
        if not os.path.exists(iPath):
            return None

        filename = ""
        for f in os.listdir(iPath):
            if "0000" == f[:4]:
                filename = f
                break

        result = {}

        # タイトル
        # 作者名
        filepath = os.path.join(iPath, filename)
        with open(filepath, 'rt') as f:
            result['title'] = f.readline().strip()
            result['writer'] = f.readline().strip()

            text = f.read()

        # Nコード
        cmplRe1 = re.compile(r'\u3000Ｎコード[ \t\u3000]*(.*)\n')
        match = cmplRe1.search(text)
        if match:
            result['ncode'] = match.group(1)

        # 掲載日
        cmplRe1 = re.compile(r'\u3000掲載日[ \t\u3000]*(.*)\n')
        match = cmplRe1.search(text)
        if match:
            result['date1'] = match.group(1)

        # 最終話掲載日
        cmplRe1 = re.compile(
            r'\u3000最終話掲載日[ \t\u3000]*(.*)\u3000(.*)\n')
        match = cmplRe1.search(text)
        if match:
            result['date2'] = match.group(1)
            result['flag'] = match.group(2)

        # あらすじ
        cmplRe1 = re.compile(
            r'あらすじ［＃大見出し終わり］\n(.*)\n［＃改ページ］'
            , re.DOTALL)
        match = cmplRe1.search(text)
        if match:
            temp = match.group(1).rstrip()

            cmplRe1 = re.compile(r'^\n+')
            result['summary'] = cmplRe1.sub(r'', temp)

        return result

    @staticmethod
    def __getRecord(iPath):
        r""" 章情報取得.

        ローカルに保存されている小説のデータを解析し、章の情報を取得する。

        Args:
            iPath  差分ファイル格納パス
        Returns:
        　　章情報リスト (リスト型)
              0..*  章情報 (ディクショナリ型)

                id              1    章の番号
                head1           0..1 大章の名称
                head2           1    小章の名称
                note1           0..1 前書き
                note2           0..1 後書き
                body            1    本文
                timestamp       1    掲載日付(YYYYMMDD)
                filename        1    ローカルデータのパス
        Raises:
            None
        """
        if not os.path.exists(iPath):
            return None

        files = os.listdir(iPath)
        for f in files:
            if "0000" == f[:4] or not f[:4].isdigit():
                files.remove(f)
        files.sort()

        result = []

        head1 = ""
        cmplHead1 = re.compile(r'［＃大見出し］(.*)［＃大見出し終わり］\n')
        cmplHead2 = re.compile(r'［＃中見出し］(.*)［＃中見出し終わり］\n')
        cmplNote1 = re.compile(r'（前書き）(.*?)［＃改ページ］\n', re.DOTALL)
        cmplNote2 = re.compile(
            r'\n［＃改ページ］\n（後書き）(.*)$', re.DOTALL)
        cmplDelSpace = re.compile(r'^\n+')
        for file in files:
            record = {}
            temp = file.split("_")
            record['id'] = temp[0]
            record['timestamp'] = temp[1]
            record['filename'] = file

            filepath = os.path.join(iPath, file)
            with open(filepath, 'rt') as f:
                text = f.read()

            # 大見出し
            match = cmplHead1.search(text)
            if match:
                head1 = match.group(1)
                text = text.replace(match.group(), "")
            record['head1'] = head1

            # 中見出し
            record['head2'] = ""
            match = cmplHead2.search(text)
            if match:
                record['head2'] = match.group(1)
                text = text.replace(match.group(), "")

            # 前書き
            record['note1'] = ""
            match = cmplNote1.search(text)
            if match:
                record['note1'] = match.group(1)
                text = text.replace(match.group(), "")

            # 後書き
            record['note2'] = ""
            match = cmplNote2.search(text)
            if match:
                record['note2'] = match.group(1)
                text = text.replace(match.group(), "")

            # 本文
            record['body'] = text

            # 文章の前の空白行を削除
            for key in ['note1', 'note2', 'body']:
                record[key] = cmplDelSpace.sub(r'', record[key]).rstrip()

            result.append(record)

        return result

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    #    @classmethod
    #    def __class_method(cls):
    #        pass

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # 特殊メソッドの定義
    # --------------------------------------------------------------------------

    #    def __init__(self):

    # ----------------------------------------------------------------------
    # インスタンス変数の定義 (非公開)
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # インスタンス変数の定義 (公開)
    # ----------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # プロパティーの定義
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # インスタンスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    def _generateFile(self, iPath, arcPath, header, bodys):
        pass

    # --------------------------------------------------------------------------
    # インスタンスメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    def generate(self, iPath, arcPath):

        # 小説情報を取得
        header = __class__.__getHeader(iPath)
        if not header:
            return

        # 本文リストを取得
        bodys = __class__.__getRecord(iPath)
        if not bodys:
            return

        header['copies'] = len(bodys)

        # 指定書式のファイルを生成
        self._generateFile(iPath, arcPath, header, bodys)


class AozoraNovelGenerator(NovelGenerator):
    r"""
    クラス名　小説生成(青空文庫形式TEXT)
    """
    # --------------------------------------------------------------------------
    # クラス定数の定義　(非公開)
    # --------------------------------------------------------------------------

    # 出力ファイル名 (拡張子なし)
    # 　{0} 作者名
    # 　{1} 小説タイトル
    # 　{2} 部数
    # 　{3} 連載有無文字
    # 　{4} Nコード
    # 　{5} 掲載日
    # 　{6} 最終話掲載日
    __OUTPUT_FILENAME = \
        "(Web小説) [{0}] {1} 全{2}部 [{4} {5} {6} {3}] (青空文庫形式txt).zip"

    # --------------------------------------------------------------------------
    # クラス定数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(非公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    #    @staticmethod
    #    def __static_method():
    #        pass

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    #    @classmethod
    #    def __class_method(cls):
    #        pass

    # --------------------------------------------------------------------------
    # 特殊メソッドの定義
    # --------------------------------------------------------------------------

    def __init__(self):
        super().__init__()

    # ----------------------------------------------------------------------
    # インスタンス変数の定義 (非公開)
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # インスタンス変数の定義 (公開)
    # ----------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # プロパティーの定義
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # インスタンスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    def _generateFile(self, iPath, arcPath, header, bodys):

        if not os.path.exists(iPath):
            return

        # 分割されてる全ての本文ファイルをメモリ上で結合
        files = [f for f in os.listdir(iPath)
                 if not os.path.isdir(os.path.join(iPath, f))]
        files.sort()

        buf = []
        i = 0
        imax = len(files)
        for f in files:
            fname = os.path.join(iPath, f)
            with open(fname, 'rt') as f2:
                buf.append(f2.read())

            if i < imax - 1:
                buf.append("［＃改ページ］\n")
            i = i + 1

        # ZIPファイルに変換
        fname = __class__.__OUTPUT_FILENAME.format(
            header['writer']
            , header['title']
            , header['copies']
            , header['flag']
            , header['ncode']
            , header['date1'][0:10]
            , header['date2'][0:10])
        fname = _escapeFileName(fname)

        zipName = os.path.join(arcPath, fname)
        with zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED) as arc:

            fname = "{0}_{1} 全{2}部.txt".format(
                header['ncode']
                , header['title']
                , header['copies'])
            arc.writestr(fname, "".join(buf))

            imgPath = os.path.join(iPath, "img")
            if os.path.exists(imgPath):
                files = os.listdir(imgPath)
                for f in files:
                    fname1 = os.path.join(imgPath, f)
                    fname2 = os.path.join("img", f)
                    arc.write(fname1, fname2)

    # --------------------------------------------------------------------------
    # インスタンスメソッドの定義　(公開)
    # --------------------------------------------------------------------------


class EPUB3NovelGenerator(NovelGenerator):
    r"""
    クラス名　小説生成(EPUB 3.0形式)
    """
    # --------------------------------------------------------------------------
    # クラス定数の定義　(非公開)
    # --------------------------------------------------------------------------

    # 出力ファイル名 (拡張子なし)
    # 　{0} 作者名
    # 　{1} 小説タイトル
    # 　{2} 部数
    # 　{3} 連載有無文字
    # 　{4} Nコード
    # 　{5} 掲載日
    # 　{6} 最終話掲載日
    __OUTPUT_FILENAME = \
        "(Web小説) [{0}] {1} 全{2}部 [{4} {5} {6} {3}].epub"

    # XHTMLファイルから呼び出されるスタイルシート
    # 　@importで__CSS_RESET, __CSS_STANDARD, __CSS_ADVANCEを取り込む
    # 　@importのスタイルシートは書き換えないで本スタイルシートで上書きする
    __CSS_BOOK = """@charset "UTF-8";
@import "style-reset.css";
@import "style-standard.css";
@import "style-advance.css";

/* -------------------------------------------------------------
Windows でチェックするときは以下の指定を利用
※チェックが済んだら必ず削除かコメントアウトすること
@import "style-check.css";
---------------------------------------------------------------- */



/* ファイル情報
----------------------------------------------------------------
【内容】
外部 CSS の一括読み込み と 作品別カスタマイズ指定

【CSSファイルバージョン】
ver.1.1.1

【当ファイル更新時の電書協EPUB 3 制作ガイドバージョン】
ver.1.1.3

【細目】
・外部 CSS の import
・作品別カスタマイズ領域

【更新履歴】
2014/11/01 ver.1.1.1
・「特殊リンク指定」を追加
・「注釈リンクの下線と色」を変更

2012/12/07 ver.1.1.0
・ファイル更新時の電書協EPUB 3 制作ガイドバージョン表記を追加

2012/08/21 ver.1.0b1
・公開版
---------------------------------------------------------------- */


/* -------------------------------------------------------------
 * 作品別カスタマイズ領域
 * ------------------------------------------------------------- */


/* 見出しのデフォルト書体指定
---------------------------------------------------------------- */
/* 横組み用 */
.hltr h1,
.hltr h2,
.hltr h3,
.hltr h4,
.hltr h5,
.hltr h6 {
  font-family: serif-ja, serif;
}
/* 縦組み用 */
.vrtl h1,
.vrtl h2,
.vrtl h3,
.vrtl h4,
.vrtl h5,
.vrtl h6 {
  font-family: serif-ja-v, serif-ja, serif;
}


/* リンク指定
---------------------------------------------------------------- */
/* 基本設定（上：横組み　下：縦組み） */
.hltr a {
}
.vrtl a {
}
/* 未訪問リンク */
a:link {
}
/* 訪問済みリンク */
a:visited {
}
/* マウスオーバー時 */
a:hover {
}
/* フォーカス時 */
a:focus {
}
/* アクティブ時 */
a:active {
}


/* 特殊リンク指定
---------------------------------------------------------------- */
/* 基本設定（上：横組み　下：縦組み） */

/* .link-01
-------------------- */
.hltr a.link-01 {
}
.vrtl a.link-01 {
}
/* 未訪問リンク */
a.link-01:link {
}
/* 訪問済みリンク */
a.link-01:visited {
}
/* マウスオーバー時 */
a.link-01:hover {
}
/* フォーカス時 */
a.link-01:focus {
}
/* アクティブ時 */
a.link-01:active {
}

/* .link-02
-------------------- */
.hltr a.link-02 {
}
.vrtl a.link-02 {
}
/* 未訪問リンク */
a.link-02:link {
}
/* 訪問済みリンク */
a.link-02:visited {
}
/* マウスオーバー時 */
a.link-02:hover {
}
/* フォーカス時 */
a.link-02:focus {
}
/* アクティブ時 */
a.link-02:active {
}

/* .link-03
-------------------- */
.hltr a.link-03 {
}
.vrtl a.link-03 {
}
/* 未訪問リンク */
a.link-03:link {
}
/* 訪問済みリンク */
a.link-03:visited {
}
/* マウスオーバー時 */
a.link-03:hover {
}
/* フォーカス時 */
a.link-03:focus {
}
/* アクティブ時 */
a.link-03:active {
}


/* 注釈リンクの下線と色 （注釈参照側）
---------------------------------------------------------------- */
/* 基本設定（上：横組み　下：縦組み） */
.hltr a.noteref {
}
.vrtl a.noteref {
}
/* 未訪問リンク */
a.noteref:link {
}
/* 訪問済みリンク */
a.noteref:visited {
}
/* マウスオーバー時 */
a.noteref:hover {
}
/* フォーカス時 */
a.noteref:focus {
}
/* アクティブ時 */
a.noteref:active {
}


/* 注釈リンクの下線と色 （注釈内容側）
---------------------------------------------------------------- */
/* 基本設定（上：横組み　下：縦組み） */
.hltr a.note {
}
.vrtl a.note {
}
/* 未訪問リンク */
a.note:link {
}
/* 訪問済みリンク */
a.note:visited {
}
/* マウスオーバー時 */
a.note:hover {
}
/* フォーカス時 */
a.note:focus {
}
/* アクティブ時 */
a.note:active {
}


/* 見出しの指定（上：横組み　下：縦組み）
---------------------------------------------------------------- */
/* 扉見出し */
.hltr .tobira-midashi {
}
.vrtl .tobira-midashi {
}
/* 大見出し */
.hltr .oo-midashi {
}
.vrtl .oo-midashi {
  font-size:   140%;
}
/* 中見出し */
.hltr .naka-midashi {
}
.vrtl .naka-midashi {
  font-size:   120%;
}
/* 小見出し */
.hltr .ko-midashi {
}
.vrtl .ko-midashi {
}


/* カバーページ
----------------------------------------------------------------
描画領域の余白をゼロに
デフォルトで左右中央揃えに
---------------------------------------------------------------- */
body.p-cover {
  margin:     0;
  padding:    0;
  text-align: center;
}
body.p-cover .main {
}


/* 画像のみのページ
----------------------------------------------------------------
描画領域の余白をゼロに
デフォルトで左右中央揃えに
---------------------------------------------------------------- */
body.p-image {
  margin:     0;
  padding:    0;
  text-align: center;
}
body.p-image .main {
}


/* テキスト中心のページ
---------------------------------------------------------------- */
body.p-text {
}
body.p-text .main {
}


/* 本扉ページ
---------------------------------------------------------------- */
body.p-titlepage {
}
body.p-titlepage .main {
}


/* 奥付ページ
---------------------------------------------------------------- */
body.p-colophon {
}
body.p-colophon .main {
}


/* 目次ページ
---------------------------------------------------------------- */
body.p-toc {
}
body.p-toc .main {
}


/* 電子版用の注意書きページ
---------------------------------------------------------------- */
body.p-caution {
}
body.p-caution .main {
}


/* 広告ページ
---------------------------------------------------------------- */
body.p-ad {
}
body.p-ad .main {
}

/* カスタマイズ */
body {
/*
  font-family: "モトヤLマルベリ3等幅", "Migu 1M", monospace, serif-ja-v, serif-ja, serif;
*/
  font-family: "Migu 1M", "モトヤLマルベリ3等幅", "@ＭＳ 明朝", serif-ja-v, serif-ja, serif;
}"""

    # リセット用スタイルシート
    __CSS_RESET = """@charset "UTF-8";


/* ファイル情報
----------------------------------------------------------------
【内容】
CSS リセット

【CSSファイルバージョン】
ver.1.2.1

【当ファイル更新時の電書協EPUB 3 制作ガイドバージョン】
ver.1.1.3

【細目】
・css reset

【更新履歴】
2014/11/01 ver.1.2.1
・「-epub(webkit)-text-align-last」を削除
・「text-underline-position」を「-epub-text-underline-position」に変更

2012/12/07 ver.1.2.0
・ファイル更新時の電書協EPUB 3 制作ガイドバージョン表記を追加
・「text-underline-position: below left;」の「below」部分を「under」に変更

2012/10/29 ver.1.1b1
・body に text-underline-position を指定
  ※ページ内すべての overline を縦組み時に右線（傍線）、
    underline を左線として設定

2012/08/21 ver.1.0b1
・公開版
---------------------------------------------------------------- */


/* css reset
---------------------------------------------------------------- */
body {
  margin:         0;
  padding:        0;
  font-size:      100%;
  vertical-align: baseline;
  line-height:    1.75;
  background:     transparent;

  word-spacing:   normal;
  letter-spacing: normal;
  white-space:    normal;
  word-wrap:      break-word;
  text-align:     justify;

  -webkit-line-break: normal;
  -epub-line-break:   normal;

  -webkit-word-break: normal;
  -epub-word-break:   normal;

  -webkit-hyphens: auto;
  -epub-hyphens:   auto;

  -webkit-text-underline-position: under left;
  -epub-text-underline-position:   under left;
}
div,p {
  display: block;
  width:   auto;
  height:  auto;
  margin:  0;
  padding: 0;
}
body,div,p {
  text-indent: 0;
}
body > p,
div  > p {
  text-indent: inherit;
}
h1,h2,h3,h4,h5,h6 {
  display:     block;
  margin:      0;
  padding:     0;
  font-size:   100%;
  font-weight: inherit;
  background:  transparent;
}
img {
  width:          auto;
  height:         auto;
  margin:         0;
  padding:        0;
  border:         none;
  vertical-align: baseline;
  background:     transparent;
}
a {
  font-style:      inherit;
  font-weight:     inherit;
  text-decoration: inherit;
  color:           inherit;
  background:      transparent;
}"""

    # 基本のスタイルシート
    __CSS_STANDARD = """@charset "UTF-8";


/* ファイル情報
----------------------------------------------------------------
【内容】
全作品共通の基本スタイル

【CSSファイルバージョン】
ver.1.3.1

【当ファイル更新時の電書協EPUB 3 制作ガイドバージョン】
ver.1.1.3

【細目】
・組み方向指定
・html指定
・ボックスの種類
・改ページ指定
・行揃え
・ブロック要素の位置揃え
・インライン要素の位置揃え
・リンク指定
・注釈
・外字画像
・画像のページフィット指定
・縦中横
・文字の向き
・上付文字・下付文字
・小書き文字
・訓点（返り点）
・圏点・傍点
・行高
・文字の間隔
・フォント指定
・太字
・斜体
・文字色
・背景色
・文字色の白黒反転
・圏点・傍点の色指定
・区切り線
・打ち消し線
・傍線
・囲み罫
・罫線
・罫線色
・行頭インデント
・突き出しインデント（ぶら下がりインデント）
・字下げ・字上げ指定
・外側の余白（マージン）指定
・内側の余白（パディング）指定
・高さ
・高さの最大値
・幅
・幅の最大値
・最大サイズ
・禁則処理のルール
・自動改行のルール
・長い単語の改行ルール
・【参考】回り込み

【更新履歴】
2014/11/01 ver.1.3.1
・「行揃え」の「-epub(webkit)-text-align-last」を削除
・「縦中横」を修正
・「文字の向き」の「.upright-1」を修正
・「文字の向き」の「.sideways」を修正

2012/12/07 ver.1.3.0
・ファイル更新時の電書協EPUB 3 制作ガイドバージョン表記を追加

2012/10/29 ver.1.2b1
・「傍線」を修正

2012/10/03 ver.1.1b1
・「行揃え」の位置揃え用の空白数を調整
・「文字の向き」の「.sideways」を修正
・「傍線」を修正

2012/08/21 ver.1.0b1
・公開版
---------------------------------------------------------------- */



/* 組み方向指定
---------------------------------------------------------------- */
/* 横組み用 */
html,
.hltr {
  -webkit-writing-mode: horizontal-tb;
  -epub-writing-mode:   horizontal-tb;
}
/* 縦組み用 */
.vrtl {
  -webkit-writing-mode: vertical-rl;
  -epub-writing-mode:   vertical-rl;
}
/*
.vltr {
  -webkit-writing-mode: vertical-lr;
  -epub-writing-mode:   vertical-lr;
}
*/


/* html指定
----------------------------------------------------------------
デフォルトフォントのみ指定
---------------------------------------------------------------- */
html {
  font-family: serif-ja, serif;
}


/* ボックスの種類
---------------------------------------------------------------- */
.display-none {
  display: none;
}
.display-inline {
  display: inline;
}
.display-inline-block {
  display: inline-block;
}
.display-block {
  display: block;
}


/* 改ページ指定
----------------------------------------------------------------
端末の処理能力等に配慮する意味もあり、
改ページは、原則としてファイルを替えることで実現する

ただし、ページ全体のスタイル指定の変更が不要で、
かつページ数が少ない場合は、ファイル数の増加を防ぐため、
下記の指定を利用する可能性もある（短い随筆やコラム的な文章の連続など）
---------------------------------------------------------------- */
/* 指定したブロックの直後で改ページ */
.pagebreak {
  page-break-after:  always;
}
/* 指定したブロックの直前で改ページ */
.pagebreak-before {
  page-break-before: always;
}
/* 指定したブロックの前後で改ページ */
.pagebreak-both {
  page-break-before: always;
  page-break-after:  always;
}


/* 行揃え
----------------------------------------------------------------
本文は原則として「text-align: justify;」
ただし、両端が揃うのが好ましくない場合は手動で以下の「align-start」を利用
行末まで均等揃えは今回含めない
---------------------------------------------------------------- */
/* 行頭揃え */
.align-left,
.align-start {
  text-align: left;
}
/* 行中揃え */
.align-center {
  text-align: center;
}
/* 行末揃え */
.align-right,
.align-end {
  text-align: right;
}
/* 両端揃え（行末は行頭揃え） */
.align-justify {
  text-align: justify;
}


/* ブロック要素の位置揃え
---------------------------------------------------------------- */
/* 絶対方向（横組みでは左右、縦組みでは上下方向のみ利用可） */
.block-align-left   { margin: 0 auto 0 0; }
.block-align-center { margin: 0 auto;     }
.block-align-right  { margin: 0 0 0 auto; }
.block-align-top    { margin: 0 0 auto 0; }
.block-align-middle { margin: auto 0;     }
.block-align-bottom { margin: auto 0 0 0; }

/* 論理方向（行頭-行中-行末） */
/* 横組み用 */
.hltr .block-align-start  { margin: 0 auto 0 0; }
.hltr .block-align-center { margin: 0 auto;     }
.hltr .block-align-end    { margin: 0 0 0 auto; }

/* 縦組み用 */
.vrtl .block-align-start  { margin: 0 0 auto 0; }
.vrtl .block-align-center { margin: auto 0;     }
.vrtl .block-align-end    { margin: auto 0 0 0; }


/* インライン要素の位置揃え
---------------------------------------------------------------- */
.valign-inherit     { vertical-align: inherit;     }
.valign-baseline    { vertical-align: baseline;    }
.valign-sub         { vertical-align: sub;         }
.valign-super       { vertical-align: super;       }
.valign-top         { vertical-align: top;         }
.valign-text-top    { vertical-align: text-top;    }
.valign-middle      { vertical-align: middle;      }
.valign-bottom      { vertical-align: bottom;      }
.valign-text-bottom { vertical-align: text-bottom; }


/* リンク指定
---------------------------------------------------------------- */
/* 基本設定 */
/* 横組み：下線　縦組み：右線 */
.hltr a {
  text-decoration: underline;
}
.vrtl a {
  text-decoration: overline;
}
/* リンク文字色（デフォルトは青） */
a:link,
a:visited,
a:hover,
a:focus,
a:active {
  color: #0000ff;
}


/* 注釈
---------------------------------------------------------------- */
/* 注釈記号の文字サイズ */
.key,
.ref {
  font-size:      smaller;
  vertical-align: super;
}


/* 外字画像
---------------------------------------------------------------- */
img.gaiji,
img.gaiji-line,
img.gaiji-wide {
  display:    inline-block;
  margin:     0;
  padding:    0;
  border:     none;
  background: transparent;
}
img.gaiji {
  width:      1em;
  height:     1em;
}
img.gaiji-line {
  width:      1em;
  height:     auto;
}
img.gaiji-wide {
  width:      auto;
  height:     1em;
}
/* 外字画像のベースライン */
.hltr img.gaiji,
.hltr img.gaiji-line,
.hltr img.gaiji-wide {
  vertical-align: text-bottom;
}
.vrtl img.gaiji,
.vrtl img.gaiji-line,
.vrtl img.gaiji-wide {
  vertical-align: baseline;
}


/* 画像のページフィット指定
----------------------------------------------------------------
「img.fit」を用いること
サイズ指定上書きの都合上、CSS ファイル上では img.fit と記述しない

<p><img class="fit max-height-050per" src="" alt=""/></p>
---------------------------------------------------------------- */
.fit {
  display:            inline-block;
  page-break-inside:  avoid;
  max-height:         100%;
  max-width:          100%;
}

/* 画像のベースライン */
.hltr .fit {
  vertical-align: top;
}
.vrtl .fit {
  vertical-align: baseline;
}


/* 縦中横
---------------------------------------------------------------- */
.tcy {
  -webkit-text-combine:         horizontal;
  -webkit-text-combine-upright: all;
  text-combine-upright:         all;
  -epub-text-combine:           horizontal;
}


/* 文字の向き
----------------------------------------------------------------
【WebKit対策】半角１文字の直立はセンターが揃わないので縦中横を利用
---------------------------------------------------------------- */
.upright-1 {
  -webkit-text-combine:         horizontal;
  -webkit-text-combine-upright: all;
  text-combine-upright:         all;
  -epub-text-combine:           horizontal;
}
.upright {
  -webkit-text-orientation: upright;
  -epub-text-orientation:   upright;
}
.sideways {
  -webkit-text-orientation: sideways;
  -epub-text-orientation:   sideways;
}


/* 上付文字・下付文字
---------------------------------------------------------------- */
/* 上付文字 */
.super {
  font-size:      smaller;
  vertical-align: super;
}
/* 下付文字 */
.sub {
  font-size:      smaller;
  vertical-align: sub;
}


/* 小書き文字
----------------------------------------------------------------
通常の文字を「ぁゃっ」のような小書き文字に見せるための指定
---------------------------------------------------------------- */
.kogaki {
  font-size:      0.75em;
}
/* 【横組み】左下 */
.hltr .kogaki {
  padding:        0 0.15em 0 0.1em;
  vertical-align: baseline;
}
/* 【縦組み】右上 */
.vrtl .kogaki {
  padding:        0.1em 0 0.15em 0;
  vertical-align: super;
}


/* 訓点（返り点）
----------------------------------------------------------------
縦組み時、上付・下付文字の上下端のスペースは調整しない
必要があれば、class を上書きすること
---------------------------------------------------------------- */
/* 記号（縦組みでは左上付） */
.kunten {
  vertical-align: sub;
  font-size:      0.67em;
}
/* 送り仮名（縦組みでは右上付） */
.kunten-okuri {
  vertical-align: super;
  font-size:      0.67em;
}


/* 圏点・傍点
---------------------------------------------------------------- */
.em-sesame {
  -webkit-text-emphasis-style: filled sesame;
  -epub-text-emphasis-style:   filled sesame;
}
.em-sesame-open {
  -webkit-text-emphasis-style: open sesame;
  -epub-text-emphasis-style:   open sesame;
}
.em-dot {
  -webkit-text-emphasis-style: filled dot;
  -epub-text-emphasis-style:   filled dot;
}
.em-dot-open {
  -webkit-text-emphasis-style: open dot;
  -epub-text-emphasis-style:   open dot;
}
.em-circle {
  -webkit-text-emphasis-style: filled circle;
  -epub-text-emphasis-style:   filled circle;
}
.em-circle-open {
  -webkit-text-emphasis-style: open circle;
  -epub-text-emphasis-style:   open circle;
}
.em-double-circle {
  -webkit-text-emphasis-style: filled double-circle;
  -epub-text-emphasis-style:   filled double-circle;
}
.em-double-circle-open {
  -webkit-text-emphasis-style: open double-circle;
  -epub-text-emphasis-style:   open double-circle;
}
.em-triangle {
  -webkit-text-emphasis-style: filled triangle;
  -epub-text-emphasis-style:   filled triangle;
}
.em-triangle-open {
  -webkit-text-emphasis-style: open triangle;
  -epub-text-emphasis-style:   open triangle;
}


/* 行高
---------------------------------------------------------------- */
.line-height-normal { line-height: normal; }
.line-height-1em    { line-height: 1.00; }
.line-height-1em50  { line-height: 1.50; }
.line-height-1em75  { line-height: 1.75; }
.line-height-2em    { line-height: 2.00; }
.line-height-2em50  { line-height: 2.50; }
.line-height-3em    { line-height: 3.00; }
.line-height-3em50  { line-height: 3.50; }
.line-height-4em    { line-height: 4.00; }
.line-height-4em50  { line-height: 4.50; }
.line-height-5em    { line-height: 5.00; }


/* 文字の間隔
----------------------------------------------------------------
本文中では四分アキ［25%］刻み以外はなるべく使わない方向で
---------------------------------------------------------------- */
/* 標準 */
.lspacing-normal { letter-spacing: normal; }

/* クリア */
.lspacing-0,
.lspacing-0em   { letter-spacing: 0; }

/* 文字数指定 */
.lspacing-0em10 { letter-spacing: 0.10em; }
.lspacing-0em20 { letter-spacing: 0.20em; }
.lspacing-0em25 { letter-spacing: 0.25em; }
.lspacing-0em30 { letter-spacing: 0.30em; }
.lspacing-0em33 { letter-spacing: 0.33em; }
.lspacing-0em40 { letter-spacing: 0.40em; }
.lspacing-0em50 { letter-spacing: 0.50em; }
.lspacing-0em60 { letter-spacing: 0.60em; }
.lspacing-0em67 { letter-spacing: 0.67em; }
.lspacing-0em70 { letter-spacing: 0.70em; }
.lspacing-0em75 { letter-spacing: 0.75em; }
.lspacing-0em80 { letter-spacing: 0.80em; }
.lspacing-0em90 { letter-spacing: 0.90em; }
.lspacing-1em   { letter-spacing: 1.00em; }
.lspacing-1em25 { letter-spacing: 1.25em; }
.lspacing-1em50 { letter-spacing: 1.50em; }
.lspacing-1em75 { letter-spacing: 1.75em; }
.lspacing-2em   { letter-spacing: 2.00em; }
.lspacing-2em25 { letter-spacing: 2.25em; }
.lspacing-2em50 { letter-spacing: 2.50em; }
.lspacing-2em75 { letter-spacing: 2.75em; }
.lspacing-3em   { letter-spacing: 3.00em; }
.lspacing-3em25 { letter-spacing: 3.25em; }
.lspacing-3em50 { letter-spacing: 3.50em; }
.lspacing-3em75 { letter-spacing: 3.75em; }
.lspacing-4em   { letter-spacing: 4.00em; }
.lspacing-4em25 { letter-spacing: 4.25em; }
.lspacing-4em50 { letter-spacing: 4.50em; }
.lspacing-4em75 { letter-spacing: 4.75em; }
.lspacing-5em   { letter-spacing: 5.00em; }


/* フォント指定
---------------------------------------------------------------- */
/* 明朝 */
.hltr .mfont,
.vrtl .mfont {
  font-family: serif-ja, serif;
}

/* ゴシック */
.hltr .gfont,
.vrtl .gfont {
  font-family: sans-serif-ja, sans-serif;
}

/* フォントサイズ（％指定） */
.font-050per { font-size:  50%; }
.font-060per { font-size:  60%; }
.font-070per { font-size:  70%; }
.font-075per { font-size:  75%; }
.font-080per { font-size:  80%; }
.font-085per { font-size:  85%; }
.font-090per { font-size:  90%; }
.font-100per { font-size: 100%; }
.font-110per { font-size: 110%; }
.font-115per { font-size: 115%; }
.font-120per { font-size: 120%; }
.font-130per { font-size: 130%; }
.font-140per { font-size: 140%; }
.font-150per { font-size: 150%; }
.font-160per { font-size: 160%; }
.font-170per { font-size: 170%; }
.font-180per { font-size: 180%; }
.font-190per { font-size: 190%; }
.font-200per { font-size: 200%; }
.font-250per { font-size: 250%; }
.font-300per { font-size: 300%; }


/* フォントサイズ（文字数指定） */
.font-0em50 { font-size:  0.50em; }
.font-0em60 { font-size:  0.60em; }
.font-0em70 { font-size:  0.70em; }
.font-0em75 { font-size:  0.75em; }
.font-0em80 { font-size:  0.80em; }
.font-0em85 { font-size:  0.85em; }
.font-0em90 { font-size:  0.90em; }
.font-1em   { font-size:  1.00em; }
.font-1em10 { font-size:  1.10em; }
.font-1em15 { font-size:  1.15em; }
.font-1em20 { font-size:  1.20em; }
.font-1em30 { font-size:  1.30em; }
.font-1em40 { font-size:  1.40em; }
.font-1em50 { font-size:  1.50em; }
.font-1em60 { font-size:  1.60em; }
.font-1em70 { font-size:  1.70em; }
.font-1em80 { font-size:  1.80em; }
.font-1em90 { font-size:  1.90em; }
.font-2em   { font-size:  2.00em; }
.font-2em50 { font-size:  2.50em; }
.font-3em   { font-size:  3.00em; }


/* 太字
---------------------------------------------------------------- */
/* 太字 */
.bold {
  font-weight: bold;
}
/* 太字解除 */
.font-weight-normal {
  font-weight: normal;
}


/* 斜体
---------------------------------------------------------------- */
/* 斜体 */
.italic {
  font-style: italic;
}
/* 斜体解除 */
.font-style-normal {
  font-style: normal;
}


/* 文字色
---------------------------------------------------------------- */
/* １Ｃ用文字色 */
.color-black       { color: #000000; }
.color-dimgray     { color: #696969; }
.color-gray        { color: #808080; }
.color-darkgray    { color: #a9a9a9; }
.color-silver      { color: #c0c0c0; }
.color-gainsboro   { color: #dcdcdc; }
.color-white       { color: #ffffff; }
.color-transparent { color: transparent; }

/* 基本色 */
.color-red         { color: #ff0000; }
.color-blue        { color: #0000ff; }
.color-cyan        { color: #00ffff; }
.color-magenta     { color: #ff00ff; }
.color-orangered   { color: #ff4500; }


/* 背景色
---------------------------------------------------------------- */
/* １Ｃ用背景色 */
.bg-black       { background-color: #000000; }
.bg-dimgray     { background-color: #696969; }
.bg-gray        { background-color: #808080; }
.bg-darkgray    { background-color: #a9a9a9; }
.bg-silver      { background-color: #c0c0c0; }
.bg-gainsboro   { background-color: #dcdcdc; }
.bg-white       { background-color: #ffffff; }
.bg-transparent { background-color: transparent; }

/* 基本色 */
.bg-red         { background-color: #ff0000; }
.bg-blue        { background-color: #0000ff; }
.bg-cyan        { background-color: #00ffff; }
.bg-magenta     { background-color: #ff00ff; }
.bg-orangered   { background-color: #ff4500; }


/* 文字色の白黒反転
---------------------------------------------------------------- */
.inverse {
  color:      #ffffff;
  background: #000000;
}


/* 圏点・傍点の色指定
----------------------------------------------------------------
インラインで .inverse を用いたとき、行間に表示される傍点色が白になり、
白背景では傍点が見えなくなってしまうことへの対処用
---------------------------------------------------------------- */
.em-black {
  -webkit-text-emphasis-color: #000000;
  -epub-text-emphasis-color:   #000000;
}


/* 区切り線
---------------------------------------------------------------- */
hr {
  border-width: 1px;
  border-color: #000000;
}
/* 【横組み】水平線 */
.hltr hr {
  margin:       0.5em 0;
  border-style: solid none none none;
}
/* 【縦組み】垂直線 */
.vrtl hr {
  margin:       0 0.5em;
  border-style: none solid none none;
}


/* 打ち消し線
---------------------------------------------------------------- */
.line-through {
  text-decoration: line-through;
}


/* 傍線
---------------------------------------------------------------- */
/* 【横組み】下線　【縦組み】右線 */
.hltr .em-line {
  text-decoration: underline;
}
.vrtl .em-line {
  text-decoration: overline;
}

/* 【横組み】上線　【縦組み】左線 */
.hltr .em-line-outside {
  text-decoration: overline;
}
.vrtl .em-line-outside {
  text-decoration: underline;
}


/* 囲み罫
----------------------------------------------------------------
線幅の指定には、罫線と同じものを使用
---------------------------------------------------------------- */
/* 上から実線、点線、二重線、破線 */
.k-solid  { border-style: solid solid solid solid;     border-width: 1px; border-color: #000000; }
.k-dotted { border-style: dotted dotted dotted dotted; border-width: 2px; border-color: #000000; }
.k-double { border-style: double double double double; border-width: 4px; border-color: #000000; }
.k-dashed { border-style: dashed dashed dashed dashed; border-width: 1px; border-color: #000000; }

/* 線色付き囲み罫（画像枠などに利用） */
.k-solid-black  { border-style: solid solid solid solid; border-width: 1px; border-color: #000000; }
.k-solid-gray   { border-style: solid solid solid solid; border-width: 1px; border-color: #808080; }
.k-solid-silver { border-style: solid solid solid solid; border-width: 1px; border-color: #c0c0c0; }
.k-solid-white  { border-style: solid solid solid solid; border-width: 1px; border-color: #ffffff; }


/* 罫線
----------------------------------------------------------------
線種や線幅など、細かな調整が必要なときは、
無理に既存のクラスを用いず新たにクラスを作成すること
---------------------------------------------------------------- */
/* 線種【実線】 */
.k-solid-top,
.k-solid-right,
.k-solid-bottom,
.k-solid-left,
.k-solid-topbottom,
.k-solid-rightleft {
  border-width: 1px;
  border-color: #000000;
}
/* 線位置【実線】 */
.k-solid-top       { border-style: solid none none none;  }
.k-solid-right     { border-style: none solid none none;  }
.k-solid-bottom    { border-style: none none solid none;  }
.k-solid-left      { border-style: none none none solid;  }
.k-solid-topbottom { border-style: solid none solid none; }
.k-solid-rightleft { border-style: none solid none solid; }

/* 線種【点線】 */
.k-dotted-top,
.k-dotted-right,
.k-dotted-bottom,
.k-dotted-left,
.k-dotted-topbottom,
.k-dotted-rightleft {
  border-width: 2px;
  border-color: #000000;
}
/* 線位置【点線】 */
.k-dotted-top       { border-style: dotted none none none;   }
.k-dotted-right     { border-style: none dotted none none;   }
.k-dotted-bottom    { border-style: none none dotted none;   }
.k-dotted-left      { border-style: none none none dotted;   }
.k-dotted-topbottom { border-style: dotted none dotted none; }
.k-dotted-rightleft { border-style: none dotted none dotted; }

/* 線種【二重線】 */
.k-double-top,
.k-double-right,
.k-double-bottom,
.k-double-left,
.k-double-topbottom,
.k-double-rightleft {
  border-width: 4px;
  border-color: #000000;
}
/* 線位置【二重線】 */
.k-double-top       { border-style: double none none none;   }
.k-double-right     { border-style: none double none none;   }
.k-double-bottom    { border-style: none none double none;   }
.k-double-left      { border-style: none none none double;   }
.k-double-topbottom { border-style: double none double none; }
.k-double-rightleft { border-style: none double none double; }

/* 線種【破線】 */
.k-dashed-top,
.k-dashed-right,
.k-dashed-bottom,
.k-dashed-left,
.k-dashed-topbottom,
.k-dashed-rightleft {
  border-width: 1px;
  border-color: #000000;
}
/* 線位置【破線】 */
.k-dashed-top       { border-style: dashed none none none;   }
.k-dashed-right     { border-style: none dashed none none;   }
.k-dashed-bottom    { border-style: none none dashed none;   }
.k-dashed-left      { border-style: none none none dashed;   }
.k-dashed-topbottom { border-style: dashed none dashed none; }
.k-dashed-rightleft { border-style: none dashed none dashed; }

/* 線幅 */
.k-0px    { border-width: 0;      }
.k-1px    { border-width: 1px;    }
.k-2px    { border-width: 2px;    }
.k-3px    { border-width: 3px;    }
.k-4px    { border-width: 4px;    }
.k-5px    { border-width: 5px;    }
.k-6px    { border-width: 6px;    }
.k-7px    { border-width: 7px;    }
.k-8px    { border-width: 8px;    }
.k-thin   { border-width: thin;   }
.k-medium { border-width: medium; }
.k-thick  { border-width: thick;  }

/* １Ｃ用の線色 */
.k-black       { border-color: #000000; }
.k-dimgray     { border-color: #696969; }
.k-gray        { border-color: #808080; }
.k-darkgray    { border-color: #a9a9a9; }
.k-silver      { border-color: #c0c0c0; }
.k-gainsboro   { border-color: #dcdcdc; }
.k-white       { border-color: #ffffff; }

/* 基本色 */
.k-red         { border-color: #ff0000; }
.k-blue        { border-color: #0000ff; }
.k-cyan        { border-color: #00ffff; }
.k-magenta     { border-color: #ff00ff; }
.k-orangered   { border-color: #ff4500; }


/* 行頭インデント
---------------------------------------------------------------- */
.indent-0,
.indent-0em  { text-indent:  0;   }
.indent-1em  { text-indent:  1em; }
.indent-2em  { text-indent:  2em; }
.indent-3em  { text-indent:  3em; }
.indent-4em  { text-indent:  4em; }
.indent-5em  { text-indent:  5em; }
.indent-6em  { text-indent:  6em; }
.indent-7em  { text-indent:  7em; }
.indent-8em  { text-indent:  8em; }
.indent-9em  { text-indent:  9em; }
.indent-10em { text-indent: 10em; }


/* 突き出しインデント（ぶら下がりインデント）
----------------------------------------------------------------
「h-」は「hanging」の略
---------------------------------------------------------------- */
/* 横組み用 */
.hltr .h-indent-0,
.hltr .h-indent-0em  { text-indent:   0;   padding-left:  0;   }
.hltr .h-indent-1em  { text-indent:  -1em; padding-left:  1em; }
.hltr .h-indent-2em  { text-indent:  -2em; padding-left:  2em; }
.hltr .h-indent-3em  { text-indent:  -3em; padding-left:  3em; }
.hltr .h-indent-4em  { text-indent:  -4em; padding-left:  4em; }
.hltr .h-indent-5em  { text-indent:  -5em; padding-left:  5em; }
.hltr .h-indent-6em  { text-indent:  -6em; padding-left:  6em; }
.hltr .h-indent-7em  { text-indent:  -7em; padding-left:  7em; }
.hltr .h-indent-8em  { text-indent:  -8em; padding-left:  8em; }
.hltr .h-indent-9em  { text-indent:  -9em; padding-left:  9em; }
.hltr .h-indent-10em { text-indent: -10em; padding-left: 10em; }

/* 縦組み用 */
.vrtl .h-indent-0,
.vrtl .h-indent-0em  { text-indent:   0;   padding-top:  0;   }
.vrtl .h-indent-1em  { text-indent:  -1em; padding-top:  1em; }
.vrtl .h-indent-2em  { text-indent:  -2em; padding-top:  2em; }
.vrtl .h-indent-3em  { text-indent:  -3em; padding-top:  3em; }
.vrtl .h-indent-4em  { text-indent:  -4em; padding-top:  4em; }
.vrtl .h-indent-5em  { text-indent:  -5em; padding-top:  5em; }
.vrtl .h-indent-6em  { text-indent:  -6em; padding-top:  6em; }
.vrtl .h-indent-7em  { text-indent:  -7em; padding-top:  7em; }
.vrtl .h-indent-8em  { text-indent:  -8em; padding-top:  8em; }
.vrtl .h-indent-9em  { text-indent:  -9em; padding-top:  9em; }
.vrtl .h-indent-10em { text-indent: -10em; padding-top: 10em; }


/* 字下げ・字上げ指定
---------------------------------------------------------------- */
/* 字下げ：横組み用 */
.hltr .start-0,
.hltr .start-0em   { margin-left:  0;      }
.hltr .start-0em25 { margin-left:  0.25em; }
.hltr .start-0em50 { margin-left:  0.50em; }
.hltr .start-0em75 { margin-left:  0.75em; }
.hltr .start-1em   { margin-left:  1.00em; }
.hltr .start-1em25 { margin-left:  1.25em; }
.hltr .start-1em50 { margin-left:  1.50em; }
.hltr .start-1em75 { margin-left:  1.75em; }
.hltr .start-2em   { margin-left:  2.00em; }
.hltr .start-2em50 { margin-left:  2.50em; }
.hltr .start-3em   { margin-left:  3.00em; }
.hltr .start-4em   { margin-left:  4.00em; }
.hltr .start-5em   { margin-left:  5.00em; }
.hltr .start-6em   { margin-left:  6.00em; }
.hltr .start-7em   { margin-left:  7.00em; }
.hltr .start-8em   { margin-left:  8.00em; }
.hltr .start-9em   { margin-left:  9.00em; }
.hltr .start-10em  { margin-left: 10.00em; }

/* 字下げ：縦組み用 */
.vrtl .start-0,
.vrtl .start-0em   { margin-top:  0;      }
.vrtl .start-0em25 { margin-top:  0.25em; }
.vrtl .start-0em50 { margin-top:  0.50em; }
.vrtl .start-0em75 { margin-top:  0.75em; }
.vrtl .start-1em   { margin-top:  1.00em; }
.vrtl .start-1em25 { margin-top:  1.25em; }
.vrtl .start-1em50 { margin-top:  1.50em; }
.vrtl .start-1em75 { margin-top:  1.75em; }
.vrtl .start-2em   { margin-top:  2.00em; }
.vrtl .start-2em50 { margin-top:  2.50em; }
.vrtl .start-3em   { margin-top:  3.00em; }
.vrtl .start-4em   { margin-top:  4.00em; }
.vrtl .start-5em   { margin-top:  5.00em; }
.vrtl .start-6em   { margin-top:  6.00em; }
.vrtl .start-7em   { margin-top:  7.00em; }
.vrtl .start-8em   { margin-top:  8.00em; }
.vrtl .start-9em   { margin-top:  9.00em; }
.vrtl .start-10em  { margin-top: 10.00em; }

/* 字上げ：横組み用 */
.hltr .end-0,
.hltr .end-0em   { margin-right:  0;      }
.hltr .end-0em25 { margin-right:  0.25em; }
.hltr .end-0em50 { margin-right:  0.50em; }
.hltr .end-0em75 { margin-right:  0.75em; }
.hltr .end-1em   { margin-right:  1.00em; }
.hltr .end-1em25 { margin-right:  1.25em; }
.hltr .end-1em50 { margin-right:  1.50em; }
.hltr .end-1em75 { margin-right:  1.75em; }
.hltr .end-2em   { margin-right:  2.00em; }
.hltr .end-2em50 { margin-right:  2.50em; }
.hltr .end-3em   { margin-right:  3.00em; }
.hltr .end-4em   { margin-right:  4.00em; }
.hltr .end-5em   { margin-right:  5.00em; }
.hltr .end-6em   { margin-right:  6.00em; }
.hltr .end-7em   { margin-right:  7.00em; }
.hltr .end-8em   { margin-right:  8.00em; }
.hltr .end-9em   { margin-right:  9.00em; }
.hltr .end-10em  { margin-right: 10.00em; }

/* 字上げ：縦組み用 */
.vrtl .end-0,
.vrtl .end-0em   { margin-bottom:  0;      }
.vrtl .end-0em25 { margin-bottom:  0.25em; }
.vrtl .end-0em50 { margin-bottom:  0.50em; }
.vrtl .end-0em75 { margin-bottom:  0.75em; }
.vrtl .end-1em   { margin-bottom:  1.00em; }
.vrtl .end-1em25 { margin-bottom:  1.25em; }
.vrtl .end-1em50 { margin-bottom:  1.50em; }
.vrtl .end-1em75 { margin-bottom:  1.75em; }
.vrtl .end-2em   { margin-bottom:  2.00em; }
.vrtl .end-2em50 { margin-bottom:  2.50em; }
.vrtl .end-3em   { margin-bottom:  3.00em; }
.vrtl .end-4em   { margin-bottom:  4.00em; }
.vrtl .end-5em   { margin-bottom:  5.00em; }
.vrtl .end-6em   { margin-bottom:  6.00em; }
.vrtl .end-7em   { margin-bottom:  7.00em; }
.vrtl .end-8em   { margin-bottom:  8.00em; }
.vrtl .end-9em   { margin-bottom:  9.00em; }
.vrtl .end-10em  { margin-bottom: 10.00em; }


/* 外側の余白（マージン）指定
----------------------------------------------------------------
字下げ・字上げと同じ要素で同時には使えないので注意
【ＮＧ例】<div class="start-2em m-top-1em">
　　　　　→字下げを内側にして <div> の入れ子とする
---------------------------------------------------------------- */
/* 四方 */
.m-auto   { margin: auto; }
.m-0,
.m-0em,
.m-000per { margin: 0; }

/* ％指定 */
.m-005per { margin:  5%; }
.m-010per { margin: 10%; }
.m-015per { margin: 15%; }
.m-020per { margin: 20%; }
.m-025per { margin: 25%; }
.m-030per { margin: 30%; }
.m-033per { margin: 33%; }
.m-040per { margin: 40%; }
.m-050per { margin: 50%; }
.m-060per { margin: 60%; }
.m-067per { margin: 67%; }
.m-070per { margin: 70%; }
.m-075per { margin: 75%; }
.m-080per { margin: 80%; }
.m-090per { margin: 90%; }

/* 文字数指定 */
.m-0em10 { margin: 0.10em; }
.m-0em20 { margin: 0.20em; }
.m-0em25 { margin: 0.25em; }
.m-0em30 { margin: 0.30em; }
.m-0em40 { margin: 0.40em; }
.m-0em50 { margin: 0.50em; }
.m-0em60 { margin: 0.60em; }
.m-0em70 { margin: 0.70em; }
.m-0em75 { margin: 0.75em; }
.m-0em80 { margin: 0.80em; }
.m-0em90 { margin: 0.90em; }
.m-1em   { margin: 1.00em; }
.m-1em25 { margin: 1.25em; }
.m-1em50 { margin: 1.50em; }
.m-1em75 { margin: 1.75em; }
.m-2em   { margin: 2.00em; }
.m-2em50 { margin: 2.50em; }
.m-3em   { margin: 3.00em; }
.m-4em   { margin: 4.00em; }
.m-5em   { margin: 5.00em; }


/* 画面上側（縦組み：行頭／横組み：行前方） */
.m-top-auto   { margin-top: auto; }
.m-top-0,
.m-top-0em,
.m-top-000per { margin-top: 0; }

/* ％指定 */
.m-top-005per { margin-top:  5%; }
.m-top-010per { margin-top: 10%; }
.m-top-015per { margin-top: 15%; }
.m-top-020per { margin-top: 20%; }
.m-top-025per { margin-top: 25%; }
.m-top-030per { margin-top: 30%; }
.m-top-033per { margin-top: 33%; }
.m-top-040per { margin-top: 40%; }
.m-top-050per { margin-top: 50%; }
.m-top-060per { margin-top: 60%; }
.m-top-067per { margin-top: 67%; }
.m-top-070per { margin-top: 70%; }
.m-top-075per { margin-top: 75%; }
.m-top-080per { margin-top: 80%; }
.m-top-090per { margin-top: 90%; }

/* 文字数指定 */
.m-top-0em25 { margin-top: 0.25em; }
.m-top-0em50 { margin-top: 0.50em; }
.m-top-0em75 { margin-top: 0.75em; }
.m-top-1em   { margin-top: 1.00em; }
.m-top-1em25 { margin-top: 1.25em; }
.m-top-1em50 { margin-top: 1.50em; }
.m-top-1em75 { margin-top: 1.75em; }
.m-top-2em   { margin-top: 2.00em; }
.m-top-2em50 { margin-top: 2.50em; }
.m-top-3em   { margin-top: 3.00em; }
.m-top-4em   { margin-top: 4.00em; }
.m-top-5em   { margin-top: 5.00em; }
.m-top-5em25 { margin-top: 5.25em; }


/* 画面左側（縦組み：行後方／横組み：行頭） */
.m-left-auto   { margin-left: auto; }
.m-left-0,
.m-left-0em,
.m-left-000per { margin-left: 0; }

/* ％指定 */
.m-left-005per { margin-left:  5%; }
.m-left-010per { margin-left: 10%; }
.m-left-015per { margin-left: 15%; }
.m-left-020per { margin-left: 20%; }
.m-left-025per { margin-left: 25%; }
.m-left-030per { margin-left: 30%; }
.m-left-033per { margin-left: 33%; }
.m-left-040per { margin-left: 40%; }
.m-left-050per { margin-left: 50%; }
.m-left-060per { margin-left: 60%; }
.m-left-067per { margin-left: 67%; }
.m-left-070per { margin-left: 70%; }
.m-left-075per { margin-left: 75%; }
.m-left-080per { margin-left: 80%; }
.m-left-090per { margin-left: 90%; }

/* 文字数指定 */
.m-left-0em25 { margin-left: 0.25em; }
.m-left-0em50 { margin-left: 0.50em; }
.m-left-0em75 { margin-left: 0.75em; }
.m-left-1em   { margin-left: 1.00em; }
.m-left-1em25 { margin-left: 1.25em; }
.m-left-1em50 { margin-left: 1.50em; }
.m-left-1em75 { margin-left: 1.75em; }
.m-left-2em   { margin-left: 2.00em; }
.m-left-2em50 { margin-left: 2.50em; }
.m-left-3em   { margin-left: 3.00em; }
.m-left-4em   { margin-left: 4.00em; }
.m-left-5em   { margin-left: 5.00em; }
.m-left-5em25 { margin-left: 5.25em; }


/* 画面右側（縦組み：行前方／横組み：行末） */
.m-right-auto   { margin-right: auto; }
.m-right-0
.m-right-0em
.m-right-000per { margin-right: 0; }

/* ％指定 */
.m-right-005per { margin-right:  5%; }
.m-right-010per { margin-right: 10%; }
.m-right-015per { margin-right: 15%; }
.m-right-020per { margin-right: 20%; }
.m-right-025per { margin-right: 25%; }
.m-right-030per { margin-right: 30%; }
.m-right-033per { margin-right: 33%; }
.m-right-040per { margin-right: 40%; }
.m-right-050per { margin-right: 50%; }
.m-right-060per { margin-right: 60%; }
.m-right-067per { margin-right: 67%; }
.m-right-070per { margin-right: 70%; }
.m-right-075per { margin-right: 75%; }
.m-right-080per { margin-right: 80%; }
.m-right-090per { margin-right: 90%; }

/* 文字数指定 */
.m-right-0em25 { margin-right: 0.25em; }
.m-right-0em50 { margin-right: 0.50em; }
.m-right-0em75 { margin-right: 0.75em; }
.m-right-1em   { margin-right: 1.00em; }
.m-right-1em25 { margin-right: 1.25em; }
.m-right-1em50 { margin-right: 1.50em; }
.m-right-1em75 { margin-right: 1.75em; }
.m-right-2em   { margin-right: 2.00em; }
.m-right-2em50 { margin-right: 2.50em; }
.m-right-3em   { margin-right: 3.00em; }
.m-right-4em   { margin-right: 4.00em; }
.m-right-5em   { margin-right: 5.00em; }
.m-right-5em25 { margin-right: 5.25em; }


/* 画面下側（縦組み：行末／横組み：行後方） */
.m-bottom-auto   { margin-bottom: auto; }
.m-bottom-0,
.m-bottom-0em,
.m-bottom-000per { margin-bottom: 0; }

/* ％指定 */
.m-bottom-005per { margin-bottom:  5%; }
.m-bottom-010per { margin-bottom: 10%; }
.m-bottom-015per { margin-bottom: 15%; }
.m-bottom-020per { margin-bottom: 20%; }
.m-bottom-025per { margin-bottom: 25%; }
.m-bottom-030per { margin-bottom: 30%; }
.m-bottom-033per { margin-bottom: 33%; }
.m-bottom-040per { margin-bottom: 40%; }
.m-bottom-050per { margin-bottom: 50%; }
.m-bottom-060per { margin-bottom: 60%; }
.m-bottom-067per { margin-bottom: 67%; }
.m-bottom-070per { margin-bottom: 70%; }
.m-bottom-075per { margin-bottom: 75%; }
.m-bottom-080per { margin-bottom: 80%; }
.m-bottom-090per { margin-bottom: 90%; }

/* 文字数指定 */
.m-bottom-0em25 { margin-bottom: 0.25em; }
.m-bottom-0em50 { margin-bottom: 0.50em; }
.m-bottom-0em75 { margin-bottom: 0.75em; }
.m-bottom-1em   { margin-bottom: 1.00em; }
.m-bottom-1em25 { margin-bottom: 1.25em; }
.m-bottom-1em50 { margin-bottom: 1.50em; }
.m-bottom-1em75 { margin-bottom: 1.75em; }
.m-bottom-2em   { margin-bottom: 2.00em; }
.m-bottom-2em50 { margin-bottom: 2.50em; }
.m-bottom-3em   { margin-bottom: 3.00em; }
.m-bottom-4em   { margin-bottom: 4.00em; }
.m-bottom-5em   { margin-bottom: 5.00em; }
.m-bottom-5em25 { margin-bottom: 5.25em; }


/* 内側の余白（パディング）指定
---------------------------------------------------------------- */
/* 四方 */
.p-0,
.p-0em,
.p-000per { padding: 0; }

/* ％指定 */
.p-005per { padding:  5%; }
.p-010per { padding: 10%; }
.p-015per { padding: 15%; }
.p-020per { padding: 20%; }
.p-025per { padding: 25%; }
.p-030per { padding: 30%; }
.p-033per { padding: 33%; }
.p-040per { padding: 40%; }
.p-050per { padding: 50%; }
.p-060per { padding: 60%; }
.p-067per { padding: 67%; }
.p-070per { padding: 70%; }
.p-075per { padding: 75%; }
.p-080per { padding: 80%; }
.p-090per { padding: 90%; }

/* 文字数指定 */
.p-0em10 { padding: 0.10em; }
.p-0em20 { padding: 0.20em; }
.p-0em25 { padding: 0.25em; }
.p-0em30 { padding: 0.30em; }
.p-0em40 { padding: 0.40em; }
.p-0em50 { padding: 0.50em; }
.p-0em60 { padding: 0.60em; }
.p-0em70 { padding: 0.70em; }
.p-0em75 { padding: 0.75em; }
.p-0em80 { padding: 0.80em; }
.p-0em90 { padding: 0.90em; }
.p-1em   { padding: 1.00em; }
.p-1em25 { padding: 1.25em; }
.p-1em50 { padding: 1.50em; }
.p-1em75 { padding: 1.75em; }
.p-2em   { padding: 2.00em; }
.p-2em50 { padding: 2.50em; }
.p-3em   { padding: 3.00em; }
.p-4em   { padding: 4.00em; }
.p-5em   { padding: 5.00em; }


/* 画面上側（縦組み：行頭／横組み：行前方） */
.p-top-0,
.p-top-0em,
.p-top-000per { padding-top: 0; }

/* ％指定 */
.p-top-005per { padding-top:  5%; }
.p-top-010per { padding-top: 10%; }
.p-top-015per { padding-top: 15%; }
.p-top-020per { padding-top: 20%; }
.p-top-025per { padding-top: 25%; }
.p-top-030per { padding-top: 30%; }
.p-top-033per { padding-top: 33%; }
.p-top-040per { padding-top: 40%; }
.p-top-050per { padding-top: 50%; }
.p-top-060per { padding-top: 60%; }
.p-top-067per { padding-top: 67%; }
.p-top-070per { padding-top: 70%; }
.p-top-075per { padding-top: 75%; }
.p-top-080per { padding-top: 80%; }
.p-top-090per { padding-top: 90%; }

/* 文字数指定 */
.p-top-0em25 { padding-top: 0.25em; }
.p-top-0em50 { padding-top: 0.50em; }
.p-top-0em75 { padding-top: 0.75em; }
.p-top-1em   { padding-top: 1.00em; }
.p-top-1em25 { padding-top: 1.25em; }
.p-top-1em50 { padding-top: 1.50em; }
.p-top-1em75 { padding-top: 1.75em; }
.p-top-2em   { padding-top: 2.00em; }
.p-top-2em50 { padding-top: 2.50em; }
.p-top-3em   { padding-top: 3.00em; }
.p-top-4em   { padding-top: 4.00em; }
.p-top-5em   { padding-top: 5.00em; }
.p-top-5em25 { padding-top: 5.25em; }


/* 画面左側（縦組み：行後方／横組み：行頭） */
.p-left-0,
.p-left-0em,
.p-left-000per { padding-left: 0; }

/* ％指定 */
.p-left-005per { padding-left:  5%; }
.p-left-010per { padding-left: 10%; }
.p-left-015per { padding-left: 15%; }
.p-left-020per { padding-left: 20%; }
.p-left-025per { padding-left: 25%; }
.p-left-030per { padding-left: 30%; }
.p-left-033per { padding-left: 33%; }
.p-left-040per { padding-left: 40%; }
.p-left-050per { padding-left: 50%; }
.p-left-060per { padding-left: 60%; }
.p-left-067per { padding-left: 67%; }
.p-left-070per { padding-left: 70%; }
.p-left-075per { padding-left: 75%; }
.p-left-080per { padding-left: 80%; }
.p-left-090per { padding-left: 90%; }

/* 文字数指定 */
.p-left-0em25 { padding-left: 0.25em; }
.p-left-0em50 { padding-left: 0.50em; }
.p-left-0em75 { padding-left: 0.75em; }
.p-left-1em   { padding-left: 1.00em; }
.p-left-1em25 { padding-left: 1.25em; }
.p-left-1em50 { padding-left: 1.50em; }
.p-left-1em75 { padding-left: 1.75em; }
.p-left-2em   { padding-left: 2.00em; }
.p-left-2em50 { padding-left: 2.50em; }
.p-left-3em   { padding-left: 3.00em; }
.p-left-4em   { padding-left: 4.00em; }
.p-left-5em   { padding-left: 5.00em; }
.p-left-5em25 { padding-left: 5.25em; }


/* 画面右側（縦組み：行前方／横組み：行末） */
.p-right-0
.p-right-0em
.p-right-000per { padding-right: 0; }

/* ％指定 */
.p-right-005per { padding-right:  5%; }
.p-right-010per { padding-right: 10%; }
.p-right-015per { padding-right: 15%; }
.p-right-020per { padding-right: 20%; }
.p-right-025per { padding-right: 25%; }
.p-right-030per { padding-right: 30%; }
.p-right-033per { padding-right: 33%; }
.p-right-040per { padding-right: 40%; }
.p-right-050per { padding-right: 50%; }
.p-right-060per { padding-right: 60%; }
.p-right-067per { padding-right: 67%; }
.p-right-070per { padding-right: 70%; }
.p-right-075per { padding-right: 75%; }
.p-right-080per { padding-right: 80%; }
.p-right-090per { padding-right: 90%; }

/* 文字数指定 */
.p-right-0em25 { padding-right: 0.25em; }
.p-right-0em50 { padding-right: 0.50em; }
.p-right-0em75 { padding-right: 0.75em; }
.p-right-1em   { padding-right: 1.00em; }
.p-right-1em25 { padding-right: 1.25em; }
.p-right-1em50 { padding-right: 1.50em; }
.p-right-1em75 { padding-right: 1.75em; }
.p-right-2em   { padding-right: 2.00em; }
.p-right-2em50 { padding-right: 2.50em; }
.p-right-3em   { padding-right: 3.00em; }
.p-right-4em   { padding-right: 4.00em; }
.p-right-5em   { padding-right: 5.00em; }
.p-right-5em25 { padding-right: 5.25em; }


/* 画面下側（縦組み：行末／横組み：行後方） */
.p-bottom-0,
.p-bottom-0em,
.p-bottom-000per { padding-bottom:  0;  }

/* ％指定 */
.p-bottom-005per { padding-bottom:  5%; }
.p-bottom-010per { padding-bottom: 10%; }
.p-bottom-015per { padding-bottom: 15%; }
.p-bottom-020per { padding-bottom: 20%; }
.p-bottom-025per { padding-bottom: 25%; }
.p-bottom-030per { padding-bottom: 30%; }
.p-bottom-033per { padding-bottom: 33%; }
.p-bottom-040per { padding-bottom: 40%; }
.p-bottom-050per { padding-bottom: 50%; }
.p-bottom-060per { padding-bottom: 60%; }
.p-bottom-067per { padding-bottom: 67%; }
.p-bottom-070per { padding-bottom: 70%; }
.p-bottom-075per { padding-bottom: 75%; }
.p-bottom-080per { padding-bottom: 80%; }
.p-bottom-090per { padding-bottom: 90%; }

/* 文字数指定 */
.p-bottom-0em25 { padding-bottom: 0.25em; }
.p-bottom-0em50 { padding-bottom: 0.50em; }
.p-bottom-0em75 { padding-bottom: 0.75em; }
.p-bottom-1em   { padding-bottom: 1.00em; }
.p-bottom-1em25 { padding-bottom: 1.25em; }
.p-bottom-1em50 { padding-bottom: 1.50em; }
.p-bottom-1em75 { padding-bottom: 1.75em; }
.p-bottom-2em   { padding-bottom: 2.00em; }
.p-bottom-2em50 { padding-bottom: 2.50em; }
.p-bottom-3em   { padding-bottom: 3.00em; }
.p-bottom-4em   { padding-bottom: 4.00em; }
.p-bottom-5em   { padding-bottom: 5.00em; }
.p-bottom-5em25 { padding-bottom: 5.25em; }


/* 高さ
---------------------------------------------------------------- */
.height-auto   { height: auto; }

/* ％指定 */
.height-010per { height:  10%; }
.height-020per { height:  20%; }
.height-025per { height:  25%; }
.height-030per { height:  30%; }
.height-033per { height:  33%; }
.height-040per { height:  40%; }
.height-050per { height:  50%; }
.height-060per { height:  60%; }
.height-067per { height:  67%; }
.height-070per { height:  70%; }
.height-075per { height:  75%; }
.height-080per { height:  80%; }
.height-090per { height:  90%; }
.height-100per { height: 100%; }

/* 文字数指定 */
.height-0em25 { height:  0.25em; }
.height-0em50 { height:  0.50em; }
.height-0em75 { height:  0.75em; }
.height-1em   { height:  1.00em; }
.height-1em25 { height:  1.25em; }
.height-1em50 { height:  1.50em; }
.height-1em75 { height:  1.75em; }
.height-2em   { height:  2.00em; }
.height-2em50 { height:  2.50em; }
.height-3em   { height:  3.00em; }
.height-4em   { height:  4.00em; }
.height-5em   { height:  5.00em; }
.height-5em25 { height:  5.25em; }
.height-6em   { height:  6.00em; }
.height-7em   { height:  7.00em; }
.height-8em   { height:  8.00em; }
.height-8em75 { height:  8.75em; }
.height-9em   { height:  9.00em; }
.height-10em  { height: 10.00em; }
.height-11em  { height: 11.00em; }
.height-12em  { height: 12.00em; }
.height-13em  { height: 13.00em; }
.height-14em  { height: 14.00em; }
.height-15em  { height: 15.00em; }
.height-20em  { height: 20.00em; }
.height-30em  { height: 30.00em; }
.height-40em  { height: 40.00em; }


/* 高さの最大値
---------------------------------------------------------------- */
.max-height-none   { max-height: none; }

/* ％指定 */
.max-height-010per { max-height:  10%; }
.max-height-020per { max-height:  20%; }
.max-height-025per { max-height:  25%; }
.max-height-030per { max-height:  30%; }
.max-height-033per { max-height:  33%; }
.max-height-040per { max-height:  40%; }
.max-height-050per { max-height:  50%; }
.max-height-060per { max-height:  60%; }
.max-height-067per { max-height:  67%; }
.max-height-070per { max-height:  70%; }
.max-height-075per { max-height:  75%; }
.max-height-080per { max-height:  80%; }
.max-height-090per { max-height:  90%; }
.max-height-100per { max-height: 100%; }

/* 文字数指定 */
.max-height-0em25 { max-height:  0.25em; }
.max-height-0em50 { max-height:  0.50em; }
.max-height-0em75 { max-height:  0.75em; }
.max-height-1em   { max-height:  1.00em; }
.max-height-1em25 { max-height:  1.25em; }
.max-height-1em50 { max-height:  1.50em; }
.max-height-1em75 { max-height:  1.75em; }
.max-height-2em   { max-height:  2.00em; }
.max-height-2em50 { max-height:  2.50em; }
.max-height-3em   { max-height:  3.00em; }
.max-height-4em   { max-height:  4.00em; }
.max-height-5em   { max-height:  5.00em; }
.max-height-5em25 { max-height:  5.25em; }
.max-height-6em   { max-height:  6.00em; }
.max-height-7em   { max-height:  7.00em; }
.max-height-8em   { max-height:  8.00em; }
.max-height-8em75 { max-height:  8.75em; }
.max-height-9em   { max-height:  9.00em; }
.max-height-10em  { max-height: 10.00em; }
.max-height-11em  { max-height: 11.00em; }
.max-height-12em  { max-height: 12.00em; }
.max-height-13em  { max-height: 13.00em; }
.max-height-14em  { max-height: 14.00em; }
.max-height-15em  { max-height: 15.00em; }
.max-height-20em  { max-height: 20.00em; }
.max-height-30em  { max-height: 30.00em; }
.max-height-40em  { max-height: 40.00em; }


/* 幅
---------------------------------------------------------------- */
.width-auto   { width: auto; }

/* ％指定 */
.width-010per { width:  10%; }
.width-020per { width:  20%; }
.width-025per { width:  25%; }
.width-030per { width:  30%; }
.width-033per { width:  33%; }
.width-040per { width:  40%; }
.width-050per { width:  50%; }
.width-060per { width:  60%; }
.width-067per { width:  67%; }
.width-070per { width:  70%; }
.width-075per { width:  75%; }
.width-080per { width:  80%; }
.width-090per { width:  90%; }
.width-100per { width: 100%; }

/* 文字数指定 */
.width-0em25 { width:  0.25em; }
.width-0em50 { width:  0.50em; }
.width-0em75 { width:  0.75em; }
.width-1em   { width:  1.00em; }
.width-1em25 { width:  1.25em; }
.width-1em50 { width:  1.50em; }
.width-1em75 { width:  1.75em; }
.width-2em   { width:  2.00em; }
.width-2em50 { width:  2.50em; }
.width-3em   { width:  3.00em; }
.width-4em   { width:  4.00em; }
.width-5em   { width:  5.00em; }
.width-5em25 { width:  5.25em; }
.width-6em   { width:  6.00em; }
.width-7em   { width:  7.00em; }
.width-8em   { width:  8.00em; }
.width-8em75 { width:  8.75em; }
.width-9em   { width:  9.00em; }
.width-10em  { width: 10.00em; }
.width-11em  { width: 11.00em; }
.width-12em  { width: 12.00em; }
.width-13em  { width: 13.00em; }
.width-14em  { width: 14.00em; }
.width-15em  { width: 15.00em; }
.width-20em  { width: 20.00em; }
.width-30em  { width: 30.00em; }
.width-40em  { width: 40.00em; }


/* 幅の最大値
---------------------------------------------------------------- */
.max-width-none   { max-width: none; }

/* ％指定 */
.max-width-010per { max-width:  10%; }
.max-width-020per { max-width:  20%; }
.max-width-025per { max-width:  25%; }
.max-width-030per { max-width:  30%; }
.max-width-033per { max-width:  33%; }
.max-width-040per { max-width:  40%; }
.max-width-050per { max-width:  50%; }
.max-width-060per { max-width:  60%; }
.max-width-067per { max-width:  67%; }
.max-width-070per { max-width:  70%; }
.max-width-075per { max-width:  75%; }
.max-width-080per { max-width:  80%; }
.max-width-090per { max-width:  90%; }
.max-width-100per { max-width: 100%; }

/* 文字数指定 */
.max-width-0em25 { max-width:  0.25em; }
.max-width-0em50 { max-width:  0.50em; }
.max-width-0em75 { max-width:  0.75em; }
.max-width-1em   { max-width:  1.00em; }
.max-width-1em25 { max-width:  1.25em; }
.max-width-1em50 { max-width:  1.50em; }
.max-width-1em75 { max-width:  1.75em; }
.max-width-2em   { max-width:  2.00em; }
.max-width-2em50 { max-width:  2.50em; }
.max-width-3em   { max-width:  3.00em; }
.max-width-4em   { max-width:  4.00em; }
.max-width-5em   { max-width:  5.00em; }
.max-width-5em25 { max-width:  5.25em; }
.max-width-6em   { max-width:  6.00em; }
.max-width-7em   { max-width:  7.00em; }
.max-width-8em   { max-width:  8.00em; }
.max-width-8em75 { max-width:  8.75em; }
.max-width-9em   { max-width:  9.00em; }
.max-width-10em  { max-width: 10.00em; }
.max-width-11em  { max-width: 11.00em; }
.max-width-12em  { max-width: 12.00em; }
.max-width-13em  { max-width: 13.00em; }
.max-width-14em  { max-width: 14.00em; }
.max-width-15em  { max-width: 15.00em; }
.max-width-20em  { max-width: 20.00em; }
.max-width-30em  { max-width: 30.00em; }
.max-width-40em  { max-width: 40.00em; }


/* 最大サイズ
---------------------------------------------------------------- */
.max-size-none   { max-height: none; max-width: none; }

/* ％指定 */
.max-size-005per { max-height:   5%; max-width:   5%; }
.max-size-010per { max-height:  10%; max-width:  10%; }
.max-size-020per { max-height:  20%; max-width:  20%; }
.max-size-025per { max-height:  25%; max-width:  25%; }
.max-size-030per { max-height:  30%; max-width:  30%; }
.max-size-033per { max-height:  33%; max-width:  33%; }
.max-size-040per { max-height:  40%; max-width:  40%; }
.max-size-050per { max-height:  50%; max-width:  50%; }
.max-size-060per { max-height:  60%; max-width:  60%; }
.max-size-067per { max-height:  67%; max-width:  67%; }
.max-size-070per { max-height:  70%; max-width:  70%; }
.max-size-075per { max-height:  75%; max-width:  75%; }
.max-size-080per { max-height:  80%; max-width:  80%; }
.max-size-090per { max-height:  90%; max-width:  90%; }
.max-size-100per { max-height: 100%; max-width: 100%; }

/* 文字数指定 */
.max-size-0em25 { max-height:  0.25em; max-width:  0.25em; }
.max-size-0em50 { max-height:  0.50em; max-width:  0.50em; }
.max-size-0em75 { max-height:  0.75em; max-width:  0.75em; }
.max-size-1em   { max-height:  1.00em; max-width:  1.00em; }
.max-size-1em25 { max-height:  1.25em; max-width:  1.25em; }
.max-size-1em50 { max-height:  1.50em; max-width:  1.50em; }
.max-size-1em75 { max-height:  1.75em; max-width:  1.75em; }
.max-size-2em   { max-height:  2.00em; max-width:  2.00em; }
.max-size-2em50 { max-height:  2.50em; max-width:  2.50em; }
.max-size-3em   { max-height:  3.00em; max-width:  3.00em; }
.max-size-4em   { max-height:  4.00em; max-width:  4.00em; }
.max-size-5em   { max-height:  5.00em; max-width:  5.00em; }
.max-size-5em25 { max-height:  5.25em; max-width:  5.25em; }
.max-size-6em   { max-height:  6.00em; max-width:  6.00em; }
.max-size-7em   { max-height:  7.00em; max-width:  7.00em; }
.max-size-8em   { max-height:  8.00em; max-width:  8.00em; }
.max-size-8em75 { max-height:  8.75em; max-width:  8.75em; }
.max-size-9em   { max-height:  9.00em; max-width:  9.00em; }
.max-size-10em  { max-height: 10.00em; max-width: 10.00em; }
.max-size-11em  { max-height: 11.00em; max-width: 11.00em; }
.max-size-12em  { max-height: 12.00em; max-width: 12.00em; }
.max-size-13em  { max-height: 13.00em; max-width: 13.00em; }
.max-size-14em  { max-height: 14.00em; max-width: 14.00em; }
.max-size-15em  { max-height: 15.00em; max-width: 15.00em; }
.max-size-20em  { max-height: 20.00em; max-width: 20.00em; }
.max-size-30em  { max-height: 30.00em; max-width: 30.00em; }
.max-size-40em  { max-height: 40.00em; max-width: 40.00em; }


/* 禁則処理のルール
---------------------------------------------------------------- */
.line-break-auto {
  -webkit-line-break: auto;
  -epub-line-break:   auto;
}
.line-break-loose {
  -webkit-line-break: loose;
  -epub-line-break:   loose;
}
.line-break-normal {
  -webkit-line-break: normal;
  -epub-line-break:   normal;
}
.line-break-strict {
  -webkit-line-break: strict;
  -epub-line-break:   strict;
}


/* 自動改行のルール
---------------------------------------------------------------- */
.word-break-normal {
  -webkit-word-break: normal;
  -epub-word-break:   normal;
}
.word-break-break-all {
  -webkit-word-break: break-all;
  -epub-word-break:   break-all;
}
.word-break-keep-all {
  -webkit-word-break: keep-all;
  -epub-word-break:   keep-all;
}


/* 長い単語の改行ルール
---------------------------------------------------------------- */
.word-wrap-normal {
  word-wrap: normal;
}
.word-wrap-break-word {
  word-wrap: break-word;
}


/* 【参考】回り込み
---------------------------------------------------------------- */
/* 行頭方向に回り込み */
.float-left,
.float-start {
  float: left;
}
/* 行末方向に回り込み */
.float-right,
.float-end {
  float: right;
}
/* 回り込みなし */
.float-none {
  float: none;
}
/* 回り込み解除 */
.float-clear {
  clear: both;
}
/* 行頭方向の回り込み解除 */
.float-clear-left,
.float-clear-start {
  clear: left;
}
/* 行末方向の回り込み解除 */
.float-clear-right,
.float-clear-end {
  clear: right;
}"""
    # 論理方向や組み込み方向の混在などに対応するためのスタイルセット
    __CSS_ADVANCE = """@charset "UTF-8";


/* ファイル情報
----------------------------------------------------------------
【内容】
全作品共通の基本スタイル（論理方向指定・組み方向の入れ子対策用）

【CSSファイルバージョン】
ver.1.3.1

【当ファイル更新時の電書協EPUB 3 制作ガイドバージョン】
ver.1.1.3

【細目】
・【組み方向の入れ子対策】リンク指定
・【組み方向の入れ子対策】外字画像
・【組み方向の入れ子対策】画像のページフィット指定
・【組み方向の入れ子対策】小書き文字
・【組み方向の入れ子対策】区切り線
・【組み方向の入れ子対策】傍線
・【論理方向指定】罫線
・【組み方向の入れ子対策】突き出しインデント（ぶら下がりインデント）
・【組み方向の入れ子対策】字下げ・字上げ指定
・【論理方向指定】外側の余白（マージン）指定
・【論理方向指定】内側の余白（パディング）指定
・【論理方向指定】行長方向のサイズ
・【論理方向指定】行長方向の最大サイズ
・【論理方向指定】行幅方向のサイズ
・【論理方向指定】行幅方向の最大サイズ

【更新履歴】
2014/11/01 ver.1.3.1
・「線位置【二重線】」を修正

2012/12/07 ver.1.3.0
・ファイル更新時の電書協EPUB 3 制作ガイドバージョン表記を追加

2012/10/29 ver.1.2b1
・「傍線」を修正

2012/10/03 ver.1.1b1
・「傍線」を修正

2012/08/21 ver.1.0b1
・公開版
---------------------------------------------------------------- */


/* 【組み方向の入れ子対策】リンク指定
---------------------------------------------------------------- */
/* 横組み：下線　縦組み：右線 */
.vrtl .hltr a {
  text-decoration: underline;
}
.hltr .vrtl a {
  text-decoration: overline;
}


/* 【組み方向の入れ子対策】外字画像
---------------------------------------------------------------- */
/* 外字画像のベースライン */
.vrtl .hltr img.gaiji,
.vrtl .hltr img.gaiji-line,
.vrtl .hltr img.gaiji-wide {
  vertical-align: text-bottom;
}
.hltr .vrtl img.gaiji,
.hltr .vrtl img.gaiji-line,
.hltr .vrtl img.gaiji-wide {
  vertical-align: baseline;
}


/* 【組み方向の入れ子対策】画像のページフィット指定
---------------------------------------------------------------- */
/* 画像のベースライン */
.vrtl .hltr .fit {
  vertical-align: top;
}
.hltr .vrtl .fit {
  vertical-align: baseline;
}


/* 【組み方向の入れ子対策】小書き文字
---------------------------------------------------------------- */
/* 【横組み】左下 */
.vrtl .hltr .kogaki {
  padding:        0 0.15em 0 0.1em;
  vertical-align: baseline;
}
/* 【縦組み】右上 */
.hltr .vrtl .kogaki {
  padding:        0.1em 0 0.15em 0;
  vertical-align: super;
}


/* 【組み方向の入れ子対策】区切り線
---------------------------------------------------------------- */
/* 【横組み】水平線 */
.vrtl .hltr hr {
  margin:       0.5em 0;
  border-style: solid none none none;
}
/* 【縦組み】垂直線 */
.hltr .vrtl hr {
  margin:       0 0.5em;
  border-style: none solid none none;
}


/* 【組み方向の入れ子対策】傍線
---------------------------------------------------------------- */
/* 【横組み】下線　【縦組み】右線 */
.vrtl .hltr .em-line {
  text-decoration: underline;
}
.hltr .vrtl .em-line {
  text-decoration: overline;
}
/* 【横組み】上線　【縦組み】左線 */
.vrtl .hltr .em-line-outside {
  text-decoration: overline;
}
.hltr .vrtl .em-line-outside {
  text-decoration: underline;
}


/* 【論理方向指定】罫線
---------------------------------------------------------------- */
/* 線種【実線】 */
.k-solid-start,
.k-solid-before,
.k-solid-end,
.k-solid-after,
.k-solid-startend,
.k-solid-beforeafter {
  border-width: 1px;
  border-color: #000000;
}
/* 線位置【実線】 */
/* 横組み用 */
.hltr .k-solid-start,       .vrtl .hltr .k-solid-start       { border-style: none none none solid;  }
.hltr .k-solid-before,      .vrtl .hltr .k-solid-before      { border-style: solid none none none;  }
.hltr .k-solid-end,         .vrtl .hltr .k-solid-end         { border-style: none solid none none;  }
.hltr .k-solid-after,       .vrtl .hltr .k-solid-after       { border-style: none none solid none;  }
.hltr .k-solid-startend,    .vrtl .hltr .k-solid-startend    { border-style: none solid none solid; }
.hltr .k-solid-beforeafter, .vrtl .hltr .k-solid-beforeafter { border-style: solid none solid none; }
/* 縦組み用 */
.vrtl .k-solid-start,       .hltr .vrtl .k-solid-start       { border-style: solid none none none;  }
.vrtl .k-solid-before,      .hltr .vrtl .k-solid-before      { border-style: none solid none none;  }
.vrtl .k-solid-end,         .hltr .vrtl .k-solid-end         { border-style: none none solid none;  }
.vrtl .k-solid-after,       .hltr .vrtl .k-solid-after       { border-style: none none none solid;  }
.vrtl .k-solid-startend,    .hltr .vrtl .k-solid-startend    { border-style: solid none solid none; }
.vrtl .k-solid-beforeafter, .hltr .vrtl .k-solid-beforeafter { border-style: none solid none solid; }

/* 線種【点線】 */
.k-dotted-start,
.k-dotted-before,
.k-dotted-end,
.k-dotted-after,
.k-dotted-startend,
.k-dotted-beforeafter {
  border-width: 2px;
  border-color: #000000;
}
/* 線位置【点線】 */
/* 横組み用 */
.hltr .k-dotted-start,       .vrtl .hltr .k-dotted-start       { border-style: none none none dotted;   }
.hltr .k-dotted-before,      .vrtl .hltr .k-dotted-before      { border-style: dotted none none none;   }
.hltr .k-dotted-end,         .vrtl .hltr .k-dotted-end         { border-style: none dotted none none;   }
.hltr .k-dotted-after,       .vrtl .hltr .k-dotted-after       { border-style: none none dotted none;   }
.hltr .k-dotted-startend,    .vrtl .hltr .k-dotted-startend    { border-style: none dotted none dotted; }
.hltr .k-dotted-beforeafter, .vrtl .hltr .k-dotted-beforeafter { border-style: dotted none dotted none; }
/* 縦組み用 */
.vrtl .k-dotted-start,       .hltr .vrtl .k-dotted-start       { border-style: dotted none none none;   }
.vrtl .k-dotted-before,      .hltr .vrtl .k-dotted-before      { border-style: none dotted none none;   }
.vrtl .k-dotted-end,         .hltr .vrtl .k-dotted-end         { border-style: none none dotted none;   }
.vrtl .k-dotted-after,       .hltr .vrtl .k-dotted-after       { border-style: none none none dotted;   }
.vrtl .k-dotted-startend,    .hltr .vrtl .k-dotted-startend    { border-style: dotted none dotted none; }
.vrtl .k-dotted-beforeafter, .hltr .vrtl .k-dotted-beforeafter { border-style: none dotted none dotted; }

/* 線種【二重線】 */
.k-double-start,
.k-double-before,
.k-double-end,
.k-double-after,
.k-double-startend,
.k-double-beforeafter {
  border-width: 4px;
  border-color: #000000;
}
/* 線位置【二重線】*/
/* 横組み用 */
.hltr .k-double-start,       .vrtl .hltr .k-double-start       { border-style: none none none double;   }
.hltr .k-double-before,      .vrtl .hltr .k-double-before      { border-style: double none none none;   }
.hltr .k-double-end,         .vrtl .hltr .k-double-end         { border-style: none double none none;   }
.hltr .k-double-after,       .vrtl .hltr .k-double-after       { border-style: none none double none;   }
.hltr .k-double-startend,    .vrtl .hltr .k-double-startend    { border-style: none double none double; }
.hltr .k-double-beforeafter, .vrtl .hltr .k-double-beforeafter { border-style: double none double none; }
/* 縦組み用 */
.vrtl .k-double-start,       .hltr .vrtl .k-double-start       { border-style: double none none none;   }
.vrtl .k-double-before,      .hltr .vrtl .k-double-before      { border-style: none double none none;   }
.vrtl .k-double-end,         .hltr .vrtl .k-double-end         { border-style: none none double none;   }
.vrtl .k-double-after,       .hltr .vrtl .k-double-after       { border-style: none none none double;   }
.vrtl .k-double-startend,    .hltr .vrtl .k-double-startend    { border-style: double none double none; }
.vrtl .k-double-beforeafter, .hltr .vrtl .k-double-beforeafter { border-style: none double none double; }

/* 線種【破線】 */
.k-dashed-start,
.k-dashed-before,
.k-dashed-end,
.k-dashed-after,
.k-dashed-startend,
.k-dashed-beforeafter {
  border-width: 1px;
  border-color: #000000;
}
/* 線位置【破線】 */
/* 横組み用 */
.hltr .k-dashed-start,       .vrtl .hltr .k-dashed-start       { border-style: none none none dashed;   }
.hltr .k-dashed-before,      .vrtl .hltr .k-dashed-before      { border-style: dashed none none none;   }
.hltr .k-dashed-end,         .vrtl .hltr .k-dashed-end         { border-style: none dashed none none;   }
.hltr .k-dashed-after,       .vrtl .hltr .k-dashed-after       { border-style: none none dashed none;   }
.hltr .k-dashed-startend,    .vrtl .hltr .k-dashed-startend    { border-style: none dashed none dashed; }
.hltr .k-dashed-beforeafter, .vrtl .hltr .k-dashed-beforeafter { border-style: dashed none dashed none; }
/* 縦組み用 */
.vrtl .k-dashed-start,       .hltr .vrtl .k-dashed-start       { border-style: dashed none none none;   }
.vrtl .k-dashed-before,      .hltr .vrtl .k-dashed-before      { border-style: none dashed none none;   }
.vrtl .k-dashed-end,         .hltr .vrtl .k-dashed-end         { border-style: none none dashed none;   }
.vrtl .k-dashed-after,       .hltr .vrtl .k-dashed-after       { border-style: none none none dashed;   }
.vrtl .k-dashed-startend,    .hltr .vrtl .k-dashed-startend    { border-style: dashed none dashed none; }
.vrtl .k-dashed-beforeafter, .hltr .vrtl .k-dashed-beforeafter { border-style: none dashed none dashed; }

/* 線幅 */
.k-0px    { border-width: 0;      }
.k-1px    { border-width: 1px;    }
.k-2px    { border-width: 2px;    }
.k-3px    { border-width: 3px;    }
.k-4px    { border-width: 4px;    }
.k-5px    { border-width: 5px;    }
.k-6px    { border-width: 6px;    }
.k-7px    { border-width: 7px;    }
.k-8px    { border-width: 8px;    }
.k-thin   { border-width: thin;   }
.k-medium { border-width: medium; }
.k-thick  { border-width: thick;  }

/* １Ｃ用の線色 */
.k-black       { border-color: #000000; }
.k-dimgray     { border-color: #696969; }
.k-gray        { border-color: #808080; }
.k-darkgray    { border-color: #a9a9a9; }
.k-silver      { border-color: #c0c0c0; }
.k-gainsboro   { border-color: #dcdcdc; }
.k-white       { border-color: #ffffff; }

/* 基本色 */
.k-red         { border-color: #ff0000; }
.k-blue        { border-color: #0000ff; }
.k-cyan        { border-color: #00ffff; }
.k-magenta     { border-color: #ff00ff; }
.k-orangered   { border-color: #ff4500; }


/* 【組み方向の入れ子対策】突き出しインデント（ぶら下がりインデント）
---------------------------------------------------------------- */
/* .hltr .vrtl [class|="h-indent"] { padding-left: 0; } */
.hltr .vrtl .h-indent-1em, .hltr .vrtl .h-indent-2em, .hltr .vrtl .h-indent-3em,
.hltr .vrtl .h-indent-4em, .hltr .vrtl .h-indent-5em, .hltr .vrtl .h-indent-6em,
.hltr .vrtl .h-indent-7em, .hltr .vrtl .h-indent-8em, .hltr .vrtl .h-indent-9em,
.hltr .vrtl .h-indent-10em {
  padding-left: 0;
}

/* .vrtl .hltr [class|="h-indent"] { padding-top: 0; } */
.vrtl .hltr .h-indent-1em, .vrtl .hltr .h-indent-2em, .vrtl .hltr .h-indent-3em,
.vrtl .hltr .h-indent-4em, .vrtl .hltr .h-indent-5em, .vrtl .hltr .h-indent-6em,
.vrtl .hltr .h-indent-7em, .vrtl .hltr .h-indent-8em, .vrtl .hltr .h-indent-9em,
.vrtl .hltr .h-indent-10em {
  padding-top: 0;
}


/* 【組み方向の入れ子対策】字下げ・字上げ指定
---------------------------------------------------------------- */
/* 字下げ */
/* .hltr .vrtl [class|="start"] { margin-left: 0; } */
.hltr .vrtl .start-0em25, .hltr .vrtl .start-0em50, .hltr .vrtl .start-0em75,
.hltr .vrtl .start-1em,   .hltr .vrtl .start-1em25, .hltr .vrtl .start-1em50,
.hltr .vrtl .start-1em75, .hltr .vrtl .start-2em,   .hltr .vrtl .start-2em50,
.hltr .vrtl .start-3em,   .hltr .vrtl .start-4em,   .hltr .vrtl .start-5em,
.hltr .vrtl .start-6em,   .hltr .vrtl .start-7em,   .hltr .vrtl .start-8em,
.hltr .vrtl .start-9em,   .hltr .vrtl .start-10em {
  margin-left: 0;
}
/* .vrtl .hltr [class|="start"] { margin-top:  0; } */
.vrtl .hltr .start-0em25, .vrtl .hltr .start-0em50, .vrtl .hltr .start-0em75,
.vrtl .hltr .start-1em,   .vrtl .hltr .start-1em25, .vrtl .hltr .start-1em50,
.vrtl .hltr .start-1em75, .vrtl .hltr .start-2em,   .vrtl .hltr .start-2em50,
.vrtl .hltr .start-3em,   .vrtl .hltr .start-4em,   .vrtl .hltr .start-5em,
.vrtl .hltr .start-6em,   .vrtl .hltr .start-7em,   .vrtl .hltr .start-8em,
.vrtl .hltr .start-9em,   .vrtl .hltr .start-10em {
  margin-top: 0;
}

/* 字上げ */
/* .hltr .vrtl [class|="end"] { margin-right:  0; } */
.hltr .vrtl .end-0em25, .hltr .vrtl .end-0em50, .hltr .vrtl .end-0em75,
.hltr .vrtl .end-1em,   .hltr .vrtl .end-1em25, .hltr .vrtl .end-1em50,
.hltr .vrtl .end-1em75, .hltr .vrtl .end-2em,   .hltr .vrtl .end-2em50,
.hltr .vrtl .end-3em,   .hltr .vrtl .end-4em,   .hltr .vrtl .end-5em,
.hltr .vrtl .end-6em,   .hltr .vrtl .end-7em,   .hltr .vrtl .end-8em,
.hltr .vrtl .end-9em,   .hltr .vrtl .end-10em {
  margin-right: 0;
}
/* .vrtl .hltr [class|="end"] { margin-bottom: 0; } */
.vrtl .hltr .end-0em25, .vrtl .hltr .end-0em50, .vrtl .hltr .end-0em75,
.vrtl .hltr .end-1em,   .vrtl .hltr .end-1em25, .vrtl .hltr .end-1em50,
.vrtl .hltr .end-1em75, .vrtl .hltr .end-2em,   .vrtl .hltr .end-2em50,
.vrtl .hltr .end-3em,   .vrtl .hltr .end-4em,   .vrtl .hltr .end-5em,
.vrtl .hltr .end-6em,   .vrtl .hltr .end-7em,   .vrtl .hltr .end-8em,
.vrtl .hltr .end-9em,   .vrtl .hltr .end-10em {
  margin-bottom: 0;
}


/* 【論理方向指定】外側の余白（マージン）指定
---------------------------------------------------------------- */
/* 行頭マージン：横組み用 */
.hltr .m-start-auto   { margin-left: auto; }
.hltr .m-start-0,
.hltr .m-start-0em,
.hltr .m-start-000per { margin-left: 0; }

/* ％指定 */
.hltr .m-start-005per { margin-left:  5%; }
.hltr .m-start-010per { margin-left: 10%; }
.hltr .m-start-015per { margin-left: 15%; }
.hltr .m-start-020per { margin-left: 20%; }
.hltr .m-start-025per { margin-left: 25%; }
.hltr .m-start-030per { margin-left: 30%; }
.hltr .m-start-033per { margin-left: 33%; }
.hltr .m-start-040per { margin-left: 40%; }
.hltr .m-start-050per { margin-left: 50%; }
.hltr .m-start-060per { margin-left: 60%; }
.hltr .m-start-067per { margin-left: 67%; }
.hltr .m-start-070per { margin-left: 70%; }
.hltr .m-start-075per { margin-left: 75%; }
.hltr .m-start-080per { margin-left: 80%; }
.hltr .m-start-090per { margin-left: 90%; }

/* 文字数指定 */
.hltr .m-start-0em25 { margin-left: 0.25em; }
.hltr .m-start-0em50 { margin-left: 0.50em; }
.hltr .m-start-0em75 { margin-left: 0.75em; }
.hltr .m-start-1em   { margin-left: 1.00em; }
.hltr .m-start-1em25 { margin-left: 1.25em; }
.hltr .m-start-1em50 { margin-left: 1.50em; }
.hltr .m-start-1em75 { margin-left: 1.75em; }
.hltr .m-start-2em   { margin-left: 2.00em; }
.hltr .m-start-2em50 { margin-left: 2.50em; }
.hltr .m-start-3em   { margin-left: 3.00em; }
.hltr .m-start-4em   { margin-left: 4.00em; }
.hltr .m-start-5em   { margin-left: 5.00em; }
.hltr .m-start-5em25 { margin-left: 5.25em; }

/* 行頭マージン：縦組み用 */
.vrtl .m-start-auto   { margin-top: auto; }
.vrtl .m-start-0,
.vrtl .m-start-0em,
.vrtl .m-start-000per { margin-top: 0; }

/* ％指定 */
.vrtl .m-start-005per { margin-top:  5%; }
.vrtl .m-start-010per { margin-top: 10%; }
.vrtl .m-start-015per { margin-top: 15%; }
.vrtl .m-start-020per { margin-top: 20%; }
.vrtl .m-start-025per { margin-top: 25%; }
.vrtl .m-start-030per { margin-top: 30%; }
.vrtl .m-start-033per { margin-top: 33%; }
.vrtl .m-start-040per { margin-top: 40%; }
.vrtl .m-start-050per { margin-top: 50%; }
.vrtl .m-start-060per { margin-top: 60%; }
.vrtl .m-start-067per { margin-top: 67%; }
.vrtl .m-start-070per { margin-top: 70%; }
.vrtl .m-start-075per { margin-top: 75%; }
.vrtl .m-start-080per { margin-top: 80%; }
.vrtl .m-start-090per { margin-top: 90%; }

/* 文字数指定 */
.vrtl .m-start-0em25 { margin-top: 0.25em; }
.vrtl .m-start-0em50 { margin-top: 0.50em; }
.vrtl .m-start-0em75 { margin-top: 0.75em; }
.vrtl .m-start-1em   { margin-top: 1.00em; }
.vrtl .m-start-1em25 { margin-top: 1.25em; }
.vrtl .m-start-1em50 { margin-top: 1.50em; }
.vrtl .m-start-1em75 { margin-top: 1.75em; }
.vrtl .m-start-2em   { margin-top: 2.00em; }
.vrtl .m-start-2em50 { margin-top: 2.50em; }
.vrtl .m-start-3em   { margin-top: 3.00em; }
.vrtl .m-start-4em   { margin-top: 4.00em; }
.vrtl .m-start-5em   { margin-top: 5.00em; }
.vrtl .m-start-5em25 { margin-top: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="m-start"] { margin-left: 0; } */
.hltr .vrtl .m-start-auto,
.hltr .vrtl .m-start-005per, .hltr .vrtl .m-start-010per, .hltr .vrtl .m-start-015per,
.hltr .vrtl .m-start-020per, .hltr .vrtl .m-start-025per, .hltr .vrtl .m-start-030per,
.hltr .vrtl .m-start-033per, .hltr .vrtl .m-start-040per, .hltr .vrtl .m-start-050per,
.hltr .vrtl .m-start-060per, .hltr .vrtl .m-start-067per, .hltr .vrtl .m-start-070per,
.hltr .vrtl .m-start-075per, .hltr .vrtl .m-start-080per, .hltr .vrtl .m-start-090per,
.hltr .vrtl .m-start-0em25,  .hltr .vrtl .m-start-0em50,  .hltr .vrtl .m-start-0em75,
.hltr .vrtl .m-start-1em,    .hltr .vrtl .m-start-1em25,  .hltr .vrtl .m-start-1em50,
.hltr .vrtl .m-start-1em75,  .hltr .vrtl .m-start-2em,    .hltr .vrtl .m-start-2em50,
.hltr .vrtl .m-start-3em,    .hltr .vrtl .m-start-4em,    .hltr .vrtl .m-start-5em,
.hltr .vrtl .m-start-5em25 {
  margin-left: 0;
}
/* .vrtl .hltr [class|="m-start"] { margin-top:  0; } */
.vrtl .hltr .m-start-auto,
.vrtl .hltr .m-start-005per, .vrtl .hltr .m-start-010per, .vrtl .hltr .m-start-015per,
.vrtl .hltr .m-start-020per, .vrtl .hltr .m-start-025per, .vrtl .hltr .m-start-030per,
.vrtl .hltr .m-start-033per, .vrtl .hltr .m-start-040per, .vrtl .hltr .m-start-050per,
.vrtl .hltr .m-start-060per, .vrtl .hltr .m-start-067per, .vrtl .hltr .m-start-070per,
.vrtl .hltr .m-start-075per, .vrtl .hltr .m-start-080per, .vrtl .hltr .m-start-090per,
.vrtl .hltr .m-start-0em25,  .vrtl .hltr .m-start-0em50,  .vrtl .hltr .m-start-0em75,
.vrtl .hltr .m-start-1em,    .vrtl .hltr .m-start-1em25,  .vrtl .hltr .m-start-1em50,
.vrtl .hltr .m-start-1em75,  .vrtl .hltr .m-start-2em,    .vrtl .hltr .m-start-2em50,
.vrtl .hltr .m-start-3em,    .vrtl .hltr .m-start-4em,    .vrtl .hltr .m-start-5em,
.vrtl .hltr .m-start-5em25 {
  margin-top: 0;
}


/* 行末マージン：横組み用 */
.hltr .m-end-auto   { margin-right: auto; }
.hltr .m-end-0,
.hltr .m-end-0em,
.hltr .m-end-000per { margin-right: 0; }

/* ％指定 */
.hltr .m-end-005per { margin-right:  5%; }
.hltr .m-end-010per { margin-right: 10%; }
.hltr .m-end-015per { margin-right: 15%; }
.hltr .m-end-020per { margin-right: 20%; }
.hltr .m-end-025per { margin-right: 25%; }
.hltr .m-end-030per { margin-right: 30%; }
.hltr .m-end-033per { margin-right: 33%; }
.hltr .m-end-040per { margin-right: 40%; }
.hltr .m-end-050per { margin-right: 50%; }
.hltr .m-end-060per { margin-right: 60%; }
.hltr .m-end-067per { margin-right: 67%; }
.hltr .m-end-070per { margin-right: 70%; }
.hltr .m-end-075per { margin-right: 75%; }
.hltr .m-end-080per { margin-right: 80%; }
.hltr .m-end-090per { margin-right: 90%; }

/* 文字数指定 */
.hltr .m-end-0em25 { margin-right: 0.25em; }
.hltr .m-end-0em50 { margin-right: 0.50em; }
.hltr .m-end-0em75 { margin-right: 0.75em; }
.hltr .m-end-1em   { margin-right: 1.00em; }
.hltr .m-end-1em25 { margin-right: 1.25em; }
.hltr .m-end-1em50 { margin-right: 1.50em; }
.hltr .m-end-1em75 { margin-right: 1.75em; }
.hltr .m-end-2em   { margin-right: 2.00em; }
.hltr .m-end-2em50 { margin-right: 2.50em; }
.hltr .m-end-3em   { margin-right: 3.00em; }
.hltr .m-end-4em   { margin-right: 4.00em; }
.hltr .m-end-5em   { margin-right: 5.00em; }
.hltr .m-end-5em25 { margin-right: 5.25em; }

/* 行末マージン：縦組み用 */
.vrtl .m-end-auto   { margin-bottom: auto; }
.vrtl .m-end-0,
.vrtl .m-end-0em,
.vrtl .m-end-000per { margin-bottom: 0; }

/* ％指定 */
.vrtl .m-end-005per { margin-bottom:  5%; }
.vrtl .m-end-010per { margin-bottom: 10%; }
.vrtl .m-end-015per { margin-bottom: 15%; }
.vrtl .m-end-020per { margin-bottom: 20%; }
.vrtl .m-end-025per { margin-bottom: 25%; }
.vrtl .m-end-030per { margin-bottom: 30%; }
.vrtl .m-end-033per { margin-bottom: 33%; }
.vrtl .m-end-040per { margin-bottom: 40%; }
.vrtl .m-end-050per { margin-bottom: 50%; }
.vrtl .m-end-060per { margin-bottom: 60%; }
.vrtl .m-end-067per { margin-bottom: 67%; }
.vrtl .m-end-070per { margin-bottom: 70%; }
.vrtl .m-end-075per { margin-bottom: 75%; }
.vrtl .m-end-080per { margin-bottom: 80%; }
.vrtl .m-end-090per { margin-bottom: 90%; }

/* 文字数指定 */
.vrtl .m-end-0em25 { margin-bottom: 0.25em; }
.vrtl .m-end-0em50 { margin-bottom: 0.50em; }
.vrtl .m-end-0em75 { margin-bottom: 0.75em; }
.vrtl .m-end-1em   { margin-bottom: 1.00em; }
.vrtl .m-end-1em25 { margin-bottom: 1.25em; }
.vrtl .m-end-1em50 { margin-bottom: 1.50em; }
.vrtl .m-end-1em75 { margin-bottom: 1.75em; }
.vrtl .m-end-2em   { margin-bottom: 2.00em; }
.vrtl .m-end-2em50 { margin-bottom: 2.50em; }
.vrtl .m-end-3em   { margin-bottom: 3.00em; }
.vrtl .m-end-4em   { margin-bottom: 4.00em; }
.vrtl .m-end-5em   { margin-bottom: 5.00em; }
.vrtl .m-end-5em25 { margin-bottom: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="m-end"] { margin-right: 0; } */
.hltr .vrtl .m-end-auto,
.hltr .vrtl .m-end-005per, .hltr .vrtl .m-end-010per, .hltr .vrtl .m-end-015per,
.hltr .vrtl .m-end-020per, .hltr .vrtl .m-end-025per, .hltr .vrtl .m-end-030per,
.hltr .vrtl .m-end-033per, .hltr .vrtl .m-end-040per, .hltr .vrtl .m-end-050per,
.hltr .vrtl .m-end-060per, .hltr .vrtl .m-end-067per, .hltr .vrtl .m-end-070per,
.hltr .vrtl .m-end-075per, .hltr .vrtl .m-end-080per, .hltr .vrtl .m-end-090per,
.hltr .vrtl .m-end-0em25,  .hltr .vrtl .m-end-0em50,  .hltr .vrtl .m-end-0em75,
.hltr .vrtl .m-end-1em,    .hltr .vrtl .m-end-1em25,  .hltr .vrtl .m-end-1em50,
.hltr .vrtl .m-end-1em75,  .hltr .vrtl .m-end-2em,    .hltr .vrtl .m-end-2em50,
.hltr .vrtl .m-end-3em,    .hltr .vrtl .m-end-4em,    .hltr .vrtl .m-end-5em,
.hltr .vrtl .m-end-5em25 {
  margin-right: 0;
}
/* .vrtl .hltr [class|="m-end"] { margin-bottom:  0; } */
.vrtl .hltr .m-end-auto,
.vrtl .hltr .m-end-005per, .vrtl .hltr .m-end-010per, .vrtl .hltr .m-end-015per,
.vrtl .hltr .m-end-020per, .vrtl .hltr .m-end-025per, .vrtl .hltr .m-end-030per,
.vrtl .hltr .m-end-033per, .vrtl .hltr .m-end-040per, .vrtl .hltr .m-end-050per,
.vrtl .hltr .m-end-060per, .vrtl .hltr .m-end-067per, .vrtl .hltr .m-end-070per,
.vrtl .hltr .m-end-075per, .vrtl .hltr .m-end-080per, .vrtl .hltr .m-end-090per,
.vrtl .hltr .m-end-0em25,  .vrtl .hltr .m-end-0em50,  .vrtl .hltr .m-end-0em75,
.vrtl .hltr .m-end-1em,    .vrtl .hltr .m-end-1em25,  .vrtl .hltr .m-end-1em50,
.vrtl .hltr .m-end-1em75,  .vrtl .hltr .m-end-2em,    .vrtl .hltr .m-end-2em50,
.vrtl .hltr .m-end-3em,    .vrtl .hltr .m-end-4em,    .vrtl .hltr .m-end-5em,
.vrtl .hltr .m-end-5em25 {
  margin-bottom: 0;
}


/* 行前方マージン：横組み用 */
.hltr .m-before-auto   { margin-top: auto; }
.hltr .m-before-0,
.hltr .m-before-0em,
.hltr .m-before-000per { margin-top: 0; }

/* ％指定 */
.hltr .m-before-005per { margin-top:  5%; }
.hltr .m-before-010per { margin-top: 10%; }
.hltr .m-before-015per { margin-top: 15%; }
.hltr .m-before-020per { margin-top: 20%; }
.hltr .m-before-025per { margin-top: 25%; }
.hltr .m-before-030per { margin-top: 30%; }
.hltr .m-before-033per { margin-top: 33%; }
.hltr .m-before-040per { margin-top: 40%; }
.hltr .m-before-050per { margin-top: 50%; }
.hltr .m-before-060per { margin-top: 60%; }
.hltr .m-before-067per { margin-top: 67%; }
.hltr .m-before-070per { margin-top: 70%; }
.hltr .m-before-075per { margin-top: 75%; }
.hltr .m-before-080per { margin-top: 80%; }
.hltr .m-before-090per { margin-top: 90%; }

/* 文字数指定 */
.hltr .m-before-0em25 { margin-top: 0.25em; }
.hltr .m-before-0em50 { margin-top: 0.50em; }
.hltr .m-before-0em75 { margin-top: 0.75em; }
.hltr .m-before-1em   { margin-top: 1.00em; }
.hltr .m-before-1em25 { margin-top: 1.25em; }
.hltr .m-before-1em50 { margin-top: 1.50em; }
.hltr .m-before-1em75 { margin-top: 1.75em; }
.hltr .m-before-2em   { margin-top: 2.00em; }
.hltr .m-before-2em50 { margin-top: 2.50em; }
.hltr .m-before-3em   { margin-top: 3.00em; }
.hltr .m-before-4em   { margin-top: 4.00em; }
.hltr .m-before-5em   { margin-top: 5.00em; }
.hltr .m-before-5em25 { margin-top: 5.25em; }

/* 行前方マージン：縦組み用 */
.vrtl .m-before-auto   { margin-right: auto; }
.vrtl .m-before-0,
.vrtl .m-before-0em,
.vrtl .m-before-000per { margin-right: 0; }

/* ％指定 */
.vrtl .m-before-005per { margin-right:  5%; }
.vrtl .m-before-010per { margin-right: 10%; }
.vrtl .m-before-015per { margin-right: 15%; }
.vrtl .m-before-020per { margin-right: 20%; }
.vrtl .m-before-025per { margin-right: 25%; }
.vrtl .m-before-030per { margin-right: 30%; }
.vrtl .m-before-033per { margin-right: 33%; }
.vrtl .m-before-040per { margin-right: 40%; }
.vrtl .m-before-050per { margin-right: 50%; }
.vrtl .m-before-060per { margin-right: 60%; }
.vrtl .m-before-067per { margin-right: 67%; }
.vrtl .m-before-070per { margin-right: 70%; }
.vrtl .m-before-075per { margin-right: 75%; }
.vrtl .m-before-080per { margin-right: 80%; }
.vrtl .m-before-090per { margin-right: 90%; }

/* 文字数指定 */
.vrtl .m-before-0em25 { margin-right: 0.25em; }
.vrtl .m-before-0em50 { margin-right: 0.50em; }
.vrtl .m-before-0em75 { margin-right: 0.75em; }
.vrtl .m-before-1em   { margin-right: 1.00em; }
.vrtl .m-before-1em25 { margin-right: 1.25em; }
.vrtl .m-before-1em50 { margin-right: 1.50em; }
.vrtl .m-before-1em75 { margin-right: 1.75em; }
.vrtl .m-before-2em   { margin-right: 2.00em; }
.vrtl .m-before-2em50 { margin-right: 2.50em; }
.vrtl .m-before-3em   { margin-right: 3.00em; }
.vrtl .m-before-4em   { margin-right: 4.00em; }
.vrtl .m-before-5em   { margin-right: 5.00em; }
.vrtl .m-before-5em25 { margin-right: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="m-before"] { margin-top: 0; } */
.hltr .vrtl .m-before-auto,
.hltr .vrtl .m-before-005per, .hltr .vrtl .m-before-010per, .hltr .vrtl .m-before-015per,
.hltr .vrtl .m-before-020per, .hltr .vrtl .m-before-025per, .hltr .vrtl .m-before-030per,
.hltr .vrtl .m-before-033per, .hltr .vrtl .m-before-040per, .hltr .vrtl .m-before-050per,
.hltr .vrtl .m-before-060per, .hltr .vrtl .m-before-067per, .hltr .vrtl .m-before-070per,
.hltr .vrtl .m-before-075per, .hltr .vrtl .m-before-080per, .hltr .vrtl .m-before-090per,
.hltr .vrtl .m-before-0em25,  .hltr .vrtl .m-before-0em50,  .hltr .vrtl .m-before-0em75,
.hltr .vrtl .m-before-1em,    .hltr .vrtl .m-before-1em25,  .hltr .vrtl .m-before-1em50,
.hltr .vrtl .m-before-1em75,  .hltr .vrtl .m-before-2em,    .hltr .vrtl .m-before-2em50,
.hltr .vrtl .m-before-3em,    .hltr .vrtl .m-before-4em,    .hltr .vrtl .m-before-5em,
.hltr .vrtl .m-before-5em25 {
  margin-top: 0;
}
/* .vrtl .hltr [class|="m-before"] { margin-right:  0; } */
.vrtl .hltr .m-before-auto,
.vrtl .hltr .m-before-005per, .vrtl .hltr .m-before-010per, .vrtl .hltr .m-before-015per,
.vrtl .hltr .m-before-020per, .vrtl .hltr .m-before-025per, .vrtl .hltr .m-before-030per,
.vrtl .hltr .m-before-033per, .vrtl .hltr .m-before-040per, .vrtl .hltr .m-before-050per,
.vrtl .hltr .m-before-060per, .vrtl .hltr .m-before-067per, .vrtl .hltr .m-before-070per,
.vrtl .hltr .m-before-075per, .vrtl .hltr .m-before-080per, .vrtl .hltr .m-before-090per,
.vrtl .hltr .m-before-0em25,  .vrtl .hltr .m-before-0em50,  .vrtl .hltr .m-before-0em75,
.vrtl .hltr .m-before-1em,    .vrtl .hltr .m-before-1em25,  .vrtl .hltr .m-before-1em50,
.vrtl .hltr .m-before-1em75,  .vrtl .hltr .m-before-2em,    .vrtl .hltr .m-before-2em50,
.vrtl .hltr .m-before-3em,    .vrtl .hltr .m-before-4em,    .vrtl .hltr .m-before-5em,
.vrtl .hltr .m-before-5em25 {
  margin-right: 0;
}


/* 行後方マージン：横組み用 */
.hltr .m-after-auto   { margin-bottom: auto; }
.hltr .m-after-0,
.hltr .m-after-0em,
.hltr .m-after-000per { margin-bottom: 0; }

/* ％指定 */
.hltr .m-after-005per { margin-bottom:  5%; }
.hltr .m-after-010per { margin-bottom: 10%; }
.hltr .m-after-015per { margin-bottom: 15%; }
.hltr .m-after-020per { margin-bottom: 20%; }
.hltr .m-after-025per { margin-bottom: 25%; }
.hltr .m-after-030per { margin-bottom: 30%; }
.hltr .m-after-033per { margin-bottom: 33%; }
.hltr .m-after-040per { margin-bottom: 40%; }
.hltr .m-after-050per { margin-bottom: 50%; }
.hltr .m-after-060per { margin-bottom: 60%; }
.hltr .m-after-067per { margin-bottom: 67%; }
.hltr .m-after-070per { margin-bottom: 70%; }
.hltr .m-after-075per { margin-bottom: 75%; }
.hltr .m-after-080per { margin-bottom: 80%; }
.hltr .m-after-090per { margin-bottom: 90%; }

/* 文字数指定 */
.hltr .m-after-0em25 { margin-bottom: 0.25em; }
.hltr .m-after-0em50 { margin-bottom: 0.50em; }
.hltr .m-after-0em75 { margin-bottom: 0.75em; }
.hltr .m-after-1em   { margin-bottom: 1.00em; }
.hltr .m-after-1em25 { margin-bottom: 1.25em; }
.hltr .m-after-1em50 { margin-bottom: 1.50em; }
.hltr .m-after-1em75 { margin-bottom: 1.75em; }
.hltr .m-after-2em   { margin-bottom: 2.00em; }
.hltr .m-after-2em50 { margin-bottom: 2.50em; }
.hltr .m-after-3em   { margin-bottom: 3.00em; }
.hltr .m-after-4em   { margin-bottom: 4.00em; }
.hltr .m-after-5em   { margin-bottom: 5.00em; }
.hltr .m-after-5em25 { margin-bottom: 5.25em; }

/* 行後方マージン：縦組み用 */
.vrtl .m-after-auto   { margin-left: auto; }
.vrtl .m-after-0,
.vrtl .m-after-0em,
.vrtl .m-after-000per { margin-left: 0; }

/* ％指定 */
.vrtl .m-after-005per { margin-left:  5%; }
.vrtl .m-after-010per { margin-left: 10%; }
.vrtl .m-after-015per { margin-left: 15%; }
.vrtl .m-after-020per { margin-left: 20%; }
.vrtl .m-after-025per { margin-left: 25%; }
.vrtl .m-after-030per { margin-left: 30%; }
.vrtl .m-after-033per { margin-left: 33%; }
.vrtl .m-after-040per { margin-left: 40%; }
.vrtl .m-after-050per { margin-left: 50%; }
.vrtl .m-after-060per { margin-left: 60%; }
.vrtl .m-after-067per { margin-left: 67%; }
.vrtl .m-after-070per { margin-left: 70%; }
.vrtl .m-after-075per { margin-left: 75%; }
.vrtl .m-after-080per { margin-left: 80%; }
.vrtl .m-after-090per { margin-left: 90%; }

/* 文字数指定 */
.vrtl .m-after-0em25 { margin-left: 0.25em; }
.vrtl .m-after-0em50 { margin-left: 0.50em; }
.vrtl .m-after-0em75 { margin-left: 0.75em; }
.vrtl .m-after-1em   { margin-left: 1.00em; }
.vrtl .m-after-1em25 { margin-left: 1.25em; }
.vrtl .m-after-1em50 { margin-left: 1.50em; }
.vrtl .m-after-1em75 { margin-left: 1.75em; }
.vrtl .m-after-2em   { margin-left: 2.00em; }
.vrtl .m-after-2em50 { margin-left: 2.50em; }
.vrtl .m-after-3em   { margin-left: 3.00em; }
.vrtl .m-after-4em   { margin-left: 4.00em; }
.vrtl .m-after-5em   { margin-left: 5.00em; }
.vrtl .m-after-5em25 { margin-left: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="m-after"] { margin-bottom: 0; } */
.hltr .vrtl .m-after-auto,
.hltr .vrtl .m-after-005per, .hltr .vrtl .m-after-010per, .hltr .vrtl .m-after-015per,
.hltr .vrtl .m-after-020per, .hltr .vrtl .m-after-025per, .hltr .vrtl .m-after-030per,
.hltr .vrtl .m-after-033per, .hltr .vrtl .m-after-040per, .hltr .vrtl .m-after-050per,
.hltr .vrtl .m-after-060per, .hltr .vrtl .m-after-067per, .hltr .vrtl .m-after-070per,
.hltr .vrtl .m-after-075per, .hltr .vrtl .m-after-080per, .hltr .vrtl .m-after-090per,
.hltr .vrtl .m-after-0em25,  .hltr .vrtl .m-after-0em50,  .hltr .vrtl .m-after-0em75,
.hltr .vrtl .m-after-1em,    .hltr .vrtl .m-after-1em25,  .hltr .vrtl .m-after-1em50,
.hltr .vrtl .m-after-1em75,  .hltr .vrtl .m-after-2em,    .hltr .vrtl .m-after-2em50,
.hltr .vrtl .m-after-3em,    .hltr .vrtl .m-after-4em,    .hltr .vrtl .m-after-5em,
.hltr .vrtl .m-after-5em25 {
  margin-bottom: 0;
}
/* .vrtl .hltr [class|="m-after"] { margin-left:  0; } */
.vrtl .hltr .m-after-auto,
.vrtl .hltr .m-after-005per, .vrtl .hltr .m-after-010per, .vrtl .hltr .m-after-015per,
.vrtl .hltr .m-after-020per, .vrtl .hltr .m-after-025per, .vrtl .hltr .m-after-030per,
.vrtl .hltr .m-after-033per, .vrtl .hltr .m-after-040per, .vrtl .hltr .m-after-050per,
.vrtl .hltr .m-after-060per, .vrtl .hltr .m-after-067per, .vrtl .hltr .m-after-070per,
.vrtl .hltr .m-after-075per, .vrtl .hltr .m-after-080per, .vrtl .hltr .m-after-090per,
.vrtl .hltr .m-after-0em25,  .vrtl .hltr .m-after-0em50,  .vrtl .hltr .m-after-0em75,
.vrtl .hltr .m-after-1em,    .vrtl .hltr .m-after-1em25,  .vrtl .hltr .m-after-1em50,
.vrtl .hltr .m-after-1em75,  .vrtl .hltr .m-after-2em,    .vrtl .hltr .m-after-2em50,
.vrtl .hltr .m-after-3em,    .vrtl .hltr .m-after-4em,    .vrtl .hltr .m-after-5em,
.vrtl .hltr .m-after-5em25 {
  margin-left: 0;
}


/* 【論理方向指定】内側の余白（パディング）指定
---------------------------------------------------------------- */
/* 行頭パディング：横組み用 */
.hltr .p-start-0,
.hltr .p-start-0em,
.hltr .p-start-000per { padding-left: 0; }

/* ％指定 */
.hltr .p-start-005per { padding-left:  5%; }
.hltr .p-start-010per { padding-left: 10%; }
.hltr .p-start-015per { padding-left: 15%; }
.hltr .p-start-020per { padding-left: 20%; }
.hltr .p-start-025per { padding-left: 25%; }
.hltr .p-start-030per { padding-left: 30%; }
.hltr .p-start-033per { padding-left: 33%; }
.hltr .p-start-040per { padding-left: 40%; }
.hltr .p-start-050per { padding-left: 50%; }
.hltr .p-start-060per { padding-left: 60%; }
.hltr .p-start-067per { padding-left: 67%; }
.hltr .p-start-070per { padding-left: 70%; }
.hltr .p-start-075per { padding-left: 75%; }
.hltr .p-start-080per { padding-left: 80%; }
.hltr .p-start-090per { padding-left: 90%; }

/* 文字数指定 */
.hltr .p-start-0em25 { padding-left: 0.25em; }
.hltr .p-start-0em50 { padding-left: 0.50em; }
.hltr .p-start-0em75 { padding-left: 0.75em; }
.hltr .p-start-1em   { padding-left: 1.00em; }
.hltr .p-start-1em25 { padding-left: 1.25em; }
.hltr .p-start-1em50 { padding-left: 1.50em; }
.hltr .p-start-1em75 { padding-left: 1.75em; }
.hltr .p-start-2em   { padding-left: 2.00em; }
.hltr .p-start-2em50 { padding-left: 2.50em; }
.hltr .p-start-3em   { padding-left: 3.00em; }
.hltr .p-start-4em   { padding-left: 4.00em; }
.hltr .p-start-5em   { padding-left: 5.00em; }
.hltr .p-start-5em25 { padding-left: 5.25em; }

/* 行頭パディング：縦組み用 */
.vrtl .p-start-0,
.vrtl .p-start-0em,
.vrtl .p-start-000per { padding-top: 0; }

/* ％指定 */
.vrtl .p-start-005per { padding-top:  5%; }
.vrtl .p-start-010per { padding-top: 10%; }
.vrtl .p-start-015per { padding-top: 15%; }
.vrtl .p-start-020per { padding-top: 20%; }
.vrtl .p-start-025per { padding-top: 25%; }
.vrtl .p-start-030per { padding-top: 30%; }
.vrtl .p-start-033per { padding-top: 33%; }
.vrtl .p-start-040per { padding-top: 40%; }
.vrtl .p-start-050per { padding-top: 50%; }
.vrtl .p-start-060per { padding-top: 60%; }
.vrtl .p-start-067per { padding-top: 67%; }
.vrtl .p-start-070per { padding-top: 70%; }
.vrtl .p-start-075per { padding-top: 75%; }
.vrtl .p-start-080per { padding-top: 80%; }
.vrtl .p-start-090per { padding-top: 90%; }

/* 文字数指定 */
.vrtl .p-start-0em25 { padding-top: 0.25em; }
.vrtl .p-start-0em50 { padding-top: 0.50em; }
.vrtl .p-start-0em75 { padding-top: 0.75em; }
.vrtl .p-start-1em   { padding-top: 1.00em; }
.vrtl .p-start-1em25 { padding-top: 1.25em; }
.vrtl .p-start-1em50 { padding-top: 1.50em; }
.vrtl .p-start-1em75 { padding-top: 1.75em; }
.vrtl .p-start-2em   { padding-top: 2.00em; }
.vrtl .p-start-2em50 { padding-top: 2.50em; }
.vrtl .p-start-3em   { padding-top: 3.00em; }
.vrtl .p-start-4em   { padding-top: 4.00em; }
.vrtl .p-start-5em   { padding-top: 5.00em; }
.vrtl .p-start-5em25 { padding-top: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="p-start"] { padding-left: 0; } */
.hltr .vrtl .p-start-005per, .hltr .vrtl .p-start-010per, .hltr .vrtl .p-start-015per,
.hltr .vrtl .p-start-020per, .hltr .vrtl .p-start-025per, .hltr .vrtl .p-start-030per,
.hltr .vrtl .p-start-033per, .hltr .vrtl .p-start-040per, .hltr .vrtl .p-start-050per,
.hltr .vrtl .p-start-060per, .hltr .vrtl .p-start-067per, .hltr .vrtl .p-start-070per,
.hltr .vrtl .p-start-075per, .hltr .vrtl .p-start-080per, .hltr .vrtl .p-start-090per,
.hltr .vrtl .p-start-0em25,  .hltr .vrtl .p-start-0em50,  .hltr .vrtl .p-start-0em75,
.hltr .vrtl .p-start-1em,    .hltr .vrtl .p-start-1em25,  .hltr .vrtl .p-start-1em50,
.hltr .vrtl .p-start-1em75,  .hltr .vrtl .p-start-2em,    .hltr .vrtl .p-start-2em50,
.hltr .vrtl .p-start-3em,    .hltr .vrtl .p-start-4em,    .hltr .vrtl .p-start-5em,
.hltr .vrtl .p-start-5em25 {
  padding-left: 0;
}
/* .vrtl .hltr [class|="p-start"] { padding-top:  0; } */
.vrtl .hltr .p-start-005per, .vrtl .hltr .p-start-010per, .vrtl .hltr .p-start-015per,
.vrtl .hltr .p-start-020per, .vrtl .hltr .p-start-025per, .vrtl .hltr .p-start-030per,
.vrtl .hltr .p-start-033per, .vrtl .hltr .p-start-040per, .vrtl .hltr .p-start-050per,
.vrtl .hltr .p-start-060per, .vrtl .hltr .p-start-067per, .vrtl .hltr .p-start-070per,
.vrtl .hltr .p-start-075per, .vrtl .hltr .p-start-080per, .vrtl .hltr .p-start-090per,
.vrtl .hltr .p-start-0em25,  .vrtl .hltr .p-start-0em50,  .vrtl .hltr .p-start-0em75,
.vrtl .hltr .p-start-1em,    .vrtl .hltr .p-start-1em25,  .vrtl .hltr .p-start-1em50,
.vrtl .hltr .p-start-1em75,  .vrtl .hltr .p-start-2em,    .vrtl .hltr .p-start-2em50,
.vrtl .hltr .p-start-3em,    .vrtl .hltr .p-start-4em,    .vrtl .hltr .p-start-5em,
.vrtl .hltr .p-start-5em25 {
  padding-top: 0;
}


/* 行末パディング：横組み用 */
.hltr .p-end-0,
.hltr .p-end-0em,
.hltr .p-end-000per { padding-right: 0; }

/* ％指定 */
.hltr .p-end-005per { padding-right:  5%; }
.hltr .p-end-010per { padding-right: 10%; }
.hltr .p-end-015per { padding-right: 15%; }
.hltr .p-end-020per { padding-right: 20%; }
.hltr .p-end-025per { padding-right: 25%; }
.hltr .p-end-030per { padding-right: 30%; }
.hltr .p-end-033per { padding-right: 33%; }
.hltr .p-end-040per { padding-right: 40%; }
.hltr .p-end-050per { padding-right: 50%; }
.hltr .p-end-060per { padding-right: 60%; }
.hltr .p-end-067per { padding-right: 67%; }
.hltr .p-end-070per { padding-right: 70%; }
.hltr .p-end-075per { padding-right: 75%; }
.hltr .p-end-080per { padding-right: 80%; }
.hltr .p-end-090per { padding-right: 90%; }

/* 文字数指定 */
.hltr .p-end-0em25 { padding-right: 0.25em; }
.hltr .p-end-0em50 { padding-right: 0.50em; }
.hltr .p-end-0em75 { padding-right: 0.75em; }
.hltr .p-end-1em   { padding-right: 1.00em; }
.hltr .p-end-1em25 { padding-right: 1.25em; }
.hltr .p-end-1em50 { padding-right: 1.50em; }
.hltr .p-end-1em75 { padding-right: 1.75em; }
.hltr .p-end-2em   { padding-right: 2.00em; }
.hltr .p-end-2em50 { padding-right: 2.50em; }
.hltr .p-end-3em   { padding-right: 3.00em; }
.hltr .p-end-4em   { padding-right: 4.00em; }
.hltr .p-end-5em   { padding-right: 5.00em; }
.hltr .p-end-5em25 { padding-right: 5.25em; }

/* 行末パディング：縦組み用 */
.vrtl .p-end-0,
.vrtl .p-end-0em,
.vrtl .p-end-000per { padding-bottom: 0; }

/* ％指定 */
.vrtl .p-end-005per { padding-bottom:  5%; }
.vrtl .p-end-010per { padding-bottom: 10%; }
.vrtl .p-end-015per { padding-bottom: 15%; }
.vrtl .p-end-020per { padding-bottom: 20%; }
.vrtl .p-end-025per { padding-bottom: 25%; }
.vrtl .p-end-030per { padding-bottom: 30%; }
.vrtl .p-end-033per { padding-bottom: 33%; }
.vrtl .p-end-040per { padding-bottom: 40%; }
.vrtl .p-end-050per { padding-bottom: 50%; }
.vrtl .p-end-060per { padding-bottom: 60%; }
.vrtl .p-end-067per { padding-bottom: 67%; }
.vrtl .p-end-070per { padding-bottom: 70%; }
.vrtl .p-end-075per { padding-bottom: 75%; }
.vrtl .p-end-080per { padding-bottom: 80%; }
.vrtl .p-end-090per { padding-bottom: 90%; }

/* 文字数指定 */
.vrtl .p-end-0em25 { padding-bottom: 0.25em; }
.vrtl .p-end-0em50 { padding-bottom: 0.50em; }
.vrtl .p-end-0em75 { padding-bottom: 0.75em; }
.vrtl .p-end-1em   { padding-bottom: 1.00em; }
.vrtl .p-end-1em25 { padding-bottom: 1.25em; }
.vrtl .p-end-1em50 { padding-bottom: 1.50em; }
.vrtl .p-end-1em75 { padding-bottom: 1.75em; }
.vrtl .p-end-2em   { padding-bottom: 2.00em; }
.vrtl .p-end-2em50 { padding-bottom: 2.50em; }
.vrtl .p-end-3em   { padding-bottom: 3.00em; }
.vrtl .p-end-4em   { padding-bottom: 4.00em; }
.vrtl .p-end-5em   { padding-bottom: 5.00em; }
.vrtl .p-end-5em25 { padding-bottom: 5.25em; }

/* 字下げ：組み方向の入れ子対策 */
/* .hltr .vrtl [class|="p-end"] { padding-right: 0; } */
.hltr .vrtl .p-end-005per, .hltr .vrtl .p-end-010per, .hltr .vrtl .p-end-015per,
.hltr .vrtl .p-end-020per, .hltr .vrtl .p-end-025per, .hltr .vrtl .p-end-030per,
.hltr .vrtl .p-end-033per, .hltr .vrtl .p-end-040per, .hltr .vrtl .p-end-050per,
.hltr .vrtl .p-end-060per, .hltr .vrtl .p-end-067per, .hltr .vrtl .p-end-070per,
.hltr .vrtl .p-end-075per, .hltr .vrtl .p-end-080per, .hltr .vrtl .p-end-090per,
.hltr .vrtl .p-end-0em25,  .hltr .vrtl .p-end-0em50,  .hltr .vrtl .p-end-0em75,
.hltr .vrtl .p-end-1em,    .hltr .vrtl .p-end-1em25,  .hltr .vrtl .p-end-1em50,
.hltr .vrtl .p-end-1em75,  .hltr .vrtl .p-end-2em,    .hltr .vrtl .p-end-2em50,
.hltr .vrtl .p-end-3em,    .hltr .vrtl .p-end-4em,    .hltr .vrtl .p-end-5em,
.hltr .vrtl .p-end-5em25 {
  padding-right: 0;
}
/* .vrtl .hltr [class|="p-end"] { padding-bottom:  0; } */
.vrtl .hltr .p-end-005per, .vrtl .hltr .p-end-010per, .vrtl .hltr .p-end-015per,
.vrtl .hltr .p-end-020per, .vrtl .hltr .p-end-025per, .vrtl .hltr .p-end-030per,
.vrtl .hltr .p-end-033per, .vrtl .hltr .p-end-040per, .vrtl .hltr .p-end-050per,
.vrtl .hltr .p-end-060per, .vrtl .hltr .p-end-067per, .vrtl .hltr .p-end-070per,
.vrtl .hltr .p-end-075per, .vrtl .hltr .p-end-080per, .vrtl .hltr .p-end-090per,
.vrtl .hltr .p-end-0em25,  .vrtl .hltr .p-end-0em50,  .vrtl .hltr .p-end-0em75,
.vrtl .hltr .p-end-1em,    .vrtl .hltr .p-end-1em25,  .vrtl .hltr .p-end-1em50,
.vrtl .hltr .p-end-1em75,  .vrtl .hltr .p-end-2em,    .vrtl .hltr .p-end-2em50,
.vrtl .hltr .p-end-3em,    .vrtl .hltr .p-end-4em,    .vrtl .hltr .p-end-5em,
.vrtl .hltr .p-end-5em25 {
  padding-bottom: 0;
}


/* 行前方パディング：横組み用 */
.hltr .p-before-0,
.hltr .p-before-0em,
.hltr .p-before-000per { padding-top: 0; }

/* ％指定 */
.hltr .p-before-005per { padding-top:  5%; }
.hltr .p-before-010per { padding-top: 10%; }
.hltr .p-before-015per { padding-top: 15%; }
.hltr .p-before-020per { padding-top: 20%; }
.hltr .p-before-025per { padding-top: 25%; }
.hltr .p-before-030per { padding-top: 30%; }
.hltr .p-before-033per { padding-top: 33%; }
.hltr .p-before-040per { padding-top: 40%; }
.hltr .p-before-050per { padding-top: 50%; }
.hltr .p-before-060per { padding-top: 60%; }
.hltr .p-before-067per { padding-top: 67%; }
.hltr .p-before-070per { padding-top: 70%; }
.hltr .p-before-075per { padding-top: 75%; }
.hltr .p-before-080per { padding-top: 80%; }
.hltr .p-before-090per { padding-top: 90%; }

/* 文字数指定 */
.hltr .p-before-0em25 { padding-top: 0.25em; }
.hltr .p-before-0em50 { padding-top: 0.50em; }
.hltr .p-before-0em75 { padding-top: 0.75em; }
.hltr .p-before-1em   { padding-top: 1.00em; }
.hltr .p-before-1em25 { padding-top: 1.25em; }
.hltr .p-before-1em50 { padding-top: 1.50em; }
.hltr .p-before-1em75 { padding-top: 1.75em; }
.hltr .p-before-2em   { padding-top: 2.00em; }
.hltr .p-before-2em50 { padding-top: 2.50em; }
.hltr .p-before-3em   { padding-top: 3.00em; }
.hltr .p-before-4em   { padding-top: 4.00em; }
.hltr .p-before-5em   { padding-top: 5.00em; }
.hltr .p-before-5em25 { padding-top: 5.25em; }

/* 行前方パディング：縦組み用 */
.vrtl .p-before-0,
.vrtl .p-before-0em,
.vrtl .p-before-000per { padding-right: 0; }

/* ％指定 */
.vrtl .p-before-005per { padding-right:  5%; }
.vrtl .p-before-010per { padding-right: 10%; }
.vrtl .p-before-015per { padding-right: 15%; }
.vrtl .p-before-020per { padding-right: 20%; }
.vrtl .p-before-025per { padding-right: 25%; }
.vrtl .p-before-030per { padding-right: 30%; }
.vrtl .p-before-033per { padding-right: 33%; }
.vrtl .p-before-040per { padding-right: 40%; }
.vrtl .p-before-050per { padding-right: 50%; }
.vrtl .p-before-060per { padding-right: 60%; }
.vrtl .p-before-067per { padding-right: 67%; }
.vrtl .p-before-070per { padding-right: 70%; }
.vrtl .p-before-075per { padding-right: 75%; }
.vrtl .p-before-080per { padding-right: 80%; }
.vrtl .p-before-090per { padding-right: 90%; }

/* 文字数指定 */
.vrtl .p-before-0em25 { padding-right: 0.25em; }
.vrtl .p-before-0em50 { padding-right: 0.50em; }
.vrtl .p-before-0em75 { padding-right: 0.75em; }
.vrtl .p-before-1em   { padding-right: 1.00em; }
.vrtl .p-before-1em25 { padding-right: 1.25em; }
.vrtl .p-before-1em50 { padding-right: 1.50em; }
.vrtl .p-before-1em75 { padding-right: 1.75em; }
.vrtl .p-before-2em   { padding-right: 2.00em; }
.vrtl .p-before-2em50 { padding-right: 2.50em; }
.vrtl .p-before-3em   { padding-right: 3.00em; }
.vrtl .p-before-4em   { padding-right: 4.00em; }
.vrtl .p-before-5em   { padding-right: 5.00em; }
.vrtl .p-before-5em25 { padding-right: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="p-before"] { padding-top: 0; } */
.hltr .vrtl .p-before-005per, .hltr .vrtl .p-before-010per, .hltr .vrtl .p-before-015per,
.hltr .vrtl .p-before-020per, .hltr .vrtl .p-before-025per, .hltr .vrtl .p-before-030per,
.hltr .vrtl .p-before-033per, .hltr .vrtl .p-before-040per, .hltr .vrtl .p-before-050per,
.hltr .vrtl .p-before-060per, .hltr .vrtl .p-before-067per, .hltr .vrtl .p-before-070per,
.hltr .vrtl .p-before-075per, .hltr .vrtl .p-before-080per, .hltr .vrtl .p-before-090per,
.hltr .vrtl .p-before-0em25,  .hltr .vrtl .p-before-0em50,  .hltr .vrtl .p-before-0em75,
.hltr .vrtl .p-before-1em,    .hltr .vrtl .p-before-1em25,  .hltr .vrtl .p-before-1em50,
.hltr .vrtl .p-before-1em75,  .hltr .vrtl .p-before-2em,    .hltr .vrtl .p-before-2em50,
.hltr .vrtl .p-before-3em,    .hltr .vrtl .p-before-4em,    .hltr .vrtl .p-before-5em,
.hltr .vrtl .p-before-5em25 {
  padding-top: 0;
}
/* .vrtl .hltr [class|="p-before"] { padding-right:  0; } */
.vrtl .hltr .p-before-005per, .vrtl .hltr .p-before-010per, .vrtl .hltr .p-before-015per,
.vrtl .hltr .p-before-020per, .vrtl .hltr .p-before-025per, .vrtl .hltr .p-before-030per,
.vrtl .hltr .p-before-033per, .vrtl .hltr .p-before-040per, .vrtl .hltr .p-before-050per,
.vrtl .hltr .p-before-060per, .vrtl .hltr .p-before-067per, .vrtl .hltr .p-before-070per,
.vrtl .hltr .p-before-075per, .vrtl .hltr .p-before-080per, .vrtl .hltr .p-before-090per,
.vrtl .hltr .p-before-0em25,  .vrtl .hltr .p-before-0em50,  .vrtl .hltr .p-before-0em75,
.vrtl .hltr .p-before-1em,    .vrtl .hltr .p-before-1em25,  .vrtl .hltr .p-before-1em50,
.vrtl .hltr .p-before-1em75,  .vrtl .hltr .p-before-2em,    .vrtl .hltr .p-before-2em50,
.vrtl .hltr .p-before-3em,    .vrtl .hltr .p-before-4em,    .vrtl .hltr .p-before-5em,
.vrtl .hltr .p-before-5em25 {
  padding-right: 0;
}


/* 行後方パディング：横組み用 */
.hltr .p-after-0,
.hltr .p-after-0em,
.hltr .p-after-000per { padding-bottom: 0; }

/* ％指定 */
.hltr .p-after-005per { padding-bottom:  5%; }
.hltr .p-after-010per { padding-bottom: 10%; }
.hltr .p-after-015per { padding-bottom: 15%; }
.hltr .p-after-020per { padding-bottom: 20%; }
.hltr .p-after-025per { padding-bottom: 25%; }
.hltr .p-after-030per { padding-bottom: 30%; }
.hltr .p-after-033per { padding-bottom: 33%; }
.hltr .p-after-040per { padding-bottom: 40%; }
.hltr .p-after-050per { padding-bottom: 50%; }
.hltr .p-after-060per { padding-bottom: 60%; }
.hltr .p-after-067per { padding-bottom: 67%; }
.hltr .p-after-070per { padding-bottom: 70%; }
.hltr .p-after-075per { padding-bottom: 75%; }
.hltr .p-after-080per { padding-bottom: 80%; }
.hltr .p-after-090per { padding-bottom: 90%; }

/* 文字数指定 */
.hltr .p-after-0em25 { padding-bottom: 0.25em; }
.hltr .p-after-0em50 { padding-bottom: 0.50em; }
.hltr .p-after-0em75 { padding-bottom: 0.75em; }
.hltr .p-after-1em   { padding-bottom: 1.00em; }
.hltr .p-after-1em25 { padding-bottom: 1.25em; }
.hltr .p-after-1em50 { padding-bottom: 1.50em; }
.hltr .p-after-1em75 { padding-bottom: 1.75em; }
.hltr .p-after-2em   { padding-bottom: 2.00em; }
.hltr .p-after-2em50 { padding-bottom: 2.50em; }
.hltr .p-after-3em   { padding-bottom: 3.00em; }
.hltr .p-after-4em   { padding-bottom: 4.00em; }
.hltr .p-after-5em   { padding-bottom: 5.00em; }
.hltr .p-after-5em25 { padding-bottom: 5.25em; }

/* 行後方パディング：縦組み用 */
.vrtl .p-after-0,
.vrtl .p-after-0em,
.vrtl .p-after-000per { padding-left: 0; }

/* ％指定 */
.vrtl .p-after-005per { padding-left:  5%; }
.vrtl .p-after-010per { padding-left: 10%; }
.vrtl .p-after-015per { padding-left: 15%; }
.vrtl .p-after-020per { padding-left: 20%; }
.vrtl .p-after-025per { padding-left: 25%; }
.vrtl .p-after-030per { padding-left: 30%; }
.vrtl .p-after-033per { padding-left: 33%; }
.vrtl .p-after-040per { padding-left: 40%; }
.vrtl .p-after-050per { padding-left: 50%; }
.vrtl .p-after-060per { padding-left: 60%; }
.vrtl .p-after-067per { padding-left: 67%; }
.vrtl .p-after-070per { padding-left: 70%; }
.vrtl .p-after-075per { padding-left: 75%; }
.vrtl .p-after-080per { padding-left: 80%; }
.vrtl .p-after-090per { padding-left: 90%; }

/* 文字数指定 */
.vrtl .p-after-0em25 { padding-left: 0.25em; }
.vrtl .p-after-0em50 { padding-left: 0.50em; }
.vrtl .p-after-0em75 { padding-left: 0.75em; }
.vrtl .p-after-1em   { padding-left: 1.00em; }
.vrtl .p-after-1em25 { padding-left: 1.25em; }
.vrtl .p-after-1em50 { padding-left: 1.50em; }
.vrtl .p-after-1em75 { padding-left: 1.75em; }
.vrtl .p-after-2em   { padding-left: 2.00em; }
.vrtl .p-after-2em50 { padding-left: 2.50em; }
.vrtl .p-after-3em   { padding-left: 3.00em; }
.vrtl .p-after-4em   { padding-left: 4.00em; }
.vrtl .p-after-5em   { padding-left: 5.00em; }
.vrtl .p-after-5em25 { padding-left: 5.25em; }

/* 組み方向の入れ子対策 */
/* .hltr .vrtl [class|="p-after"] { padding-bottom: 0; } */
.hltr .vrtl .p-after-005per, .hltr .vrtl .p-after-010per, .hltr .vrtl .p-after-015per,
.hltr .vrtl .p-after-020per, .hltr .vrtl .p-after-025per, .hltr .vrtl .p-after-030per,
.hltr .vrtl .p-after-033per, .hltr .vrtl .p-after-040per, .hltr .vrtl .p-after-050per,
.hltr .vrtl .p-after-060per, .hltr .vrtl .p-after-067per, .hltr .vrtl .p-after-070per,
.hltr .vrtl .p-after-075per, .hltr .vrtl .p-after-080per, .hltr .vrtl .p-after-090per,
.hltr .vrtl .p-after-0em25,  .hltr .vrtl .p-after-0em50,  .hltr .vrtl .p-after-0em75,
.hltr .vrtl .p-after-1em,    .hltr .vrtl .p-after-1em25,  .hltr .vrtl .p-after-1em50,
.hltr .vrtl .p-after-1em75,  .hltr .vrtl .p-after-2em,    .hltr .vrtl .p-after-2em50,
.hltr .vrtl .p-after-3em,    .hltr .vrtl .p-after-4em,    .hltr .vrtl .p-after-5em,
.hltr .vrtl .p-after-5em25 {
  padding-bottom: 0;
}
/* .vrtl .hltr [class|="p-after"] { padding-left:  0; } */
.vrtl .hltr .p-after-005per, .vrtl .hltr .p-after-010per, .vrtl .hltr .p-after-015per,
.vrtl .hltr .p-after-020per, .vrtl .hltr .p-after-025per, .vrtl .hltr .p-after-030per,
.vrtl .hltr .p-after-033per, .vrtl .hltr .p-after-040per, .vrtl .hltr .p-after-050per,
.vrtl .hltr .p-after-060per, .vrtl .hltr .p-after-067per, .vrtl .hltr .p-after-070per,
.vrtl .hltr .p-after-075per, .vrtl .hltr .p-after-080per, .vrtl .hltr .p-after-090per,
.vrtl .hltr .p-after-0em25,  .vrtl .hltr .p-after-0em50,  .vrtl .hltr .p-after-0em75,
.vrtl .hltr .p-after-1em,    .vrtl .hltr .p-after-1em25,  .vrtl .hltr .p-after-1em50,
.vrtl .hltr .p-after-1em75,  .vrtl .hltr .p-after-2em,    .vrtl .hltr .p-after-2em50,
.vrtl .hltr .p-after-3em,    .vrtl .hltr .p-after-4em,    .vrtl .hltr .p-after-5em,
.vrtl .hltr .p-after-5em25 {
  padding-left: 0;
}


/* 【論理方向指定】行長方向のサイズ
----------------------------------------------------------------
行長方向と行幅方向のサイズ指定は、固定値、最大値とも
同じ要素内では同時に利用できないので注意

※以下のように入れ子で対応は可能

<div class="measure-10em">
<div class="extent-5em25">
<p>内容</p>
</div>
</div>
---------------------------------------------------------------- */
.measure-auto { height: auto; width: auto; }

/* ％指定 */
/* 横組み用 */
.hltr .measure-010per, .vrtl .hltr .measure-010per { height: auto; width:  10%; }
.hltr .measure-020per, .vrtl .hltr .measure-020per { height: auto; width:  20%; }
.hltr .measure-025per, .vrtl .hltr .measure-025per { height: auto; width:  25%; }
.hltr .measure-030per, .vrtl .hltr .measure-030per { height: auto; width:  30%; }
.hltr .measure-033per, .vrtl .hltr .measure-033per { height: auto; width:  33%; }
.hltr .measure-040per, .vrtl .hltr .measure-040per { height: auto; width:  40%; }
.hltr .measure-050per, .vrtl .hltr .measure-050per { height: auto; width:  50%; }
.hltr .measure-060per, .vrtl .hltr .measure-060per { height: auto; width:  60%; }
.hltr .measure-067per, .vrtl .hltr .measure-067per { height: auto; width:  67%; }
.hltr .measure-070per, .vrtl .hltr .measure-070per { height: auto; width:  70%; }
.hltr .measure-075per, .vrtl .hltr .measure-075per { height: auto; width:  75%; }
.hltr .measure-080per, .vrtl .hltr .measure-080per { height: auto; width:  80%; }
.hltr .measure-090per, .vrtl .hltr .measure-090per { height: auto; width:  90%; }
.hltr .measure-100per, .vrtl .hltr .measure-100per { height: auto; width: 100%; }
/* 縦組み用 */
.vrtl .measure-010per, .hltr .vrtl .measure-010per { height:  10%; width: auto; }
.vrtl .measure-020per, .hltr .vrtl .measure-020per { height:  20%; width: auto; }
.vrtl .measure-025per, .hltr .vrtl .measure-025per { height:  25%; width: auto; }
.vrtl .measure-030per, .hltr .vrtl .measure-030per { height:  30%; width: auto; }
.vrtl .measure-033per, .hltr .vrtl .measure-033per { height:  33%; width: auto; }
.vrtl .measure-040per, .hltr .vrtl .measure-040per { height:  40%; width: auto; }
.vrtl .measure-050per, .hltr .vrtl .measure-050per { height:  50%; width: auto; }
.vrtl .measure-060per, .hltr .vrtl .measure-060per { height:  60%; width: auto; }
.vrtl .measure-067per, .hltr .vrtl .measure-067per { height:  67%; width: auto; }
.vrtl .measure-070per, .hltr .vrtl .measure-070per { height:  70%; width: auto; }
.vrtl .measure-075per, .hltr .vrtl .measure-075per { height:  75%; width: auto; }
.vrtl .measure-080per, .hltr .vrtl .measure-080per { height:  80%; width: auto; }
.vrtl .measure-090per, .hltr .vrtl .measure-090per { height:  90%; width: auto; }
.vrtl .measure-100per, .hltr .vrtl .measure-100per { height: 100%; width: auto; }

/* 文字数指定 */
/* 横組み用 */
.hltr .measure-0em25, .vrtl .hltr .measure-0em25 { height: auto; width:  0.25em; }
.hltr .measure-0em50, .vrtl .hltr .measure-0em50 { height: auto; width:  0.50em; }
.hltr .measure-0em75, .vrtl .hltr .measure-0em75 { height: auto; width:  0.75em; }
.hltr .measure-1em,   .vrtl .hltr .measure-1em   { height: auto; width:  1.00em; }
.hltr .measure-1em25, .vrtl .hltr .measure-1em25 { height: auto; width:  1.25em; }
.hltr .measure-1em50, .vrtl .hltr .measure-1em50 { height: auto; width:  1.50em; }
.hltr .measure-1em75, .vrtl .hltr .measure-1em75 { height: auto; width:  1.75em; }
.hltr .measure-2em,   .vrtl .hltr .measure-2em   { height: auto; width:  2.00em; }
.hltr .measure-2em50, .vrtl .hltr .measure-2em50 { height: auto; width:  2.50em; }
.hltr .measure-3em,   .vrtl .hltr .measure-3em   { height: auto; width:  3.00em; }
.hltr .measure-4em,   .vrtl .hltr .measure-4em   { height: auto; width:  4.00em; }
.hltr .measure-5em,   .vrtl .hltr .measure-5em   { height: auto; width:  5.00em; }
.hltr .measure-5em25, .vrtl .hltr .measure-5em25 { height: auto; width:  5.25em; }
.hltr .measure-6em,   .vrtl .hltr .measure-6em   { height: auto; width:  6.00em; }
.hltr .measure-7em,   .vrtl .hltr .measure-7em   { height: auto; width:  7.00em; }
.hltr .measure-8em,   .vrtl .hltr .measure-8em   { height: auto; width:  8.00em; }
.hltr .measure-8em75, .vrtl .hltr .measure-8em75 { height: auto; width:  8.75em; }
.hltr .measure-9em,   .vrtl .hltr .measure-9em   { height: auto; width:  9.00em; }
.hltr .measure-10em,  .vrtl .hltr .measure-10em  { height: auto; width: 10.00em; }
.hltr .measure-11em,  .vrtl .hltr .measure-11em  { height: auto; width: 11.00em; }
.hltr .measure-12em,  .vrtl .hltr .measure-12em  { height: auto; width: 12.00em; }
.hltr .measure-13em,  .vrtl .hltr .measure-13em  { height: auto; width: 13.00em; }
.hltr .measure-14em,  .vrtl .hltr .measure-14em  { height: auto; width: 14.00em; }
.hltr .measure-15em,  .vrtl .hltr .measure-15em  { height: auto; width: 15.00em; }
.hltr .measure-20em,  .vrtl .hltr .measure-20em  { height: auto; width: 20.00em; }
.hltr .measure-30em,  .vrtl .hltr .measure-30em  { height: auto; width: 30.00em; }
.hltr .measure-40em,  .vrtl .hltr .measure-40em  { height: auto; width: 40.00em; }
/* 縦組み用 */
.vrtl .measure-0em25, .hltr .vrtl .measure-0em25 { height:  0.25em; width: auto; }
.vrtl .measure-0em50, .hltr .vrtl .measure-0em50 { height:  0.50em; width: auto; }
.vrtl .measure-0em75, .hltr .vrtl .measure-0em75 { height:  0.75em; width: auto; }
.vrtl .measure-1em,   .hltr .vrtl .measure-1em   { height:  1.00em; width: auto; }
.vrtl .measure-1em25, .hltr .vrtl .measure-1em25 { height:  1.25em; width: auto; }
.vrtl .measure-1em50, .hltr .vrtl .measure-1em50 { height:  1.50em; width: auto; }
.vrtl .measure-1em75, .hltr .vrtl .measure-1em75 { height:  1.75em; width: auto; }
.vrtl .measure-2em,   .hltr .vrtl .measure-2em   { height:  2.00em; width: auto; }
.vrtl .measure-2em50, .hltr .vrtl .measure-2em50 { height:  2.50em; width: auto; }
.vrtl .measure-3em,   .hltr .vrtl .measure-3em   { height:  3.00em; width: auto; }
.vrtl .measure-4em,   .hltr .vrtl .measure-4em   { height:  4.00em; width: auto; }
.vrtl .measure-5em,   .hltr .vrtl .measure-5em   { height:  5.00em; width: auto; }
.vrtl .measure-5em25, .hltr .vrtl .measure-5em25 { height:  5.25em; width: auto; }
.vrtl .measure-6em,   .hltr .vrtl .measure-6em   { height:  6.00em; width: auto; }
.vrtl .measure-7em,   .hltr .vrtl .measure-7em   { height:  7.00em; width: auto; }
.vrtl .measure-8em,   .hltr .vrtl .measure-8em   { height:  8.00em; width: auto; }
.vrtl .measure-8em75, .hltr .vrtl .measure-8em75 { height:  8.75em; width: auto; }
.vrtl .measure-9em,   .hltr .vrtl .measure-9em   { height:  9.00em; width: auto; }
.vrtl .measure-10em,  .hltr .vrtl .measure-10em  { height: 10.00em; width: auto; }
.vrtl .measure-11em,  .hltr .vrtl .measure-11em  { height: 11.00em; width: auto; }
.vrtl .measure-12em,  .hltr .vrtl .measure-12em  { height: 12.00em; width: auto; }
.vrtl .measure-13em,  .hltr .vrtl .measure-13em  { height: 13.00em; width: auto; }
.vrtl .measure-14em,  .hltr .vrtl .measure-14em  { height: 14.00em; width: auto; }
.vrtl .measure-15em,  .hltr .vrtl .measure-15em  { height: 15.00em; width: auto; }
.vrtl .measure-20em,  .hltr .vrtl .measure-20em  { height: 20.00em; width: auto; }
.vrtl .measure-30em,  .hltr .vrtl .measure-30em  { height: 30.00em; width: auto; }
.vrtl .measure-40em,  .hltr .vrtl .measure-40em  { height: 40.00em; width: auto; }


/* 【論理方向指定】行長方向の最大サイズ
---------------------------------------------------------------- */
.max-measure-none { max-height: none; max-width: none; }

/* ％指定 */
/* 横組み用 */
.hltr .max-measure-010per, .vrtl .hltr .max-measure-010per { max-height: none; max-width:  10%; }
.hltr .max-measure-020per, .vrtl .hltr .max-measure-020per { max-height: none; max-width:  20%; }
.hltr .max-measure-025per, .vrtl .hltr .max-measure-025per { max-height: none; max-width:  25%; }
.hltr .max-measure-030per, .vrtl .hltr .max-measure-030per { max-height: none; max-width:  30%; }
.hltr .max-measure-033per, .vrtl .hltr .max-measure-033per { max-height: none; max-width:  33%; }
.hltr .max-measure-040per, .vrtl .hltr .max-measure-040per { max-height: none; max-width:  40%; }
.hltr .max-measure-050per, .vrtl .hltr .max-measure-050per { max-height: none; max-width:  50%; }
.hltr .max-measure-060per, .vrtl .hltr .max-measure-060per { max-height: none; max-width:  60%; }
.hltr .max-measure-067per, .vrtl .hltr .max-measure-067per { max-height: none; max-width:  67%; }
.hltr .max-measure-070per, .vrtl .hltr .max-measure-070per { max-height: none; max-width:  70%; }
.hltr .max-measure-075per, .vrtl .hltr .max-measure-075per { max-height: none; max-width:  75%; }
.hltr .max-measure-080per, .vrtl .hltr .max-measure-080per { max-height: none; max-width:  80%; }
.hltr .max-measure-090per, .vrtl .hltr .max-measure-090per { max-height: none; max-width:  90%; }
.hltr .max-measure-100per, .vrtl .hltr .max-measure-100per { max-height: none; max-width: 100%; }
/* 縦組み用 */
.vrtl .max-measure-010per, .hltr .vrtl .max-measure-010per { max-height:  10%; max-width: none; }
.vrtl .max-measure-020per, .hltr .vrtl .max-measure-020per { max-height:  20%; max-width: none; }
.vrtl .max-measure-025per, .hltr .vrtl .max-measure-025per { max-height:  25%; max-width: none; }
.vrtl .max-measure-030per, .hltr .vrtl .max-measure-030per { max-height:  30%; max-width: none; }
.vrtl .max-measure-033per, .hltr .vrtl .max-measure-033per { max-height:  33%; max-width: none; }
.vrtl .max-measure-040per, .hltr .vrtl .max-measure-040per { max-height:  40%; max-width: none; }
.vrtl .max-measure-050per, .hltr .vrtl .max-measure-050per { max-height:  50%; max-width: none; }
.vrtl .max-measure-060per, .hltr .vrtl .max-measure-060per { max-height:  60%; max-width: none; }
.vrtl .max-measure-067per, .hltr .vrtl .max-measure-067per { max-height:  67%; max-width: none; }
.vrtl .max-measure-070per, .hltr .vrtl .max-measure-070per { max-height:  70%; max-width: none; }
.vrtl .max-measure-075per, .hltr .vrtl .max-measure-075per { max-height:  75%; max-width: none; }
.vrtl .max-measure-080per, .hltr .vrtl .max-measure-080per { max-height:  80%; max-width: none; }
.vrtl .max-measure-090per, .hltr .vrtl .max-measure-090per { max-height:  90%; max-width: none; }
.vrtl .max-measure-100per, .hltr .vrtl .max-measure-100per { max-height: 100%; max-width: none; }

/* 文字数指定 */
/* 横組み用 */
.hltr .max-measure-0em25, .vrtl .hltr .max-measure-0em25 { max-height: none; max-width:  0.25em; }
.hltr .max-measure-0em50, .vrtl .hltr .max-measure-0em50 { max-height: none; max-width:  0.50em; }
.hltr .max-measure-0em75, .vrtl .hltr .max-measure-0em75 { max-height: none; max-width:  0.75em; }
.hltr .max-measure-1em,   .vrtl .hltr .max-measure-1em   { max-height: none; max-width:  1.00em; }
.hltr .max-measure-1em25, .vrtl .hltr .max-measure-1em25 { max-height: none; max-width:  1.25em; }
.hltr .max-measure-1em50, .vrtl .hltr .max-measure-1em50 { max-height: none; max-width:  1.50em; }
.hltr .max-measure-1em75, .vrtl .hltr .max-measure-1em75 { max-height: none; max-width:  1.75em; }
.hltr .max-measure-2em,   .vrtl .hltr .max-measure-2em   { max-height: none; max-width:  2.00em; }
.hltr .max-measure-2em50, .vrtl .hltr .max-measure-2em50 { max-height: none; max-width:  2.50em; }
.hltr .max-measure-3em,   .vrtl .hltr .max-measure-3em   { max-height: none; max-width:  3.00em; }
.hltr .max-measure-4em,   .vrtl .hltr .max-measure-4em   { max-height: none; max-width:  4.00em; }
.hltr .max-measure-5em,   .vrtl .hltr .max-measure-5em   { max-height: none; max-width:  5.00em; }
.hltr .max-measure-5em25, .vrtl .hltr .max-measure-5em25 { max-height: none; max-width:  5.25em; }
.hltr .max-measure-6em,   .vrtl .hltr .max-measure-6em   { max-height: none; max-width:  6.00em; }
.hltr .max-measure-7em,   .vrtl .hltr .max-measure-7em   { max-height: none; max-width:  7.00em; }
.hltr .max-measure-8em,   .vrtl .hltr .max-measure-8em   { max-height: none; max-width:  8.00em; }
.hltr .max-measure-8em75, .vrtl .hltr .max-measure-8em75 { max-height: none; max-width:  8.75em; }
.hltr .max-measure-9em,   .vrtl .hltr .max-measure-9em   { max-height: none; max-width:  9.00em; }
.hltr .max-measure-10em,  .vrtl .hltr .max-measure-10em  { max-height: none; max-width: 10.00em; }
.hltr .max-measure-11em,  .vrtl .hltr .max-measure-11em  { max-height: none; max-width: 11.00em; }
.hltr .max-measure-12em,  .vrtl .hltr .max-measure-12em  { max-height: none; max-width: 12.00em; }
.hltr .max-measure-13em,  .vrtl .hltr .max-measure-13em  { max-height: none; max-width: 13.00em; }
.hltr .max-measure-14em,  .vrtl .hltr .max-measure-14em  { max-height: none; max-width: 14.00em; }
.hltr .max-measure-15em,  .vrtl .hltr .max-measure-15em  { max-height: none; max-width: 15.00em; }
.hltr .max-measure-20em,  .vrtl .hltr .max-measure-20em  { max-height: none; max-width: 20.00em; }
.hltr .max-measure-30em,  .vrtl .hltr .max-measure-30em  { max-height: none; max-width: 30.00em; }
.hltr .max-measure-40em,  .vrtl .hltr .max-measure-40em  { max-height: none; max-width: 40.00em; }
/* 縦組み用 */
.vrtl .max-measure-0em25, .hltr .vrtl .max-measure-0em25 { max-height:  0.25em; max-width: none; }
.vrtl .max-measure-0em50, .hltr .vrtl .max-measure-0em50 { max-height:  0.50em; max-width: none; }
.vrtl .max-measure-0em75, .hltr .vrtl .max-measure-0em75 { max-height:  0.75em; max-width: none; }
.vrtl .max-measure-1em,   .hltr .vrtl .max-measure-1em   { max-height:  1.00em; max-width: none; }
.vrtl .max-measure-1em25, .hltr .vrtl .max-measure-1em25 { max-height:  1.25em; max-width: none; }
.vrtl .max-measure-1em50, .hltr .vrtl .max-measure-1em50 { max-height:  1.50em; max-width: none; }
.vrtl .max-measure-1em75, .hltr .vrtl .max-measure-1em75 { max-height:  1.75em; max-width: none; }
.vrtl .max-measure-2em,   .hltr .vrtl .max-measure-2em   { max-height:  2.00em; max-width: none; }
.vrtl .max-measure-2em50, .hltr .vrtl .max-measure-2em50 { max-height:  2.50em; max-width: none; }
.vrtl .max-measure-3em,   .hltr .vrtl .max-measure-3em   { max-height:  3.00em; max-width: none; }
.vrtl .max-measure-4em,   .hltr .vrtl .max-measure-4em   { max-height:  4.00em; max-width: none; }
.vrtl .max-measure-5em,   .hltr .vrtl .max-measure-5em   { max-height:  5.00em; max-width: none; }
.vrtl .max-measure-5em25, .hltr .vrtl .max-measure-5em25 { max-height:  5.25em; max-width: none; }
.vrtl .max-measure-6em,   .hltr .vrtl .max-measure-6em   { max-height:  6.00em; max-width: none; }
.vrtl .max-measure-7em,   .hltr .vrtl .max-measure-7em   { max-height:  7.00em; max-width: none; }
.vrtl .max-measure-8em,   .hltr .vrtl .max-measure-8em   { max-height:  8.00em; max-width: none; }
.vrtl .max-measure-8em75, .hltr .vrtl .max-measure-8em75 { max-height:  8.75em; max-width: none; }
.vrtl .max-measure-9em,   .hltr .vrtl .max-measure-9em   { max-height:  9.00em; max-width: none; }
.vrtl .max-measure-10em,  .hltr .vrtl .max-measure-10em  { max-height: 10.00em; max-width: none; }
.vrtl .max-measure-11em,  .hltr .vrtl .max-measure-11em  { max-height: 11.00em; max-width: none; }
.vrtl .max-measure-12em,  .hltr .vrtl .max-measure-12em  { max-height: 12.00em; max-width: none; }
.vrtl .max-measure-13em,  .hltr .vrtl .max-measure-13em  { max-height: 13.00em; max-width: none; }
.vrtl .max-measure-14em,  .hltr .vrtl .max-measure-14em  { max-height: 14.00em; max-width: none; }
.vrtl .max-measure-15em,  .hltr .vrtl .max-measure-15em  { max-height: 15.00em; max-width: none; }
.vrtl .max-measure-20em,  .hltr .vrtl .max-measure-20em  { max-height: 20.00em; max-width: none; }
.vrtl .max-measure-30em,  .hltr .vrtl .max-measure-30em  { max-height: 30.00em; max-width: none; }
.vrtl .max-measure-40em,  .hltr .vrtl .max-measure-40em  { max-height: 40.00em; max-width: none; }


/* 【論理方向指定】行幅方向のサイズ
---------------------------------------------------------------- */
.extent-auto { height: auto; width: auto; }

/* ％指定 */
/* 横組み用 */
.hltr .extent-010per, .vrtl .hltr .extent-010per { height:  10%; width: auto; }
.hltr .extent-020per, .vrtl .hltr .extent-020per { height:  20%; width: auto; }
.hltr .extent-025per, .vrtl .hltr .extent-025per { height:  25%; width: auto; }
.hltr .extent-030per, .vrtl .hltr .extent-030per { height:  30%; width: auto; }
.hltr .extent-033per, .vrtl .hltr .extent-033per { height:  33%; width: auto; }
.hltr .extent-040per, .vrtl .hltr .extent-040per { height:  40%; width: auto; }
.hltr .extent-050per, .vrtl .hltr .extent-050per { height:  50%; width: auto; }
.hltr .extent-060per, .vrtl .hltr .extent-060per { height:  60%; width: auto; }
.hltr .extent-067per, .vrtl .hltr .extent-067per { height:  67%; width: auto; }
.hltr .extent-070per, .vrtl .hltr .extent-070per { height:  70%; width: auto; }
.hltr .extent-075per, .vrtl .hltr .extent-075per { height:  75%; width: auto; }
.hltr .extent-080per, .vrtl .hltr .extent-080per { height:  80%; width: auto; }
.hltr .extent-090per, .vrtl .hltr .extent-090per { height:  90%; width: auto; }
.hltr .extent-100per, .vrtl .hltr .extent-100per { height: 100%; width: auto; }
/* 縦組み用 */
.vrtl .extent-010per, .hltr .vrtl .extent-010per { height: auto; width:  10%; }
.vrtl .extent-020per, .hltr .vrtl .extent-020per { height: auto; width:  20%; }
.vrtl .extent-025per, .hltr .vrtl .extent-025per { height: auto; width:  25%; }
.vrtl .extent-030per, .hltr .vrtl .extent-030per { height: auto; width:  30%; }
.vrtl .extent-033per, .hltr .vrtl .extent-033per { height: auto; width:  33%; }
.vrtl .extent-040per, .hltr .vrtl .extent-040per { height: auto; width:  40%; }
.vrtl .extent-050per, .hltr .vrtl .extent-050per { height: auto; width:  50%; }
.vrtl .extent-060per, .hltr .vrtl .extent-060per { height: auto; width:  60%; }
.vrtl .extent-067per, .hltr .vrtl .extent-067per { height: auto; width:  67%; }
.vrtl .extent-070per, .hltr .vrtl .extent-070per { height: auto; width:  70%; }
.vrtl .extent-075per, .hltr .vrtl .extent-075per { height: auto; width:  75%; }
.vrtl .extent-080per, .hltr .vrtl .extent-080per { height: auto; width:  80%; }
.vrtl .extent-090per, .hltr .vrtl .extent-090per { height: auto; width:  90%; }
.vrtl .extent-100per, .hltr .vrtl .extent-100per { height: auto; width: 100%; }

/* 文字数指定 */
/* 横組み用 */
.hltr .extent-0em25, .vrtl .hltr .extent-0em25 { height:  0.25em; width: auto; }
.hltr .extent-0em50, .vrtl .hltr .extent-0em50 { height:  0.50em; width: auto; }
.hltr .extent-0em75, .vrtl .hltr .extent-0em75 { height:  0.75em; width: auto; }
.hltr .extent-1em,   .vrtl .hltr .extent-1em   { height:  1.00em; width: auto; }
.hltr .extent-1em25, .vrtl .hltr .extent-1em25 { height:  1.25em; width: auto; }
.hltr .extent-1em50, .vrtl .hltr .extent-1em50 { height:  1.50em; width: auto; }
.hltr .extent-1em75, .vrtl .hltr .extent-1em75 { height:  1.75em; width: auto; }
.hltr .extent-2em,   .vrtl .hltr .extent-2em   { height:  2.00em; width: auto; }
.hltr .extent-2em50, .vrtl .hltr .extent-2em50 { height:  2.50em; width: auto; }
.hltr .extent-3em,   .vrtl .hltr .extent-3em   { height:  3.00em; width: auto; }
.hltr .extent-4em,   .vrtl .hltr .extent-4em   { height:  4.00em; width: auto; }
.hltr .extent-5em,   .vrtl .hltr .extent-5em   { height:  5.00em; width: auto; }
.hltr .extent-5em25, .vrtl .hltr .extent-5em25 { height:  5.25em; width: auto; }
.hltr .extent-6em,   .vrtl .hltr .extent-6em   { height:  6.00em; width: auto; }
.hltr .extent-7em,   .vrtl .hltr .extent-7em   { height:  7.00em; width: auto; }
.hltr .extent-8em,   .vrtl .hltr .extent-8em   { height:  8.00em; width: auto; }
.hltr .extent-8em75, .vrtl .hltr .extent-8em75 { height:  8.75em; width: auto; }
.hltr .extent-9em,   .vrtl .hltr .extent-9em   { height:  9.00em; width: auto; }
.hltr .extent-10em,  .vrtl .hltr .extent-10em  { height: 10.00em; width: auto; }
.hltr .extent-11em,  .vrtl .hltr .extent-11em  { height: 11.00em; width: auto; }
.hltr .extent-12em,  .vrtl .hltr .extent-12em  { height: 12.00em; width: auto; }
.hltr .extent-13em,  .vrtl .hltr .extent-13em  { height: 13.00em; width: auto; }
.hltr .extent-14em,  .vrtl .hltr .extent-14em  { height: 14.00em; width: auto; }
.hltr .extent-15em,  .vrtl .hltr .extent-15em  { height: 15.00em; width: auto; }
.hltr .extent-20em,  .vrtl .hltr .extent-20em  { height: 20.00em; width: auto; }
.hltr .extent-30em,  .vrtl .hltr .extent-30em  { height: 30.00em; width: auto; }
.hltr .extent-40em,  .vrtl .hltr .extent-40em  { height: 40.00em; width: auto; }
/* 縦組み用 */
.vrtl .extent-0em25, .hltr .vrtl .extent-0em25 { height: auto; width:  0.25em; }
.vrtl .extent-0em50, .hltr .vrtl .extent-0em50 { height: auto; width:  0.50em; }
.vrtl .extent-0em75, .hltr .vrtl .extent-0em75 { height: auto; width:  0.75em; }
.vrtl .extent-1em,   .hltr .vrtl .extent-1em   { height: auto; width:  1.00em; }
.vrtl .extent-1em25, .hltr .vrtl .extent-1em25 { height: auto; width:  1.25em; }
.vrtl .extent-1em50, .hltr .vrtl .extent-1em50 { height: auto; width:  1.50em; }
.vrtl .extent-1em75, .hltr .vrtl .extent-1em75 { height: auto; width:  1.75em; }
.vrtl .extent-2em,   .hltr .vrtl .extent-2em   { height: auto; width:  2.00em; }
.vrtl .extent-2em50, .hltr .vrtl .extent-2em50 { height: auto; width:  2.50em; }
.vrtl .extent-3em,   .hltr .vrtl .extent-3em   { height: auto; width:  3.00em; }
.vrtl .extent-4em,   .hltr .vrtl .extent-4em   { height: auto; width:  4.00em; }
.vrtl .extent-5em,   .hltr .vrtl .extent-5em   { height: auto; width:  5.00em; }
.vrtl .extent-5em25, .hltr .vrtl .extent-5em25 { height: auto; width:  5.25em; }
.vrtl .extent-6em,   .hltr .vrtl .extent-6em   { height: auto; width:  6.00em; }
.vrtl .extent-7em,   .hltr .vrtl .extent-7em   { height: auto; width:  7.00em; }
.vrtl .extent-8em,   .hltr .vrtl .extent-8em   { height: auto; width:  8.00em; }
.vrtl .extent-8em75, .hltr .vrtl .extent-8em75 { height: auto; width:  8.75em; }
.vrtl .extent-9em,   .hltr .vrtl .extent-9em   { height: auto; width:  9.00em; }
.vrtl .extent-10em,  .hltr .vrtl .extent-10em  { height: auto; width: 10.00em; }
.vrtl .extent-11em,  .hltr .vrtl .extent-11em  { height: auto; width: 11.00em; }
.vrtl .extent-12em,  .hltr .vrtl .extent-12em  { height: auto; width: 12.00em; }
.vrtl .extent-13em,  .hltr .vrtl .extent-13em  { height: auto; width: 13.00em; }
.vrtl .extent-14em,  .hltr .vrtl .extent-14em  { height: auto; width: 14.00em; }
.vrtl .extent-15em,  .hltr .vrtl .extent-15em  { height: auto; width: 15.00em; }
.vrtl .extent-20em,  .hltr .vrtl .extent-20em  { height: auto; width: 20.00em; }
.vrtl .extent-30em,  .hltr .vrtl .extent-30em  { height: auto; width: 30.00em; }
.vrtl .extent-40em,  .hltr .vrtl .extent-40em  { height: auto; width: 40.00em; }


/* 【論理方向指定】行幅方向の最大サイズ
---------------------------------------------------------------- */
.max-extent-none { max-height: none; max-width: none; }

/* ％指定 */
/* 横組み用 */
.hltr .max-extent-010per, .vrtl .hltr .max-extent-010per { max-height:  10%; max-width: none; }
.hltr .max-extent-020per, .vrtl .hltr .max-extent-020per { max-height:  20%; max-width: none; }
.hltr .max-extent-025per, .vrtl .hltr .max-extent-025per { max-height:  25%; max-width: none; }
.hltr .max-extent-030per, .vrtl .hltr .max-extent-030per { max-height:  30%; max-width: none; }
.hltr .max-extent-033per, .vrtl .hltr .max-extent-033per { max-height:  33%; max-width: none; }
.hltr .max-extent-040per, .vrtl .hltr .max-extent-040per { max-height:  40%; max-width: none; }
.hltr .max-extent-050per, .vrtl .hltr .max-extent-050per { max-height:  50%; max-width: none; }
.hltr .max-extent-060per, .vrtl .hltr .max-extent-060per { max-height:  60%; max-width: none; }
.hltr .max-extent-067per, .vrtl .hltr .max-extent-067per { max-height:  67%; max-width: none; }
.hltr .max-extent-070per, .vrtl .hltr .max-extent-070per { max-height:  70%; max-width: none; }
.hltr .max-extent-075per, .vrtl .hltr .max-extent-075per { max-height:  75%; max-width: none; }
.hltr .max-extent-080per, .vrtl .hltr .max-extent-080per { max-height:  80%; max-width: none; }
.hltr .max-extent-090per, .vrtl .hltr .max-extent-090per { max-height:  90%; max-width: none; }
.hltr .max-extent-100per, .vrtl .hltr .max-extent-100per { max-height: 100%; max-width: none; }
/* 縦組み用 */
.vrtl .max-extent-010per, .hltr .vrtl .max-extent-010per { max-height: none; max-width:  10%; }
.vrtl .max-extent-020per, .hltr .vrtl .max-extent-020per { max-height: none; max-width:  20%; }
.vrtl .max-extent-025per, .hltr .vrtl .max-extent-025per { max-height: none; max-width:  25%; }
.vrtl .max-extent-030per, .hltr .vrtl .max-extent-030per { max-height: none; max-width:  30%; }
.vrtl .max-extent-033per, .hltr .vrtl .max-extent-033per { max-height: none; max-width:  33%; }
.vrtl .max-extent-040per, .hltr .vrtl .max-extent-040per { max-height: none; max-width:  40%; }
.vrtl .max-extent-050per, .hltr .vrtl .max-extent-050per { max-height: none; max-width:  50%; }
.vrtl .max-extent-060per, .hltr .vrtl .max-extent-060per { max-height: none; max-width:  60%; }
.vrtl .max-extent-067per, .hltr .vrtl .max-extent-067per { max-height: none; max-width:  67%; }
.vrtl .max-extent-070per, .hltr .vrtl .max-extent-070per { max-height: none; max-width:  70%; }
.vrtl .max-extent-075per, .hltr .vrtl .max-extent-075per { max-height: none; max-width:  75%; }
.vrtl .max-extent-080per, .hltr .vrtl .max-extent-080per { max-height: none; max-width:  80%; }
.vrtl .max-extent-090per, .hltr .vrtl .max-extent-090per { max-height: none; max-width:  90%; }
.vrtl .max-extent-100per, .hltr .vrtl .max-extent-100per { max-height: none; max-width: 100%; }

/* 文字数指定 */
/* 横組み用 */
.hltr .max-extent-0em25, .vrtl .hltr .max-extent-0em25 { max-height:  0.25em; max-width: none; }
.hltr .max-extent-0em50, .vrtl .hltr .max-extent-0em50 { max-height:  0.50em; max-width: none; }
.hltr .max-extent-0em75, .vrtl .hltr .max-extent-0em75 { max-height:  0.75em; max-width: none; }
.hltr .max-extent-1em,   .vrtl .hltr .max-extent-1em   { max-height:  1.00em; max-width: none; }
.hltr .max-extent-1em25, .vrtl .hltr .max-extent-1em25 { max-height:  1.25em; max-width: none; }
.hltr .max-extent-1em50, .vrtl .hltr .max-extent-1em50 { max-height:  1.50em; max-width: none; }
.hltr .max-extent-1em75, .vrtl .hltr .max-extent-1em75 { max-height:  1.75em; max-width: none; }
.hltr .max-extent-2em,   .vrtl .hltr .max-extent-2em   { max-height:  2.00em; max-width: none; }
.hltr .max-extent-2em50, .vrtl .hltr .max-extent-2em50 { max-height:  2.50em; max-width: none; }
.hltr .max-extent-3em,   .vrtl .hltr .max-extent-3em   { max-height:  3.00em; max-width: none; }
.hltr .max-extent-4em,   .vrtl .hltr .max-extent-4em   { max-height:  4.00em; max-width: none; }
.hltr .max-extent-5em,   .vrtl .hltr .max-extent-5em   { max-height:  5.00em; max-width: none; }
.hltr .max-extent-5em25, .vrtl .hltr .max-extent-5em25 { max-height:  5.25em; max-width: none; }
.hltr .max-extent-6em,   .vrtl .hltr .max-extent-6em   { max-height:  6.00em; max-width: none; }
.hltr .max-extent-7em,   .vrtl .hltr .max-extent-7em   { max-height:  7.00em; max-width: none; }
.hltr .max-extent-8em,   .vrtl .hltr .max-extent-8em   { max-height:  8.00em; max-width: none; }
.hltr .max-extent-8em75, .vrtl .hltr .max-extent-8em75 { max-height:  8.75em; max-width: none; }
.hltr .max-extent-9em,   .vrtl .hltr .max-extent-9em   { max-height:  9.00em; max-width: none; }
.hltr .max-extent-10em,  .vrtl .hltr .max-extent-10em  { max-height: 10.00em; max-width: none; }
.hltr .max-extent-11em,  .vrtl .hltr .max-extent-11em  { max-height: 11.00em; max-width: none; }
.hltr .max-extent-12em,  .vrtl .hltr .max-extent-12em  { max-height: 12.00em; max-width: none; }
.hltr .max-extent-13em,  .vrtl .hltr .max-extent-13em  { max-height: 13.00em; max-width: none; }
.hltr .max-extent-14em,  .vrtl .hltr .max-extent-14em  { max-height: 14.00em; max-width: none; }
.hltr .max-extent-15em,  .vrtl .hltr .max-extent-15em  { max-height: 15.00em; max-width: none; }
.hltr .max-extent-20em,  .vrtl .hltr .max-extent-20em  { max-height: 20.00em; max-width: none; }
.hltr .max-extent-30em,  .vrtl .hltr .max-extent-30em  { max-height: 30.00em; max-width: none; }
.hltr .max-extent-40em,  .vrtl .hltr .max-extent-40em  { max-height: 40.00em; max-width: none; }
/* 縦組み用 */
.vrtl .max-extent-0em25, .hltr .vrtl .max-extent-0em25 { max-height: none; max-width:  0.25em; }
.vrtl .max-extent-0em50, .hltr .vrtl .max-extent-0em50 { max-height: none; max-width:  0.50em; }
.vrtl .max-extent-0em75, .hltr .vrtl .max-extent-0em75 { max-height: none; max-width:  0.75em; }
.vrtl .max-extent-1em,   .hltr .vrtl .max-extent-1em   { max-height: none; max-width:  1.00em; }
.vrtl .max-extent-1em25, .hltr .vrtl .max-extent-1em25 { max-height: none; max-width:  1.25em; }
.vrtl .max-extent-1em50, .hltr .vrtl .max-extent-1em50 { max-height: none; max-width:  1.50em; }
.vrtl .max-extent-1em75, .hltr .vrtl .max-extent-1em75 { max-height: none; max-width:  1.75em; }
.vrtl .max-extent-2em,   .hltr .vrtl .max-extent-2em   { max-height: none; max-width:  2.00em; }
.vrtl .max-extent-2em50, .hltr .vrtl .max-extent-2em50 { max-height: none; max-width:  2.50em; }
.vrtl .max-extent-3em,   .hltr .vrtl .max-extent-3em   { max-height: none; max-width:  3.00em; }
.vrtl .max-extent-4em,   .hltr .vrtl .max-extent-4em   { max-height: none; max-width:  4.00em; }
.vrtl .max-extent-5em,   .hltr .vrtl .max-extent-5em   { max-height: none; max-width:  5.00em; }
.vrtl .max-extent-5em25, .hltr .vrtl .max-extent-5em25 { max-height: none; max-width:  5.25em; }
.vrtl .max-extent-6em,   .hltr .vrtl .max-extent-6em   { max-height: none; max-width:  6.00em; }
.vrtl .max-extent-7em,   .hltr .vrtl .max-extent-7em   { max-height: none; max-width:  7.00em; }
.vrtl .max-extent-8em,   .hltr .vrtl .max-extent-8em   { max-height: none; max-width:  8.00em; }
.vrtl .max-extent-8em75, .hltr .vrtl .max-extent-8em75 { max-height: none; max-width:  8.75em; }
.vrtl .max-extent-9em,   .hltr .vrtl .max-extent-9em   { max-height: none; max-width:  9.00em; }
.vrtl .max-extent-10em,  .hltr .vrtl .max-extent-10em  { max-height: none; max-width: 10.00em; }
.vrtl .max-extent-11em,  .hltr .vrtl .max-extent-11em  { max-height: none; max-width: 11.00em; }
.vrtl .max-extent-12em,  .hltr .vrtl .max-extent-12em  { max-height: none; max-width: 12.00em; }
.vrtl .max-extent-13em,  .hltr .vrtl .max-extent-13em  { max-height: none; max-width: 13.00em; }
.vrtl .max-extent-14em,  .hltr .vrtl .max-extent-14em  { max-height: none; max-width: 14.00em; }
.vrtl .max-extent-15em,  .hltr .vrtl .max-extent-15em  { max-height: none; max-width: 15.00em; }
.vrtl .max-extent-20em,  .hltr .vrtl .max-extent-20em  { max-height: none; max-width: 20.00em; }
.vrtl .max-extent-30em,  .hltr .vrtl .max-extent-30em  { max-height: none; max-width: 30.00em; }
.vrtl .max-extent-40em,  .hltr .vrtl .max-extent-40em  { max-height: none; max-width: 40.00em; }"""

    # --------------------------------------------------------------------------
    # クラス定数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(非公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラス変数の定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    #    @staticmethod
    #    def __static_method():
    #        pass

    # --------------------------------------------------------------------------
    # スタティックメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    #    @classmethod
    #    def __class_method(cls):
    #        pass

    # --------------------------------------------------------------------------
    # クラスメソッドの定義　(公開)
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # 特殊メソッドの定義
    # --------------------------------------------------------------------------

    def __init__(self):
        super().__init__()

    # ----------------------------------------------------------------------
    # インスタンス変数の定義 (非公開)
    # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    # インスタンス変数の定義 (公開)
    # ----------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # プロパティーの定義
    # --------------------------------------------------------------------------

    # --------------------------------------------------------------------------
    # インスタンスメソッドの定義　(非公開)
    # --------------------------------------------------------------------------

    def _generateFile(self, iPath, arcPath, header, bodys):

        if not os.path.exists(iPath):
            return

        # epubファイルに変換
        fname = __class__.__OUTPUT_FILENAME.format(
            header['writer']
            , header['title']
            , header['copies']
            , header['flag']
            , header['ncode']
            , header['date1'][0:10]
            , header['date2'][0:10])
        fname = _escapeFileName(fname)
        zipName = os.path.join(arcPath, fname)

        with zipfile.ZipFile(zipName, 'w', zipfile.ZIP_DEFLATED) as arc:

            # mimetypeファイルはZIPファイルの先頭に配置し無圧縮
            arc.writestr(
                "mimetype", "application/epub+zip", zipfile.ZIP_STORED)

            arc.writestr(
                "META-INF/container.xml"
                , """<?xml version="1.0"?>
<container
 version="1.0"
 xmlns="urn:oasis:names:tc:opendocument:xmlns:container"
>
<rootfiles>
<rootfile
 full-path="item/standard.opf"
 media-type="application/oebps-package+xml"
/>
</rootfiles>
</container>""")

            arc.writestr(
                "item/standard.opf"
                , self._makePackageDocument(iPath, header, bodys))

            arc.writestr(
                "item/navigation-documents.xhtml"
                , self._makeNavigationDocuments(iPath, header, bodys))

            arc.writestr(
                "item/style/book-style.css"
                , __class__.__CSS_BOOK)

            arc.writestr(
                "item/style/style-reset.css"
                , __class__.__CSS_RESET)

            arc.writestr(
                "item/style/style-standard.css"
                , __class__.__CSS_STANDARD)

            arc.writestr(
                "item/style/style-advance.css"
                , __class__.__CSS_ADVANCE)

            arc.writestr(
                "item/xhtml/p-summary.xhtml"
                , self._makeSummary(iPath, header, bodys))

            arc.writestr(
                "item/xhtml/p-titlepage.xhtml"
                , self._maketTitlePage(iPath, header, bodys))

            chap = ""
            for body in bodys:
                for key in ['note1', 'body', 'note2']:
                    if body[key]:
                        fname, data = self._makeChapterHtml(
                            iPath, header, body, key, chap != body['head1'])
                        arc.writestr("item/xhtml/{}".format(fname), data)

                        chap = body['head1']

            imgPath = os.path.join(iPath, "img")
            if os.path.exists(imgPath):
                files = os.listdir(imgPath)
                for f in files:
                    fname1 = os.path.join(imgPath, f)
                    fname2 = os.path.join("item/img", f)
                    arc.write(fname1, fname2)

    def _makePackageDocument(self, iPath, header, bodys):

        # 本文ファイルのリストを生成
        record = []
        record2 = []
        for body in bodys:
            if body['note1']:
                record.append(
                    "<item media-type=\"application/xhtml+xml\""
                    " id=\"p-{0}-1\""
                    " href=\"xhtml/p-{0}-1.xhtml\"/>\n".format(body['id']))
                record2.append(
                    "<itemref linear=\"yes\""
                    " idref=\"p-{0}-1\" />\n".format(body['id']))

            if body['body']:
                record.append(
                    "<item media-type=\"application/xhtml+xml\""
                    " id=\"p-{0}-2\""
                    " href=\"xhtml/p-{0}-2.xhtml\"/>\n".format(body['id']))
                record2.append(
                    "<itemref linear=\"yes\""
                    " idref=\"p-{0}-2\" />\n".format(body['id']))

            if body['note2']:
                record.append(
                    "<item media-type=\"application/xhtml+xml\""
                    " id=\"p-{0}-3\""
                    " href=\"xhtml/p-{0}-3.xhtml\"/>\n".format(body['id']))
                record2.append(
                    "<itemref linear=\"yes\""
                    " idref=\"p-{0}-3\" />\n".format(body['id']))

        # 画像ファイルのリストを生成
        record3 = []
        imgpath = os.path.join(iPath, "img")
        if os.path.exists(imgpath):
            for file in os.listdir(imgpath):
                fname, ext = os.path.splitext(file)
                ext = ext[1:]
                if "jpg" == ext:
                    ext = "jpeg"

                record3.append(
                    "<item media-type=\"img/{0}\""
                    " id=\"{1}\" href=\"img/{2}\"/>".format(
                        ext, fname, file))

        return r"""<?xml version="1.0" encoding="UTF-8"?>
<package
 xmlns="http://www.idpf.org/2007/opf"
 version="3.0"
 xml:lang="ja"
 unique-identifier="unique-id"
 prefix="ebpaj: http://www.ebpaj.jp/"
>

<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">

<!-- 作品名 -->
<dc:title id="title">{0}</dc:title>

<!-- 著者名 -->
<dc:creator id="creator01">{1}</dc:creator>
<meta refines="#creator01" property="role" scheme="marc:relators">aut</meta>
<meta refines="#creator01" property="display-seq">1</meta>

<!-- 言語 -->
<dc:language>ja</dc:language>

<!-- ファイルid -->
<!---
<dc:identifier id="unique-id">urn:uuid:707317b8-acab-46c2-a171-2da9afaec4bf</dc:identifier>
-->
<dc:identifier id="unique-id">narouTo.py-{2}</dc:identifier>

<!-- 更新日 -->
<meta property="dcterms:modified">{3}T{4}:00Z</meta>

<!-- etc. -->
<meta property="ebpaj:guide-version">1.1.3</meta>

</metadata>


<manifest>

<!-- navigation -->
<item media-type="application/xhtml+xml" id="toc" href="navigation-documents.xhtml" properties="nav"/>

<!-- style -->
<item media-type="text/css" id="book-style"     href="style/book-style.css"/>
<item media-type="text/css" id="style-reset"    href="style/style-reset.css"/>
<item media-type="text/css" id="style-standard" href="style/style-standard.css"/>
<item media-type="text/css" id="style-advance"  href="style/style-advance.css"/>
<!--
<item media-type="text/css" id="style-check"    href="style/style-check.css"/>
-->

<!-- image -->
<!--
<item media-type="image/jpeg" id="cover"           href="image/cover.jpg" properties="cover-image"/>
<item media-type="image/png"  id="logo-bunko"      href="image/logo-bunko.png"/>
<item media-type="image/gif"  id="headmark"        href="image/headmark.gif"/>
<item media-type="image/png"  id="gaiji-min-u728d" href="image/gaiji-min-u8fe6.png"/>
<item media-type="image/jpeg" id="img-001"         href="image/img-001.jpg"/>
<item media-type="image/png"  id="img-002"         href="image/img-002.png"/>
<item media-type="image/png"  id="img-003"         href="image/img-003.png"/>
<item media-type="image/png"  id="img-004"         href="image/img-004.png"/>
-->
{7}

<!-- xhtml -->
<item media-type="application/xhtml+xml" id="p-titlepage"   href="xhtml/p-titlepage.xhtml"/>
<item media-type="application/xhtml+xml" id="p-summary"     href="xhtml/p-summary.xhtml"/>
{5}</manifest>

<spine page-progression-direction="rtl">
<itemref linear="yes" idref="p-titlepage"  properties="page-spread-left"/>
<itemref linear="yes" idref="p-summary"/>
{6}</spine>

</package>""".format(
            header['title']
            , header['writer']
            , header['ncode']
            , header['date2'][0:10]
            , header['date2'][11:]
            , "".join(record)
            , "".join(record2)
            , "".join(record3))

    def _makeNavigationDocuments(self, iPath, header, bodys):

        temp = ""
        record = []
        for body in bodys:

            if temp != body['head1']:
                number = "2"
                if body['note1']:
                    number = "1"
                record.append(
                    "<li><a href=\"xhtml/p-{0}-{2}.xhtml\">{1}</a>"
                    "</li>\n".format(
                        body['id'], body['head1'], number))

            if body['note1']:
                record.append(
                    "<li><a href=\"xhtml/p-{0}-1.xhtml\">{1}(前書き)</a>"
                    "</li>\n".format(
                        body['id'], body['head2']))

            if body['body']:
                record.append(
                    "<li><a href=\"xhtml/p-{0}-2.xhtml\">{1}</a>"
                    "</li>\n".format(
                        body['id'], body['head2']))

            if body['note2']:
                record.append(
                    "<li><a href=\"xhtml/p-{0}-3.xhtml\">{1}(後書き)</a>"
                    "</li>\n".format(
                        body['id'], body['head2']))

            temp = body['head1']

        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:epub="http://www.idpf.org/2007/ops"
 xml:lang="ja"
>
<head>
<meta charset="UTF-8"/>
<title>{0}</title>
</head>
<body>

<nav epub:type="toc" id="toc">
<h1>{0}</h1>
<ol>
<li><a href="xhtml/p-titlepage.xhtml">表紙</a></li>
<li><a href="xhtml/p-summary.xhtml">あらすじ</a></li>
{1}</ol>
</nav>

</body>
</html>""".format(
            header['title']
            , "".join(record))

    def _makeSummary(self, iPath, header, bodys):

        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html
xmlns="http://www.w3.org/1999/xhtml"
xmlns:epub="http://www.idpf.org/2007/ops"
xml:lang="ja"
class="vrtl"
>
<head>
<meta charset="UTF-8"/>
<title>{0}</title>
<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>
</head>

<body class="p-text">
<div class="main">
<h1 class="oo-midashi" id="toc-000">あらすじ</h1>
<p><br/></p>
{1}</div>
</body>
</html>""".format(
            header['title']
            , header['summary'])

    def _maketTitlePage(self, iPath, header, bodys):
        return """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html
 xmlns="http://www.w3.org/1999/xhtml"
 xmlns:epub="http://www.idpf.org/2007/ops"
 xml:lang="ja"
 class="vrtl"
>
<head>
<meta charset="UTF-8"/>
<title>{0}</title>
<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>
</head>
<body class="p-titlepage">
<div class="main">

<div class="book-title">
<div class="book-title-main">
<p>{0}</p>
</div>
</div>

<p><br/></p>

<div class="author">
<p>作者　　　　　{1}</p>
</div>

<div class="label">
<p class="label-name">Ｎコード　　　{2}</p>
</div>
<div class="label">
<p class="label-name">掲載日　　　　{3}</p>
</div>
<div class="label">
<p class="label-name">最終話掲載日　{4}　{5}</p>
</div>

</div>
</body>
</html>""".format(
            header['title']
            , header['writer']
            , header['ncode']
            , header['date1']
            , header['date2']
            , header['flag'])

    __RE_CRLF_BR = re.compile(r'\n')
    __RE_HAIRU = re.compile(r"［＃（(.*?)）入る］")
    __RE_AOZORARUBY_TO_HTML = re.compile(r"｜(.*?)《(.*?)》")

    def _makeChapterHtml(self, iPath, header, body, key, flagChap):

        id = body['id']
        text = body[key]

        # ファイル名の生成
        note = ""
        if 'note1' == key:
            fname = "p-{0}-1.xhtml".format(body['id'])
            id = id + "-1"
            note = "（前書き）"

        elif 'body' == key:
            fname = "p-{0}-2.xhtml".format(body['id'])
            id = id + "-2"

        elif 'note2' == key:
            fname = "p-{0}-3.xhtml".format(body['id'])
            note = "（後書き）"
            id = id + "-3"

        # HTMLの特殊文字に変換
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;').replace('>', '&gt;')

        # 改行コードを<br/>に変換
        text = __class__.__RE_CRLF_BR.sub(r'<br />', text)

        # 青空文庫の画像タグをHTMLタグに変換
        match = __class__.__RE_HAIRU.search(text)
        while match:
            submatch = match.group()

            tmp = "<p><img class=\"fit\" src=\"../{0}\" alt=\"\"/></p>".format(
                match.group(1))

            text = text.replace(submatch, tmp)
            match = __class__.__RE_HAIRU.search(text)

        # 青空文庫のルビタグをHTMLタグに変換
        match = __class__.__RE_AOZORARUBY_TO_HTML.search(text)
        while match:
            submatch = match.group()

            tmp = "<ruby>" \
                  "<rb>{0}</rb><rp>（</rp><rt>{1}</rt><rp>）</rp>" \
                  "</ruby>".format(
                match.group(1), match.group(2))

            text = text.replace(submatch, tmp)
            match = __class__.__RE_AOZORARUBY_TO_HTML.search(text)

        # 見出し
        chap1 = ""
        if flagChap:
            chap1 = \
                "<h1 class=\"oo-midashi\"   id=\"toc-{1}\">{0}</h1>" \
                "\n<p><br/></p>\n".format(body['head1'], id)

            chap2 = "<h1 class=\"naka-midashi\">{0}{1}</h1>" \
                    "\n".format(body['head2'], note)
        else:
            chap2 = "<h1 class=\"naka-midashi\" id=\"toc-{1}\">{0}{2}</h1>" \
                    "\n".format(body['head2'], id, note)

        return fname, """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html
xmlns="http://www.w3.org/1999/xhtml"
xmlns:epub="http://www.idpf.org/2007/ops"
xml:lang="ja"
class="vrtl"
>
<head>
<meta charset="UTF-8"/>
<title>{0}</title>
<link rel="stylesheet" type="text/css" href="../style/book-style.css"/>
</head>

<body class="p-text">
<div class="main">
{1}
{2}
<p><br/></p>
{3}</div>
</body>
</html>""".format(
            header['title']
            , chap1
            , chap2
            , text)

    # --------------------------------------------------------------------------
    # インスタンスメソッドの定義　(公開)
    # --------------------------------------------------------------------------


# ------------------------------------------------------------------------------
# 関数の定義　(非公開)
# ------------------------------------------------------------------------------

def _escapeFileName(filename):
    r""" ファイル名をエスケープ

    ファイル名として使えない文字を代替文字に変換する

    Args:
        filename  処理対象のファイル名
    Returns:
        変換後のファイル名
    Raises:
        None
    """
    return filename.replace('/', '／').replace(':', '：')


def __startup():
    r""" メイン処理(コマンドラインから呼ばれる).

    各種パラメータを整理しメイン処理へ引き渡す。

    Args:
        None
    Returns:
        None
    Raises:
        None
    """
    try:
        # 引数パーサーの起動
        parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter
            , description=textwrap.dedent('''\
                「小説家になろう」サイトの小説をダウンロードをする.

                カレントパスにNコードのディレクトリを作成し、差分の管理も兼ねて各部ごとのテキストファイルを保存する.

                ダウンロード元サイトのUTF-8にてファイルを出力する.
                サーバー側の負荷を考えて1部取得毎にディレイ(1秒)を設定する.
                ''')
            , epilog=textwrap.dedent('''\

                更新の有無だけを取得し表示する (ダウンロードをしない)
                $ narouTo.py N9669BK N4251CR N6316BN
                　　or
                $ narouTo.py N9669BK N4251CR N6316BN --aozora -s

                ダウンロードをして、青空文庫形式TEXTファイルを生成する場合
                $ narouTo.py N9669BK N4251CR N6316BN --aozora

                ダウンロードをせず、取得済みのローカルデータから青空文庫形式TEXTファイルを生成する場合
                $ narouTo.py N9669BK N4251CR N6316BN --aozora --local


                Nコード例　 「小説家になろう」 http://syosetu.com/
                N9669BK     理不尽な孫の手　無職転生　- 異世界行ったら本気だす -
                N4251CR     理不尽な孫の手　無職転生　- 蛇足編 -
                N9038DG     理不尽な孫の手　ジョブレス・オブリージュ (無職転生)
                N3765DP     理不尽な孫の手　古龍の昔話 (無職転生)
                N6316BN     伏瀬　　　　　　転生したらスライムだった件
                N5240BC     七沢またり      死神を食べた少女
                N9815CK     七沢またり      火輪を抱いた少女
                N7551BN     七沢またり      勇者、或いは化物と呼ばれた少女
                N0722CA     七沢またり      ロゼッタは引き篭もりたい
                N0388EE     七沢またり      みつばものがたり
                N3730BN     紫炎            まのわ ～魔物倒す・能力奪う・私強くなる～
                N7903DT     紫炎            渚さんはガベージダンプを猫と歩む。
                N6112BX     紫炎            ロリババアロボ ー ６歳からの楽しい傭兵生活 ー
                N4830BU     香月　美夜      本好きの下剋上　～司書になるためには手段を選んでいられません～
                N7835CJ     香月　美夜      本好きの下剋上　SS置き場
                N2662CA     金髪ロリ文庫    田中のアトリエ　～年齢イコール彼女いない歴の錬金術師～
                N3556O      天酒之瓢        Knight's & Magic
                N2267BE     鼠色猫          Ｒｅ：ゼロから始める異世界生活
                N0624DL     もちもち物質    私は戦うダンジョンマスター
                N6006CW     棚架ユウ　　　　転生したら剣でした
                N0695BS     ラチム          かんすとっぷ！
                N1576CU     漂月　　　　　　人狼への転生、魔王の副官
                N8725K      橙乃ままれ　　　ログ・ホライズン
                N4402BD     丸山くがね　　　オーバーロード：前編
                N1839BD     丸山くがね　　　オーバーロード：後編
                N8462CR     アネコユサギ　　俺だけ帰れるクラス転移
                N3009BK     アネコユサギ　　盾の勇者の成り上がり
                N8497BJ     アネコユサギ　　ディメンションウェーブ
                N1443BP     冬原パトラ      異世界はスマートフォンとともに。
                N5966BH     氷純            詰みかけ転生領主の改革
                N7648BN     秋ぎつね        マギクラフト・マイスター
                N2710DB     江口　連        とんでもスキルで異世界放浪メシ
                N1406CR     花黒子          駆除人
                N2468CA     くろかた        治癒魔法の間違った使い方～戦場を駆ける回復要員～
                N8697CX     ブロッコリーライオン  聖者無双　～サラリーマン、異世界で生き残るために歩む道～
                N3406U      渡辺　恒彦      理想のヒモ生活
                N9902BN     愛七ひろ        デスマーチからはじまる異世界狂想曲
                N3378DG     雪月花          異世界ですが魔物栽培しています。
                N4908BV     ロッド　　　　　サモナーさんが行く
                N9442CW     ナハァト　　　　その者。のちに・・・
                N5530CF     CHIROLU 　　　　うちの娘の為ならば、俺はもしかしたら魔王も倒せるかもしれない 。
                N5258BX     あぶさん        蝉だって転生すれば竜になる
                N5011BC     支援BIS         辺境の老騎士
                N3250CL     わい            セブンス
                N1247P      Ceez            リアデイルの大地にて
                N8034BA     春野隠者        ゴブリンの王国

                N7975CR     馬場翁　　　　　蜘蛛ですが、なにか？
                N7031BS     十本スイ        金色の文字使い　～勇者四人に巻き込まれたユニークチート～
                N8802BQ     Ｙ．Ａ          八男って、それはないでしょう！
                N1103CL     マーブル        異世界でカボチャプリン

                narouTo.py N9669BK N4251CR N9038DG N3765DP N6316BN N5240BC N9815CK N7551BN N0722CA N0388EE N3730BN N7903DT N6112BX N4830BU N7835CJ N2662CA N3556O N2267BE N0624DL N6006CW N0695BS N1576CU N8725K N4402BD N1839BD N8462CR N3009BK N8497BJ N1443BP N5966BH N7648BN N2710DB N1406CR N2468CA N8697CX N3406U N9902BN N3378DG N4908BV N9442CW N5530CF N5258BX N5011BC N3250CL N1247P N8034BA N7975CR N7031BS N8802BQ N1103CL --aozora
                '''))
        parser.add_argument('ncode', nargs='+'
                            , help="「小説家になろう」のNコード")

        parser.add_argument('--aozora', action='store_true'
                            , help="青空文庫形式TEXTのファイルを生成する")

        parser.add_argument('--epub3', action='store_true'
                            , help="EPUB 3.0形式のファイルを生成する")

        parser.add_argument('-l', '--local', action='store_true'
                            , help="取得済みのローカルデータからファイルを生成する")

        parser.add_argument("-s", action='store_true'
                            , help="更新の有無だけを取得し表示する")

        parser.add_argument('--version', action='version'
                            , version="%(prog)s " + __PROGRAM_VERSION
                            , help="バージョン情報を表示する")

        args = parser.parse_args()

        novelGenerator = None
        if args.aozora:
            novelGenerator = AozoraNovelGenerator()

        elif args.epub3:
            novelGenerator = EPUB3NovelGenerator()

        else:
            args.s = True

        for ncode in args.ncode:
            ncode = ncode.upper()
            oPath = os.path.join(__PATH_WORK, ncode)

            result = None
            if not args.local:
                result = Downloader.getNovel(ncode, oPath, args.s)

            if args.local or result:
                novelGenerator.generate(oPath, __PATH_ARCHIVE)
    except:
        pass


# ------------------------------------------------------------------------------
# 関数の定義　(公開)
# ------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# メイン処理
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    __startup()