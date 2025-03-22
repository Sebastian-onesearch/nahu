import pandas as pd
import streamlit as st
import io

# Streamlit app title and description
st.title("NAHU Price Update Tool")
st.write("Upload your product list and price list to update prices.")

# File uploaders for the product list and price list
uploaded_product_list = st.file_uploader("Upload product list Excel file", type=["xlsx"])
uploaded_price_list = st.file_uploader("Upload price list CSV file", type=["csv"])

if uploaded_product_list and uploaded_price_list:
    # Read the uploaded files into dataframes
    df = pd.read_excel(uploaded_product_list)
    df2 = pd.read_csv(uploaded_price_list, sep=';', encoding='latin1')
    
    # Display previews of the uploaded files
    st.subheader("Product List Preview")
    st.dataframe(df.head())
    
    st.subheader("Price List Preview")
    st.dataframe(df2.head())
    
    # Display column names for verification
    st.write("Product list columns:", df.columns.tolist())
    st.write("Price list columns:", df2.columns.tolist())
    
    # Add USD exchange rate input
    st.subheader("USD Exchange Rate")
    usd_price = st.number_input(
        "Enter the USD to local currency exchange rate:", 
        min_value=1, 
        value=1000,  # Default value as int
        step=1,
        format="%d",  # Force integer format
        help="This rate will be used to convert prices in USD to local currency."
    )
    st.write(f"Current USD exchange rate: {int(usd_price)}")

    if st.button("Update Prices"):
        sku_to_precio = dict(zip(df2["Ítem"], df2["Precio Venta"]))

        for idx, row in df.iterrows():
            sku = row["SKU (OBLIGATORIO)"]
            if sku in sku_to_precio:
                price = sku_to_precio[sku]
                if isinstance(price, str):
                    tipo_moneda = price.split()[0]
                    if tipo_moneda == 'U$S':
                        updated_price = int(float(price.split()[1].replace('.', '').replace(',','.')) * usd_price)
                        updated_price = ((updated_price + 99) // 100) * 100
                    else:
                        price_str = price.replace('$', '').replace('.', '').replace(',', '.').strip()
                        updated_price = int(float(price_str))
                    sku_to_precio[sku] = updated_price
                df.at[idx, "Precio"] = sku_to_precio[sku]
        
        # Display the updated product list
        st.subheader("Updated Product List")
        st.dataframe(df)
        
        # Provide a download link for the updated Excel file
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        
        buffer.seek(0)
        st.download_button(
            label="Download updated Excel file",
            data=buffer,
            file_name="listado_tienda_updated.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("Please upload both the product list and price list files to proceed.")

