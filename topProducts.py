import streamlit as st
import mysql.connector as sql
import pandas as pd
import matplotlib.pyplot as plt

title = st.container()
dbdesc = st.container()
topProducts = st.container()

with title:
    st.title('Classic Models Performance Dashboard')
    
with dbdesc:
    st.header('Database Description')
    st.caption('For this project, we used the "classicmodels" sample MySQL \
               database.  According to the creator, this database is a sample \
               of a "retailer of scale models of classic cars database. It \
               contains typical business data such as customers, products, \
               sales orders, sales order line items, etc."')
    st.caption('This database can be installed at \
               https://www.mysqltutorial.org/mysql-sample-database.aspx')

    
    
with topProducts:
    st.header('Top products in selected time period:')
    
    # Create a slider to select the range of months for evaluation
    monthrange = st.select_slider(label = 'Select range of months to evaluate',
                                  options = ['Jan', 'Feb', 'Mar', 'Apr', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'],
                                  value = ['Jan', 'Dec'])
    
    # Dict to convert month string to integer
    monthmap = {'Jan': 1,
                'Feb': 2,
                'Mar': 3,
                'Apr': 4,
                'May': 5,
                'Jun': 6,
                'Jul': 7,
                'Aug': 8,
                'Sept': 9,
                'Oct': 10,
                'Nov': 11,
                'Dec': 12}

    # Select whether to order by units or dollars
    measure = st.selectbox(label = 'Order by Units or Dollars sold?',
                           options = ['Units', 'Dollars'])
    
    # Read SQL data
    c = sql.connect(host='localhost',
                    port=3306
                    database='classicmodels',
                    user='jbPublic',
                    password='mySQLconn3ct')   # Enter user password here
    


    cmd = ('SELECT MONTH(O.orderDate) AS ordMonth,       ' +
	   '       YEAR(O.orderDate) AS ordYear,         ' +
       '       D.productCode,                        ' +
       '       P.productName,                        ' +
       '       D.quantityOrdered,                    ' +
       '       D.priceEach                           ' +
       '  FROM orders AS O                           ' +
       '  JOIN orderdetails AS D USING (orderNumber) ' +
       '  JOIN products AS P USING (productCode)')

    df = pd.read_sql(cmd, c)
    
    # Clean the data based on inputs above
    df = df[(df['ordMonth'] >= monthmap[monthrange[0]]) & (df['ordMonth'] <= monthmap[monthrange[1]])]
    df['ordRevs'] = df['quantityOrdered'] * df['priceEach']
    df = df.rename(columns = {'quantityOrdered': 'Units', 'ordRevs': 'Dollars'})
    df = df.groupby(['productCode', 'productName']).sum()[['Units', 'priceEach', 'Dollars']].reset_index().sort_values(measure, ascending = True)
    df = df.head(10).set_index('productName').drop(['productCode', 'priceEach'], axis = 1)
    
    # Create the plot using inputs above
    fig1 = plt.figure()
    plt.subplot(1,1,1)
    plt.style.use('ggplot')
    df[measure].plot.barh(legend = False)
    plt.title('Top 10 Products')
    plt.ylabel('Product Name')
    plt.xlabel('Product Sales in {0}'.format(measure))
    current_values = plt.gca().get_xticks()
    st.pyplot(fig1)

