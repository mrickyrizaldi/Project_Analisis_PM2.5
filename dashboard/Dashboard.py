import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Judul dashboard
st.title("Dashboard Analisis Data Polutan PM2.5 Guanyuan (2013-2017) 🌍")

with st.expander("Lihat Deskripsi Lengkap"):
    st.write("""
        Ini adalah dashboard interaktif untuk menganalisis data polusi udara PM2.5 di Guanyuan dalam rentang
        01 Maret 2013 - 28 Februari 2017. Anda dapat menggunakan filter untuk melihat tren PM2.5 berdasarkan musim, 
        tipe hari, Kategori dan tahun serta melihat visualisasinya berdasarkan Musim, Tipe Hari, Kombinasi Keduanya bahkan
        distribusi kategorinya.
    """)

# Fungsi untuk load data
@st.cache_data
def load_data():
    df = pd.read_csv('all_data.csv')
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df.set_index('datetime', inplace=True)
    return df

# Fungsi untuk mendapatkan filter berdasarkan musim, tipe hari, kategori dan rentang waktu
def filter_data(df, musim=None, tipe_hari=None, rentang_waktu=None, kategori=None):
    # Filter berdasarkan musim
    if musim:
        df = df[df['musim'].isin(musim)]
    # Filter berdasarkan tipe hari (Weekday/Weekend)
    if tipe_hari:
        df = df[df['tipe_hari'].isin(tipe_hari)]
    # Filter berdasarkan rentang waktu
    if rentang_waktu:
        df = df.loc[rentang_waktu[0]:rentang_waktu[1]]
    # Filter berdasarkan kategori
    if kategori:
        df = df[df['Kategori_PM2.5'].isin(kategori)]
    return df

# Load data
df = load_data()

with st.sidebar:
    st.title("Filter Data PM2.5")
    # Tambahkan gambar di sidebar
    st.image(
        "https://static.vecteezy.com/system/resources/previews/035/684/830/non_2x/pollution-pm2-5-icon-dust-in-the-air-safety-concept-illustration-vector.jpg",
        use_container_width=True,
        caption="Analisis PM2.5")

    # Pilih rentang waktu
    rentang_waktu = st.date_input(
        "Rentang Waktu",
        value=(),
        min_value=df.index.min(),
        max_value=df.index.max()
    )
    # Tangani input rentang waktu dengan try-except
    try:
        if len(rentang_waktu) == 2:
            start_date, end_date = rentang_waktu
        else:
            raise ValueError("Rentang waktu belum dipilih.")  # Paksa ke except jika tidak ada dua tanggal
    except:
        start_date, end_date = df.index.min(), df.index.max()  # Gunakan rentang penuh

    # Pilih musim
    musim = st.multiselect(
        'Pilih Musim',
        options=df['musim'].unique(),
        default=[]
    )

    # Pilih tipe hari
    tipe_hari = st.multiselect(
        'Pilih Tipe Hari',
        options=df['tipe_hari'].unique(),
        default=[]
    )

    # Pilih Kategori
    kategori = st.multiselect(
        'Pilih Kategori',
        options=df['Kategori_PM2.5'].unique(),
        default=[]
    )
    st.caption('Copyright (c) MrickyJrs 2025')

# Terapkan filter ke data
filtered_data = filter_data(df, musim=musim, tipe_hari=tipe_hari, rentang_waktu=rentang_waktu, kategori=kategori)

# Tampilkan data yang difilter
st.write("Data yang Difilter:")
show_data = st.checkbox("Tampilkan Data")
if show_data:
    st.dataframe(filtered_data)

# Fungsi untuk membuat grafik bar chart interaktif
def create_bar_chart(data, x_col, y_col, title, xlabel, ylabel, hue_col=None):
    fig = px.bar(data, x=x_col, y=y_col, color=hue_col, title=title, labels={x_col: xlabel, y_col: ylabel},
                 template="plotly_white", color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_layout(title_font_size=16, xaxis_title_font_size=12, yaxis_title_font_size=12,
                      xaxis=dict(showgrid=True), yaxis=dict(showgrid=True))
    st.plotly_chart(fig)

# Fungsi untuk membuat line chart interaktif
def create_line_chart(data, x_col, y_col, hue_col, title, xlabel, ylabel):
    fig = px.line(data, x=x_col, y=y_col, color=hue_col, markers=True, title=title, labels={x_col: xlabel, y_col: ylabel},
                  template="plotly_white", color_discrete_sequence=px.colors.qualitative.T10)
    fig.update_layout(title_font_size=16, xaxis_title_font_size=12, yaxis_title_font_size=12,
                      xaxis=dict(showgrid=True), yaxis=dict(showgrid=True))
    st.plotly_chart(fig)

# Fungsi Membuat Clustered Bar Chart Interaktif
def create_clustered_bar_chart(data, x_col, y_col, hue_col, title, xlabel, ylabel, hue_order=None, order=None):
    if hue_order is None:
        hue_order = sorted(data[hue_col].unique())
    if order is None:
        order = sorted(data[x_col].unique())
    fig = px.bar(data_frame=data, x=x_col, y=y_col, color=hue_col, category_orders={x_col: order, hue_col: hue_order},
                 color_discrete_sequence=px.colors.qualitative.T10, title=title, labels={x_col: xlabel, y_col: ylabel})
    fig.update_layout(barmode='group', title_text=title, title_font_size=16, xaxis_title=xlabel, yaxis_title=ylabel,
                      xaxis=dict(tickmode='array'), legend_title=hue_col)
    st.plotly_chart(fig)

# Fungsi untuk membuat boxplot Interaktif
def create_boxplot(data, x_col, y_col, title, xlabel, ylabel):
    fig = px.box(data_frame=data, x=x_col, y=y_col, color=x_col, color_discrete_sequence=px.colors.sequential.Viridis,
                 title=title, labels={x_col: xlabel, y_col: ylabel})
    fig.update_layout(title_text=title, title_font_size=16, xaxis_title=xlabel, yaxis_title=ylabel,
                      xaxis=dict(tickmode='array'), legend_title=x_col)
    st.plotly_chart(fig)

# Fungsi untuk membuat heatmap
def create_heatmap(data, title, cbar_label, fmt=".1f", cmap="YlGnBu", yaxis_title="Musim/Tipe Hari",
                   hovertemplate="Konsentrasi PM2.5: %{z} µg/m³<br>Musim: %{y}<br>Tahun: %{x}<extra></extra>"):
    data = data.where(pd.notna(data), None)
    # Gabungkan index jika multi-index
    if isinstance(data.index, pd.MultiIndex):
        data.index = data.index.map(lambda x: f"{x[0]} - {x[1]}")

    fig = go.Figure(data=go.Heatmap(
        z=data.values, x=data.columns, y=data.index, colorscale=cmap,
        colorbar=dict(title=cbar_label),
        hovertemplate=hovertemplate
    ))

    if data.shape[0] < 10 and data.shape[1] < 10:
        for i in range(len(data.index)):
            for j in range(len(data.columns)):
                if pd.notna(data.iloc[i, j]):
                    color_text = "white" if data.iloc[i, j] > data.mean().mean() else "black"
                    fig.add_annotation(
                        x=data.columns[j], y=data.index[i], text=f"{data.iloc[i, j]:{fmt}}",
                        showarrow=False, font=dict(size=12, color=color_text), align="center"
                    )
    fig.update_layout(
        title=title, xaxis_title="Tahun", yaxis_title=yaxis_title,
        height=600, width=800, xaxis=dict(tickmode='array', tickvals=data.columns,
                                          ticktext=[str(year) for year in data.columns])
    )
    return fig

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["Berdasarkan Musim", "Berdasarkan Tipe Hari", "Kombinasi Musim dan Tipe Hari",
                                  "Berdasarkan Kategori"])

with tab1:
    st.header('Analisis PM2.5 Berdasarkan Musim')
    musim_stats = filtered_data.groupby('musim')['PM2.5'].mean().reset_index()
    musim_tahun_stats = filtered_data.groupby(['year', 'musim'])['PM2.5'].mean().reset_index()

    with st.expander("Bar Chart: Konsentrasi PM2.5 pada Musim Dingin, Gugur, Panas, dan Semi"):
        # Bar Chart per Musim
        create_bar_chart(musim_stats, x_col='musim', y_col='PM2.5', title='Rata-rata Konsentrasi PM2.5 Berdasarkan Musim',
                         xlabel='Musim', ylabel='Konsentrasi PM2.5 (µg/m³)', hue_col='musim')

    with st.expander("Clustered Bar Chart: Konsentrasi PM2.5 Berdasarkan Musim dan Tahun (2013-2017)"):
        # Clustered Bar Chart per Musim dan Tahun
        create_clustered_bar_chart(musim_tahun_stats, 'year', 'PM2.5', 'musim',
                                   'Konsentrasi Rata-rata PM2.5 per Musim (2013-2017)', 'Tahun', 'Konsentrasi PM2.5 (µg/m³)',
                                   hue_order=['Musim Dingin', 'Musim Gugur', 'Musim Panas', 'Musim Semi'])

    with st.expander("Heat Map: Konsentrasi PM2.5 Berdasarkan Musim dan Tahun (2013-2017)"):
        # Heatmap per Musim dan Tahun
        heatmap_data_1 = musim_tahun_stats.pivot_table(index='musim', columns='year', values='PM2.5')
        fig1 = create_heatmap(heatmap_data_1, 'Konsentrasi PM2.5 per Musim dan Tahun (2013-2017)', 'Konsentrasi PM2.5 (µg/m³)', yaxis_title="Musim")
        st.plotly_chart(fig1)

    with st.expander("Line Chart: Tren Konsentrasi PM2.5 Berdasarkan Musim dan Tahun (2013-2017)"):
        # Line Chart per Musim dan Tahun
        create_line_chart(musim_tahun_stats, x_col='year', y_col='PM2.5', hue_col='musim',
                          title='Tren Konsentrasi PM2.5 Berdasarkan Musim dan Tahun', xlabel='Tahun', ylabel='Konsentrasi PM2.5 (µg/m³)')

    with st.expander("Box Plot: Distribusi PM2.5 Berdasarkan Musim"):
        # Box Plot: Distribusi PM2.5 Berdasarkan Musim
        create_boxplot(filtered_data, 'musim', 'PM2.5','Distribusi Konsentrasi PM2.5 Berdasarkan Musim',
                       'Musim', 'Konsentrasi PM2.5 (µg/m³)')

with tab2:
    st.header('Analisis PM2.5 Berdasarkan Tipe Hari')
    tipe_hari_stats = filtered_data.groupby('tipe_hari')['PM2.5'].mean().reset_index()
    tipe_hari_tahun_stats = filtered_data.groupby(['year', 'tipe_hari'])['PM2.5'].mean().reset_index()

    with st.expander("Bar Chart: Konsentrasi PM2.5 pada Weekday dan Weekend"):
        # Bar Chart per Tipe Hari
        create_bar_chart(tipe_hari_stats, x_col='tipe_hari', y_col='PM2.5', title='Rata-rata Konsentrasi PM2.5 pada Weekday dan Weekend',
                         xlabel='Tipe Hari', ylabel='Konsentrasi PM2.5 (µg/m³)', hue_col='tipe_hari')

    with st.expander("Heat Map: Konsentrasi PM2.5 per Tipe Hari dan Tahun (2013-2017)"):
        # Heatmap per Tipe Hari dan Tahun
        heatmap_data_2 = tipe_hari_tahun_stats.pivot_table(index='tipe_hari', columns='year', values='PM2.5')
        fig2 = create_heatmap(heatmap_data_2, 'Konsentrasi PM2.5 per Tipe Hari dan Tahun (2013-2017)', 'Konsentrasi PM2.5 (µg/m³)', yaxis_title="Tipe Hari")
        st.plotly_chart(fig2)

    with st.expander("Line Chart: Tren Konsentrasi PM2.5 Berdasarkan Tipe Hari dan Tahun (2013-2017)"):
        # Line Chart per Tipe Hari dan Tahun
        create_line_chart(tipe_hari_tahun_stats, x_col='year', y_col='PM2.5', hue_col='tipe_hari',
                          title='Konsentrasi PM2.5 per Tipe Hari dan Tahun', xlabel='Tahun', ylabel='Konsentrasi PM2.5 (µg/m³)')

    with st.expander("Box Plot: Distribusi PM2.5 Berdasarkan Tipe Hari"):
        # Box Plot: Distribusi PM2.5 Berdasarkan Tipe Hari
        create_boxplot(filtered_data, 'tipe_hari', 'PM2.5', 'Distribusi Konsentrasi PM2.5 Berdasarkan Tipe Hari',
                       'Tipe Hari', 'Konsentrasi PM2.5 (µg/m³)')

with tab3:
    # Bagian 3: Kombinasi Musim dan Tipe Hari
    st.header('Analisis Kombinasi Musim dan Tipe Hari')
    gabungan_stats = filtered_data.groupby(['musim', 'tipe_hari'])['PM2.5'].mean().reset_index()
    heatmap_gabungan = filtered_data.groupby(['musim', 'tipe_hari', 'year'])['PM2.5'].mean().reset_index()

    with st.expander("Clustered Bar Chart: Konsentrasi PM2.5 per Musim dan Tipe Hari"):
        # Clustered Bar Chart per Musim dan Tipe Hari
        create_clustered_bar_chart(gabungan_stats, 'musim', 'PM2.5', 'tipe_hari',
                                   'Konsentrasi Rata-rata PM2.5 per Musim (Weekday vs Weekend)', 'Musim',
                                   'Konsentrasi PM2.5 (µg/m³)',
                                   order=['Musim Dingin', 'Musim Semi', 'Musim Panas', 'Musim Gugur'])

    with st.expander("Heatmap: Konsentrasi PM2.5 per Musim dan Tipe Hari (2013-2017)"):
        # Heatmap Kombinasi Musim dan Tipe Hari
        heatmap_data_3 = heatmap_gabungan.pivot_table(index=['musim','tipe_hari'], columns='year', values='PM2.5')
        fig3 = create_heatmap(heatmap_data_3, 'Konsentrasi PM2.5 per Musim dan Tipe Hari (2013-2017)', 'Konsentrasi PM2.5 (µg/m³)')
        st.plotly_chart(fig3)

with tab4:
    st.header('Analisis Lanjutan Berdasarkan Kategori PM2.5')
    with st.expander("Lihat Penjelasan Kategori"):
        st.write("""
                Konsentrasi Partikulat (PM2.5)
                - Kategori Baik = 0-15.5 µg/m³.
                - Kategori Sedang = 15.6-55.4 µg/m³.
                - Kategori Tidak Sehat = 55.5-150.4 µg/m³.
                - Kategori Sangat Tidak Sehat = 150.5-250.4 µg/m³.
                - Kategori Berbahaya = >250.5 µg/m³.
                
                Source: [BMKG](https://www.bmkg.go.id/kualitas-udara/pm25)
        """)
    with st.expander("Heatmap: Distribusi Kategori PM2.5 (2013-2017)"):
        # Analisis Lanjutan Berdasarkan Kategori PM2.5
        kategori_order = ["Baik", "Sedang", "Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"]
        kategori_stats = (filtered_data.groupby('year')['Kategori_PM2.5'].value_counts(normalize=True).unstack()
                .reindex(columns=kategori_order, fill_value=0) * 100
        )
        # Heatmap Kategori PM2.5 (2013-2017)
        fig4 = create_heatmap(kategori_stats.T, 'Persentase Distribusi Kategori PM2.5 (2013-2017)', 'Persentase Kategori PM2.5 (%)',
                              yaxis_title="Kategori PM2.5", hovertemplate="Distribusi : %{z} % <br>Kategori: %{y}<br>Tahun: %{x}<extra></extra>")
        st.plotly_chart(fig4)

st.caption('Copyright (c) MrickyJrs 2025')
