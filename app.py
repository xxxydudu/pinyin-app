# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, send_from_directory
from pypinyin import pinyin, Style

app = Flask(__name__)

COMPOUND_SURNAMES = {
    "欧阳","司马","司徒","司空","上官","诸葛","尉迟","长孙","夏侯","东方","南宫","公孙",
    "公羊","公冶","公良","公西","公输","皇甫","宇文","轩辕","令狐","钟离","独孤","慕容",
    "闻人","闾丘","东郭","西门","南门","北堂","太史","澹台","濮阳","第五","仲孙","叔孙",
    "申屠","乐正","拓跋","赫连","纳兰","呼延","宗政","百里","端木","谷梁","梁丘","乌孙",
    "即墨","宰父","夹谷","微生","公皙","公晞"
}
SURNAME_READING = {
    "单":"shan","曾":"zeng","解":"xie","区":"ou","乐":"yue","柏":"bai","任":"ren","翟":"zhai","殷":"yin"
}

def split_name(fullname: str):
    s = (fullname or "").strip().replace(" ", "")
    if not s: return "", ""
    if len(s) >= 2 and s[:2] in COMPOUND_SURNAMES: return s[:2], s[2:]
    return s[0], s[1:]

def pinyin_style(tone: str):
    return Style.TONE3 if tone=="num" else (Style.TONE if tone=="mark" else Style.NORMAL)

def join_tokens(tokens, case_mode="capitalize", sep=" "):
    if case_mode=="lower": tokens=[t.lower() for t in tokens]
    elif case_mode=="upper": tokens=[t.upper() for t in tokens]
    else: tokens=[t.capitalize() for t in tokens]
    return sep.join(tokens)

def to_initials(tokens, upper=False):
    s = "".join([t[0] for t in tokens if t])
    return s.upper() if upper else s.lower()

@app.get("/")
def home():
    return send_from_directory(".", "index.html")

@app.get("/api/ping")
def ping():
    return jsonify(ok=True, msg="pong")

@app.post("/api/pinyin")
def api_pinyin():
    data = request.get_json(silent=True) or {}
    fullname = (data.get("name") or "").strip()
    tone = (data.get("tone") or "none").lower()
    case_mode = (data.get("case") or "capitalize").lower()
    sep = data.get("sep", " ")
    mode = (data.get("mode") or "full").lower()
    if not fullname:
        return jsonify(ok=False, error="name is required"), 400

    surname, given = split_name(fullname)
    tokens = []

    if surname:
        if surname in COMPOUND_SURNAMES:
            tokens += [x[0] for x in pinyin(surname, style=pinyin_style(tone))]
        else:
            fixed = SURNAME_READING.get(surname)
            if fixed: tokens.append(fixed)
            else: tokens += [pinyin(surname, style=pinyin_style(tone))[0][0]]

    if given:
        tokens += [x[0] for x in pinyin(given, style=pinyin_style(tone))]

    result = to_initials(tokens, upper=(case_mode=="upper")) if mode=="initials" \
             else join_tokens(tokens, case_mode=case_mode, sep=sep)

    return jsonify(ok=True, input=fullname, surname=surname, given=given, tokens=tokens, result=result)

if __name__ == "__main__":
    from importlib.util import find_spec
    try:
        import pypinyin  # 确保已安装
    except Exception:
        print("Installing pypinyin ...")

    import os
    port = int(os.getenv("PORT", 5000))   # 云端端口或本地5000
    app.run(host="0.0.0.0", port=port, debug=False)

