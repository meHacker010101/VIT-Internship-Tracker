import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from database import get_updated_data

google_sheet_url = "https://docs.google.com/spreadsheets/d/1ZudQZq_OOMLZr5qojWo9y5UzBhA_BK-neIn15jpZUUo/edit?usp=sharing"
df = get_updated_data(google_sheet_url)

# Tab 1: Branch-wise Placement
def tab1_content(df):
    st.header("Branch-wise Internship")
    branch_code = st.selectbox('Select Branch Code', df['branch_code'].unique())
    branch_data = df[df['branch_code'] == branch_code]
    company_count = branch_data.groupby('company').agg(
        Number_of_Students=('name', 'count'),
        Average_Stipend=('stipend', 'mean')
    ).reset_index()

    #  Branch Statistics:
    st.subheader(f"Statistics for {branch_code} : ")
    selection_count = branch_data['name'].count()
    st.write(f"- Number of Selections : {selection_count}")

    avg_stipend = branch_data['stipend'].mean().round(2)
    st.write(f"- Average Stipend : {avg_stipend}")

    highest_stipend = branch_data['stipend'].max()
    st.write(f"- Maximum Stipend : {highest_stipend}")

    least_stipend = branch_data['stipend'].min()
    st.write(f"- Minimum Stipend : {least_stipend}")

    median_stipend = branch_data['stipend'].median()
    st.write(f"- Median Stipend : {median_stipend}")

    company_count.columns = ['Company', 'Number of Students', 'Average Stipend']
    company_count['Average Stipend'] = company_count['Average Stipend'].fillna('-')
    st.subheader(f"Companies and Average Stipend offered under {branch_code}:")
    # st.dataframe(company_count, height=700, width=600)
    st.table(company_count)
    fig = px.pie(company_count, names='Company', values='Number of Students', title=f'Company vs Students in {branch_code}')
    st.plotly_chart(fig)

    fig = px.bar(company_count,
                 x='Number of Students',
                 y='Company',
                 text='Number of Students',  # Display numbers on bars
                 orientation='h',  # Horizontal orientation
                 title='Number of Students Selected by Company',
                 color='Number of Students',  # Color by number of students
                 color_continuous_scale=px.colors.sequential.Plasma)  # Color scale

    # Update layout
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')  # Show numbers outside bars
    fig.update_layout(
        xaxis_title='Number of Students',
        yaxis_title='Company',
        title_font=dict(size=20),
        font=dict(size=14),
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
    )

    # Show figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    selected_company = st.selectbox('Select Company to see Registration Numbers and Names',
                                    company_count['Company'].unique())

    if selected_company:
        # Get registration numbers and names for the selected company
        selected_students = branch_data[branch_data['company'] == selected_company]
        registration_numbers = selected_students['registration number'].tolist()
        names = selected_students['name'].tolist()

        # Show registration numbers and names in a popup
        with st.expander(f"Registration Numbers and Names for {selected_company}", expanded=False):
            for reg_num, name in zip(registration_numbers, names):
                st.write(f"{reg_num}  -  {name}")


# Tab 2: Internship Stats
def tab2_content(df):
    # Aggregating the data based on company
    company_data = df.groupby('company').agg(
        Number_of_Students=('name', 'count'),
        Average_Stipend=('stipend', 'mean')
    ).reset_index()

    # 3D-style bar chart using Plotly's go.Bar
    fig_3d = go.Figure(data=[go.Bar(
        x=company_data['company'],  # Company names on the x-axis
        y=company_data['Number_of_Students'],  # Number of Students on the y-axis
        text=company_data['Number_of_Students'],  # Display the number of students on hover
        textposition='auto',
        marker=dict(
            color=company_data['Number_of_Students'],  # Color bars based on values
            colorscale='Viridis',  # Set a color scale for the bars
            showscale=True,  # Display the color scale legend
        )
    )])

    # Customize layout to give 3D visual impression
    fig_3d.update_layout(
        title="Company vs Number of Students (3D Bar Chart)",
        xaxis_title="Company",
        yaxis_title="Number of Students",
        height=600,
        width=700,
        template="plotly_dark",  # Dark theme
        font=dict(size=12),
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent background
        scene=dict(
            xaxis=dict(title='Company'),
            yaxis=dict(title='Number of Students'),
            zaxis=dict(title=''),
        ),
    )

    # Display the 3D bar chart in Streamlit
    st.plotly_chart(fig_3d)

    # 2D colorful bar chart using Plotly Express
    fig_colorful_bar = px.bar(
        company_data,
        x='company',
        y='Number_of_Students',
        title="Number of Students vs Companies",
        color='Number_of_Students',  # Color bars based on the number of students
        color_continuous_scale=px.colors.sequential.Plasma  # Use a colorful continuous scale
    )

    # Customize the layout for better visibility and aesthetics
    fig_colorful_bar.update_layout(
        xaxis_title="Company",
        yaxis_title="Number of Selections",
        height=600,
        width=800,
        template="plotly_dark",  # Dark theme
        font=dict(size=12),
        bargap=0.1  # Adjust gap between bars for a cleaner look
    )
    # st.plotly_chart(fig_colorful_bar)

    company_list = df['company'].unique()

    # Convert the company list to a list, and ensure 'Google' is the first option
    # company_list = sorted(company_list, key=lambda x: (x != 'Google', x))
    company_name = st.selectbox('Select Company', company_list)

    selected_comp_db = df[df['company'] == company_name]
    num_students = selected_comp_db['name'].count()
    st.write(f"Total selections in {company_name} : {num_students}")
    st.write(f"Branches under {company_name} : ")

    branch_wise_data = selected_comp_db.groupby('branch_code').agg(
        Number_of_Students=('name', 'count'),
    ).reset_index()



    branch_wise_data.columns = ["Branch", "Number of Students"]
    st.table(branch_wise_data)

    if len(branch_wise_data) > 1:
        # Create a pie chart using Plotly
        fig = px.pie(branch_wise_data, values='Number of Students', names='Branch',
                     title=f'Student Distribution by Branch for {company_name}',
                     hole=0.3)  # Optional: for a donut chart, set hole > 0

        st.plotly_chart(fig)

    if selected_comp_db['stipend'].nunique() > 1:
        # Aggregate the stipend offers
        stipend_data = selected_comp_db.groupby('stipend').size().reset_index(name='Number of Offers')

        # Create a pie chart using Plotly
        fig = px.pie(stipend_data, values='Number of Offers', names='stipend',
                     title=f'Stipend Distribution for {company_name}',
                     hole=0.3)  # Optional: for a donut chart, set hole > 0

        st.plotly_chart(fig)

    registration_numbers = selected_comp_db['registration number'].tolist()
    names = selected_comp_db['name'].tolist()
    with st.expander(f"Registration Numbers and Names for {company_name}", expanded=False):
        for reg_num, name in zip(registration_numbers, names):
            st.write(f"{reg_num}  -  {name}")


# Tab 3: Overall Stats
def tab3_content(df):
    st.subheader("Overall Statics : ")
    stipend_data = df.dropna(subset=['stipend'])
    min_stipend = stipend_data['stipend'].min()
    max_stipend = stipend_data['stipend'].max()
    avg_stipend = stipend_data['stipend'].mean().round(2)
    median_stipend = stipend_data['stipend'].median()
    total_students = df['name'].count()
    st.write(f"- *Minimum Stipend*: {min_stipend}")
    st.write(f"- *Maximum Stipend*: {max_stipend}")
    st.write(f"- *Average Stipend*: {avg_stipend}")
    st.write(f"- *Median Stipend*: {median_stipend}")
    st.write(f"- *Number of Students got Internships*: {total_students}")

    st.warning(
        "*Note:*\n"
        "- Stipend information is not available for some companies (shown as 'Not Provided'), and the bar chart below includes a 'Not Provided' category.\n"
        "- The statistics may not include off-campus offers."
    )

    # print(stipend_data)

    def categorize_stipend(stipend):
        if pd.isna(stipend):  # Check for NaN
            return 'Not Provided'
        elif stipend <= 50000:
            return '<= 50k'
        elif 50000 < stipend <= 100000:
            return '50k - 1lakh'
        else:
            return '> 1lakh'


    # Apply the categorization
    df['stipend_range'] = df['stipend'].apply(categorize_stipend)

    # Count the number of students in each stipend range
    stipend_count = df['stipend_range'].value_counts().reset_index()
    stipend_count.columns = ['Stipend Range', 'Number of Students']
    stipend_order = ['Not Provided', '<= 50k', '50k - 1lakh', '> 1lakh']
    stipend_count['Stipend Range'] = pd.Categorical(stipend_count['Stipend Range'], categories=stipend_order,
                                                    ordered=True)

    # Sort the DataFrame based on the custom order
    stipend_count = stipend_count.sort_values('Stipend Range')

    # Create the bar graph
    fig = px.bar(stipend_count,
                 x='Stipend Range',
                 y='Number of Students',
                 title='Number of Students by Stipend Range',
                 color='Number of Students',
                 color_continuous_scale=px.colors.sequential.Plasma)

    # Update layout
    fig.update_layout(
        xaxis_title='Stipend Range',
        yaxis_title='Number of Students',
        title_font=dict(size=20),
        font=dict(size=14),
    )

    # Show the graph in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    all_branch_data = df.groupby('branch_code').agg(
        Number_of_Students=('name', 'count'),
        Average_Stipend=('stipend', 'mean')
    ).reset_index()

    all_branch_data.columns = ['Branch', 'Number of Students', 'Average Stipend']
    all_branch_data['Average Stipend'] = all_branch_data['Average Stipend'].fillna(0)
    st.table(all_branch_data)

    company_data = df.groupby('company').agg(
        Number_of_Students=('name', 'count'),
        Average_Stipend=('stipend', 'mean')
    ).reset_index()

    num_companies = company_data['company'].nunique()
    st.write(f"Total number of companies visited : {num_companies}")

    company_data.columns = ['Company', 'Number of Students', 'Average Stipend']
    company_data['Average Stipend'] = company_data['Average Stipend'].fillna('-')
    st.write("List of Companies : ")
    st.table(company_data)

def tab4_content(df):
    st.subheader("Search Student Details")
    search_type = st.selectbox("Search by", ["Registration Number", "Name"])

    if search_type == "Registration Number":
        reg_number = st.text_input("Enter Registration Number:")
    else:
        name_substring = st.text_input("Enter Student Name:")

    # Search button
    if st.button("Search"):
        if search_type == "Registration Number" and reg_number:
            # Filter data based on registration number
            result = df[df['registration number'].str.strip() == reg_number.strip()]
            if not result.empty:
                # Display results
                st.write("**Student Details:**")
                st.write(f"**Name:** {result['name'].values[0]}")
                st.write(f"**Company:** {result['company'].values[0]}")
                st.write(f"**Stipend:** {result['stipend'].values[0]}")
            else:
                st.warning("No records found.")

        elif search_type == "Name" and name_substring:
            # Filter data based on name substring (case insensitive)
            result = df[df['name'].str.contains(name_substring.strip(), case=False, na=False)]

            if not result.empty:
                # Display results in a table
                st.write("**Matching Students:**")
                # result.columns = ['Student Name', 'Company Name', 'Stipend Amount']
                st.table(result[['registration number', 'name', 'company', 'stipend']])  # Display relevant columns
            else:
                st.warning("No matching records found.")
