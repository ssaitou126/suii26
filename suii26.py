import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import yaml
import requests
import io

# 年月日時設定
now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).replace(
    tzinfo=None
)
nowday = now.strftime("%Y%m01")
nowyear = now.strftime("%Y")
thismonth = datetime.datetime(now.year, now.month, 1)
lastmonth = thismonth + datetime.timedelta(days=-1)
lastday = lastmonth.strftime("%Y%m01")
diff = now - thismonth
difday = diff.days
difsec = diff.seconds
diftime = int((difday * 24) + (difsec / 60 / 60))
tmrw = now + datetime.timedelta(days=1)
mdngt = datetime.datetime(tmrw.year, tmrw.month, tmrw.day, 0, 0, 0)
difhr = int((mdngt - now).total_seconds() / 60 / 60)



# 設定情報の読み込み
rivdict = yaml.safe_load(open("urls26.yaml", "r"))

# グラフ描画関数
def grfdrw(url_key):
    url_template = rivdict[url_key]["url"]
    urll = url_template.replace("datelabel", lastday).replace("yearlabel", nowyear)
    urln = url_template.replace("datelabel", nowday).replace("yearlabel", nowyear)
    
    # requestsを使用してデータを取得し、エンコーディングを指定してからpandasに渡す
    # サーバーによるブロックを防ぐためにUser-Agentを設定
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    
    res_l = requests.get(urll, headers=headers)
    res_l.encoding = "euc_jp"
    dfls = pd.read_html(io.StringIO(res_l.text))    
    res_n = requests.get(urln, headers=headers)
    res_n.encoding = "euc_jp"
    dfns = pd.read_html(io.StringIO(res_n.text))

    dfll = dfls[1].iloc[2:-1, :]
    dfnn = dfns[1].iloc[2 : difday + 3, :]
    dfc = pd.concat([dfll, dfnn])
    df3w = dfc.iloc[-28:, 1:]
    df3wd = dfc.iloc[-28:, 0]
    tiklist = df3wd.values.tolist()
    newtik = [_[5:10] for _ in tiklist]

    df = df3w.apply(pd.to_numeric, errors="coerce")
    arr = np.array(df).ravel().tolist()
    grf = pd.Series(arr)
    smin = grf.min()
    smax = grf.max()
    idx = 672 - difhr - 2
    if np.isnan(grf[idx]):
        srct = grf[idx - 1]
    else:
        srct = grf[idx]
    rname = f"{dfns[0].iloc[1, 3]}　{dfns[0].iloc[1, 1]}"
    headertxt = f"{rname}　　　　最大=　{smax}m　　最小=　{smin}m　　直近=　{srct}m"
    st.write(headertxt)

    x = [*range(0, 672)]
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(grf)
    ax.fill_between(x, grf, smin - 0.2, color="c", alpha=0.2)
    ax.set_xticks(np.arange(0, 672, 24), newtik, rotation=45)
    ax.set_ylim(smin - 0.2, smax + 0.2)
    ax.grid()
    st.pyplot(fig)


# チェックボックスの設定
st.sidebar.write("### '26鮎河川")

for key, info in rivdict.items():
    if st.sidebar.checkbox(info["label"]):
        grfdrw(key)


st.text("※国土交通省水文水質データベースのデータを利用して表示します")

# ホームページへのリンク
link1 = "[AyuZyのホームページ](https://sites.google.com/view/ayuzy)"
st.sidebar.markdown(link1, unsafe_allow_html=True)
