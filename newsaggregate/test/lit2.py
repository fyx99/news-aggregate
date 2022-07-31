import streamlit as st
import pandas as pd
import altair as alt


@st.cache
def get_postgres_data():
    import psycopg2
    conn =  psycopg2.connect(dbname="newsaggregate", host="138.68.74.3", port="5432", user="postgres", password="u3fph3ßü98fg43f34f3")
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("""
        select feed, DATE_TRUNC('hour', update_date) as date from articles where update_date > CURRENT_DATE - INTERVAL '5 days' and update_date < CURRENT_DATE 
    """)
    data = cursor.fetchall()

    return pd.DataFrame(data, columns=["feed", "date"])



@st.cache
def get_docker_processes():
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(hostname="138.68.74.3", username="root", password="xI-1928ReDROP")
    stdin, stdout, stderr = ssh.exec_command("docker ps -n 10")
    lines = stdout.readlines()
    ssh.close()

    return lines


try:
    df = get_postgres_data()

    counts_simple = df.groupby(["date"]).agg(len)
    counts = df.groupby(["date", "feed"]).agg(len)


    print(counts.head())

    # data = df.loc[countries]
    # data /= 1000000.0
    st.write("### Articles Crawled per Feed")

    #data = data.T.reset_index()
    # data = pd.melt(data, id_vars=["index"]).rename(
    #     columns={"index": "year", "value": "Gross Agricultural Product ($B)"}
    # )

    chart = (
        alt.Chart(counts.reset_index())
        .mark_line()
        .encode(
            x="date:T",
            y="0:Q",
            color="feed:N"
        )
    )
    st.altair_chart(chart, use_container_width=True)


    import matplotlib.pyplot as plt
    import numpy as np



    st.pyplot(counts_simple.plot().get_figure())
    lines = get_docker_processes()
    for line in lines:
        st.write(line)



except Exception as e:
    st.error(e)