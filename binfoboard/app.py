import sys
sys.path.append(".")

import streamlit as st
import plotly.express as px
import pandas as pd

from model import *
import binfocrawler


def main():
    st.set_page_config(
        page_title="binfocrawler",
        page_icon="🧑‍⚖️",
    )

    con = init_database()

    st.write("# 입법예고 등록의견 통계")

    bill_id = st.sidebar.text_input("billId (링크 우측에 있는 값)")
    bar_btn = st.sidebar.button("막대 그래프", use_container_width=True)
    pie_btn = st.sidebar.button("원형 그래프", use_container_width=True)
    refresh_btn = st.sidebar.button("갱신", use_container_width=True)

    if refresh_btn:
        if binfocrawler.get_last_index(bill_id) == 0:
            st.markdown("갱신에 실패하였습니다.")
            return
        update_database(con, bill_id)
        st.markdown("갱신이 완료되었습니다.")

    if bar_btn or pie_btn:
        if binfocrawler.get_last_index(bill_id) == 0:
            return

        info = binfocrawler.get_info(bill_id)
        st.markdown(f"""
#### {info.title.split("(")[0]}
> 제안일자: {info.date}  
> 제안자: {info.proposers}  
> 제안회기: {info.nth}  
  
  
{info.content.replace(".", ".\n\n")}""")    
    
    df = get_counts(con, bill_id)
    if bar_btn:
        st.plotly_chart(px.bar(df, x="date", y=["agree", "disagree"], barmode="group",
                               title=info.title))
    if pie_btn:
        count = df[["agree", "disagree"]].sum()
        agree = count["agree"]
        disagree = count["disagree"]
        count = pd.DataFrame([("agree", agree), ("disagree", disagree)], columns=["label", "value"])

        fig = (px.pie(count, names="label", values="value", title=info.title)
            .update_traces(textinfo='label+percent')
            .update_layout(showlegend=False))
        st.plotly_chart(fig)
            
if __name__ == "__main__":
    main()
