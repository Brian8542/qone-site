# -*- coding: utf-8 -*-
"""Marburg-style restructure for the main qone.kr site (2026-11-27).

Structure and design language follow marburg.com (navy top bar with dropdown menus,
search in the header, full-width slider, collection banner strip, "Digital Catalogs" /
"Sample" text+media rows, journal cards, light 3-column footer). All content, images and
copy are QONE's own; no Marburg assets are used.

What it does (idempotent, run from repo root:  python3 scripts/mb_skin.py):
  1. Keeps every legacy home page untouched in content: copies each language home to
     /{lang}/overview/ ("QONE at a glance") before the new home is built.
  2. Rebuilds the 4 language homes in the Marburg order, reusing the legacy H1, the
     retailer-logo (trust) section and the contact form section verbatim.
  3. Replaces header, mobile menu and footer on every main-site page (<header class="hd">),
     adds /assets/mb/mb.css + mb.js (menus, search, slider, carousel) and a site search index.
  Catalog sub-sites (/cushioni/, /yiwu/, /costco/) keep their own design.
"""
import json, re, os, html as H, pathlib, sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
BASE = "https://www.qone.kr"
e = lambda s: H.escape(str(s), quote=True)
LANGS = ["en", "ko", "ja", "ru"]
P = {"en": "", "ko": "/ko", "ja": "/ja", "ru": "/ru"}
MARK = 'class="mbh"'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Montserrat:wght@300;400;500;600&display=swap">')
ASSET_V = "20261127"

def U(l, path):  # localized internal url
    return P[l] + path

INQ = {"en": "/inquiry/", "ko": "/ko/inquiry/", "ja": "/ja/inquiry/", "ru": "/ru/inquiry/"}
COMPANY = {"en": "/company/", "ko": "/ko/company/", "ja": "/ja/company/", "ru": "/ru/overview/"}
FOAM = {"en": "/foam-brick-wall-panels/", "ko": "/ko/pomblock/", "ja": "/ja/cushion-renga/", "ru": "/ru/3d-paneli-pod-kirpich/"}
INSUL = {"en": "/insulation-wallpaper/", "ko": "/ko/gyeollo-dannyeol/", "ja": "/ja/ketsuro-taisaku/", "ru": "/ru/teploizolyacionnye-oboi/"}
CAMP = {"en": "/folding-camping-mat/", "ko": "/ko/chabak-camping-mat/", "ja": "/ja/camping-mat/", "ru": "/ru/turisticheskiy-kovrik/"}
OEMG = {"en": "/korea-foam-manufacturer/", "ko": "/ko/pe-foam-oem/", "ja": "/ja/korea-oem/", "ru": "/ru/proizvoditel-iz-korei/"}
CUSH = {"en": "/cushioni/catalog/", "ko": "/cushioni/ko/catalog/", "ja": "/cushioni/ja/catalog/", "ru": "/cushioni/catalog/"}
YIWU = {"en": "/yiwu/", "ko": "/yiwu/ko/", "ja": "/yiwu/ja/", "ru": "/yiwu/"}
DOCL = {"en": "EN", "ko": "KO", "ja": "JA", "ru": "EN"}
COVL = {"en": "en", "ko": "ko", "ja": "ja", "ru": "en"}

T = {
 "en": dict(
  nav=[("PRODUCTS", [("Collections", [("Foam Blocks", FOAM["en"]), ("Insulation Wallpaper", INSUL["en"]), ("Silk & Wall Décor", "/products/wall-decor/"), ("Camping & Living Mats", CAMP["en"]), ("All Products", "/products/")]),
                     ("Catalogs", [("CUSHIONI Catalog", CUSH["en"]), ("Value Retail Catalog", YIWU["en"]), ("Downloads", "/downloads/")])]),
       ("MANUFACTURING", [("Factory", [("Yeoju Factory", "/factory/"), ("OEM & Private Label", "/oem/"), ("Work with a Korean PE-foam maker", OEMG["en"])])]),
       ("FOR BUYERS", [("Service", [("Send an Inquiry", INQ["en"]), ("Partnership", "/partner/"), ("FAQ", "/faq/"), ("Guides", "/guides/")])]),
       ("QONE WORLD", [("About", [("Company", COMPANY["en"]), ("Our Story", "/story/"), ("QONE at a Glance", "/overview/"), ("Journal", "/guides/")])])],
  b2b=("WHOLESALE", "/partner/"), search="Search products and pages", menu="Menu", close="Close", inquiry="Inquiry",
  noresult="No results", more="Discover now",
  slides=[("FOAM BLOCK", "Just stick it on. The space transforms.", FOAM["en"]), ("LIVING MAT", "Soft, safe floors for every room", "/products/camping/"), ("THE ORIGINAL", "Since 2013 — the CUSHIONI story", "/story/")],
  strip=[("Foam Blocks", FOAM["en"], "col-foamblock"), ("Insulation Wallpaper", INSUL["en"], "col-insulation"), ("Silk Wallpaper", "/products/wall-decor/", "col-silk"), ("Camping Mats", CAMP["en"], "col-camping")],
  cat_h="Digital Catalogs", cat_btn="Discover Now!", cat_p=["Browse the full CUSHIONI range in our interactive web catalog: foam blocks, insulation and silk wallpaper, camping and living mats, with sizes, packing and photos for every item.", "Prefer PDF? Download the company profile, the product catalog and five product sheets, ready to forward to your buying team."],
  cov=["Product Catalog", "Company Profile", "Silk Wallpaper", "Insulation Wallpaper", "Foam Blocks", "Camping Mat", "Herringbone Mat"],
  smp_h="Request Samples", smp_btn="Request Samples Now!", smp_p=["See and feel the quality before you order. Tell us the products, sizes and the market you sell to, and our factory team in Yeoju will prepare a sample set and reply by email.", "Every CUSHIONI product is made in our own plant in Korea, from PE foam sheet to printing, cutting and packing."],
  trust_h="Trusted retail partners", jr_h="QONE Journal", jr_more="Read more", story_t="The CUSHIONI Foam Block Story", story_d="Since 2013",
  glance_h="Everything about QONE in one place", glance_p="Factory, products, certificates, history, films and FAQ: the complete company overview.", glance_btn="QONE at a Glance",
  f_service="Service", f_info="Information", f_prod="Products", f_social="Social",
  f_service_l=[("Send an Inquiry", INQ["en"]), ("FAQ", "/faq/"), ("Downloads", "/downloads/"), ("Guides", "/guides/"), ("CUSHIONI Catalog", CUSH["en"])],
  f_info_l=[("Company", COMPANY["en"]), ("Our Story", "/story/"), ("QONE at a Glance", "/overview/"), ("Factory", "/factory/"), ("OEM & Private Label", "/oem/"), ("Partnership", "/partner/"), ("Value Retail Range", YIWU["en"]), ("Privacy", "/privacy/")],
  f_prod_l=[("Foam brick wall panels", FOAM["en"]), ("Insulation wallpaper", INSUL["en"]), ("Camping mat guide", CAMP["en"]), ("Work with our factory", OEMG["en"]), ("All products", "/products/")],
  glance_title="QONE at a Glance | Factory, products and history | QONE Corporation"),
 "ko": dict(
  nav=[("제품", [("컬렉션", [("폼블럭", FOAM["ko"]), ("단열벽지", INSUL["ko"]), ("실크벽지·월데코", "/ko/products/wall-decor/"), ("캠핑·리빙매트", CAMP["ko"]), ("전체 제품", "/ko/products/")]),
               ("카탈로그", [("쿠셔니 카탈로그", CUSH["ko"]), ("밸류 리테일 카탈로그", YIWU["ko"]), ("자료 다운로드", "/ko/downloads/")])]),
       ("제조", [("공장", [("여주 공장 소개", "/ko/factory/"), ("OEM·PB 개발", "/ko/oem/"), ("PE폼 OEM 제조", OEMG["ko"])])]),
       ("바이어", [("서비스", [("문의하기", INQ["ko"]), ("수출 파트너", "/ko/partner/"), ("자주 묻는 질문", "/ko/faq/"), ("가이드", "/ko/guides/")])]),
       ("큐원", [("소개", [("회사 소개", COMPANY["ko"]), ("브랜드 스토리", "/ko/story/"), ("큐원 한눈에 보기", "/ko/overview/"), ("큐원 저널", "/ko/guides/")])])],
  b2b=("홀세일", "/ko/partner/"), search="제품·페이지 검색", menu="메뉴", close="닫기", inquiry="문의",
  noresult="검색 결과가 없습니다", more="자세히 보기",
  slides=[("FOAM BLOCK", "붙이는 것만으로, 공간이 달라집니다", FOAM["ko"]), ("LIVING MAT", "모든 방을 위한 부드럽고 안전한 바닥", "/ko/products/camping/"), ("THE ORIGINAL", "2013년부터, 쿠셔니 폼블럭 이야기", "/ko/story/")],
  strip=[("폼블럭", FOAM["ko"], "col-foamblock"), ("단열벽지", INSUL["ko"], "col-insulation"), ("실크벽지", "/ko/products/wall-decor/", "col-silk"), ("캠핑매트", CAMP["ko"], "col-camping")],
  cat_h="디지털 카탈로그", cat_btn="카탈로그 보기", cat_p=["폼블럭, 단열벽지, 실크벽지, 캠핑·리빙매트까지 쿠셔니 전 제품을 웹 카탈로그로 한 번에 보실 수 있습니다. 품목마다 규격, 포장, 사진을 함께 정리했습니다.", "PDF가 필요하시면 회사소개서, 제품 카탈로그, 제품별 소개서 5종을 내려받아 바로 전달하실 수 있습니다."],
  cov=["제품 카탈로그", "회사소개서", "실크벽지", "단열벽지", "폼블럭", "캠핑매트", "헤링본매트"],
  smp_h="샘플 요청", smp_btn="샘플 요청하기", smp_p=["주문 전에 품질을 직접 확인해 보세요. 필요한 제품과 규격, 판매 채널을 알려주시면 여주 공장에서 샘플을 준비해 이메일로 안내드립니다.", "쿠셔니 전 제품은 PE폼 원단부터 인쇄, 재단, 포장까지 한국 자체 공장에서 만듭니다."],
  trust_h="함께하는 유통 파트너", jr_h="큐원 저널", jr_more="자세히 보기", story_t="쿠셔니 폼블럭 이야기", story_d="2013년부터",
  glance_h="큐원의 모든 것을 한곳에", glance_p="공장, 제품, 인증, 연혁, 영상, 자주 묻는 질문까지 회사 전체 소개를 모았습니다.", glance_btn="큐원 한눈에 보기",
  f_service="서비스", f_info="회사 정보", f_prod="제품 안내", f_social="소셜",
  f_service_l=[("문의하기", INQ["ko"]), ("자주 묻는 질문", "/ko/faq/"), ("자료 다운로드", "/ko/downloads/"), ("가이드", "/ko/guides/"), ("쿠셔니 카탈로그", CUSH["ko"])],
  f_info_l=[("회사 소개", COMPANY["ko"]), ("브랜드 스토리", "/ko/story/"), ("큐원 한눈에 보기", "/ko/overview/"), ("공장 소개", "/ko/factory/"), ("OEM·PB 개발", "/ko/oem/"), ("수출 파트너", "/ko/partner/"), ("코스트코 입점 지원", "/costco/"), ("밸류 리테일(이우)", YIWU["ko"]), ("개인정보처리방침", "/ko/privacy/")],
  f_prod_l=[("폼블럭 시공 가이드", FOAM["ko"]), ("결로·외풍 단열벽지", INSUL["ko"]), ("캠핑·차박매트", CAMP["ko"]), ("PE폼 OEM 제조", OEMG["ko"]), ("전체 제품", "/ko/products/")],
  glance_title="큐원 한눈에 보기 | 공장·제품·연혁 | 주식회사 큐원 QONE"),
 "ja": dict(
  nav=[("製品", [("コレクション", [("クッションレンガ", FOAM["ja"]), ("断熱壁紙", INSUL["ja"]), ("シルク壁紙・ウォールデコ", "/ja/products/wall-decor/"), ("キャンプ・リビングマット", CAMP["ja"]), ("全製品", "/ja/products/")]),
               ("カタログ", [("CUSHIONIカタログ", CUSH["ja"]), ("100均カタログ", YIWU["ja"]), ("資料ダウンロード", "/ja/downloads/")])]),
       ("製造", [("工場", [("驪州工場", "/ja/factory/"), ("OEM・PB開発", "/ja/oem/"), ("韓国工場とOEM", OEMG["ja"])])]),
       ("バイヤー向け", [("サービス", [("お問い合わせ", INQ["ja"]), ("輸出提携", "/ja/partner/"), ("よくある質問", "/ja/faq/"), ("ガイド", "/ja/guides/")])]),
       ("QONEについて", [("会社", [("会社案内", COMPANY["ja"]), ("ブランドストーリー", "/ja/story/"), ("QONEのすべて", "/ja/overview/"), ("QONEジャーナル", "/ja/guides/")])])],
  b2b=("卸売", "/ja/partner/"), search="製品・ページを検索", menu="メニュー", close="閉じる", inquiry="お問い合わせ",
  noresult="該当する結果がありません", more="詳しく見る",
  slides=[("FOAM BLOCK", "貼るだけで、空間が変わる。", FOAM["ja"]), ("LIVING MAT", "どの部屋にも、やわらかく安全な床を", "/ja/products/camping/"), ("THE ORIGINAL", "2013年から。クッショニーの物語", "/ja/story/")],
  strip=[("クッションレンガ", FOAM["ja"], "col-foamblock"), ("断熱壁紙", INSUL["ja"], "col-insulation"), ("シルク壁紙", "/ja/products/wall-decor/", "col-silk"), ("キャンプマット", CAMP["ja"], "col-camping")],
  cat_h="デジタルカタログ", cat_btn="カタログを見る", cat_p=["クッションレンガ、断熱壁紙、シルク壁紙、キャンプ・リビングマットまで、CUSHIONIの全製品をWebカタログでご覧いただけます。各品目のサイズ・梱包・写真もまとめています。", "PDFが必要な場合は、会社案内・製品カタログ・製品別資料5種をダウンロードして、そのまま社内でご共有いただけます。"],
  cov=["製品カタログ", "会社案内", "シルク壁紙", "断熱壁紙", "クッションレンガ", "キャンプマット", "ヘリンボーンマット"],
  smp_h="サンプル請求", smp_btn="サンプルを請求する", smp_p=["ご注文の前に、品質を実際にお確かめください。製品・サイズ・販売チャネルをお知らせいただければ、驪州工場でサンプルをご用意し、メールでご案内します。", "CUSHIONIの全製品は、PEフォーム原反から印刷・裁断・梱包まで、韓国の自社工場で製造しています。"],
  trust_h="取引実績のある小売パートナー", jr_h="QONEジャーナル", jr_more="続きを読む", story_t="クッショニー・フォームブロックの物語", story_d="2013年から",
  glance_h="QONEのすべてを、ひとつのページに", glance_p="工場、製品、認証、沿革、映像、よくある質問まで、会社の全体像をまとめました。", glance_btn="QONEのすべて",
  f_service="サービス", f_info="会社情報", f_prod="製品ガイド", f_social="ソーシャル",
  f_service_l=[("お問い合わせ", INQ["ja"]), ("よくある質問", "/ja/faq/"), ("資料ダウンロード", "/ja/downloads/"), ("ガイド", "/ja/guides/"), ("CUSHIONIカタログ", CUSH["ja"])],
  f_info_l=[("会社案内", COMPANY["ja"]), ("ブランドストーリー", "/ja/story/"), ("QONEのすべて", "/ja/overview/"), ("工場紹介", "/ja/factory/"), ("OEM・PB開発", "/ja/oem/"), ("輸出提携", "/ja/partner/"), ("100均向け商品", YIWU["ja"]), ("プライバシーポリシー", "/ja/privacy/")],
  f_prod_l=[("クッションレンガとは", FOAM["ja"]), ("冬の結露・寒さ対策", INSUL["ja"]), ("キャンプマットの選び方", CAMP["ja"]), ("韓国工場とOEM・PB", OEMG["ja"]), ("全製品", "/ja/products/")],
  glance_title="QONEのすべて｜工場・製品・沿革｜QONE Corporation"),
 "ru": dict(
  nav=[("ПРОДУКЦИЯ", [("Коллекции", [("3D-панели под кирпич", FOAM["ru"]), ("Теплоизоляционные обои", INSUL["ru"]), ("Шёлковые обои и декор", "/ru/products/wall-decor/"), ("Туристические и домашние коврики", CAMP["ru"]), ("Вся продукция", "/ru/products/")]),
                       ("Каталоги", [("Каталог CUSHIONI", CUSH["ru"]), ("Каталог для дискаунтеров", YIWU["ru"]), ("Материалы", "/ru/downloads/")])]),
       ("ПРОИЗВОДСТВО", [("Завод", [("Завод в Ёджу", "/ru/factory/"), ("OEM и СТМ", "/ru/oem/"), ("Сотрудничество с заводом", OEMG["ru"])])]),
       ("ПОКУПАТЕЛЯМ", [("Сервис", [("Отправить запрос", INQ["ru"]), ("Партнёрство", "/ru/partner/"), ("Вопросы и ответы", "/ru/faq/"), ("Статьи", "/ru/guides/")])]),
       ("О QONE", [("Компания", [("QONE в цифрах", "/ru/overview/"), ("Наша история", "/ru/story/"), ("Журнал QONE", "/ru/guides/")])])],
  b2b=("ОПТ", "/ru/partner/"), search="Поиск по сайту", menu="Меню", close="Закрыть", inquiry="Запрос",
  noresult="Ничего не найдено", more="Подробнее",
  slides=[("FOAM BLOCK", "Просто приклейте — и пространство преобразится", FOAM["ru"]), ("LIVING MAT", "Мягкий и безопасный пол для любой комнаты", "/ru/products/camping/"), ("THE ORIGINAL", "С 2013 года — история CUSHIONI", "/ru/story/")],
  strip=[("3D-панели", FOAM["ru"], "col-foamblock"), ("Теплоизоляция", INSUL["ru"], "col-insulation"), ("Шёлковые обои", "/ru/products/wall-decor/", "col-silk"), ("Туристические коврики", CAMP["ru"], "col-camping")],
  cat_h="Цифровые каталоги", cat_btn="Открыть каталог", cat_p=["Весь ассортимент CUSHIONI в интерактивном веб-каталоге: 3D-панели, теплоизоляционные и шёлковые обои, туристические и домашние коврики — с размерами, упаковкой и фотографиями.", "Нужен PDF? Скачайте презентацию компании, каталог продукции и пять листов по товарам — их удобно переслать отделу закупок."],
  cov=["Каталог продукции", "О компании", "Шёлковые обои", "Теплоизоляционные обои", "3D-панели", "Туристический коврик", "Коврик «ёлочка»"],
  smp_h="Образцы", smp_btn="Запросить образцы", smp_p=["Оцените качество до заказа. Укажите товары, размеры и рынок сбыта — наша команда на заводе в Ёджу подготовит набор образцов и ответит по электронной почте.", "Вся продукция CUSHIONI производится на нашем заводе в Корее: от листа вспененного полиэтилена до печати, резки и упаковки."],
  trust_h="Наши розничные партнёры", jr_h="Журнал QONE", jr_more="Читать далее", story_t="История CUSHIONI Foam Block", story_d="С 2013 года",
  glance_h="Всё о QONE на одной странице", glance_p="Завод, продукция, сертификаты, история, видео и ответы на вопросы — полный обзор компании.", glance_btn="QONE в цифрах",
  f_service="Сервис", f_info="Информация", f_prod="Продукция", f_social="Соцсети",
  f_service_l=[("Отправить запрос", INQ["ru"]), ("Вопросы и ответы", "/ru/faq/"), ("Материалы", "/ru/downloads/"), ("Статьи", "/ru/guides/"), ("Каталог CUSHIONI", CUSH["ru"])],
  f_info_l=[("QONE в цифрах", "/ru/overview/"), ("Наша история", "/ru/story/"), ("Завод", "/ru/factory/"), ("OEM и СТМ", "/ru/oem/"), ("Партнёрство", "/ru/partner/"), ("Товары для дискаунтеров", YIWU["ru"]), ("Политика конфиденциальности", "/ru/privacy/")],
  f_prod_l=[("3D-панели под кирпич", FOAM["ru"]), ("Теплоизоляционные обои", INSUL["ru"]), ("Как выбрать туристический коврик", CAMP["ru"]), ("Сотрудничество с заводом", OEMG["ru"]), ("Вся продукция", "/ru/products/")],
  glance_title="QONE в цифрах | Завод, продукция, история | QONE Corporation"),
}
LANG_NAMES = [("en", "EN", "/"), ("ko", "KO", "/ko/"), ("ja", "JA", "/ja/"), ("ru", "RU", "/ru/")]
CHEV = '<svg class="mb-chev" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>'
SRCH = '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="8.5" cy="8.5" r="6" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="M13 13l5 5" stroke="currentColor" stroke-width="1.8"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M3.5 6l8.5 7 8.5-7" fill="none" stroke="currentColor" stroke-width="1.7"/></svg>'
BURG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="1.8"/></svg>'

def header(l, cur):
    s = T[l]; out = []
    for i, (top, groups) in enumerate(s["nav"]):
        g = "".join(f'<p class="mb-dd-h">{e(gh)}</p>' + "".join(f'<a href="{u}">{e(t)}</a>' for t, u in items) + ('<span class="mb-dd-sep"></span>' if j < len(groups) - 1 else "")
                    for j, (gh, items) in enumerate(groups))
        out.append(f'<div class="mb-it"><button class="mb-top" type="button" aria-expanded="false" aria-controls="mbdd{i}">{e(top)} {CHEV}</button><div class="mb-dd" id="mbdd{i}">{g}</div></div>')
        if i == 2:
            out.append(f'<form class="mb-search" role="search" action="#" data-lang="{l}"><label class="sr">{e(s["search"])}</label>{SRCH}<input type="search" name="q" placeholder="{e(s["search"])}" autocomplete="off" aria-label="{e(s["search"])}"><div class="mb-sr" role="listbox" data-none="{e(s["noresult"])}"></div></form>')
    out.append(f'<a class="mb-top mb-b2b" href="{s["b2b"][1]}">{e(s["b2b"][0])}</a>')
    langs = "".join(f'<a href="{u}" hreflang="{c}"{" class=on aria-current=true" if c == l else ""}>{n}</a>' for c, n, u in LANG_NAMES)
    cl = dict((c, n) for c, n, u in LANG_NAMES)[l]
    return (f'<header class="hd mbh" data-mb="{ASSET_V}"><div class="mb-bar">'
            f'<a class="mb-logo" href="{P[l]}/" aria-label="QONE"><img src="/assets/img/qone-logo.png" alt="QONE Corporation" width="120" height="40"></a>'
            f'<nav class="mb-nav" aria-label="Main">{"".join(out)}</nav>'
            f'<div class="mb-util"><div class="mb-it mb-lang"><button class="mb-top" type="button" aria-expanded="false" aria-controls="mbddl">{cl} {CHEV}</button><div class="mb-dd mb-dd-l" id="mbddl">{langs}</div></div>'
            f'<a class="mb-ic" href="{INQ[l]}" aria-label="{e(s["inquiry"])}" title="{e(s["inquiry"])}">{MAIL}</a>'
            f'<button class="mb-ic mb-burger" type="button" data-menu aria-expanded="false" aria-controls="menu" aria-label="{e(s["menu"])}">{BURG}</button></div>'
            f'</div><span class="prog" aria-hidden="true"></span></header>')

def drawer(l):
    s = T[l]; parts = []
    for top, groups in s["nav"]:
        links = "".join(f'<a href="{u}">{e(t)}</a>' for gh, items in groups for t, u in items)
        parts.append(f'<details class="mb-acc"><summary>{e(top)}</summary><div>{links}</div></details>')
    langs = "".join(f'<a href="{u}" hreflang="{c}"{" class=on" if c == l else ""}>{n}</a>' for c, n, u in LANG_NAMES)
    return (f'<div class="menu mb-drawer" id="menu"><div class="mb-dr-top"><a class="mb-logo" href="{P[l]}/"><img src="/assets/img/qone-logo.png" alt="QONE" width="96" height="32"></a>'
            f'<button class="x" type="button" data-menu aria-label="{e(s["close"])}">×</button></div>'
            f'<form class="mb-search mb-search-m" role="search" action="#" data-lang="{l}">{SRCH}<input type="search" name="q" placeholder="{e(s["search"])}" autocomplete="off" aria-label="{e(s["search"])}"><div class="mb-sr" role="listbox" data-none="{e(s["noresult"])}"></div></form>'
            f'{"".join(parts)}<a class="mb-acc-a" href="{s["b2b"][1]}">{e(s["b2b"][0])}</a><a class="mb-acc-a" href="{INQ[l]}">{e(s["inquiry"])}</a>'
            f'<div class="lng mb-dr-lng">{langs}</div></div>')

def footer(l, sns):
    s = T[l]
    col = lambda h, items: f'<div><p class="mb-fh">{e(h)}</p>' + "".join(f'<a href="{u}">{e(t)}</a>' for t, u in items) + "</div>"
    return (f'<footer class="foot mbf"><div class="mb-fwrap"><div class="mb-fgrid">'
            f'<div class="mb-flogo"><a href="{P[l]}/" aria-label="QONE"><img src="/assets/img/qone-logo.png" alt="QONE Corporation" width="132" height="44" loading="lazy"></a>'
            f'<p>QONE Corporation<br>166 Yeonha-dong-ro, Yeoju-si, Gyeonggi-do 12646, Korea<br>T +82-31-768-5650 · F +82-31-884-5651<br><a href="mailto:chl@qone.kr">chl@qone.kr</a></p></div>'
            f'{col(s["f_service"], s["f_service_l"])}{col(s["f_info"], s["f_info_l"])}{col(s["f_prod"], s["f_prod_l"])}'
            f'<div><p class="mb-fh">{e(s["f_social"])}</p>{sns}</div></div></div>'
            f'<div class="mb-fbot">Copyright © 2026 QONE Corporation | <a href="{P[l]}/">www.qone.kr</a></div></footer>')

def section(html_, sid):
    m = re.search(r'<section\b[^>]*\bid="' + re.escape(sid) + r'"', html_)
    if not m: return ""
    d = 0
    for t in re.finditer(r'<section\b|</section>', html_[m.start():]):
        d += 1 if t.group(0) != '</section>' else -1
        if d == 0: return html_[m.start():m.start() + t.end()]
    return ""

def journal_items(l):
    out = []
    for g in ["installing-foam-wall-panels", "insulation-wallpaper-vs-regular-wallpaper", "understanding-katri-certification"]:
        f = ROOT / (P[l].lstrip("/") + "/" if P[l] else "") / "guides" / g / "index.html"
        if f.exists():
            t = re.search(r"<title>(.*?)</title>", f.read_text(encoding="utf-8"), re.S).group(1)
            t = H.unescape(re.split(r"\s[|｜]\s?", t)[0]).strip()
            out.append((t, U(l, f"/guides/{g}/")))
    return out

JR_IMG = ["/assets/mb/col-foamblock", "/assets/mb/col-insulation", "/assets/img/ba-after"]

def pic(src, alt, w, h, cls="", eager=False):
    ld = 'fetchpriority="high" decoding="async"' if eager else 'loading="lazy" decoding="async"'
    return f'<picture class="{cls}"><source type="image/webp" srcset="{src}.webp"><img src="{src}.jpg" alt="{e(alt)}" width="{w}" height="{h}" {ld}></picture>'

def home_main(l, legacy):
    s = T[l]
    h1 = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", legacy).group(1)
    h1 = re.sub(r"<[^>]+>", " ", h1); h1 = re.sub(r"\s+", " ", h1).strip(); h1 = re.sub(r"\s+([,.。、!?])", r"\1", h1); h1 = re.sub(r"([、。])\s+", r"\1", h1)
    slides = "".join(
        f'<div class="mb-slide{" on" if i == 0 else ""}" data-i="{i}">{pic(["/assets/mb/hero-1", "/assets/mb/hero-2", "/assets/mb/hero-3"][i], t + " — " + sub, 1920, 872, "mb-slide-i", eager=(i == 0))}'
        f'<div class="mb-slide-c"><p class="mb-slide-t">{e(t)}</p><span class="mb-slide-r"></span><p class="mb-slide-s">{e(sub)}</p><a class="mb-btn mb-btn-w" href="{u}">{e(s["more"])}<span class="sr"> — {e(t)}</span></a></div></div>'
        for i, (t, sub, u) in enumerate(s["slides"]))
    dots = "".join(f'<button type="button" aria-label="{i + 1}" data-go="{i}"{" class=on" if i == 0 else ""}></button>' for i in range(len(s["slides"])))
    strip = "".join(f'<a class="mb-col" href="{u}">{pic("/assets/mb/" + img, t, 624, 627)}<span class="mb-col-c"><b>{e(t)}</b><i>{e(s["more"])}</i></span></a>' for t, u, img in s["strip"])
    cl, dl = COVL[l], DOCL[l]
    covers = [("catalog", f"/assets/ad/docs/QONE_Product_Catalog_{dl}.pdf"), ("company", f"/assets/ad/docs/QONE_Company_Profile_{dl}.pdf"),
              ("p1", f"/assets/ad/docs/QONE_P1_SilkWallpaper_{dl}.pdf"), ("p2", f"/assets/ad/docs/QONE_P2_InsulationWallpaper_{dl}.pdf"),
              ("p3", f"/assets/ad/docs/QONE_P3_FoamBlocks_{dl}.pdf"), ("p4", f"/assets/ad/docs/QONE_P4_CampingMat_{dl}.pdf"), ("p5", f"/assets/ad/docs/QONE_P5_HerringboneMat_{dl}.pdf")]
    cov = "".join(f'<a class="mb-cov" href="{u}" target="_blank" rel="noopener"><picture><source type="image/webp" srcset="/assets/ad/cover/{k}-{cl}.webp"><img src="/assets/ad/cover/{k}-{cl}.jpg" alt="{e(n)} (PDF)" width="420" height="594" loading="lazy" decoding="async"></picture><span>{e(n)} · PDF</span></a>'
                  for (k, u), n in zip(covers, s["cov"]))
    jr = journal_items(l)
    cards = "".join(f'<a class="mb-card" href="{u}">{pic(JR_IMG[i % 3], t, 624, 400)}<b>{e(t)}</b><span class="mb-more">{e(s["jr_more"])}</span></a>' for i, (t, u) in enumerate(jr))
    cards += f'<a class="mb-card" href="{U(l, "/story/")}">{pic("/assets/mb/hero-3", s["story_t"], 624, 400)}<b>{e(s["story_t"])}</b><small>{e(s["story_d"])}</small><span class="mb-more">{e(s["jr_more"])}</span></a>'
    trust = section(legacy, "trust"); contact = section(legacy, "contact")
    kick = lambda t: re.sub(r'(<p class="kick">)\s*\d+\s*·\s*', r'\1', t)
    trust, contact = kick(trust), kick(contact)
    return f'''<main id="main" class="mb-home">
<section class="mb-hero" aria-roledescription="carousel" aria-label="QONE collections">{slides}
  <button class="mb-arr mb-prev" type="button" aria-label="Previous">‹</button><button class="mb-arr mb-next" type="button" aria-label="Next">›</button><div class="mb-dots">{dots}</div></section>
<section class="mb-sec mb-intro"><div class="mb-wrap"><h1 class="mb-h1">{e(h1)}</h1><div class="mb-cols">{strip}</div></div></section>
<section class="mb-sec" id="catalogs"><div class="mb-wrap mb-row"><div class="mb-txt"><h2 class="mb-h2">{e(s["cat_h"])}</h2><a class="mb-btn" href="{CUSH[l]}">{e(s["cat_btn"])}</a>{"".join(f"<p>{e(p)}</p>" for p in s["cat_p"])}</div>
  <div class="mb-car" data-car><button class="mb-car-b mb-car-p" type="button" aria-label="Previous">‹</button><div class="mb-car-t">{cov}</div><button class="mb-car-b mb-car-n" type="button" aria-label="Next">›</button><div class="mb-car-d"></div></div></div></section>
<section class="mb-sec"><div class="mb-wrap mb-row"><div class="mb-txt"><h2 class="mb-h2">{e(s["smp_h"])}</h2><a class="mb-btn" href="{INQ[l]}">{e(s["smp_btn"])}</a>{"".join(f"<p>{e(p)}</p>" for p in s["smp_p"])}</div>
  <a class="mb-media" href="{INQ[l]}">{pic("/assets/mb/samples", s["smp_h"], 1200, 900)}</a></div></section>
{trust}
<section class="mb-sec mb-jr"><div class="mb-wrap"><h2 class="mb-h2 mb-c">{e(s["jr_h"])}</h2><div class="mb-cards">{cards}</div></div></section>
<section class="mb-sec mb-glance"><div class="mb-wrap mb-glance-in"><div><h2 class="mb-h2">{e(s["glance_h"])}</h2><p>{e(s["glance_p"])}</p></div><a class="mb-btn" href="{U(l, "/overview/")}">{e(s["glance_btn"])}</a></div></section>
{contact}
</main>'''

def add_assets(h):
    if "/assets/mb/mb.css" in h: return h
    h = h.replace("</head>", FONTS + f'<link rel="stylesheet" href="/assets/mb/mb.css?v={ASSET_V}">\n</head>', 1)
    return h.replace("</body>", f'<script src="/assets/mb/mb.js?v={ASSET_V}" defer></script>\n</body>', 1)

def lang_of(h):
    m = re.search(r'<html[^>]*\blang="([a-z]{2})', h); return m.group(1) if m and m.group(1) in T else None

def skin(h, l):
    i = h.find('<header class="hd'); j = h.find("</header>", i)
    if i < 0 or j < 0: return h
    sns = re.search(r'<nav class="sns6"[\s\S]*?</nav>', h)
    sns = sns.group(0) if sns else DEFAULT_SNS
    h = h[:i] + header(l, "") + h[j + 9:]
    mi = h.find('<div class="menu" id="menu">')
    if mi >= 0:
        d, k = 0, mi
        for m in re.finditer(r'<div\b|</div>', h[mi:]):
            d += 1 if m.group(0) == '<div' else -1
            if d == 0: k = mi + m.end(); break
        h = h[:mi] + drawer(l) + h[k:]
    fi = h.find('<footer class="foot'); fj = h.find("</footer>", fi)
    if fi >= 0 and fj >= 0: h = h[:fi] + footer(l, sns) + h[fj + 9:]
    return add_assets(h)

_h = (ROOT / "index.html").read_text(encoding="utf-8")
_m = re.search(r'<nav class="sns6"[\s\S]*?</nav>', _h)
DEFAULT_SNS = _m.group(0) if _m else ""

def wr(p, t):
    p.parent.mkdir(parents=True, exist_ok=True); p.write_text(t, encoding="utf-8")

def main():
    homes = {l: ROOT / (P[l].lstrip("/") + "/index.html" if P[l] else "index.html") for l in LANGS}
    # 1) overview copies of the legacy homes (only once)
    for l, p in homes.items():
        ov = ROOT / (P[l].lstrip("/") + "/" if P[l] else "") / "overview" / "index.html"
        legacy = p.read_text(encoding="utf-8")
        if MARK in legacy and ov.exists(): continue
        url = BASE + U(l, "/overview/")
        t = re.sub(r"<title>[\s\S]*?</title>", f"<title>{e(T[l]['glance_title'])}</title>", legacy, count=1)
        t = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{url}"', t, count=1)
        t = re.sub(r'<meta property="og:url" content="[^"]*"', f'<meta property="og:url" content="{url}"', t, count=1)
        t = re.sub(r'(<link rel="alternate" hreflang="(\w+|x-default)" href=")[^"]*(")', lambda m: m.group(1) + BASE + U("en" if m.group(2) == "x-default" else m.group(2), "/overview/") + m.group(3), t)
        wr(ov, t)
    # 2) new homes
    for l, p in homes.items():
        h = p.read_text(encoding="utf-8")
        if MARK in h and 'class="mb-home"' in h: continue
        legacy = (ROOT / (P[l].lstrip("/") + "/" if P[l] else "") / "overview" / "index.html").read_text(encoding="utf-8")
        h = re.sub(r"<main[\s\S]*?</main>", lambda m: home_main(l, legacy), h, count=1)
        h = re.sub(r'<script type="application/ld\+json">\s*\{"@context": "https://schema.org", "@type": "VideoObject"[\s\S]*?</script>', "", h)
        wr(p, h)
    # 3) skin every main-site page
    n = 0; idx = {l: [] for l in LANGS}
    for p in ROOT.rglob("*.html"):
        if ".git" in p.parts: continue
        h = p.read_text(encoding="utf-8")
        if '<header class="hd' not in h: continue
        l = lang_of(h)
        if not l: continue
        if MARK not in h:
            h = skin(h, l); wr(p, h); n += 1
        rel = "/" + str(p.relative_to(ROOT)).replace("index.html", "")
        t = re.search(r"<title>([\s\S]*?)</title>", h); d = re.search(r'<meta name="description" content="([^"]*)"', h)
        if t and "noindex" not in h[:4000] and not rel.startswith("/costco/"):
            idx[l].append({"t": H.unescape(re.split(r"\s[|｜]\s?", t.group(1))[0]).strip(), "d": (lambda x: "" if re.search(r"(?i)costco|코스트코|コストコ|костко", x) else x[:140])(H.unescape(d.group(1))) if d else "", "u": rel})
    # catalog sub-sites in the index too
    for l in LANGS:
        idx[l] += [{"t": T[l]["nav"][0][1][1][1][0][0], "d": "", "u": CUSH[l]}, {"t": T[l]["nav"][0][1][1][1][1][0], "d": "", "u": YIWU[l]}]
        wr(ROOT / "assets" / "mb" / f"search-{l}.json", json.dumps(sorted(idx[l], key=lambda x: x["u"]), ensure_ascii=False, separators=(",", ":")))
    # sitemap: add overview pages
    for sm in ["sitemap.xml", "sitemap-en.xml"]:
        f = ROOT / sm
        if f.exists():
            t = f.read_text(encoding="utf-8")
            if "/overview/</loc>" not in t:
                add = "".join(f"\n  <url><loc>{BASE}{U(l, '/overview/')}</loc><lastmod>2026-11-27</lastmod><priority>0.7</priority></url>" for l in LANGS)
                wr(f, t.replace("</urlset>", add.lstrip("\n") + "\n</urlset>"))
    print("skinned", n, "pages; search index", {l: len(v) for l, v in idx.items()})

if __name__ == "__main__":
    main()
