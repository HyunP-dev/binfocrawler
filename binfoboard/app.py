import sys
sys.path.append(".")

import streamlit as st
import plotly.express as px

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
    button = st.sidebar.button("분석", use_container_width=True)

    if button:
        if binfocrawler.get_last_index(bill_id) == 0:
            return
        # update_database(con, bill_id)
        info = binfocrawler.get_info(bill_id)
        print(info)
        st.markdown(f"""
#### {info.title.split("(")[0]}
> 제안일자: {info.date}  
> 제안자: {info.proposers}  
> 제안회기: {info.nth}  
  
  
{info.content.replace(".", ".\n\n")}""")
        df = get_counts(con, bill_id)
        st.plotly_chart(px.bar(df, x="date", y=["agree", "disagree"], barmode="group",
                               title=info.title))
    else:
        st.markdown(
        """
        본 대시보드는 등록된 의안에 대한 국민들의 의견이 얼마나 갈리는지
        시각화 해주는 대시보드 입니다. 
        """
        )

if __name__ == "__main__":
    main()
