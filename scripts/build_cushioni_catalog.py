#!/usr/bin/env python3
"""Build the CUSHIONI factory catalog from public SmartStore listings.

No prices, discounts or shipping fees are written to HTML, JSON or image alt text.
"""
import html
import json
import re
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PARTIAL = Path("/tmp/cushioni-partial.json")
IMG_L = ROOT / "assets/cs/img/l"
IMG_T = ROOT / "assets/cs/img/t"
UA = "Mozilla/5.0 (compatible; QONE-catalog/1.0)"

# Owner decision: these store listings are not QONE foam goods and stay out of the catalog.
REMOVED_STORE_IDS = {
    "5938619367",   # Hanil electric blanket
    "6332551319",   # freezer rice containers
    "10566599095",  # vitamin shower filter
    "9129084938",   # mini travel shower filter set
    "9128994727",   # travel shower head with filter
    "9128944501",   # vitamin shower filter, 3 types
    "9128926379",   # moisturizing vitamin shower filter
    "10007094888",  # grain canisters, 5+5
    "7453257784",   # grain canisters, 5 pieces
    "10389507173",  # bamboo mat
    "6726150133",   # bamboo body pillow
    "11858926120",  # folding walking aid
    "6724285602",   # camping chair
    "6724203719",   # 50 L storage box
    "6724325699",   # ethnic knee blanket
    "13626258374",  # acoustic art board
    "6715842525",   # carpet tile
    "11609767285",  # carpet tile
    "12628219607",  # terrazzo floor tile
    "13622474747", "13622474748", "13622474749", "13622474750",
    "13622474751", "13622474752", "13622474753", "13622474754",
    "13622474755", "13622474756", "13622474757", "13622474758",
}

# Owner-supplied photos (web/*.jpg). Color chips around 210 px stay at native size.
OWNER_PHOTO_IDS = {
    "C-0002", "C-0006", "C-0011", "C-0013", "C-0014", "C-0015", "C-0016", "C-0017",
    "C-0018", "C-0020", "C-0021", "C-0022", "C-0023", "C-0025", "C-0026", "C-0027",
    "C-0028", "C-0030", "C-0031", "C-0032", "C-0033", "C-0034", "C-0036", "C-0038",
    "C-0040", "C-0043", "C-0047", "C-0049", "C-0051", "C-0054", "C-0056", "C-0058",
    "C-0059", "C-0062", "C-0065", "C-0067", "C-0068", "C-0069", "C-0072", "C-0076",
    "C-0077", "C-0079", "C-0080", "C-0097", "C-0106", "C-0108", "C-0110",
}
CHIP_MAX = 320

EXTRA = [
    {"id": "10512486547", "name_ko": "쿠셔니 70cm x 2.5m 만능벽지 셀프도배 스티커접착식 폼벽지", "images": [], "blurb_ko": "기존 벽지 위에 붙이는 셀프도배용 실크 단열벽지입니다.", "src": "silk"},
    {"id": "10032351303", "name_ko": "쿠셔니 붙이는벽지 실크 단열 스티커 결로방지 셀프도배 폭 50cm 2.5m, 바이올렛", "images": [], "blurb_ko": "기존 벽지 위에 붙이면 도배가 끝나는 셀프 도배용 실크벽지입니다.", "src": "silk"},
    {"id": "4881039327", "name_ko": "쿠셔니 붙이는벽지 실크 단열 스티커 결로방지 셀프도배 폭 50cm 2.5m, 라임그린", "images": [], "blurb_ko": "기존 벽지 위에 붙이면 도배가 끝나는 셀프 도배용 실크벽지입니다.", "src": "silk"},
    {"id": "4861311982", "name_ko": "쿠셔니 붙이는 단열 실크 벽지 70cm 30m, 격자 스노우화이트", "images": [], "blurb_ko": "기존 벽지 위에 붙이면 도배가 끝나는 격자 패턴 실크벽지입니다.", "src": "silk"},
    {"id": "4625770285", "name_ko": "쿠셔니 붙이는 단열 실크 벽지 70cm 10m, 격자 스노우화이트", "images": [], "blurb_ko": "기존 벽지 위에 붙이면 도배가 끝나는 격자 패턴 실크벽지입니다.", "src": "silk"},
    {"id": "4625767527", "name_ko": "쿠셔니 접착식 단열벽지 폭50cmx30m 실크벽지", "images": [], "blurb_ko": "접착식 실크 단열벽지 롤입니다.", "src": "silk"},
    {"id": "10207384330", "name_ko": "쿠셔니 캠핑매트 발포 엠보싱 접이식 돗자리 + 보관 가방 2단 200x140cm 2개", "images": ["https://shop-phinf.pstatic.net/20240417_19/1713327696292c1ttC_JPEG/114463592025496788_588831356.jpg"], "blurb_ko": "2단 엠보싱 캠핑매트 2장과 보관 가방입니다. 공원, 캠핑, 차박에 펼쳐 씁니다.", "src": "camp"},
    {"id": "6724325699", "name_ko": "무릎담요 캠핑이불 에스닉 러그 블랭킷", "images": ["https://shop-phinf.pstatic.net/20240306_188/1709696797231DixGm_JPEG/110832695930446608_931991563.jpg"], "blurb_ko": "캠핑용 에스닉 패턴 무릎담요입니다.", "src": "camp"},
    {"id": "6724285602", "name_ko": "경량캠핑의자 접이식캠핑의자", "images": ["https://shop-phinf.pstatic.net/20220527_55/1653612838363gvvOg_JPEG/54748684049263125_1489043567.jpg"], "blurb_ko": "접이식 경량 캠핑의자입니다.", "src": "camp"},
    {"id": "6724203719", "name_ko": "다용도 폴딩 박스 캠핑 차박 필수템 정리수납함 50L", "images": ["https://shop-phinf.pstatic.net/20220527_135/1653623690016t5RHz_JPEG/54759472900076507_1177377183.jpg"], "blurb_ko": "캠핑과 차박용 50리터 접이식 수납 박스입니다.", "src": "camp"},
    {"id": "10566599095", "name_ko": "비타민 샤워필터 1개+1개", "images": ["https://shop-phinf.pstatic.net/20250211_183/1739249723636nM86q_JPEG/21266810489329531_2133737435.jpg"], "blurb_ko": "비타민 샤워필터 2개 구성입니다.", "src": "household"},
    {"id": "10389507173", "name_ko": "대나무돗자리 대자리 청대자리 싱글사이즈", "images": ["https://shop-phinf.pstatic.net/20240530_212/17170437534432eEdw_JPEG/118179652123471248_2072443260.jpg"], "blurb_ko": "천연 대나무 싱글 돗자리입니다. 표면을 가공해 매끄럽고, 거실과 침실에 깔 수 있습니다.", "src": "household"},
    {"id": "10007094888", "name_ko": "잡곡용기 쌀보관통 1.3리터 5+5개입 밀폐용기", "images": ["https://shop-phinf.pstatic.net/20221025_113/1666681933620kYVcl_JPEG/67817767437386027_1775609104.jpg"], "blurb_ko": "1.3리터 밀폐 잡곡용기 10개 세트입니다.", "src": "household"},
    {"id": "9129084938", "name_ko": "허그미 여행용샤워필터 미니3종세트", "images": ["https://shop-phinf.pstatic.net/20240710_7/1720582207419UIxkS_JPEG/31475887719174359_654353579.jpg"], "blurb_ko": "여행용 미니 샤워필터 3종 세트입니다.", "src": "household"},
    {"id": "9128994727", "name_ko": "허그미 여행용 샤워기 필터 수압상승샤워기 샤워필터", "images": ["https://shop-phinf.pstatic.net/20230829_66/1693302073491xYG8t_JPEG/11605505307257651_1039033521.jpg"], "blurb_ko": "여행용 샤워기 헤드와 필터입니다.", "src": "household"},
    {"id": "9128944501", "name_ko": "비타민 샤워필터 샤워기필터 석회수 녹물 염소제거 3종", "images": ["https://shop-phinf.pstatic.net/20230829_110/16933004472430JGdB_JPEG/43375984623898000_1901849951.jpg"], "blurb_ko": "석회수, 녹물, 염소 제거를 표기한 비타민 샤워필터 3종입니다.", "src": "household"},
    {"id": "9128926379", "name_ko": "허그미 피부보습 비타민 샤워필터 샤워기필터", "images": ["https://shop-phinf.pstatic.net/20240328_77/1711610438343tIDli_JPEG/38913122223871638_1194369403.jpg"], "blurb_ko": "허그미 비타민 샤워필터입니다.", "src": "household"},
    {"id": "7453257784", "name_ko": "이츠라움 잡곡용기 다용도 잡곡통 1.3L x 5개입 세트", "images": ["https://shop-phinf.pstatic.net/20221025_113/1666681933620kYVcl_JPEG/67817767437386027_1775609104.jpg"], "blurb_ko": "1.3리터 잡곡통 5개 세트입니다.", "src": "household"},
    {"id": "6726150133", "name_ko": "대나무 죽부인 베개 여름바디필로우 국내산 담양죽부인", "images": ["https://shop-phinf.pstatic.net/20230420_261/1681960599512KuNyQ_JPEG/28678978339783298_845057806.jpg"], "blurb_ko": "담양산으로 안내된 대나무 죽부인입니다.", "src": "household"},
    {"id": "6332551319", "name_ko": "냉동밥보관용기 전자레인지용 밀폐용기16개+16개", "images": [], "blurb_ko": "전자레인지에 사용할 수 있는 냉동밥 밀폐용기 32개 구성입니다.", "src": "household"},
    {"id": "5938619367", "name_ko": "한일의료기 전기요 무자계 EMF 매트 담요 캠핑 차박 대형(135x180)", "images": [], "blurb_ko": "한일의료기 이름의 대형 전기요입니다. 캠핑과 차박용으로 안내되어 있습니다.", "src": "household"},
    {"id": "9380634886", "name_ko": "논슬립 유아 놀이방 아기 매트 150x200x1.2cm 알파벳 유아리빙매트", "images": ["https://shop-phinf.pstatic.net/20231016_104/1697441263343eHheB_JPEG/25647402159345787_1438247764.jpg"], "blurb_ko": "논슬립 유아 리빙매트, 알파벳 패턴, 150 x 200 cm, 두께 1.2 cm.", "src": "kids"},
]

COLORS = [
    ("스노우화이트", "Snow White", "スノーホワイト", "blanco nieve"),
    ("웜그레이", "Warm Gray", "ウォームグレー", "gris cálido"),
    ("프렌치블루", "French Blue", "フレンチブルー", "azul francés"),
    ("딥그린", "Deep Green", "ディープグリーン", "verde profundo"),
    ("보이블루", "Boy Blue", "ボーイブルー", "azul boy"),
    ("라임그린", "Lime Green", "ライムグリーン", "verde lima"),
    ("샌드베이지", "Sand Beige", "サンドベージュ", "beige arena"),
    ("스톤베이지", "Stone Beige", "ストーンベージュ", "beige piedra"),
    ("실버그레이", "Silver Gray", "シルバーグレー", "gris plata"),
    ("멜란지그레이", "Melange Gray", "メランジュグレー", "gris melange"),
    ("카키그레이", "Khaki Gray", "カーキグレー", "gris caqui"),
    ("레드브라운", "Red Brown", "レッドブラウン", "marrón rojizo"),
    ("모카브라운", "Mocha Brown", "モカブラウン", "marrón moca"),
    ("파스텔옐로우", "Pastel Yellow", "パステルイエロー", "amarillo pastel"),
    ("파스텔핑크", "Pastel Pink", "パステルピンク", "rosa pastel"),
    ("파스텔그린", "Pastel Green", "パステルグリーン", "verde pastel"),
    ("파스텔블루", "Pastel Blue", "パステルブルー", "azul pastel"),
    ("코발트블루", "Cobalt Blue", "コバルトブルー", "azul cobalto"),
    ("체리핑크", "Cherry Pink", "チェリーピンク", "rosa cereza"),
    ("라이트블루", "Light Blue", "ライトブルー", "azul claro"),
    ("크림베이지", "Cream Beige", "クリームベージュ", "beige crema"),
    ("레드화이트", "Red and White", "レッドホワイト", "rojo y blanco"),
    ("와인앤라이트", "Wine and Light", "ワインアンドライト", "vino y claro"),
    ("화이트마블", "White Marble", "ホワイトマーブル", "mármol blanco"),
    ("블랙마블", "Black Marble", "ブラックマーブル", "mármol negro"),
    ("직사각타일", "Rectangular Tile", "長方形タイル", "baldosa rectangular"),
    ("정사각타일", "Square Tile", "正方形タイル", "baldosa cuadrada"),
    ("스노우", "Snow", "スノー", "nieve"),
    ("에메랄드", "Emerald", "エメラルド", "esmeralda"),
    ("바이올렛", "Violet", "バイオレット", "violeta"),
    ("알파벳", "Alphabet", "アルファベット", "abecedario"),
    ("빨간모자", "Red Riding Hood", "赤ずきん", "caperucita"),
    ("화이트", "White", "ホワイト", "blanco"),
    ("베이지", "Beige", "ベージュ", "beige"),
    ("블랙", "Black", "ブラック", "negro"),
    ("카키", "Khaki", "カーキ", "caqui"),
    ("그레이", "Gray", "グレー", "gris"),
    ("월넛", "Walnut", "ウォールナット", "nogal"),
    ("오크", "Oak", "オーク", "roble"),
    ("체리", "Cherry", "チェリー", "cerezo"),
    ("테라조", "Terrazzo", "テラゾー", "terrazo"),
]

CATS = [
    ("wall-decor", {"en": "Wall decor", "ko": "벽 장식", "ja": "壁デコ", "es": "Decoración de pared"}),
    ("living", {"en": "Living", "ko": "리빙", "ja": "リビング", "es": "Living"}),
    ("camping", {"en": "Camping", "ko": "캠핑", "ja": "キャンプ", "es": "Camping"}),
    ("household", {"en": "Household", "ko": "생활잡화", "ja": "生活雑貨", "es": "Hogar"}),
]

UI = {
    "en": {
        "brand": "CUSHIONI", "sub": "Factory catalog", "lang": "en", "html": "en",
        "nav_cat": "Catalog", "nav_req": "Request a quote", "home": "CUSHIONI",
        "h1": "CUSHIONI factory catalog",
        "lead": "QONE’s CUSHIONI factory line for overseas wholesale buyers: peel-and-stick wall panels, wallpaper, and foam mats. Search by name or filter by category, then send a quote request to chl@qone.kr.",
        "search": "Search products", "ph": "Try wallpaper, foam block, camping mat",
        "showing": "{n} of {t} products", "all": "All",
        "add": "Add to quote list", "added": "In your quote list", "remove": "Remove",
        "empty": "Your list is empty. Add products from the catalog with the + button.",
        "list": "Quote list", "send": "Request a quote for these", "clear": "Clear list",
        "none": "No products match. Clear the search or pick another category.",
        "reset": "Clear filters",
        "end_h": "Ask the factory for a quote.",
        "end_p": "Tell us the items, quantities and market. We reply by email within one business day.",
        "mail": "chl@qone.kr", "req": "Request a quote",
        "foot": "QONE Corporation, 166 Yeonha-dong-ro, Yeoju-si, Gyeonggi-do, Korea. CUSHIONI wall panels, wallpaper and mats are produced at the Yeoju factory.",
        "disc": "Product photos are the public store photographs. Wholesale terms are confirmed by email. This catalog does not list retail offers.",
        "crumb_home": "CUSHIONI", "close": "Close", "prev": "Previous product", "next": "Next product",
        "cat": "Category", "size": "Size", "color": "Color / options", "mat": "Material", "pack": "Pack", "origin": "Origin",
        "full": "Open product page", "page_cta": "Add it on the catalog",
        "quote_h": "Request a quote",
        "quote_l": "Tell us your company and the items you want. We reply within one business day.",
        "next_h": "What happens next",
        "steps": ["We reply within one business day.", "We confirm samples for qualified buyer inquiries.", "We send the quote to your email."],
        "co": "Company", "nm": "Your name", "em": "Work email", "cty": "Country", "items": "Items of interest",
        "msg": "Message", "msg_ph": "Quantities, packaging and timing",
        "agree": "I agree that QONE may use this information to reply to my request.",
        "sendbtn": "Send request", "subj": "[CUSHIONI catalog]",
        "thanks_h": "Request received", "thanks_p": "Thank you. We will reply to your email within one business day.",
        "back": "Back to the catalog", "err_req": "Please fill in the required fields.", "err_em": "Please enter a valid email address.",
        "err_size": "Attachments are over 10 MB in total. Send a link instead.", "sending": "Sending…",
        "landing_h": "QONE’s own CUSHIONI line",
        "landing_l": "Peel-and-stick wall finishes, living mats and camping goods from the Yeoju factory, listed for overseas B2B buyers.",
        "view": "View the catalog",
    },
    "ko": {
        "brand": "CUSHIONI", "sub": "공장 카탈로그", "lang": "ko", "html": "ko",
        "nav_cat": "카탈로그", "nav_req": "견적 요청", "home": "쿠셔니",
        "h1": "쿠셔니 공장 카탈로그",
        "lead": "여주 공장의 쿠셔니 벽패널, 단열벽지, 폼 매트를 해외 바이어용으로 정리했습니다. 이름이나 카테고리로 찾고, 견적은 chl@qone.kr 로 요청해 주세요.",
        "search": "제품 검색", "ph": "벽지, 폼블럭, 캠핑매트",
        "showing": "{t}종 중 {n}종", "all": "전체",
        "add": "견적 리스트에 담기", "added": "견적 리스트에 담김", "remove": "빼기",
        "empty": "리스트가 비어 있습니다. 카탈로그에서 + 버튼으로 담아 주세요.",
        "list": "견적 리스트", "send": "이 제품들 견적 요청", "clear": "리스트 비우기",
        "none": "맞는 제품이 없습니다. 검색을 지우거나 다른 카테고리를 골라 주세요.",
        "reset": "필터 지우기",
        "end_h": "공장에 견적을 요청하세요.",
        "end_p": "원하는 제품과 수량, 시장을 알려 주세요. 영업일 기준 하루 안에 이메일로 답합니다.",
        "mail": "chl@qone.kr", "req": "견적 요청",
        "foot": "주식회사 큐원, 경기도 여주시 연라동로 166. 쿠셔니 벽패널, 벽지, 매트는 여주 공장에서 생산합니다.",
        "disc": "제품 사진은 공개 스토어 사진입니다. 도매 조건은 이메일로 확인합니다.",
        "crumb_home": "쿠셔니", "close": "닫기", "prev": "이전 제품", "next": "다음 제품",
        "cat": "카테고리", "size": "규격", "color": "색상 / 옵션", "mat": "소재", "pack": "구성", "origin": "생산",
        "full": "제품 페이지 열기", "page_cta": "카탈로그에서 담기",
        "quote_h": "견적 요청",
        "quote_l": "회사와 원하는 제품을 알려 주세요. 영업일 기준 하루 안에 답합니다.",
        "next_h": "다음 단계",
        "steps": ["영업일 기준 하루 안에 답합니다.", "자격 있는 바이어 문의에는 샘플을 안내합니다.", "견적은 이메일로 보냅니다."],
        "co": "회사", "nm": "이름", "em": "업무용 이메일", "cty": "국가", "items": "관심 제품",
        "msg": "메시지", "msg_ph": "수량, 포장, 일정",
        "agree": "이 요청에 답하기 위해 큐원이 정보를 사용하는 데 동의합니다.",
        "sendbtn": "요청 보내기", "subj": "[쿠셔니 카탈로그]",
        "thanks_h": "요청을 받았습니다", "thanks_p": "감사합니다. 영업일 기준 하루 안에 이메일로 답하겠습니다.",
        "back": "카탈로그로", "err_req": "필수 항목을 입력해 주세요.", "err_em": "올바른 이메일 주소를 입력해 주세요.",
        "err_size": "첨부 파일이 합계 10MB를 넘습니다. 링크로 보내 주세요.", "sending": "보내는 중…",
        "landing_h": "큐원이 만드는 쿠셔니",
        "landing_l": "여주 공장의 붙이는 벽마감, 리빙매트, 캠핑 제품을 해외 바이어용으로 정리했습니다.",
        "view": "카탈로그 보기",
    },
    "ja": {
        "brand": "CUSHIONI", "sub": "工場カタログ", "lang": "ja", "html": "ja",
        "nav_cat": "カタログ", "nav_req": "見積依頼", "home": "クシオニ",
        "h1": "クシオニ工場カタログ",
        "lead": "驪州工場のCUSHIONI壁パネル、断熱壁紙、フォームマットです。名前やカテゴリで絞り、見積は chl@qone.kr へ依頼してください。",
        "search": "製品を検索", "ph": "壁紙、フォームブロック、キャンプマット",
        "showing": "{t}点中 {n}点", "all": "すべて",
        "add": "見積リストに追加", "added": "見積リストに追加済み", "remove": "外す",
        "empty": "リストは空です。カタログの + から追加してください。",
        "list": "見積リスト", "send": "これらの見積を依頼", "clear": "リストを空にする",
        "none": "一致する製品がありません。検索を消すか、別のカテゴリを選んでください。",
        "reset": "条件を消す",
        "end_h": "工場に見積を依頼する。",
        "end_p": "品目、数量、市場を教えてください。1営業日以内にメールで返信します。",
        "mail": "chl@qone.kr", "req": "見積依頼",
        "foot": "QONE Corporation、京畿道驪州市連羅洞路166。クシオニの壁パネル、壁紙、マットは驪州工場で生産しています。",
        "disc": "写真は公開ストアの写真です。卸条件はメールで確認します。",
        "crumb_home": "クシオニ", "close": "閉じる", "prev": "前の製品", "next": "次の製品",
        "cat": "カテゴリ", "size": "サイズ", "color": "色 / オプション", "mat": "素材", "pack": "入数", "origin": "生産",
        "full": "製品ページを開く", "page_cta": "カタログで追加",
        "quote_h": "見積依頼",
        "quote_l": "会社名と希望製品を教えてください。1営業日以内に返信します。",
        "next_h": "このあと",
        "steps": ["1営業日以内に返信します。", "対象となるバイヤーにはサンプルを案内します。", "見積はメールで送ります。"],
        "co": "会社", "nm": "お名前", "em": "仕事用メール", "cty": "国", "items": "希望製品",
        "msg": "メッセージ", "msg_ph": "数量、梱包、時期",
        "agree": "この依頼への返信のためにQONEが情報を使うことに同意します。",
        "sendbtn": "送信", "subj": "[CUSHIONI catalog]",
        "thanks_h": "依頼を受け付けました", "thanks_p": "ありがとうございます。1営業日以内にメールで返信します。",
        "back": "カタログへ", "err_req": "必須項目を入力してください。", "err_em": "正しいメールアドレスを入力してください。",
        "err_size": "添付が合計10MBを超えています。リンクで送ってください。", "sending": "送信中…",
        "landing_h": "QONEのCUSHIONI",
        "landing_l": "驪州工場の貼る壁材、リビングマット、キャンプ用品を海外バイヤー向けにまとめています。",
        "view": "カタログを見る",
    },
    "es": {
        "brand": "CUSHIONI", "sub": "Catálogo de fábrica", "lang": "es", "html": "es",
        "nav_cat": "Catálogo", "nav_req": "Pedir cotización", "home": "CUSHIONI",
        "h1": "Catálogo de fábrica CUSHIONI",
        "lead": "Línea de fábrica CUSHIONI de QONE para compradores mayoristas: paneles de pared, papel pintado y esterillas de espuma. Busque por nombre o categoría y pida cotización a chl@qone.kr.",
        "search": "Buscar productos", "ph": "papel pintado, panel, esterilla",
        "showing": "{n} de {t} productos", "all": "Todos",
        "add": "Añadir a la lista", "added": "En su lista", "remove": "Quitar",
        "empty": "La lista está vacía. Añada productos con el botón +.",
        "list": "Lista de cotización", "send": "Pedir cotización de estos", "clear": "Vaciar lista",
        "none": "Ningún producto coincide. Borre la búsqueda o elija otra categoría.",
        "reset": "Quitar filtros",
        "end_h": "Pida una cotización a la fábrica.",
        "end_p": "Indique artículos, cantidades y mercado. Respondemos por correo en un día laborable.",
        "mail": "chl@qone.kr", "req": "Pedir cotización",
        "foot": "QONE Corporation, 166 Yeonha-dong-ro, Yeoju-si, Gyeonggi-do, Corea. Los paneles, papeles y esterillas CUSHIONI se fabrican en Yeoju.",
        "disc": "Las fotos son las de la tienda pública. Las condiciones mayoristas se confirman por correo.",
        "crumb_home": "CUSHIONI", "close": "Cerrar", "prev": "Producto anterior", "next": "Producto siguiente",
        "cat": "Categoría", "size": "Medida", "color": "Color / opciones", "mat": "Material", "pack": "Pack", "origin": "Origen",
        "full": "Abrir la ficha", "page_cta": "Añadirlo en el catálogo",
        "quote_h": "Pedir cotización",
        "quote_l": "Cuéntenos su empresa y los artículos. Respondemos en un día laborable.",
        "next_h": "Qué sigue",
        "steps": ["Respondemos en un día laborable.", "Confirmamos muestras para consultas de compradores cualificados.", "Enviamos la cotización por correo."],
        "co": "Empresa", "nm": "Su nombre", "em": "Email de trabajo", "cty": "País", "items": "Artículos",
        "msg": "Mensaje", "msg_ph": "Cantidades, embalaje y plazos",
        "agree": "Acepto que QONE use estos datos para responder a mi solicitud.",
        "sendbtn": "Enviar", "subj": "[CUSHIONI catalog]",
        "thanks_h": "Solicitud recibida", "thanks_p": "Gracias. Responderemos a su correo en un día laborable.",
        "back": "Volver al catálogo", "err_req": "Complete los campos obligatorios.", "err_em": "Escriba un email válido.",
        "err_size": "Los adjuntos superan 10 MB en total. Envíe un enlace.", "sending": "Enviando…",
        "landing_h": "La línea propia CUSHIONI de QONE",
        "landing_l": "Revestimientos autoadhesivos, esterillas de living y camping de la fábrica de Yeoju, para compradores mayoristas.",
        "view": "Ver el catálogo",
    },
}

FAM_COPY = {
    "silk": {
        "en": "Peel-and-stick silk-texture insulation wallpaper. The release film comes off and the sheet sticks to an existing wall, with no paste. Made at QONE’s Yeoju factory for wholesale and private label.",
        "ko": "기존 벽지 위에 이형지를 떼고 붙이는 실크 질감 단열벽지입니다. 여주 공장에서 생산하며, 도매와 자체 브랜드 주문을 받습니다.",
        "ja": "既存の壁に剥がして貼るシルク調の断熱壁紙です。驪州工場で製造し、卸とプライベートブランドに対応します。",
        "es": "Papel pintado aislante de tacto seda, autoadhesivo. Se despega el film y se pega sobre la pared existente. Fabricado en Yeoju para mayoristas y marca propia.",
        "title": {"en": "Peel-and-stick silk wallpaper", "ko": "붙이는 실크 단열벽지", "ja": "貼るシルク断熱壁紙", "es": "Papel pintado seda autoadhesivo"},
        "mat": "PE foam sheet, printed face, adhesive and release film",
        "origin": "QONE Yeoju factory, Korea",
        "factory": True,
        "cat": "wall-decor",
    },
    "foam": {
        "en": "Self-adhesive 3D PE foam wall panel, molded at QONE’s Yeoju factory. It adds a cushioned, insulating face over an existing wall and is aimed at wholesale and private-label programs.",
        "ko": "여주 공장에서 성형하는 점착식 3D PE 폼 벽패널입니다. 기존 벽 위에 쿠션과 단열면을 더하며, 도매와 자체 브랜드 주문을 받습니다.",
        "ja": "驪州工場で成形する粘着式3D PEフォーム壁パネルです。既存の壁にクッションと断熱面を足します。卸とPBに対応します。",
        "es": "Panel de pared 3D de espuma PE autoadhesivo, moldeado en la fábrica de Yeoju. Añade una cara acolchada y aislante sobre la pared existente.",
        "title": {"en": "3D foam wall panel", "ko": "3D 폼블럭 벽패널", "ja": "3Dフォーム壁パネル", "es": "Panel de pared 3D de espuma"},
        "mat": "PE foam, self-adhesive backing",
        "origin": "QONE Yeoju factory, Korea",
        "factory": True,
        "cat": "wall-decor",
    },
    "acoustic": {
        "en": "Adhesive acoustic art board, 30 × 30 cm, described on the store as a 2-in-1 perforated panel that also accepts magnets. Sold on QONE’s CUSHIONI store for wholesale inquiry.",
        "ko": "30 × 30 cm 점착식 타공 아트보드입니다. 스토어에는 자석 겸용 2-in-1 흡음 패널로 안내되어 있습니다.",
        "ja": "30×30cmの粘着式穴あきアートボードです。ストアではマグネット兼用の2-in-1吸音パネルとして案内されています。",
        "es": "Tablero acústico adhesivo de 30 × 30 cm. La tienda lo describe como panel perforado 2 en 1 que también admite imanes.",
        "title": {"en": "Adhesive acoustic art board", "ko": "점착식 방음 아트보드", "ja": "粘着吸音アートボード", "es": "Tablero acústico adhesivo"},
        "mat": "Perforated acoustic board",
        "origin": "Listed on the CUSHIONI store",
        "cat": "wall-decor",
    },
    "camp-mat": {
        "en": "Folding closed-cell PE foam camping mat with a storage bag. It unfolds flat for camping, car camping and picnics and slows moisture from the ground. Made at QONE’s Yeoju factory.",
        "ko": "보관 가방이 있는 접이식 독립기포 PE 폼 캠핑매트입니다. 캠핑, 차박, 피크닉에 펼치며 바닥 습기를 줄입니다. 여주 공장에서 생산합니다.",
        "ja": "収納バッグ付きの折りたたみ独立気泡PEフォームキャンプマットです。キャンプ、車中泊、ピクニックに広げ、地面の湿気を抑えます。驪州工場製です。",
        "es": "Esterilla de camping de espuma PE de célula cerrada, plegable, con bolsa. Se abre plana para camping, furgo y picnic y frena la humedad del suelo. Hecha en Yeoju.",
        "title": {"en": "Folding camping mat", "ko": "접이식 캠핑매트", "ja": "折りたたみキャンプマット", "es": "Esterilla de camping plegable"},
        "mat": "Closed-cell PE foam",
        "origin": "QONE Yeoju factory, Korea",
        "factory": True,
        "cat": "camping",
    },
    "camp-chair": {
        "en": "Lightweight folding camping chair listed on QONE’s CUSHIONI store.",
        "ko": "쿠셔니 스토어에 올라 있는 경량 접이식 캠핑의자입니다.",
        "ja": "CUSHIONIストア掲載の軽量折りたたみキャンプチェアです。",
        "es": "Silla de camping plegable y ligera, publicada en la tienda CUSHIONI.",
        "title": {"en": "Lightweight folding camping chair", "ko": "경량 접이식 캠핑의자", "ja": "軽量折りたたみキャンプチェア", "es": "Silla de camping plegable"},
        "mat": "Folding chair",
        "origin": "Listed on the CUSHIONI store",
        "cat": "camping",
    },
    "camp-box": {
        "en": "50-liter folding storage box for camping and car camping, listed on the CUSHIONI store.",
        "ko": "캠핑과 차박용 50리터 접이식 수납 박스입니다.",
        "ja": "キャンプと車中泊向けの50L折りたたみ収納ボックスです。",
        "es": "Caja de almacenaje plegable de 50 litros para camping y furgo.",
        "title": {"en": "50 L folding storage box", "ko": "50L 접이식 수납 박스", "ja": "50L折りたたみ収納ボックス", "es": "Caja plegable de 50 L"},
        "mat": "Folding storage box",
        "origin": "Listed on the CUSHIONI store",
        "cat": "camping",
    },
    "blanket": {
        "en": "Ethnic-pattern knee blanket for camping, listed on the CUSHIONI store.",
        "ko": "캠핑용 에스닉 패턴 무릎담요입니다.",
        "ja": "キャンプ向けエスニック柄のひざ掛けです。",
        "es": "Manta para las rodillas de dibujo étnico, para camping.",
        "title": {"en": "Ethnic camping knee blanket", "ko": "에스닉 캠핑 무릎담요", "ja": "エスニックキャンプひざ掛け", "es": "Manta étnica de camping"},
        "mat": "Textile blanket",
        "origin": "Listed on the CUSHIONI store",
        "cat": "camping",
    },
    "electric": {
        "en": "Large electric mat blanket, 135 × 180 cm, listed on the CUSHIONI store under the Hanil Medical name and described for camping and car camping.",
        "ko": "한일의료기 이름으로 안내된 135 × 180 cm 대형 전기요입니다. 캠핑과 차박용으로 스토어에 올라가 있습니다.",
        "ja": "ハンイル医療器の名称で掲載された135×180cmの大型電気毛布です。キャンプと車中泊向けと案内されています。",
        "es": "Manta eléctrica grande de 135 × 180 cm, publicada en la tienda con el nombre Hanil Medical, descrita para camping y furgo.",
        "title": {"en": "Large electric camping blanket", "ko": "대형 전기 캠핑 담요", "ja": "大型電気キャンプ毛布", "es": "Manta eléctrica grande de camping"},
        "mat": "Electric mat blanket",
        "origin": "Listed under the Hanil Medical name",
        "cat": "camping",
    },
    "herringbone": {
        "en": "Non-slip herringbone PE living mat. The textured face and grip backing are for living rooms and play spaces. Made at QONE’s Yeoju factory.",
        "ko": "논슬립 헤링본 PE 거실매트입니다. 거실과 놀이 공간용이며 여주 공장에서 생산합니다.",
        "ja": "滑り止めヘリンボーンのPEリビングマットです。居間と遊び空間向け。驪州工場製です。",
        "es": "Esterilla de living PE con dibujo de espiga y base antideslizante, para salón y juego. Hecha en Yeoju.",
        "title": {"en": "Non-slip herringbone living mat", "ko": "논슬립 헤링본 거실매트", "ja": "滑り止めヘリンボーンマット", "es": "Esterilla de living en espiga"},
        "mat": "PE foam",
        "origin": "QONE Yeoju factory, Korea",
        "factory": True,
        "cat": "living",
    },
    "kids": {
        "en": "Non-slip kids’ living mat, 150 × 200 cm and 1.2 cm thick, for playrooms. Made as a CUSHIONI PE foam mat at QONE’s Yeoju factory.",
        "ko": "150 × 200 cm, 두께 1.2 cm 논슬립 유아 리빙매트입니다. 놀이방용 PE 폼 매트로 여주 공장에서 생산합니다.",
        "ja": "150×200cm、厚さ1.2cmの滑り止めキッズリビングマットです。プレイルーム向け。驪州工場のPEフォームです。",
        "es": "Esterilla infantil antideslizante de 150 × 200 cm y 1,2 cm de grosor, para la zona de juego. Espuma PE hecha en Yeoju.",
        "title": {"en": "Non-slip kids’ play mat", "ko": "논슬립 유아 놀이매트", "ja": "滑り止めキッズプレイマット", "es": "Esterilla infantil antideslizante"},
        "mat": "PE foam",
        "origin": "QONE Yeoju factory, Korea",
        "factory": True,
        "cat": "living",
    },
    "tile-carpet": {
        "en": "Carpet tile, 50 × 50 cm, sold in a 20-piece pack on the CUSHIONI store for living-room floors. The listing does not describe it as a PE foam panel from the Yeoju factory.",
        "ko": "50 × 50 cm 타일카페트 20매입입니다. 거실 바닥을 스스로 깔 수 있는 쿠셔니 바닥재입니다.",
        "ja": "50×50cmのタイルカーペット20枚入りです。自分で敷けるクシオニの床材です。",
        "es": "Loseta de moqueta de 50 × 50 cm, pack de 20, para salón y suelos. Acabado de suelo CUSHIONI.",
        "title": {"en": "Carpet tile, 20 pieces", "ko": "타일카페트 20매", "ja": "タイルカーペット20枚", "es": "Loseta de moqueta, 20 piezas"},
        "mat": "Carpet tile",
        "origin": "QONE CUSHIONI floor line",
        "cat": "living",
    },
    "deco": {
        "en": "Peel-and-stick deco floor sheet, 600 × 300 mm, listed on the CUSHIONI store. Pattern and pack size are in the product name. The listing does not describe it as a PE foam panel from the Yeoju factory.",
        "ko": "600 × 300 mm 점착식 데코타일 시트입니다. 패턴과 매수는 제품명에 있습니다. 쿠셔니 바닥재입니다.",
        "ja": "600×300mmの貼るデコタイルシートです。柄と入数は製品名にあります。クシオニの床材です。",
        "es": "Lámina de baldosa deco autoadhesiva de 600 × 300 mm. El dibujo y el número de piezas van en el nombre. Acabado de suelo CUSHIONI.",
        "title": {"en": "Peel-and-stick deco tile", "ko": "점착식 데코타일", "ja": "貼るデコタイル", "es": "Baldosa deco autoadhesiva"},
        "mat": "Adhesive floor sheet",
        "origin": "QONE CUSHIONI floor line",
        "cat": "living",
    },
    "terrazzo": {
        "en": "Terrazzo puzzle floor tile, sold as a 7-piece box on the CUSHIONI store. The listing does not describe it as a PE foam panel from the Yeoju factory.",
        "ko": "테라조 패턴 퍼즐 바닥타일 1박스 7매입니다. 거실에 스스로 깔 수 있는 쿠셔니 바닥재입니다.",
        "ja": "テラゾー柄のパズル床タイル、1箱7枚です。自分で敷けるクシオニの床材です。",
        "es": "Baldosa puzzle de terrazo, caja de 7 piezas, para un suelo de salón que se instala uno mismo.",
        "title": {"en": "Terrazzo floor tile, 7-piece box", "ko": "테라조 바닥타일 7매", "ja": "テラゾー床タイル7枚", "es": "Baldosa terrazo, caja de 7"},
        "mat": "Puzzle floor tile",
        "origin": "QONE CUSHIONI floor line",
        "cat": "living",
    },
    "walker": {
        "en": "Folding walking aid with height adjustment and storage, listed on the CUSHIONI store.",
        "ko": "높이 조절과 수납이 되는 접이식 보행보조기입니다. 쿠셔니 스토어에 올라가 있습니다.",
        "ja": "高さ調節と収納付きの折りたたみ歩行器です。CUSHIONIストアに掲載されています。",
        "es": "Andador plegable con altura regulable y almacenamiento, publicado en la tienda CUSHIONI.",
        "title": {"en": "Folding walking aid", "ko": "접이식 보행보조기", "ja": "折りたたみ歩行器", "es": "Andador plegable"},
        "mat": "Folding walking aid",
        "origin": "Listed on the CUSHIONI store",
        "cat": "household",
    },
    "shower": {
        "en": "Shower filter from the CUSHIONI store listing. The store text describes a vitamin filter for shower water.",
        "ko": "쿠셔니 스토어에 올라 있는 샤워필터입니다. 스토어 문구는 비타민 샤워필터로 안내합니다.",
        "ja": "CUSHIONIストア掲載のシャワーフィルターです。ストアではビタミンシャワーフィルターとして案内されています。",
        "es": "Filtro de ducha de la tienda CUSHIONI. El texto de la tienda lo describe como filtro vitamínico para el agua de la ducha.",
        "title": {"en": "Vitamin shower filter", "ko": "비타민 샤워필터", "ja": "ビタミンシャワーフィルター", "es": "Filtro de ducha vitamínico"},
        "mat": "Shower filter",
        "origin": "Listed on the CUSHIONI store",
        "cat": "household",
    },
    "bamboo-mat": {
        "en": "Single-size bamboo mat. The store describes a smooth, processed natural bamboo surface for living rooms and bedrooms.",
        "ko": "싱글 사이즈 대나무 돗자리입니다. 스토어는 가공한 천연 대나무 표면으로 거실과 침실에 깐다고 안내합니다.",
        "ja": "シングルサイズの竹ござです。ストアでは加工した天然竹の表面で、居間と寝室に敷くと案内されています。",
        "es": "Estera de bambú individual. La tienda describe una superficie de bambú natural alisado para salón y dormitorio.",
        "title": {"en": "Single bamboo mat", "ko": "싱글 대나무 돗자리", "ja": "シングル竹ござ", "es": "Estera de bambú individual"},
        "mat": "Natural bamboo",
        "origin": "Listed on the CUSHIONI store",
        "cat": "living",
    },
    "bamboo-pillow": {
        "en": "Bamboo body pillow. The store describes it as a domestic Damyang bamboo piece for hot nights.",
        "ko": "대나무 죽부인입니다. 스토어는 국내 담양산으로 안내합니다.",
        "ja": "竹夫人です。ストアでは韓国・潭陽産と案内されています。",
        "es": "Almohada corporal de bambú. La tienda la describe como pieza de bambú de Damyang.",
        "title": {"en": "Bamboo body pillow", "ko": "대나무 죽부인", "ja": "竹夫人", "es": "Almohada corporal de bambú"},
        "mat": "Bamboo",
        "origin": "Described as Damyang, Korea",
        "cat": "household",
    },
    "grain": {
        "en": "Airtight grain canister, 1.3 liters, sold as a multi-piece set on the CUSHIONI store.",
        "ko": "1.3리터 밀폐 잡곡용기 세트입니다. 쿠셔니 스토어에 올라가 있습니다.",
        "ja": "1.3Lの密閉雑穀容器セットです。CUSHIONIストアに掲載されています。",
        "es": "Bote hermético para grano de 1,3 litros, en juego, publicado en la tienda CUSHIONI.",
        "title": {"en": "1.3 L airtight grain canisters", "ko": "1.3L 밀폐 잡곡용기", "ja": "1.3L密閉雑穀容器", "es": "Botes herméticos de 1,3 L"},
        "mat": "Airtight canister",
        "origin": "Listed on the CUSHIONI store",
        "cat": "household",
    },
    "freezer": {
        "en": "Freezer rice containers for the microwave, a 16 + 16 piece set, listed on the CUSHIONI store.",
        "ko": "전자레인지용 냉동밥 밀폐용기 16개+16개 세트입니다.",
        "ja": "電子レンジ対応の冷凍ごはん容器、16個+16個セットです。",
        "es": "Recipientes para arroz congelado, aptos para microondas, juego de 16 + 16.",
        "title": {"en": "Freezer rice containers, 32 pieces", "ko": "냉동밥 밀폐용기 32개", "ja": "冷凍ごはん容器32個", "es": "Recipientes para arroz, 32 piezas"},
        "mat": "Food storage container",
        "origin": "Listed on the CUSHIONI store",
        "cat": "household",
    },
}


def esc(s):
    return html.escape(s or "", quote=True)


def clean_text(t):
    t = (t or "").replace("\\", " ")
    t = re.sub(r"\[[^\]]*\]\([^)]*\)", " ", t)
    t = re.sub(r"https?://\S+", " ", t)
    t = re.sub(r"#\S+", " ", t)
    t = re.sub(r"~~.*?~~", " ", t)
    t = re.sub(r"\d[\d,]*\s*원", " ", t)
    t = re.sub(r"\d+\s*%", " ", t)
    t = re.sub(r"배송비", " ", t)
    t = re.sub(r"(무료배송|오늘출발|평일\s*\d+시\s*마감|평점\s*[\d.]*|리뷰\s*[\d,]*|찜하기|다른 옵션 상품보기|할인)", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" -–—.,:)")
    if "http" in t or "%" in t:
        return ""
    return t


def family_of(name):
    n = name
    if "전기요" in n:
        return "electric"
    if "캠핑매트" in n or ("돗자리" in n and "캠핑" in n):
        return "camp-mat"
    if "캠핑의자" in n:
        return "camp-chair"
    if "폴딩" in n and "박스" in n:
        return "camp-box"
    if "무릎담요" in n or "블랭킷" in n or "캠핑이불" in n:
        return "blanket"
    if "헤링본" in n:
        return "herringbone"
    if "유아" in n or "아기 매트" in n:
        return "kids"
    if "타일카페트" in n:
        return "tile-carpet"
    if "테라조" in n:
        return "terrazzo"
    if "데코타일" in n:
        return "deco"
    if "아트보" in n or "흡음" in n or "방음" in n:
        return "acoustic"
    if "보행" in n or "실버카" in n:
        return "walker"
    if "샤워" in n:
        return "shower"
    if "죽부인" in n:
        return "bamboo-pillow"
    if "대나무" in n or "대자리" in n:
        return "bamboo-mat"
    if "잡곡" in n or "쌀보관" in n:
        return "grain"
    if "냉동밥" in n:
        return "freezer"
    if "실크" in n or "만능벽지" in n:
        return "silk"
    if any(k in n for k in ("폼블럭", "폼벽지", "단열벽지", "벽지")):
        return "foam"
    return "foam"


def color_of(name):
    for ko, en, ja, es in COLORS:
        if ko in name:
            return {"ko": ko, "en": en, "ja": ja, "es": es}
    return {"ko": "", "en": "", "ja": "", "es": ""}


def size_of(name):
    n = name.replace("×", "x").replace("X", "x")
    thick = ""
    mt = re.search(r"두께\s*(\d+(?:\.\d+)?)\s*(mm|cm|t)?", n, re.I)
    if mt:
        unit = (mt.group(2) or "mm").lower()
        if unit == "t":
            unit = "mm"
        thick = f", {mt.group(1)} {unit} thick"
    m = re.search(
        r"(\d+(?:\.\d+)?)\s*(mm|cm|m)?\s*x\s*(\d+(?:\.\d+)?)\s*(mm|cm|m)?(?:\s*x\s*(\d+(?:\.\d+)?)\s*(mm|cm|m)?)?",
        n,
        re.I,
    )
    if m:
        a, ua, b, ub, c, uc = m.groups()
        unit = (ub or ua or "cm").lower()
        ua = (ua or unit).lower()
        ub = (ub or unit).lower()
        s = f"{a} {ua} × {b} {ub}"
        if c:
            s += f" × {c} {(uc or ub).lower()}"
        return s + thick
    m2 = re.search(r"(?:폭\s*)?(\d+(?:\.\d+)?)\s*cm\s+(\d+(?:\.\d+)?)\s*m", n, re.I)
    if m2:
        return f"{m2.group(1)} cm × {m2.group(2)} m" + thick
    m3 = re.search(r"(\d+(?:\.\d+)?)\s*리터", name)
    if m3:
        return m3.group(1) + " L"
    m4 = re.search(r"(?<![\d.])(\d+(?:\.\d+)?)\s*L\b", name)
    if m4:
        return m4.group(1) + " L"
    return thick.lstrip(", ")


def pack_of(name):
    bits = []
    for m in re.finditer(r"(\d+)\s*\+\s*(\d+)\s*개", name):
        bits.append(f"{m.group(1)}+{m.group(2)}")
    for m in re.finditer(r"(\d+)\s*(장세트|매입|장|매|개입|개)", name):
        label = {"장세트": "sheets / set", "매입": "pieces", "장": "sheets", "매": "pieces", "개입": "pieces", "개": "pieces"}[m.group(2)]
        bits.append(f"{m.group(1)} {label}")
    if "2개" in name and "2단" in name:
        bits.append("2 mats")
    # dedupe
    out = []
    for b in bits:
        if b not in out:
            out.append(b)
    return ", ".join(out[:3])


def pattern_of(name, lang):
    pairs = {
        "en": [("격자", "grid"), ("버티칼", "vertical"), ("러시안", "Russian stacked stone"), ("대리석", "marble"),
               ("우드", "wood grain"), ("샌드", "check sand"), ("체크샌드", "check sand"), ("모노", "mono"),
               ("파벽돌", "brick"), ("벽돌", "brick"), ("스톤", "stone"), ("엠보싱", "embossed"), ("3단", "3-fold"), ("2단", "2-fold")],
        "ko": [("격자", "격자"), ("버티칼", "버티칼"), ("러시안", "러시안 단층석"), ("대리석", "대리석"),
               ("우드", "우드"), ("샌드", "체크샌드"), ("모노", "모노"), ("파벽돌", "파벽돌"), ("벽돌", "벽돌"), ("스톤", "스톤"),
               ("엠보싱", "엠보싱"), ("3단", "3단"), ("2단", "2단")],
        "ja": [("격자", "格子"), ("버티칼", "縦柄"), ("러시안", "ロシアンストーン"), ("대리석", "大理石"),
               ("우드", "木目"), ("샌드", "チェックサンド"), ("모노", "モノ"), ("파벽돌", "レンガ"), ("벽돌", "レンガ"), ("스톤", "ストーン"),
               ("엠보싱", "エンボス"), ("3단", "3つ折り"), ("2단", "2つ折り")],
        "es": [("격자", "cuadrícula"), ("버티칼", "vertical"), ("러시안", "piedra rusa"), ("대리석", "mármol"),
               ("우드", "madera"), ("샌드", "arena a cuadros"), ("모노", "mono"), ("파벽돌", "ladrillo"), ("벽돌", "ladrillo"),
               ("스톤", "piedra"), ("엠보싱", "gofrado"), ("3단", "3 pliegues"), ("2단", "2 pliegues")],
    }
    hits = []
    for ko, label in pairs[lang]:
        if ko == "샌드" and "체크샌드" not in name and "샌드 폼" not in name and "샌드폼" not in name:
            continue
        if ko in name and label not in hits:
            hits.append(label)
    return ", ".join(hits[:3])


def line_key(name):
    fam = family_of(name)
    for k in ("러시안", "대리석", "우드", "체크샌드", "샌드", "모노", "파벽돌", "스톤", "실크", "헤링본", "테라조", "데코", "타일카페트"):
        if k in name:
            return fam + ":" + k
    return fam


FOAM_KIND = {
    "en": [
        ("러시안", "Russian stacked-stone foam panel"),
        ("대리석", "Marble foam wall panel"),
        ("체크샌드", "Check-sand foam wall panel"),
        ("샌드", "Check-sand foam wall panel"),
        ("우드", "Wood-grain foam wall panel"),
        ("모노", "Mono foam wall panel"),
        ("파벽돌", "Brick foam wall panel"),
        ("벽돌", "Brick foam wall panel"),
        ("스톤", "Stone foam wall panel"),
    ],
    "ko": [
        ("러시안", "러시안 단층석 폼블럭"),
        ("대리석", "대리석 폼블럭"),
        ("체크샌드", "체크샌드 폼블럭"),
        ("샌드", "체크샌드 폼블럭"),
        ("우드", "우드 폼블럭"),
        ("모노", "모노 폼블럭"),
        ("파벽돌", "파벽돌 폼블럭"),
        ("벽돌", "벽돌 폼블럭"),
        ("스톤", "스톤 폼블럭"),
    ],
    "ja": [
        ("러시안", "ロシアンストーン壁パネル"),
        ("대리석", "大理石フォームパネル"),
        ("체크샌드", "チェックサンド壁パネル"),
        ("샌드", "チェックサンド壁パネル"),
        ("우드", "木目フォームパネル"),
        ("모노", "モノフォームパネル"),
        ("파벽돌", "レンガフォームパネル"),
        ("벽돌", "レンガフォームパネル"),
        ("스톤", "ストーンフォームパネル"),
    ],
    "es": [
        ("러시안", "Panel de piedra rusa"),
        ("대리석", "Panel de mármol"),
        ("체크샌드", "Panel arena a cuadros"),
        ("샌드", "Panel arena a cuadros"),
        ("우드", "Panel veta de madera"),
        ("모노", "Panel mono"),
        ("파벽돌", "Panel ladrillo"),
        ("벽돌", "Panel ladrillo"),
        ("스톤", "Panel de piedra"),
    ],
}
EXTRA_BITS = {
    "en": {"v2": "v2", "roll": "roll", "set12": "12-sheet set", "sheet1": "1 sheet", "colors9": "9 colors", "accent": "accent wall"},
    "ko": {"v2": "v2", "roll": "롤", "set12": "12장 세트", "sheet1": "1장", "colors9": "9컬러", "accent": "포인트"},
    "ja": {"v2": "v2", "roll": "ロール", "set12": "12枚セット", "sheet1": "1枚", "colors9": "9色", "accent": "アクセント"},
    "es": {"v2": "v2", "roll": "rollo", "set12": "juego de 12", "sheet1": "1 pieza", "colors9": "9 colores", "accent": "acento"},
}


def _bits(name, lang):
    b = EXTRA_BITS[lang]
    out = []
    if re.search(r"v2", name, re.I):
        out.append(b["v2"])
    if "롤" in name:
        out.append(b["roll"])
    if "12장" in name:
        out.append(b["set12"])
    elif re.search(r"(?<!\d)1장", name):
        out.append(b["sheet1"])
    if "9컬러" in name or "9색" in name:
        out.append(b["colors9"])
    if "포인트" in name:
        out.append(b["accent"])
    return out


def title_of(p, lang):
    if p.get("titles") and p["titles"].get(lang):
        return p["titles"][lang]
    return _title_parts(p, lang)


def _title_parts(p, lang):
    name = p["name_ko"]
    fam = p["fam"]
    if fam == "foam":
        base = None
        for ko, label in FOAM_KIND[lang]:
            if ko == "샌드" and "체크샌드" not in name and "샌드 폼" not in name and "샌드폼" not in name:
                continue
            if ko in name:
                base = label
                break
        if not base:
            base = {"en": "Self-adhesive foam wall panel", "ko": "점착식 폼 벽패널", "ja": "粘着フォーム壁パネル", "es": "Panel de espuma autoadhesivo"}[lang]
    elif fam == "shower":
        if "미니" in name:
            base = {"en": "Mini travel shower filter set", "ko": "여행용 미니 샤워필터 세트", "ja": "旅行用ミニシャワーフィルターセット", "es": "Set mini de filtro de ducha"}[lang]
        elif "보습" in name:
            base = {"en": "Moisturizing vitamin shower filter", "ko": "보습 비타민 샤워필터", "ja": "保湿ビタミンシャワーフィルター", "es": "Filtro de ducha vitamínico hidratante"}[lang]
        elif "3종" in name:
            base = {"en": "Vitamin shower filter, 3 types", "ko": "비타민 샤워필터 3종", "ja": "ビタミンシャワーフィルター3種", "es": "Filtro de ducha vitamínico, 3 tipos"}[lang]
        elif "1개+1개" in name:
            base = {"en": "Vitamin shower filter, 2 pieces", "ko": "비타민 샤워필터 2개", "ja": "ビタミンシャワーフィルター2個", "es": "Filtro de ducha vitamínico, 2 piezas"}[lang]
        elif "샤워기" in name and "필터" in name:
            base = {"en": "Travel shower head with filter", "ko": "여행용 샤워기 필터", "ja": "旅行用シャワーヘッドとフィルター", "es": "Alcachofa de ducha de viaje con filtro"}[lang]
        else:
            base = FAM_COPY[fam]["title"][lang]
    elif fam == "silk":
        base = FAM_COPY["silk"]["title"][lang]
        if "만능" in name and lang == "en":
            base = "All-purpose silk insulation wallpaper"
    else:
        base = FAM_COPY[fam]["title"][lang]
    def folded(s):
        return re.sub(r"[^a-z0-9가-힣]", "", (s or "").lower())

    parts = [base]
    seen = {folded(base)}
    def add(piece):
        key = folded(piece)
        if piece and key and not any(key in s or s in key for s in seen if len(s) > 2 and len(key) > 2):
            parts.append(piece)
            seen.add(key)
    add(p["color"][lang])
    add(p["size"])
    pat = pattern_of(name, lang)
    if pat:
        for piece in pat.split(", "):
            add(piece)
    bits = _bits(name, lang)
    if fam != "shower" and p["pack"] and not any(k in bits for k in (EXTRA_BITS[lang]["set12"], EXTRA_BITS[lang]["sheet1"])):
        add(p["pack"])
    for bit in bits:
        add(bit)
    if fam == "foam" and len(parts) == 1:
        add({"en": "peel-and-stick insulation sheet", "ko": "점착 단열벽지", "ja": "貼る断熱シート", "es": "lámina aislante autoadhesiva"}[lang])
    return ", ".join(parts)


def assign_titles(products):
    for lang in ("en", "ko", "ja", "es"):
        groups = {}
        for p in products:
            groups.setdefault(_title_parts(p, lang), []).append(p)
        for title, group in groups.items():
            if len(group) == 1:
                group[0].setdefault("titles", {})[lang] = title
                continue
            used = {}
            for p in group:
                label = title
                # last resort so two listings never share a card name
                n = 2
                candidate = label
                while candidate in used:
                    candidate = f"{label} ({n})"
                    n += 1
                used[candidate] = p
                p.setdefault("titles", {})[lang] = candidate


def load_products():
    items = json.loads(PARTIAL.read_text())
    by = {}
    for raw in items + EXTRA:
        pid = raw["id"]
        cur = by.get(pid)
        images = [u.split("?")[0] for u in raw.get("images") or []]
        blurb = clean_text(raw.get("blurb_ko") or "")
        if cur is None:
            by[pid] = {"id": pid, "name_ko": raw["name_ko"], "images": images, "blurb_ko": blurb}
        else:
            if raw["name_ko"] and len(raw["name_ko"]) >= len(cur["name_ko"]):
                cur["name_ko"] = raw["name_ko"]
            if len(images) > len(cur["images"]):
                cur["images"] = images
            if len(blurb) > len(cur["blurb_ko"]):
                cur["blurb_ko"] = blurb
    for sid in list(by):
        if str(sid) in REMOVED_STORE_IDS:
            del by[sid]
    products = []
    for raw in by.values():
        fam = family_of(raw["name_ko"])
        meta = FAM_COPY[fam]
        p = {
            "store_id": raw["id"],
            "name_ko": raw["name_ko"],
            "images": raw["images"],
            "blurb_ko": raw["blurb_ko"],
            "fam": fam,
            "cat": meta["cat"],
            "color": color_of(raw["name_ko"]),
            "size": size_of(raw["name_ko"]),
            "pack": pack_of(raw["name_ko"]),
            "mat": meta["mat"] if meta.get("factory") else "",
            "origin": meta["origin"] if meta.get("factory") else "",
            "fallback": False,
        }
        products.append(p)
    own_path = ROOT / "cushioni" / "own-images.json"
    own = json.loads(own_path.read_text()) if own_path.exists() else {}
    for p in products:
        url = own.get(p["store_id"])
        if url:
            p["images"] = [url.split("?")[0]]
            p["own_photo"] = True
    # family photo fallback
    pool = {}
    for p in products:
        if p["images"]:
            pool.setdefault(line_key(p["name_ko"]), p["images"][0])
    for p in products:
        if not p["images"]:
            img = pool.get(line_key(p["name_ko"])) or pool.get(p["fam"])
            if img:
                p["images"] = [img]
                p["fallback"] = True
    cat_pool = {}
    for p in products:
        if p["images"] and p["cat"] not in cat_pool:
            cat_pool[p["cat"]] = p["images"][0]
    for p in products:
        if not p["images"] and p["cat"] in cat_pool:
            p["images"] = [cat_pool[p["cat"]]]
            p["fallback"] = True
    existing = {}
    pj = ROOT / "cushioni" / "products.json"
    if pj.exists():
        for row in json.loads(pj.read_text(encoding="utf-8")):
            existing[str(row["store_id"])] = row["id"]
    used = set(existing.values())
    nxt = 1

    def alloc():
        nonlocal nxt
        while f"C-{nxt:04d}" in used:
            nxt += 1
        cid = f"C-{nxt:04d}"
        used.add(cid)
        nxt += 1
        return cid

    for p in products:
        p["cid"] = existing.get(p["store_id"]) or alloc()
        p["ph"] = p["cid"].lower()
        if p["cid"] in OWNER_PHOTO_IDS:
            p["fallback"] = False
            p["owner_photo"] = True
    assign_titles(products)
    return products


def arrange_products(products):
    def diversify(items):
        groups = {}
        for p in items:
            groups.setdefault(line_key(p["name_ko"]), []).append(p)
        for group in groups.values():
            group.sort(key=lambda p: (1 if p.get("chip") else 0, p["cid"]))
        keys = list(groups)
        out = []
        while any(groups[k] for k in keys):
            for k in keys:
                if groups[k]:
                    out.append(groups[k].pop(0))
        return out

    def mix(group):
        cols = {slug: diversify([p for p in group if p["cat"] == slug]) for slug, _ in CATS}
        out = []
        while any(cols[slug] for slug, _ in CATS):
            for slug, _ in CATS:
                if cols[slug]:
                    out.append(cols[slug].pop(0))
        return out

    owner = [p for p in products if p.get("owner_photo")]
    other = [p for p in products if not p.get("fallback") and not p.get("owner_photo")]
    shared = [p for p in products if p.get("fallback")]
    return mix(owner) + mix(other) + mix(shared)


def install_owner_photos(products):
    """Replace line photos with the owner's JPEGs. Metadata is dropped; chips are not enlarged."""
    IMG_L.mkdir(parents=True, exist_ok=True)
    IMG_T.mkdir(parents=True, exist_ok=True)
    src_dir = Path("/tmp/owner-photos/web")
    sources_path = ROOT / "cushioni" / "image-sources.json"
    sources = json.loads(sources_path.read_text()) if sources_path.exists() else {}
    installed = 0
    missing = []
    for p in products:
        if p["cid"] not in OWNER_PHOTO_IDS:
            continue
        raw = src_dir / f"{p['ph']}.jpg"
        if not raw.exists():
            if sources.get(p["ph"]) != "owner":
                missing.append(p["cid"])
            continue
        im = Image.open(raw).convert("RGB")
        clean = Image.frombytes("RGB", im.size, im.tobytes())
        large = clean.copy()
        large.thumbnail((960, 960))
        large.save(IMG_L / f"{p['ph']}.webp", "WEBP", quality=78, method=6)
        large.save(IMG_L / f"{p['ph']}.jpg", "JPEG", quality=82, optimize=True)
        thumb = clean.copy()
        thumb.thumbnail((420, 420))
        thumb.save(IMG_T / f"{p['ph']}.webp", "WEBP", quality=74, method=6)
        thumb.save(IMG_T / f"{p['ph']}.jpg", "JPEG", quality=78, optimize=True)
        sources[p["ph"]] = "owner"
        installed += 1
    sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2))
    print("owner photos written", installed, "missing", missing)
    return installed


def download_images(products):
    IMG_L.mkdir(parents=True, exist_ok=True)
    IMG_T.mkdir(parents=True, exist_ok=True)
    cache = {}
    missing = []
    sources_path = ROOT / "cushioni" / "image-sources.json"
    sources = json.loads(sources_path.read_text()) if sources_path.exists() else {}

    def fetch(url):
        if url in cache:
            return cache[url]
        req = urllib.request.Request(url + "?type=f750_750", headers={"User-Agent": UA, "Referer": "https://smartstore.naver.com/"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
            im = Image.open(BytesIO(data)).convert("RGB")
        except Exception as e:
            cache[url] = None
            print("img fail", url, e)
            return None
        cache[url] = im
        return im

    for p in products:
        if not p["images"]:
            missing.append(p["cid"] + " " + p["name_ko"])
            continue
        ready = IMG_L / f"{p['ph']}.webp"
        src = p["images"][0]
        prev = sources.get(p["ph"])
        if prev == "owner" and ready.exists() and (IMG_T / f"{p['ph']}.jpg").exists():
            with Image.open(ready) as im0:
                p["w"], p["h"] = im0.size
            with Image.open(IMG_T / f"{p['ph']}.jpg") as im1:
                p["tw"], p["th"] = im1.size
            p["fallback"] = False
            p["owner_photo"] = True
            p["chip"] = max(p["w"], p["h"]) <= CHIP_MAX
            continue
        if ready.exists() and (IMG_T / f"{p['ph']}.jpg").exists() and prev == src:
            with Image.open(ready) as im0:
                p["w"], p["h"] = im0.size
            with Image.open(IMG_T / f"{p['ph']}.jpg") as im1:
                p["tw"], p["th"] = im1.size
            continue
        im = fetch(src)
        if im is None:
            missing.append(p["cid"] + " " + p["name_ko"])
            p["images"] = []
            continue
        w, h = im.size
        p["w"], p["h"] = w, h
        large = im.copy()
        large.thumbnail((960, 960))
        large.save(IMG_L / f"{p['ph']}.webp", "WEBP", quality=78, method=6)
        large.save(IMG_L / f"{p['ph']}.jpg", "JPEG", quality=82, optimize=True)
        thumb = im.copy()
        thumb.thumbnail((420, 420))
        thumb.save(IMG_T / f"{p['ph']}.webp", "WEBP", quality=74, method=6)
        thumb.save(IMG_T / f"{p['ph']}.jpg", "JPEG", quality=78, optimize=True)
        p["tw"], p["th"] = thumb.size
        sources[p["ph"]] = src
        sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2))
    return missing


def desc_of(p, lang):
    base = FAM_COPY[p["fam"]][lang]
    bits = []
    if p["size"]:
        bits.append(p["size"])
    if p["color"][lang]:
        bits.append(p["color"][lang])
    pat = pattern_of(p["name_ko"], lang)
    if pat:
        bits.append(pat)
    if p["pack"] and lang == "en":
        bits.append(p["pack"])
    spec = ", ".join(bits)
    if lang == "ko" and p["blurb_ko"]:
        text = p["blurb_ko"]
        if spec:
            text = text + " 규격: " + spec + "."
        return text
    if spec:
        return base + " " + spec + "."
    return base


def alt_of(p, lang):
    name = title_of(p, lang)
    if p.get("fallback"):
        if lang == "ko":
            return name + " 제품군 사진"
        if lang == "ja":
            return name + "のシリーズ写真"
        if lang == "es":
            return "Foto de la línea: " + name
        return "Photo of this CUSHIONI product line: " + name
    return name


LANGS = ["en", "ko", "ja", "es"]
LOCALE = {"en": "en_US", "ko": "ko_KR", "ja": "ja_JP", "es": "es_ES"}


def base_of(lang):
    return "/cushioni/" if lang == "en" else f"/cushioni/{lang}/"


def absu(path):
    return "https://www.qone.kr" + path


def hreflang(path_fn):
    bits = []
    for lang in LANGS:
        bits.append(f'<link rel="alternate" hreflang="{lang}" href="{absu(path_fn(lang))}">')
    bits.append(f'<link rel="alternate" hreflang="x-default" href="{absu(path_fn("en"))}">')
    return "".join(bits)


ICON = "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%232443E8'/%3E%3Ccircle cx='32' cy='14' r='5' fill='%23fff'/%3E%3Ctext x='32' y='50' font-size='30' font-family='Arial,sans-serif' font-weight='bold' fill='white' text-anchor='middle'%3EC%3C/text%3E%3C/svg%3E"
GTAG = """<script>(function(){var d=0;function L(){if(d)return;d=1;var s=document.createElement("script");s.async=1;s.src="https://www.googletagmanager.com/gtag/js?id=G-3WS8ZB6PX8";document.head.appendChild(s)}["pointerdown","keydown","scroll","touchstart"].forEach(function(e){addEventListener(e,L,{once:true,passive:true})});addEventListener("load",function(){setTimeout(L,3500)})})();</script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-3WS8ZB6PX8');</script>"""
PLUS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
MAIL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18v12H3z"/><path d="M3 7l9 6 9-6"/></svg>'


def head(title, desc, canon, path_fn, image):
    langs = hreflang(path_fn)
    ogloc = "".join(f'<meta property="og:locale:alternate" content="{LOCALE[l]}">' for l in LANGS if LOCALE[l] != LOCALE["en"] or True)
    return f"""<!doctype html>
<html lang="{UI[canon_lang(canon)]['html']}" data-lang="{UI[canon_lang(canon)]['lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{esc(canon)}">{langs}
<meta property="og:type" content="website"><meta property="og:site_name" content="QONE CUSHIONI"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{esc(canon)}"><meta property="og:locale" content="{LOCALE[canon_lang(canon)]}"><meta property="og:image" content="{esc(image)}">
<meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#2443E8">
<link rel="icon" href="data:image/svg+xml,{ICON}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Zen+Kaku+Gothic+New:wght@400;700&display=swap">
<link rel="stylesheet" href="/assets/yw/yw.css?v=cs1">
<link rel="stylesheet" href="/assets/cs/cs.css?v=cs2">
{GTAG}
"""


def canon_lang(url):
    if "/cushioni/ko/" in url:
        return "ko"
    if "/cushioni/ja/" in url:
        return "ja"
    if "/cushioni/es/" in url:
        return "es"
    return "en"


def header(lang, current):
    u = UI[lang]
    b = base_of(lang)
    def a(key, href, label):
        cur = ' aria-current="page"' if current == key else ""
        return f'<a href="{href}"{cur}>{label}</a>'
    langs = []
    # language switcher keeps the same leaf; caller passes via current page builders
    return f"""<a class="skip" href="#main">Skip to content</a><header class="yh"><div class="yh-in">
  <a class="brand" href="{b}"><span class="bq">QONE</span><span class="bt">{esc(u['sub'])}</span></a>
  <nav class="yn" aria-label="CUSHIONI">{a('cat', b+'catalog/', esc(u['nav_cat']))}{a('req', b+'request/', esc(u['nav_req']))}</nav>
  {{LANGS}}
  <button class="lbtn" type="button" data-open-list aria-haspopup="dialog"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8h12l-1 12H7L6 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg><span class="lbt">{esc(u['list'])}</span><b class="lcount" aria-live="polite">0</b></button>
</div><nav class="mnav" aria-label="Menu">{a('home', b, esc(u['home']))}{a('cat', b+'catalog/', esc(u['nav_cat']))}{a('req', b+'request/', esc(u['nav_req']))}</nav></header>"""


def lang_switch(leaf):
    bits = ['<div class="lg" role="group" aria-label="Language">']
    for lang in LANGS:
        href = (base_of(lang) + leaf).replace("//", "/")
        if not href.endswith("/") and not href.endswith(".html"):
            pass
        cur = ' aria-current="true"' if False else ""
        bits.append(f'<a href="{href}" hreflang="{lang}" lang="{lang}">{lang.upper()}</a>')
    bits.append("</div>")
    # mark current by replacing after we know lang — done in page()
    return "".join(bits)


def with_current_lang(block, lang, leaf):
    out = []
    for l in LANGS:
        href = base_of(l) + leaf
        cur = ' aria-current="true"' if l == lang else ""
        out.append(f'<a href="{href}" hreflang="{l}" lang="{l}"{cur}>{l.upper()}</a>')
    lg = '<div class="lg" role="group" aria-label="Language">' + "".join(out) + "</div>"
    return block.replace("{LANGS}", lg)


def footer(lang, products):
    u = UI[lang]
    b = base_of(lang)
    cats = "".join(
        f'<a href="{b}c/{slug}/">{esc(label[lang])}</a>'
        for slug, label in CATS
        if any(p["cat"] == slug for p in products)
    )
    return f"""<footer class="yf"><div class="wrap">
  <div class="yf-top"><a class="brand inv" href="{b}"><span class="bq">QONE</span><span class="bt">{esc(u['sub'])}</span></a>
    <p>{esc(u['foot'])}</p><a class="yf-mail" href="mailto:chl@qone.kr">{MAIL}chl@qone.kr</a></div>
  <nav class="yf-cats" aria-label="{esc(u['nav_cat'])}">{cats}</nav>
  <div class="yf-links"><a href="{b}catalog/">{esc(u['nav_cat'])}</a><a href="{b}request/">{esc(u['nav_req'])}</a><a href="/">{'QONE'}</a><a href="/inquiry/">Inquiry</a><a href="/privacy/">Privacy</a></div>
  <p class="disc">{esc(u['disc'])}</p>
  <p class="copy">© QONE Corporation</p>
</div></footer>"""


def drawer(lang):
    u = UI[lang]
    b = base_of(lang)
    return f"""<div class="dr" id="list" role="dialog" aria-modal="true" aria-labelledby="dr-h" hidden>
  <div class="dr-bg" data-close-list></div>
  <div class="dr-p"><div class="dr-hd"><h2 id="dr-h">{esc(u['list'])}</h2><button class="ib" type="button" data-close-list aria-label="{esc(u['close'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div>
    <p class="dr-empty">{esc(u['empty'])}</p><ul class="dr-ul"></ul>
    <div class="dr-ft"><a class="bt-y" href="{b}request/" data-send-list>{esc(u['send'])}</a><button class="bt-l" type="button" data-clear-list>{esc(u['clear'])}</button></div></div>
</div>"""


def modal(lang):
    u = UI[lang]
    return f"""<dialog class="md" id="md" aria-labelledby="md-n">
  <div class="md-in"><button class="ib md-x" type="button" data-md-close aria-label="{esc(u['close'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg></button>
  <div class="md-ph"><picture><source type="image/webp"><img alt="" width="440" height="440"></picture></div>
  <div class="md-tx"><p class="md-ref"></p><h2 id="md-n"></h2><p class="md-d" id="md-d"></p>
    <dl><dt>{esc(u['cat'])}</dt><dd data-f="c"></dd><dt>{esc(u['size'])}</dt><dd data-f="s"></dd><dt>{esc(u['color'])}</dt><dd data-f="opt"></dd>
    <dt>{esc(u['mat'])}</dt><dd data-f="mt"></dd><dt>{esc(u['pack'])}</dt><dd data-f="p"></dd><dt>{esc(u['origin'])}</dt><dd data-f="o"></dd></dl>
    <a class="md-more" href="#">{esc(u['full'])}</a>
    <button class="bt-y md-add" type="button" aria-pressed="false" data-l-add="{esc(u['add'])}" data-l-added="{esc(u['added'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg><span>{esc(u['add'])}</span></button>
    <div class="md-nav"><button class="ib" type="button" data-md-prev aria-label="{esc(u['prev'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button><button class="ib" type="button" data-md-next aria-label="{esc(u['next'])}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button></div>
  </div></div>
</dialog>"""


def yw_boot(lang, products=None):
    u = UI[lang]
    live = {p["cat"] for p in products} if products else set()
    cats = {slug: label[lang] for slug, label in CATS if slug in live}
    csi = {}
    if products:
        for p in products:
            csi[p["cid"]] = [title_of(p, lang), p["ph"], p["size"]]
    boot = {
        "lang": lang,
        "req": base_of(lang) + "request/",
        "base": base_of(lang),
        "cat": cats,
        "t": {
            "add": u["add"], "added": u["added"], "remove": u["remove"],
            "showing": u["showing"], "err_req": u["err_req"], "err_em": u["err_em"],
            "err_size": u["err_size"], "sending": u["sending"], "send": u["sendbtn"],
            "subj": u["subj"],
        },
    }
    return "<script>window.CS=" + json.dumps(boot, ensure_ascii=False) + ";window.CSI=" + json.dumps(csi, ensure_ascii=False) + ";</script>\n<script src=\"/assets/cs/cs.js?v=cs2\" defer></script>"


def card(p, lang, eager=False):
    u = UI[lang]
    name = title_of(p, lang)
    alt = alt_of(p, lang)
    sub = p["size"] or p["color"][lang] or FAM_COPY[p["fam"]]["title"][lang]
    opt = ", ".join(x for x in (p["color"][lang], pattern_of(p["name_ko"], lang)) if x)
    q = " ".join([name, p["name_ko"], p["cid"], p["size"], opt, p["pack"], FAM_COPY[p["fam"]]["title"]["en"]]).lower()
    lazy = "" if eager else ' loading="lazy" decoding="async"'
    pri = ' fetchpriority="high"' if eager else ""
    w, h = p.get("tw", 320), p.get("th", 320)
    chip = " is-chip" if p.get("chip") else ""
    return (
        f'<li class="pc{chip}" id="{p["cid"]}" data-id="{p["cid"]}" data-c="{p["cat"]}" data-q="{esc(q)}" '
        f'data-n="{esc(name)}" data-ko="{esc(p["name_ko"])}" data-s="{esc(p["size"])}" data-opt="{esc(opt)}" '
        f'data-mt="{esc(p["mat"])}" data-p="{esc(p["pack"])}" data-o="{esc(p["origin"])}" data-d="{esc(desc_of(p, lang))}" '
        f'data-alt="{esc(alt)}" data-ph="{p["ph"]}" data-w="{p.get("w",800)}" data-h="{p.get("h",800)}">'
        f'<button class="pc-o" type="button" aria-haspopup="dialog"><span class="pc-i"><picture>'
        f'<source type="image/webp" srcset="/assets/cs/img/t/{p["ph"]}.webp">'
        f'<img src="/assets/cs/img/t/{p["ph"]}.jpg" alt="{esc(alt)}" width="{w}" height="{h}"{pri}{lazy}></picture></span>'
        f'<span class="pc-n">{esc(name)}</span><span class="pc-s">{esc(sub)}</span>'
        f'<span class="pc-ko" lang="ko">{esc(p["name_ko"])}</span></button>'
        f'<button class="pc-a" type="button" aria-pressed="false" aria-label="{esc(u["add"])}: {esc(name)}">{PLUS}</button></li>'
    )


def product_ld(p, lang, url):
    data = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": title_of(p, lang),
        "description": desc_of(p, lang),
        "sku": p["cid"],
        "category": dict(CATS)[p["cat"]][lang] if False else next(label[lang] for slug, label in CATS if slug == p["cat"]),
        "color": p["color"][lang] or None,
        "size": p["size"] or None,
        "image": absu(f"/assets/cs/img/l/{p['ph']}.webp"),
        "url": url,
        "brand": {"@type": "Brand", "name": "CUSHIONI"},
        "inLanguage": lang,
        "additionalProperty": [
            {"@type": "PropertyValue", "name": "Korean name", "value": p["name_ko"]},
        ],
    }
    if FAM_COPY[p["fam"]].get("factory"):
        data["material"] = p["mat"]
        data["countryOfOrigin"] = "KR"
        data["manufacturer"] = {"@type": "Organization", "@id": "https://www.qone.kr/#org", "name": "QONE Corporation"}
    if p["pack"]:
        data["additionalProperty"].append({"@type": "PropertyValue", "name": "Pack", "value": p["pack"]})
    # drop nulls
    data = {k: v for k, v in data.items() if v}
    return json.dumps(data, ensure_ascii=False)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def page_shell(lang, title, desc, leaf, current, body, products, ld=""):
    b = base_of(lang)
    canon = absu(b + leaf)
    img = absu("/assets/cs/img/l/c-0001.webp")
    h = head(title, desc, canon, lambda l: base_of(l) + leaf, img)
    hdr = with_current_lang(header(lang, current), lang, leaf)
    html_doc = h + ld + "</head>\n<body>\n" + hdr + body + footer(lang, products) + drawer(lang) + yw_boot(lang, products) + "\n</body></html>\n"
    rel = (b + leaf).lstrip("/")
    write(ROOT / rel / "index.html", html_doc)


def build_catalog(products, lang, only=None):
    u = UI[lang]
    shown = [p for p in products if only is None or p["cat"] == only]
    counts = {slug: sum(1 for p in products if p["cat"] == slug) for slug, _ in CATS}
    if only:
        slug = only
        label = next(lab[lang] for s, lab in CATS if s == slug)
        h1 = label
        lead = u["lead"]
        leaf = f"c/{slug}/"
        title = f"{label} | CUSHIONI | QONE"
        crumb = f'<nav class="cr" aria-label="Breadcrumb"><ol><li><a href="{base_of(lang)}">{esc(u["crumb_home"])}</a></li><li><a href="{base_of(lang)}catalog/">{esc(u["nav_cat"])}</a></li><li aria-current="page">{esc(label)}</li></ol></nav>'
        chips = ""
        current = "cat"
    else:
        h1 = u["h1"]
        lead = u["lead"]
        leaf = "catalog/"
        title = f"{u['h1']} | QONE"
        crumb = f'<nav class="cr" aria-label="Breadcrumb"><ol><li><a href="{base_of(lang)}">{esc(u["crumb_home"])}</a></li><li aria-current="page">{esc(u["nav_cat"])}</li></ol></nav>'
        chips = '<div class="chips" role="group" aria-label="Category">' + f'<button type="button" class="chip" data-cat="" aria-pressed="true">{esc(u["all"])} <span>{len(products)}</span></button>'
        for slug, lab in CATS:
            if not counts[slug]:
                continue
            chips += f'<button type="button" class="chip" data-cat="{slug}" aria-pressed="false">{esc(lab[lang])} <span>{counts[slug]}</span></button>'
        chips += "</div>"
        current = "cat"
    cards = "".join(card(p, lang, eager=(i < 4 and not only)) for i, p in enumerate(shown))
    n = len(shown)
    total = len(products) if only is None else n
    desc = lead[:155]
    itemlist = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": h1,
        "url": absu(base_of(lang) + leaf),
        "inLanguage": lang,
        "numberOfItems": n,
        "publisher": {"@id": "https://www.qone.kr/#org"},
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": n,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "url": absu(base_of(lang) + "p/" + p["ph"] + "/"),
                    "name": title_of(p, lang),
                }
                for i, p in enumerate(shown, 1)
            ],
        },
    }
    ld = '<script type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False) + "</script>"
    body = f"""<main id="main" class="cat-pg">
<section class="ph peg"><div class="wrap">{crumb}<h1>{esc(h1)}</h1><p class="lead">{esc(lead)}</p></div></section>
<div class="fb"><div class="wrap">
  <div class="fb-r"><label class="srch"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/></svg><span class="vh">{esc(u['search'])}</span><input type="search" id="q" placeholder="{esc(u['ph'])}" autocomplete="off"></label>
  <p class="cnt" aria-live="polite" data-total="{n}">{u['showing'].replace('{n}', str(n)).replace('{t}', str(total))}</p></div>
  {chips}
</div></div>
<div class="wrap"><ul class="grid" id="grid">{cards}</ul>
<div class="none" hidden><p>{esc(u['none'])}</p><button class="bt-l" type="button" data-reset>{esc(u['reset'])}</button></div></div>
<section class="end"><div class="wrap"><div class="tag tag-end">
  <h2>{esc(u['end_h'])}</h2><p>{esc(u['end_p'])}</p>
  <div class="cta"><a class="bt-b" href="{base_of(lang)}request/">{esc(u['req'])}</a><a class="bt-l" href="mailto:chl@qone.kr">{MAIL}chl@qone.kr</a></div>
</div></div></section>
</main>"""
    # modal only on catalog pages
    rel_body = body + modal(lang)
    page_shell(lang, title, desc, leaf, current, rel_body, products, ld)


def build_product(p, lang, products):
    u = UI[lang]
    name = title_of(p, lang)
    b = base_of(lang)
    leaf = f"p/{p['ph']}/"
    url = absu(b + leaf)
    desc = desc_of(p, lang)[:160]
    rows = [
        (u["cat"], next(lab[lang] for s, lab in CATS if s == p["cat"])),
        (u["size"], p["size"] or "—"),
        (u["color"], ", ".join(x for x in (p["color"][lang], pattern_of(p["name_ko"], lang)) if x) or "—"),
        (u["mat"], p["mat"] or "—"),
        (u["pack"], p["pack"] or "—"),
        (u["origin"], p["origin"] or "—"),
    ]
    dl = "".join(f"<dt>{esc(k)}</dt><dd>{esc(v)}</dd>" for k, v in rows)
    alt = alt_of(p, lang)
    crumb = f'<nav class="cr" aria-label="Breadcrumb"><ol><li><a href="{b}">{esc(u["crumb_home"])}</a></li><li><a href="{b}catalog/">{esc(u["nav_cat"])}</a></li><li aria-current="page">{esc(name)}</li></ol></nav>'
    body = f"""<main id="main">
<section class="ph peg"><div class="wrap">{crumb}</div></section>
<div class="wrap pd">
  <div class="pd-ph{' is-chip' if p.get('chip') else ''}"><picture><source type="image/webp" srcset="/assets/cs/img/l/{p['ph']}.webp"><img src="/assets/cs/img/l/{p['ph']}.jpg" alt="{esc(alt)}" width="{p.get('w',800)}" height="{p.get('h',800)}"></picture></div>
  <div>
    <p class="kick">{esc(p['cid'])}</p>
    <h1>{esc(name)}</h1>
    <p class="ko" lang="ko">{esc(p['name_ko'])}</p>
    <p class="lead">{esc(desc_of(p, lang))}</p>
    <dl>{dl}</dl>
    <div class="cta"><a class="bt-y" href="{b}catalog/#{p['cid']}">{esc(u['page_cta'])}</a><a class="bt-b" href="{b}request/?items={p['cid']}">{esc(u['req'])}</a><a class="bt-l" href="mailto:chl@qone.kr">{MAIL}chl@qone.kr</a></div>
    <p class="note">{esc(u['end_p'])}</p>
  </div>
</div>
</main>"""
    ld = '<script type="application/ld+json">' + product_ld(p, lang, url) + "</script>"
    page_shell(lang, f"{name} | CUSHIONI | QONE", desc, leaf, "cat", body, [p], ld)


def build_landing(products, lang):
    u = UI[lang]
    b = base_of(lang)
    counts = {slug: sum(1 for p in products if p["cat"] == slug) for slug, _ in CATS}
    bays = []
    for slug, lab in CATS:
        if not counts[slug]:
            continue
        sample = next(p for p in products if p["cat"] == slug and p["images"])
        bays.append(
            f'<li class="bay"><a href="{b}c/{slug}/"><span class="bay-w"><span><picture><source type="image/webp" srcset="/assets/cs/img/t/{sample["ph"]}.webp"><img src="/assets/cs/img/t/{sample["ph"]}.jpg" alt="{esc(alt_of(sample, lang))}" width="180" height="180"></picture></span></span>'
            f'<span class="bay-t"><span class="bay-n">{esc(lab[lang])}</span><span class="bay-c">{counts[slug]}</span></span></a></li>'
        )
    body = f"""<main id="main">
<section class="hero peg"><div class="wrap">
  <p class="kick">QONE · Yeoju</p>
  <h1>{esc(u['landing_h'])}</h1>
  <p class="lead">{esc(u['landing_l'])}</p>
  <div class="cta"><a class="bt-y" href="{b}catalog/">{esc(u['view'])}</a><a class="bt-l" href="{b}request/">{esc(u['req'])}</a></div>
</div></section>
<section class="sec"><div class="wrap"><ul class="bays">{''.join(bays)}</ul></div></section>
<section class="end"><div class="wrap"><div class="tag tag-end"><h2>{esc(u['end_h'])}</h2><p>{esc(u['end_p'])}</p>
  <div class="cta"><a class="bt-b" href="{b}request/">{esc(u['req'])}</a><a class="bt-l" href="mailto:chl@qone.kr">{MAIL}chl@qone.kr</a></div>
</div></div></section>
</main>"""
    page_shell(lang, f"{u['landing_h']} | QONE", u["landing_l"], "", "home", body, products)


def build_request(lang, products):
    u = UI[lang]
    b = base_of(lang)
    steps = "".join(f"<li>{esc(s)}</li>" for s in u["steps"])
    body = f"""<main id="main">
<section class="ph peg"><div class="wrap"><nav class="cr" aria-label="Breadcrumb"><ol><li><a href="{b}">{esc(u['crumb_home'])}</a></li><li aria-current="page">{esc(u['quote_h'])}</li></ol></nav><h1>{esc(u['quote_h'])}</h1><p class="lead">{esc(u['quote_l'])}</p></div></section>
<div class="wrap rq-g">
<form id="ywf" class="ywf" action="https://formsubmit.co/chl@qone.kr" method="POST" enctype="multipart/form-data" novalidate>
  <input type="hidden" name="_subject" value="{esc(u['subj'])}">
  <input type="hidden" name="_next" value="{absu(b+'thanks/')}">
  <input type="hidden" name="_template" value="table">
  <input type="hidden" name="_captcha" value="false"><input type="hidden" name="_replyto" value="">
  <input type="hidden" name="_autoresponse" value="{esc(u['thanks_p'])}"><input type="hidden" name="language" value="{lang}">
  <div class="hp" aria-hidden="true"><label>Leave empty <input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>
  <div class="f"><label for="f-co">{esc(u['co'])}<em class="rq">*</em></label><input id="f-co" name="company" required autocomplete="organization"></div>
  <div class="f"><label for="f-nm">{esc(u['nm'])}<em class="rq">*</em></label><input id="f-nm" name="name" required autocomplete="name"></div>
  <div class="f"><label for="f-em">{esc(u['em'])}<em class="rq">*</em></label><input id="f-em" type="email" name="email" required autocomplete="email"></div>
  <div class="f"><label for="f-ct">{esc(u['cty'])}<em class="rq">*</em></label><input id="f-ct" name="country" required autocomplete="country-name"></div>
  <div class="f w"><label for="f-items">{esc(u['items'])}</label><div class="rq-list" aria-live="polite"></div><textarea id="f-items" name="items" rows="4"></textarea></div>
  <div class="f w"><label for="f-msg">{esc(u['msg'])}<em class="rq">*</em></label><textarea id="f-msg" name="message" rows="5" required placeholder="{esc(u['msg_ph'])}"></textarea></div>
  <div class="f w agree"><label><input type="checkbox" name="consent" value="yes" required> {esc(u['agree'])}</label></div>
  <div class="f w subm"><button class="bt-y" type="submit">{esc(u['sendbtn'])}</button><p class="msg" role="alert"></p></div>
</form>
<aside class="rq-a tag"><h2>{esc(u['next_h'])}</h2><ol>{steps}</ol>
  <a class="yf-mail dark" href="mailto:chl@qone.kr">{MAIL}chl@qone.kr</a>
  <p class="hint"><a href="/inquiry/">Inquiry form</a></p></aside>
</div>
</main>"""
    page_shell(lang, f"{u['quote_h']} | CUSHIONI | QONE", u["quote_l"], "request/", "req", body, products)


def build_thanks(lang, products):
    u = UI[lang]
    b = base_of(lang)
    body = f"""<main id="main"><section class="ph peg"><div class="wrap"><h1>{esc(u['thanks_h'])}</h1><p class="lead">{esc(u['thanks_p'])}</p>
    <div class="cta"><a class="bt-y" href="{b}catalog/">{esc(u['back'])}</a><a class="bt-l" href="mailto:chl@qone.kr">{MAIL}chl@qone.kr</a></div>
    </div></section></main>"""
    page_shell(lang, f"{u['thanks_h']} | CUSHIONI | QONE", u["thanks_p"], "thanks/", "req", body, products)


def patch_nav(n_wall, n_living, n_camp):
    inserts = {
        ROOT / "products/wall-decor/index.html": (
            '<p class="cat-count">25 products</p>',
            '<p class="cat-count">25 products</p>\n    <p class="sec-sub"><a href="/cushioni/c/wall-decor/">Full CUSHIONI wall decor catalog</a> — every peel-and-stick wallpaper and foam panel from the Yeoju factory. <a href="/cushioni/request/">Request a quote</a> or email chl@qone.kr.</p>',
        ),
        ROOT / "products/home-living/index.html": (
            '<p class="cat-count">8 products</p>',
            '<p class="cat-count">8 products</p>\n    <p class="sec-sub"><a href="/cushioni/c/living/">Full CUSHIONI living catalog</a> — herringbone mats and kids’ play mats from the Yeoju factory. <a href="/cushioni/request/">Request a quote</a> or email chl@qone.kr.</p>',
        ),
        ROOT / "products/camping/index.html": (
            '<p class="cat-count">9 products</p>',
            '<p class="cat-count">9 products</p>\n    <p class="sec-sub"><a href="/cushioni/c/camping/">Full CUSHIONI camping catalog</a> — folding PE foam mats from the Yeoju factory. <a href="/cushioni/request/">Request a quote</a> or email chl@qone.kr.</p>',
        ),
        ROOT / "ko/products/wall-decor/index.html": (
            '<p class="cat-count">25 개 제품</p>',
            '<p class="cat-count">25 개 제품</p>\n    <p class="sec-sub"><a href="/cushioni/ko/c/wall-decor/">쿠셔니 벽 장식 카탈로그</a> — 여주 공장의 붙이는 벽지와 폼블럭. 견적은 <a href="/cushioni/ko/request/">견적 요청</a> 또는 chl@qone.kr.</p>',
        ),
        ROOT / "ko/products/home-living/index.html": (
            '<p class="cat-count">8 개 제품</p>',
            '<p class="cat-count">8 개 제품</p>\n    <p class="sec-sub"><a href="/cushioni/ko/c/living/">쿠셔니 리빙 카탈로그</a>. 견적은 <a href="/cushioni/ko/request/">견적 요청</a> 또는 chl@qone.kr.</p>',
        ),
        ROOT / "ko/products/camping/index.html": (
            '<p class="cat-count">9 개 제품</p>',
            '<p class="cat-count">9 개 제품</p>\n    <p class="sec-sub"><a href="/cushioni/ko/c/camping/">쿠셔니 캠핑 카탈로그</a>. 견적은 <a href="/cushioni/ko/request/">견적 요청</a> 또는 chl@qone.kr.</p>',
        ),
        ROOT / "ja/products/wall-decor/index.html": (
            '<p class="cat-count">25 製品</p>',
            '<p class="cat-count">25 製品</p>\n    <p class="sec-sub"><a href="/cushioni/ja/c/wall-decor/">クシオニ壁デコカタログ</a>。見積は <a href="/cushioni/ja/request/">見積依頼</a> または chl@qone.kr。</p>',
        ),
        ROOT / "ja/products/home-living/index.html": (
            '<p class="cat-count">8 製品</p>',
            '<p class="cat-count">8 製品</p>\n    <p class="sec-sub"><a href="/cushioni/ja/c/living/">クシオニリビングカタログ</a>。見積は <a href="/cushioni/ja/request/">見積依頼</a> または chl@qone.kr。</p>',
        ),
        ROOT / "ja/products/camping/index.html": (
            '<p class="cat-count">9 製品</p>',
            '<p class="cat-count">9 製品</p>\n    <p class="sec-sub"><a href="/cushioni/ja/c/camping/">クシオニキャンプカタログ</a>。見積は <a href="/cushioni/ja/request/">見積依頼</a> または chl@qone.kr。</p>',
        ),
        ROOT / "ru/products/wall-decor/index.html": (
            '<p class="cat-count">25 позиций</p>',
            '<p class="cat-count">25 позиций</p>\n    <p class="sec-sub"><a href="/cushioni/c/wall-decor/">Полный каталог CUSHIONI — настенный декор</a>. Запрос: <a href="/cushioni/request/">форма</a> или chl@qone.kr.</p>',
        ),
        ROOT / "ru/products/home-living/index.html": (
            '<p class="cat-count">8 позиций</p>',
            '<p class="cat-count">8 позиций</p>\n    <p class="sec-sub"><a href="/cushioni/c/living/">Полный каталог CUSHIONI — living</a>. Запрос: <a href="/cushioni/request/">форма</a> или chl@qone.kr.</p>',
        ),
        ROOT / "ru/products/camping/index.html": (
            '<p class="cat-count">9 позиций</p>',
            '<p class="cat-count">9 позиций</p>\n    <p class="sec-sub"><a href="/cushioni/c/camping/">Полный каталог CUSHIONI — кемпинг</a>. Запрос: <a href="/cushioni/request/">форма</a> или chl@qone.kr.</p>',
        ),
    }
    for path, (old, new) in inserts.items():
        text = path.read_text(encoding="utf-8")
        if "/cushioni/" in text and old in text and new.split("\n")[1].strip() in text:
            continue
        if old not in text:
            print("skip missing", path)
            continue
        if new.split("\n")[1].strip()[:40] in text:
            continue
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
    # products index card
    card = """      <a class="cat-preview-card" href="/cushioni/catalog/">
        <div data-bg="/assets/img/foam-wallpaper-hero.webp" class="cp-img" style="background-size:cover"></div>
        <div class="cp-body">
          <h4>CUSHIONI CATALOG</h4>
          <p>The full factory line from the Yeoju plant — wall decor, living mats and camping goods for wholesale buyers.</p>
          <div class="cp-count">Factory catalog</div>
        </div>
      </a>
"""
    p = ROOT / "products/index.html"
    t = p.read_text(encoding="utf-8")
    if 'href="/cushioni/catalog/"' not in t:
        t = t.replace(
            '      <a class="cat-preview-card" href="/products/sourcing/">',
            card + '      <a class="cat-preview-card" href="/products/sourcing/">',
            1,
        )
        p.write_text(t, encoding="utf-8")
    # footers
    for path in [ROOT / "index.html", ROOT / "products/index.html"]:
        t = path.read_text(encoding="utf-8")
        needle = '<a href="/yiwu/">Value Retail Range</a>'
        add = needle + '<a href="/cushioni/catalog/">CUSHIONI catalog</a>'
        if 'href="/cushioni/catalog/"' not in t and needle in t:
            path.write_text(t.replace(needle, add, 1), encoding="utf-8")
    ru = ROOT / "ru/index.html"
    t = ru.read_text(encoding="utf-8")
    needle = '<a href="/yiwu/">Товары для дискаунтеров</a>'
    if t.count(needle) and 'href="/cushioni/catalog/"' not in t:
        t = t.replace(needle, needle + '<a href="/cushioni/catalog/">Каталог CUSHIONI</a>', 1)
        ru.write_text(t, encoding="utf-8")


def patch_sitemaps(products):
    def add(path, urls):
        text = path.read_text(encoding="utf-8")
        extra = []
        for u in urls:
            if u in text:
                continue
            extra.append(f"<url><loc>{u}</loc></url>")
        if extra:
            text = text.replace("</urlset>", "".join(extra) + "</urlset>")
            path.write_text(text, encoding="utf-8")
    live_cats = [s for s, _ in CATS if any(p["cat"] == s for p in products)]
    en, ko, ja, es = [], [], [], []
    leaves = ["", "catalog/", "request/", "thanks/"] + [f"c/{s}/" for s in live_cats] + [f"p/{p['ph']}/" for p in products]
    for leaf in leaves:
        en.append(absu("/cushioni/" + leaf))
        ko.append(absu("/cushioni/ko/" + leaf))
        ja.append(absu("/cushioni/ja/" + leaf))
        es.append(absu("/cushioni/es/" + leaf))
    add(ROOT / "sitemap-en.xml", en)
    add(ROOT / "sitemap-ko.xml", ko)
    add(ROOT / "sitemap-ja.xml", ja)
    add(ROOT / "sitemap-es.xml", es)
    keep = {p["ph"] for p in products}
    url_re = re.compile(r"<url><loc>([^<]+)</loc></url>")
    for path in (ROOT / "sitemap-en.xml", ROOT / "sitemap-ko.xml", ROOT / "sitemap-ja.xml", ROOT / "sitemap-es.xml"):
        text = path.read_text(encoding="utf-8")

        def repl(m):
            loc = m.group(1)
            if "/cushioni/" not in loc:
                return m.group(0)
            prod = re.search(r"/p/(c-\d+)/", loc)
            if prod and prod.group(1) not in keep:
                return ""
            cat = re.search(r"/c/([a-z-]+)/", loc)
            if cat and cat.group(1) not in live_cats:
                return ""
            return m.group(0)

        path.write_text(url_re.sub(repl, text), encoding="utf-8")
    imgs = []
    for p in products:
        if not p["images"]:
            continue
        imgs.append(
            f"<image:image><image:loc>https://www.qone.kr/assets/cs/img/l/{p['ph']}.webp</image:loc>"
            f"<image:title>{esc(title_of(p, 'en'))}</image:title></image:image>"
        )
    block = "<url><loc>https://www.qone.kr/cushioni/catalog/</loc>" + "".join(imgs) + "</url>"
    path = ROOT / "sitemap-images.xml"
    text = path.read_text(encoding="utf-8")
    text2, n = re.subn(r"<url><loc>https://www\.qone\.kr/cushioni/catalog/</loc>.*?</url>", block, text, count=1)
    if n == 0:
        text2 = text.replace("</urlset>", block + "</urlset>")
    path.write_text(text2, encoding="utf-8")


def patch_llms(products):
    path = ROOT / "llms.txt"
    text = path.read_text(encoding="utf-8")
    counts = {slug: sum(1 for p in products if p["cat"] == slug) for slug, _ in CATS}
    live = [(slug, n) for slug, n in counts.items() if n]
    names = {"wall-decor": "wall decor", "living": "living", "camping": "camping", "household": "household"}
    count_line = ", ".join(f"{names[s]} {n}" for s, n in live) + f". Total {len(products)}."
    link_line = " · ".join(
        f"{names[s].title() if s != 'wall-decor' else 'Wall decor'} https://www.qone.kr/cushioni/c/{s}/" for s, _ in live
    )
    block = f"""

## CUSHIONI factory catalog
- Wholesale catalog of QONE's CUSHIONI factory line (peel-and-stick wall panels, wallpaper, and foam mats). English copy, Korean names kept. No prices are published; buyers request a quote at chl@qone.kr or https://www.qone.kr/cushioni/request/ .
- Catalog: https://www.qone.kr/cushioni/catalog/ · Korean https://www.qone.kr/cushioni/ko/catalog/ · Japanese https://www.qone.kr/cushioni/ja/catalog/ · Spanish https://www.qone.kr/cushioni/es/catalog/
- Counts: {count_line}
- {link_line}
"""
    if "/cushioni/catalog/" in text:
        text = re.sub(r"\n## CUSHIONI factory catalog\n(?:- .*\n){1,6}", block, text, count=1)
        path.write_text(text, encoding="utf-8")
        return
    path.write_text(text.rstrip() + block, encoding="utf-8")


def audit(products):
    bad = []
    pat = re.compile(r"(\d[\d,]*\s*원|\d+\s*%|할인|배송비|~~|\$\s?\d|KRW|USD|\bprice\b|\bsale\b)", re.I)
    for p in products:
        blob = " ".join([p["name_ko"], p["blurb_ko"], title_of(p, "en"), desc_of(p, "en"), p["mat"], p["origin"], alt_of(p, "en")])
        if pat.search(blob):
            bad.append((p["cid"], pat.search(blob).group(0)))
    # scan generated html
    hits = 0
    for f in (ROOT / "cushioni").rglob("*.html"):
        t = f.read_text(encoding="utf-8", errors="ignore")
        if pat.search(t):
            hits += 1
            if hits <= 8:
                m = pat.search(t)
                bad.append((str(f.relative_to(ROOT)), m.group(0)))
    return bad


def write_photo_map(products):
    import csv
    path = ROOT / "cushioni" / "photos-needed.csv"
    rows = [p for p in products if p.get("fallback")]
    rows.sort(key=lambda p: p["cid"])
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "store_id", "name_ko", "name_en", "current_image"])
        for p in rows:
            w.writerow([
                p["cid"],
                p["store_id"],
                p["name_ko"],
                title_of(p, "en"),
                f"/assets/cs/img/l/{p['ph']}.webp",
            ])
    print("photo map", path, len(rows))


def remove_dropped(products):
    keep = {p["ph"] for p in products}
    live_cats = {p["cat"] for p in products}
    for lang in ("", "ko/", "ja/", "es/"):
        root = ROOT / "cushioni" / lang
        pdir = root / "p"
        if pdir.exists():
            for d in pdir.iterdir():
                if d.is_dir() and d.name not in keep:
                    for child in d.iterdir():
                        child.unlink()
                    d.rmdir()
        cdir = root / "c"
        if cdir.exists():
            for d in cdir.iterdir():
                if d.is_dir() and d.name not in live_cats:
                    for child in d.iterdir():
                        child.unlink()
                    d.rmdir()
    for folder in (IMG_L, IMG_T):
        if not folder.exists():
            continue
        for f in folder.iterdir():
            if f.stem not in keep and f.suffix in {".webp", ".jpg", ".jpeg"}:
                f.unlink()
    sources_path = ROOT / "cushioni" / "image-sources.json"
    if sources_path.exists():
        sources = json.loads(sources_path.read_text(encoding="utf-8"))
        sources = {k: v for k, v in sources.items() if k in keep}
        sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    products = load_products()
    print("products", len(products))
    for slug, _ in CATS:
        print(slug, sum(1 for p in products if p["cat"] == slug))
    install_owner_photos(products)
    missing = download_images(products)
    products = arrange_products(products)
    print("missing images", len(missing))
    products = [p for p in products if (IMG_T / f"{p['ph']}.jpg").exists()]
    print("with images", len(products))
    data = []
    for p in products:
        data.append({
            "id": p["cid"],
            "store_id": p["store_id"],
            "category": p["cat"],
            "name_en": title_of(p, "en"),
            "name_ko": p["name_ko"],
            "name_ja": title_of(p, "ja"),
            "name_es": title_of(p, "es"),
            "size": p["size"],
            "color": p["color"]["en"],
            "pack": p["pack"],
            "material": p["mat"],
            "origin": p["origin"],
            "description_en": desc_of(p, "en"),
            "description_ko": desc_of(p, "ko"),
            "image": f"/assets/cs/img/l/{p['ph']}.webp",
            "image_is_line_photo": p.get("fallback", False),
        })
    write(ROOT / "cushioni" / "products.json", json.dumps(data, ensure_ascii=False, indent=2))
    for lang in LANGS:
        build_landing(products, lang)
        build_catalog(products, lang, only=None)
        for slug, _ in CATS:
            if any(p["cat"] == slug for p in products):
                build_catalog(products, lang, only=slug)
        build_request(lang, products)
        build_thanks(lang, products)
        for p in products:
            build_product(p, lang, products)
        print("built", lang)
    counts = {slug: sum(1 for p in products if p["cat"] == slug) for slug, _ in CATS}
    patch_nav(counts["wall-decor"], counts["living"], counts["camping"])
    remove_dropped(products)
    patch_sitemaps(products)
    patch_llms(products)
    write_photo_map(products)
    bad = audit(products)
    print("audit", bad[:12], "count", len(bad))
    report = {
        "total": len(products),
        "by_category": counts,
        "line_photos": sum(1 for p in products if p.get("fallback")),
        "missing_images_dropped_or_failed": missing,
    }
    print(json.dumps(report, ensure_ascii=False)[:2000])


if __name__ == "__main__":
    main()
