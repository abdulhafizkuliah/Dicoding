#import library
import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load datasets
customers_df = pd.read_csv('dashboard/customers_dataset.csv')
#geolocation_df = pd.read_csv('geolocation_dataset.csv')
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

# Display results in Streamlit

st.title("E-Commerce Dashboard")

# Create a bar plot for top sales categories from 2017-2018
st.subheader('Top 5 Sales Categories in 2017 and 2018')
plt.figure(figsize=(12, 6))
sns.barplot(x='product_category_name_english', y='price', data=sales_by_category.head(5), palette='viridis')
plt.title(f'Total Penjualan per "Kategori Produk" Tertinggi dari {start_date} sampai {end_date}')
plt.xlabel('Kategori Produk')
plt.ylabel('Total Penjualan')
plt.xticks(rotation=45)
st.pyplot(plt)

# Create a line plot for monthly payments of the top 5 selling product categories
st.subheader('Monthly Payments of the Top 5 Selling Product Categories')
plt.figure(figsize=(12, 8))
sns.lineplot(data=df_top_5, x='month_year', y='price', hue='product_category_name', marker='o', linestyle='-', palette='rainbow')
plt.title('Monthly Payments of the 5 Top Selling Product Categories')
plt.legend(title='Kategori Produk')
plt.xlabel('Date')
plt.ylabel('Amount')
plt.grid(True)
plt.xticks(rotation=45)
st.pyplot(plt)
