#import library
import streamlit as st 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

# Hapus peringatan yang tidak perlu
warnings.simplefilter(action='ignore', category=FutureWarning)

# Load datasets
customers_df = pd.read_csv('dashboard/customers_dataset.csv')
order_items_df = pd.read_csv('dashboard/order_items_dataset.csv')
order_payments_df = pd.read_csv('dashboard/order_payments_dataset.csv')
order_reviews_df = pd.read_csv('dashboard/order_reviews_dataset.csv')
orders_df = pd.read_csv('dashboard/orders_dataset.csv')
product_category_name_translation_df = pd.read_csv('dashboard/product_category_name_translation.csv')
products_df = pd.read_csv('dashboard/products_dataset.csv')
sellers_df = pd.read_csv('dashboard/sellers_dataset.csv')

# Convert 'order_purchase_timestamp' to datetime
orders_df['order_purchase_timestamp'] = pd.to_datetime(orders_df['order_purchase_timestamp'])
order_reviews_df['review_creation_date'] = pd.to_datetime(order_reviews_df['review_creation_date'])

# Data merge
all_df = orders_df.merge(order_items_df, on="order_id", how="left") 
all_df = all_df.merge(order_payments_df, on="order_id", how="outer")
all_df = all_df.merge(order_reviews_df, on="order_id", how="outer")
all_df = all_df.merge(products_df, on="product_id", how="outer")
all_df = all_df.merge(customers_df, on="customer_id", how="outer")  
all_df = all_df.merge(sellers_df, on="seller_id", how="outer")

# Gabungkan DataFrame yang dibutuhkan
merged_df = pd.merge(order_items_df, products_df, on='product_id', how='left')
merged_df = pd.merge(merged_df, product_category_name_translation_df, on='product_category_name', how='left')
merged_df = pd.merge(merged_df, orders_df, on='order_id', how='left')

# Filter data untuk tahun 2017 dan 2018
merged_df['order_purchase_year'] = merged_df['order_purchase_timestamp'].dt.year
df_2017_2018 = merged_df[(merged_df['order_purchase_year'] == 2017) | (merged_df['order_purchase_year'] == 2018)]

#adw
df_2017_2018['order_purchase_timestamp'] = pd.to_datetime(df_2017_2018['order_purchase_timestamp'])

# Extract only the date part
df_2017_2018['order_purchase_date'] = df_2017_2018['order_purchase_timestamp'].dt.date

# Convert the date part back to datetime format
df_2017_2018['order_purchase_date'] = pd.to_datetime(df_2017_2018['order_purchase_date'])

# Group data by product category and sum the price for both 2017 and 2018
sales_by_category_year = df_2017_2018.groupby(['product_category_name_english'])['price'].sum().reset_index()

# Sort values by total sales in descending order
sales_by_category_year = sales_by_category_year.sort_values('price', ascending=False)

#input from user
min_date = df_2017_2018["order_purchase_date"].min()
max_date = df_2017_2018["order_purchase_date"].max()
 
with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("dashboard/bangkitmantap.jpg")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

filteredDf_2017_2018 = df_2017_2018[(df_2017_2018["order_purchase_date"] >= str(start_date)) & (df_2017_2018["order_purchase_date"] <= str(end_date))]

# Hitung total penjualan per kategori produk
sales_by_category = filteredDf_2017_2018.groupby(['product_category_name_english', 'order_purchase_date'])['price'].sum().reset_index()

# Sort values by total sales in descending order
sales_by_category = sales_by_category.sort_values('price', ascending=False)

# Translate product category names
category_translation = {
  'beleza_saude': 'health_beauty',
  'cama_mesa_banho': 'bed_bath_table',
  'esporte_lazer': 'sports_leisure',
  'informatica_acessorios': 'computers_accessories',
  'relogios_presentes': 'watches_gifts'
}

all_df['product_category_name'] = all_df['product_category_name'].replace(category_translation)

# Create time-based aggregation
all_df['month_year'] = all_df['order_purchase_timestamp'].dt.strftime('%Y %m')
df_grouped = all_df.groupby(['month_year', 'product_category_name']).agg({'price': 'sum'}).reset_index()

# Calculate total sales per category and select the top 5 categories
total_sales_per_category = df_grouped.groupby('product_category_name')['price'].mean()
top_5_categories = total_sales_per_category.nlargest(5).index
df_top_5 = df_grouped[df_grouped['product_category_name'].isin(top_5_categories)]

# Mengambil data yang diperlukan untuk RFM analysis
rfm_df = all_df[['customer_id', 'order_purchase_timestamp', 'order_id', 'price']]

# Menentukan tanggal terbaru dalam dataset
latest_date = rfm_df['order_purchase_timestamp'].max()

# Membuat RFM DataFrame
rfm_analysis = rfm_df.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (latest_date - x.max()).days, # Recency
    'order_id': 'count', # Frequency
    'price': 'sum' # Monetary
    })

rfm_analysis.rename(columns={
    'order_purchase_timestamp': 'Recency',
    'order_id': 'Frequency',
    'price': 'Monetary'
    }, inplace=True)

# Display results in Streamlit
st.title('Data Analysis Project Report:sparkles:')
st.header(":green[E-Commerce Public Dashboard]")

paraghraph1 = '''
This Data Analysis Project aims to find insights on what product categories have the highest sales from September 2016 to August 2018 and also to see the monthly sales trends. It is expected that something interesting will be obtained from the sales trend. Thus, the following question arises :
1. What are the five product categories with the highest sales from September 2016 to August 2018?
2. From these five product categories, what is the trend of monthly payment amounts over the period of September 2016 - August 2018?

To answer these questions, Data Wrangling, Exploratory Data Analysis, 
and Visualization & Explanatory Data Analysis were conducted, as detailed in the attached Google Colab notebook.
https://bit.ly/ProyekAnalisisData

:blue-background[**Insights**] :
- The idea to answer the first question is to find the total sales of each product category from September 2016 to August 2018 and then rank them in order of the largest. The 5 product categories with the highest sales will be taken.
- The idea to answer the second question is to define a new data frame containing the monthly sales of the 5 product categories.

The results obtained from this series of things are as follows
'''
st.markdown(paraghraph1)

# Create a bar plot for top sales categories 2017-2018
st.subheader(':blue[Top 5 Sales Categories]')
st.markdown("***Interactive Mode***")
plt.figure(figsize=(12, 6))
sns.barplot(x='product_category_name_english', y='price', data=sales_by_category.head(5), palette='viridis')
plt.title(f'Total Penjualan per "Kategori Produk" Tertinggi dari {start_date} sampai {end_date}')
plt.xlabel('Kategori Produk')
plt.ylabel('Total Penjualan')
plt.xticks(rotation=45)
st.pyplot(plt)

st.markdown('''
    :orange[Note] : Noticed that these 5 product categories can be changed for each time range that inputted by the user on the left side of the chart''')

# Create a bar plot
st.markdown("***Static Mode***")
plt.figure(figsize=(12, 6))
sns.barplot(x='product_category_name_english', y='price', data=sales_by_category_year.head(5),palette='viridis')

plt.title('Total Penjualan per Kategori Produk Tertinggi dari September 2016 hingga Agustus 2018')
plt.xlabel('Kategori Produk')
plt.ylabel('Total Penjualan')
plt.xticks(rotation=45)
st.pyplot(plt)

st.markdown('''
    :orange[Note] : These 5 product categories are the highest selling product categories from September 2016 to August 2018.''')

# Create a line plot for monthly payments of the top 5 selling product categories
st.subheader(':blue[Monthly Payments of the Top 5 Selling Product Categories]')
plt.figure(figsize=(12, 8))
sns.lineplot(data=df_top_5, x='month_year', y='price', hue='product_category_name', marker='o', linestyle='-', palette='rainbow')
plt.title('Monthly Payments of the 5 Top Selling Product Categories')
plt.legend(title='Kategori Produk')
plt.xlabel('Date')
plt.ylabel('Total')
plt.grid(True)
plt.xticks(rotation=45)
st.pyplot(plt)

st.markdown('''
    :orange[Note] : These 5 product categories are the highest selling product categories from September 2016 to August 2018.''')

st.subheader(":blue[Further Analysis]")

paraghraph2 = '''
In this section, RFM Analysis will be carried out on the customers.

RFM analysis is one of the commonly used methods to segment customers (grouping customers into categories) based on three parameters, namely recency, frequency, and monetary.
- Recency: a parameter used to see when a customer last made a transaction.
- Frequency: this parameter is used to identify how often a customer makes a transaction.
- Monetary: this last parameter is used to identify how much revenue comes from the customer.
'''
st.markdown(paraghraph2)

#template plot RFM dari dicoding
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="Recency", x="customer_id", data=rfm_analysis.sort_values(by="Recency", ascending=False).head(5), palette=colors, ax=ax[0])

ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='x', labelsize=15)
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=90)

sns.barplot(y="Frequency", x="customer_id", data=rfm_analysis.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='x', labelsize=15)
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=90)

sns.barplot(y="Monetary", x="customer_id", data=rfm_analysis.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='x', labelsize=15)
ax[2].set_xticklabels(ax[2].get_xticklabels(), rotation=90)

plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
st.pyplot(plt)

st.markdown('''
    :orange[Note] : These 5 best customers were obtained based on 3 categories, which are Recency, Frequency, and Monetary (separately).''')

st.subheader(':blue[Conclusion]')

paraghraph4 = ''' 
The conclusions obtained from the results of data analysis are explained as follows

1. What are the five product categories with the highest sales from September 2016 to August 2018?

The 5 product categories that have the highest total sales are `health_beauty`, `watches_gifts`, `bed_bath_table`, `sports_leisure`, and `computers_accessories`.

2. From these five product categories, what is the trend of monthly payment amounts over the period of September 2016 - August 2018?

According to Visualisazion & Explanatory Analysis :
- The highest payments of `health_beauty` was in August 2018, which was around 120,000 (tends to go up every month)
- The highest payments of `watches_gifts` was in May 2018, which was around 120,000 (tends to fluctuate every month)
- The highest payments of `bed_bath_table` was in November 2017, which was around 90,000 (tend to fluctuate every month)
- The highest payments of `sports_leisure` was in January 2018, which was around 90,000 (fluctuating monthly and trending down since 2018)
- The highest payments of `computers_accessories` was in February 2018, which was around 100,000 (fluctuating monthly and trending down since 2018)

3. (From Further Analysis) As a result, 5 best customers were obtained based on 3 categories, which are Recency, Frequency, and Monetary (separately). With the following notes.
- The Recency value between customers is very close, which is around 700 (700 days in two years).
- The Frequency and Monetary values of Best Customer#1 are quite high compared to the other 4 best customers.
'''

st.markdown(paraghraph4)
