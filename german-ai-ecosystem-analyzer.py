import streamlit as st
import pandas as pd
from crewai import Agent, Task, Crew, Process
from langchain_groq import ChatGroq
import os

# Set page config
st.set_page_config(
    page_title="German AI Startup Ecosystem Analyzer",
    page_icon="🤖",
    layout="wide"
)

# Title and description
st.title("German AI Startup Ecosystem Analyzer")
st.write("""
This application provides in-depth analysis of the German AI Startup ecosystem. 
Upload your dataset and ask questions to get detailed insights from our AI agents.
""")

# File upload and API key input
groq_api_key = st.text_input("Enter your Groq API key:", type="password")
uploaded_file = st.file_uploader("Upload your AI startups dataset (Excel file)", type=['xlsx'])

if uploaded_file and groq_api_key:
    # Read the dataset
    df = pd.read_excel(uploaded_file)
    
    # Set up Groq
    os.environ["GROQ_API_KEY"] = groq_api_key
    GROQ_LLM = ChatGroq(model_name="groq/llama2-70b-4096", temperature=0.3)

    # Define agents
    data_processor = Agent(
        role='Data Processing Specialist',
        goal='Process and structure startup data for analysis',
        backstory="""You are an expert in data analysis with deep knowledge of 
        startup ecosystems. Your role is to process and structure raw startup 
        data to enable meaningful analysis.""",
        llm=GROQ_LLM,
        verbose=True
    )

    market_analyst = Agent(
        role='Market Research Analyst',
        goal='Analyze market trends and patterns in the startup ecosystem',
        backstory="""You are a seasoned market analyst specializing in AI and 
        technology startups. You excel at identifying patterns, trends, and 
        market opportunities.""",
        llm=GROQ_LLM,
        verbose=True
    )

    insight_generator = Agent(
        role='Strategic Insight Generator',
        goal='Generate actionable insights and recommendations',
        backstory="""You are an expert in synthesizing complex startup ecosystem 
        data into clear, actionable insights. You specialize in identifying key 
        trends and making strategic recommendations.""",
        llm=GROQ_LLM,
        verbose=True
    )

    # Create query interface
    query_type = st.selectbox(
        "What type of analysis would you like to perform?",
        ["Market Overview", "Sector Analysis", "Funding Patterns", "Technology Trends", "Custom Query"]
    )

    if query_type == "Custom Query":
        custom_query = st.text_input("Enter your specific question about the German AI startup ecosystem:")
    else:
        custom_query = None

    if st.button("Generate Analysis"):
        startup_data = df.to_json(orient='records')

        # Define tasks based on query type
        data_processing_task = Task(
            description=f"""Process the startup data and prepare it for analysis. 
            Focus on cleaning and structuring the data for the following query type: {query_type}
            Data: {startup_data}""",
            agent=data_processor
        )

        analysis_task = Task(
            description=f"""Analyze the processed data to identify patterns and trends.
            Query type: {query_type}
            Custom query: {custom_query if custom_query else 'None'}
            Consider factors like funding, technology focus, geographic distribution, and growth patterns.""",
            agent=market_analyst
        )

        insight_task = Task(
            description=f"""Generate comprehensive insights and recommendations based on the analysis.
            Focus on actionable takeaways and strategic implications for stakeholders in the German AI ecosystem.""",
            agent=insight_generator
        )

        # Create and run the crew
        crew = Crew(
            agents=[data_processor, market_analyst, insight_generator],
            tasks=[data_processing_task, analysis_task, insight_task],
            process=Process.sequential
        )

        with st.spinner("Analyzing data..."):
            result = crew.kickoff()

        # Display results in organized sections
        st.subheader("Analysis Results")
        
        # Create tabs for different sections of the analysis
        tab1, tab2, tab3 = st.tabs(["Key Findings", "Detailed Analysis", "Recommendations"])
        
        with tab1:
            st.markdown(data_processing_task.output.raw)
        
        with tab2:
            st.markdown(analysis_task.output.raw)
        
        with tab3:
            st.markdown(insight_task.output.raw)

else:
    st.warning("Please upload your dataset and provide your Groq API key to begin the analysis.")

# Add footer with usage instructions
st.markdown("---")
st.markdown("""
### How to Use This Tool
1. Upload your Excel file containing German AI startup data
2. Enter your Groq API key
3. Select an analysis type or enter a custom query
4. Click "Generate Analysis" to receive insights

The analysis will provide you with structured insights about the German AI startup ecosystem based on your specific questions and needs.
""")
