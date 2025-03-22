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
    
    if st.button("Update Prices"):
        # Create a dictionary mapping SKU to Precio Venta
        sku_to_precio = dict(zip(df2["Ítem"], df2["Precio Venta"]))
        
        # Update the "Precio" column in the product list based on matching SKU
        for idx, row in df.iterrows():
            sku = row["SKU (OBLIGATORIO)"]
            if sku in sku_to_precio:
                price = sku_to_precio[sku]
                if isinstance(price, str):
                    # Convert price from string format to integer
                    price_str = price.replace('$', '').replace('.', '').replace(',', '.').strip()
                    sku_to_precio[sku] = int(float(price_str))
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
