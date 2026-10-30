"""Shared name normalisation + category sets for non-crypto perp markets (stocks/indices/commodities/FX/ETF/pre-IPO)."""
import re
COMMODITY = set("""XAU XAG XPT XPD XCU XNG XBR GOLD SILVER PLATINUM PALLADIUM COPPER OIL WTI WTIOIL BRENT BRENTOIL OILBRENT OILWTI BZ CL NG NATGAS GAS
USOIL UKOIL CORN WHEAT SOY SOYBEAN COFFEE SUGAR COCOA COTTON URANIUM TTF ALUMINIUM ALUMINUM NICKEL ZINC LEAD HEATINGOIL HO GOLDJM SILVERJM
XAUXAG XAUXPT PAPER""".split()) - {"GAS","PAPER"}
INDEX = set("""SP500 SPX500 US500 USA500 NDX NDX100 NAS100 NASDAQ100 US100 USA100 USTECH TECH100 TECH100M DJI DOWJONES US30 DOW HSI HK50 JP225 JPN225 N225 NIKKEI225 NIKKEI
DAX GER40 GER DE40 UK100 FTSE KR200 KRCOMP KOSPI KOSPI1 TUR30 XYZ100 SMALL2000 RUSSELL2000 RUSSELL US2000 VIX VOL DXY USDEX MAG7 MAGS SEMIS SEMI ROBOT INFOTECH
NUCLEAR DEFENSE ENERGY BIOTECH USENERGY NIFTY NIFTY5 NIFTYBK IBOV FLKR H100X BVIV""".split()) - {"ENERGY","DEFENSE","BIOTECH","ROBOT","NUCLEAR","INFOTECH","SEMIS"} | {"VNTL_THEME"}
THEME_BASKET = set("MAG7 SEMIS ROBOT INFOTECH NUCLEAR DEFENSE ENERGY BIOTECH SEMI USENERGY".split())
INDEX |= THEME_BASKET
RATES = set("USBOND US10Y 10Y 2Y 30Y".split())
OTHER_IDX = set("H100 B200".split())   # GPU price indices
CCY = set("EUR GBP JPY CHF AUD NZD CAD KRW HKD INR SGD TRY ZAR BRL CNH MXN".split())
FX_RE = re.compile(r"^(?:%s)(?:USD)?$|^USD(?:%s)$|^(?:%s)2(?:%s)$" % ("|".join(CCY),"|".join(CCY),"|".join(CCY),"|".join(CCY|{"USD"})))
ETF = set("""QQQ SPY IWM DIA VOO TQQQ SQQQ SOXL SOXS SOXX SMH XLE XLK XLU XLV XBI IBB GDX URNM URA USO TLT TMF TBT UVXY EWJ EWY EWZ EWT EWH KWEB INDA KORU TZA TSLL NVDL
MSTU MUU GGLL AMZU METU AAPU MSFU QLD SKUU SKDD BITO IBIT JEPQ SGOV BOTZ DRV KODEX200 CSOPSAMSUNG2L CSOPSKHYNIX2L CSOPSK2LHKD CSOPSS2LHKD IGV DRAM GLD GLDMINE GLDM NCLD SHAZ
SNXX STXX KSTR TREAD EWZS XNDU MVLL BNC FWDI PURRDAT""".split()) - {"SHAZ","SNXX","STXX","KSTR","TREAD","BNC","FWDI","PURRDAT","XNDU","MVLL"} | {"SHAZ"}
PREIPO = set("OPENAI OPENAIIPO ANTHROPIC ANTHROPICIPO ANTHROP ANTH OAI SPACEX SPCX SPCXX POLYMARKET MOONSHOT XAI STRIPE DATABRICKS UNITREE SHEIN SHEINHKD CEREBRAS ANSEM".split()) - {"ANSEM","XAI"}
GOLD_TOKENS = set("PAXG XAUT".split())          # tokenised gold = crypto-asset on most venues; excluded from counts
CRYPTO_INDEX = set("TOTAL2 OTHERS BTCD".split())

def norm(sym: str) -> str:
    s = sym.upper()
    s = s.split(":")[-1]                      # hyperliquid dex prefix
    s = re.sub(r"^(NC(?:SK|FX|CO|SI))", "", s)  # bingx
    s = re.sub(r"^PF_", "", s)
    s = re.sub(r"\.US", "", s)
    s = re.sub(r"(_24_5|_1)?-USD$", "", s)
    s = re.sub(r"(_USDT_PERP|_USDC_PERP|_USDT|_USDC|-USDT-SWAP|-USDT|-PERP|USDT|USDC)$", "", s)
    s = re.sub(r"-?USD$", "", s) if not FX_RE.match(s) and s not in ("USD",) else s
    s = re.sub(r"2USD$", "", s)
    s = re.sub(r"STOCK$", "", s) if len(s) > 6 else s
    return s

def category(base: str, tagged_noncrypto: bool = False):
    """Return one of stocks/indices/commodities/fx/etf/preipo/other/token_gold/crypto or None."""
    b = base
    if b in GOLD_TOKENS: return "token_gold"
    if b in CRYPTO_INDEX: return "crypto"
    if b in RATES: return "other"
    if b in OTHER_IDX: return "other"
    if b in COMMODITY: return "commodities"
    if b in INDEX: return "indices"
    if FX_RE.match(b) and b not in ("USD",): return "fx"
    if b in PREIPO: return "preipo"
    if b in ETF: return "etf"
    return "stocks" if tagged_noncrypto else None
