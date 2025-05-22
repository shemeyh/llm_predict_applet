import streamlit as st
import os
from datetime import datetime
import asyncio # Though Streamlit handles its own loop, useful for structure
from logic.forecast_single_question import forecast_single_question

async def get_forecast_results(user_question: str, resolution_criteria: str, user_news: str, api_key: str):
    """Sets API key, constructs question details, calls forecast, and handles errors."""
    try:
        os.environ['OPENAI_API_KEY'] = api_key
        
        question_details = {
            "title": user_question,
            "description": f"{user_question}\n\nResolution Criteria:\n{resolution_criteria}",
            "fine_print": "",
            "resolution_criteria": resolution_criteria,
            "publish_time": datetime.now().isoformat(),
            "close_time": datetime.now().isoformat(), # Dummy date
            "resolve_time": datetime.now().isoformat(), # Dummy date
            "id": 0,  # Dummy ID
            "type": "binary" 
        }
        
        full_results_json = await forecast_single_question(
            question_details=question_details,
            cache_seed=42, # Example cache seed
            is_multiple_choice=False, # Assuming binary
            options=None, # No options for binary
            news=user_news
        )
        return full_results_json
    except Exception as e:
        return {"error": str(e)}

def display_deliberation_phase(deliberation_data):
    if not deliberation_data:
        st.info("No deliberation data to display.")
        return

    st.header("Phase 1: Initial Expert Forecasts")
    
    # deliberation_data is expected to be a dictionary where keys are expert names
    # and values are dictionaries of their analyses (based on the sample and previous step).
    # The previous step stored `forecast_data.get("results")` into `st.session_state.deliberation_results`.
    # Let's assume `deliberation_data` here refers to `st.session_state.deliberation_results`.

    for expert_name, data in deliberation_data.items():
        with st.expander(f"Expert: {expert_name}", expanded=False):
            if not isinstance(data, dict): # Basic check if data is not as expected
                st.warning(f"Could not display data for {expert_name} due to unexpected format.")
                continue

            st.markdown("#### Perspective Relevance")
            st.write(data.get('perspective_relevance', "Not provided"))

            st.markdown("#### Status Quo Assessment")
            st.write(data.get('status_quo', "Not provided"))

            st.markdown("#### Perspective-Derived Factors")
            factors = data.get('perspective_derived_factors', [])
            if factors:
                for factor_item in factors:
                    factor_name = factor_item.get('factor', 'Unnamed Factor')
                    factor_effect = factor_item.get('effect', 'No effect description')
                    st.markdown(f"- **{factor_name}:** {factor_effect}")
            else:
                st.write("No specific factors provided.")

            st.markdown("#### 'No' Scenario")
            st.write(data.get('no_scenario', "Not provided"))

            st.markdown("#### 'Yes' Scenario")
            st.write(data.get('yes_scenario', "Not provided"))

            st.markdown("#### Final Reasoning (Phase 1)")
            st.write(data.get('final_reasoning', "Not provided"))
            
            probability = data.get('final_probability')
            if probability is not None:
                st.metric(label="Forecasted Probability (Phase 1)", value=f"{probability}%")
            else:
                st.write("Final probability not provided.")

def display_group_results_phase(group_results_data):
    if not group_results_data:
        # It's possible this phase doesn't always exist, so not finding data might be normal.
        # st.info("No group review data to display.") 
        return 

    st.header("Phase 2: Expert Peer Review")

    # group_results_data is expected to be a dictionary where keys are reviewing expert names
    # and values are dictionaries containing their review/critique.
    # Assumes this refers to `st.session_state.group_results`.

    for expert_name, review_data in group_results_data.items():
        with st.expander(f"Review by: {expert_name}", expanded=False):
            if not isinstance(review_data, dict):
                st.warning(f"Could not display review data for {expert_name} due to unexpected format.")
                continue

            st.markdown(f"**Engaging With:** {review_data.get('forecaster_to_engage', 'N/A')}")
            
            response_type = review_data.get('response_type', 'N/A').title()
            st.markdown(f"**Response Type:** {response_type}")
            
            st.markdown("#### Response:")
            st.write(review_data.get('response', "No response text provided."))

def display_revision_phase(revision_data):
    if not revision_data:
        # It's possible this phase doesn't always exist.
        # st.info("No revision data to display.")
        return

    st.header("Phase 3: Revised Expert Forecasts")

    # revision_data is expected to be a dictionary where keys are expert names
    # and values are dictionaries of their revised analyses.
    # Assumes this refers to `st.session_state.revision_results`.

    for expert_name, data in revision_data.items():
        with st.expander(f"Expert: {expert_name} (Revision)", expanded=False):
            if not isinstance(data, dict):
                st.warning(f"Could not display revision data for {expert_name} due to unexpected format.")
                continue

            initial_prob = data.get('my_phase1_final_probability')
            if initial_prob is not None:
                st.metric(label="Initial Probability (Phase 1)", value=f"{initial_prob}%")
            
            st.markdown("#### Reasoning for Revision")
            st.write(data.get('reasoning_for_revised_probability', "No revision reasoning provided."))
            
            revised_prob = data.get('revised_probability')
            if revised_prob is not None:
                st.metric(label="Revised Probability (Phase 3)", value=f"{revised_prob}%")
            else:
                st.write("Revised probability not provided.")
            
            # Optionally, if other details like factors/scenarios can also be revised and are present,
            # they could be displayed here as well, similar to the deliberation phase display.
            # For now, focusing on what's explicitly in the 'revision_results' sample structure.
            # Example:
            # if 'perspective_derived_factors' in data: # Check if factors were part of revision output
            #     st.markdown("#### Revised Perspective-Derived Factors")
            #     factors = data.get('perspective_derived_factors', [])
            #     if factors:
            #         for factor_item in factors:
            #             factor_name = factor_item.get('factor', 'Unnamed Factor')
            #             factor_effect = factor_item.get('effect', 'No effect description')
            #             st.markdown(f"- **{factor_name}:** {factor_effect}")
            #     else:
            #         st.write("No specific revised factors provided.")

def main():
    st.set_page_config(page_title="AI Forecasting Applet", layout="wide")
    st.title("🔮 AI Forecasting Applet")

    # Initialize session state variables
    if 'final_result' not in st.session_state:
        st.session_state.final_result = None
    if 'summarization' not in st.session_state:
        st.session_state.summarization = None
    if 'deliberation_results' not in st.session_state:
        st.session_state.deliberation_results = None
    if 'group_results' not in st.session_state:
        st.session_state.group_results = None
    if 'revision_results' not in st.session_state:
        st.session_state.revision_results = None
    if 'deliberation_mean_probability' not in st.session_state:
        st.session_state.deliberation_mean_probability = None
    if 'revision_mean_probability' not in st.session_state:
        st.session_state.revision_mean_probability = None
    
    st.write("Welcome! This applet uses AI to forecast the probability of an event based on your input.")
    st.write("Please fill in the details below and click 'Get Forecast'.")

    st.subheader("1. Your Question")
    user_question = st.text_input("Enter the question you want a forecast for (e.g., 'Will X happen by Y date?'):", key="user_question")

    st.subheader("2. Resolution Criteria")
    resolution_criteria = st.text_area("Specify how this question will be judged true or false (e.g., 'Based on official report from Z'):", height=100, key="resolution_criteria")

    st.subheader("3. Relevant News Articles")
    user_news = st.text_area("Paste any relevant news article text below (one article per line or separated by double newlines is fine):", height=200, key="user_news")

    st.subheader("4. Your OpenAI API Key")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password", key="api_key", help="Your API key is kept confidential and used only for this session's forecast.")

    st.markdown("---") # Visual separator

    col1, col2, col3 = st.columns([2,1,2]) # Create columns for button alignment
    with col2: # Place button in the middle column
        run_button = st.button("Get Forecast", use_container_width=True)

    # Placeholder for logic when button is clicked
    if run_button:
        # Retrieve inputs from session_state
        user_question_val = st.session_state.user_question
        resolution_criteria_val = st.session_state.resolution_criteria
        user_news_val = st.session_state.user_news
        api_key_val = st.session_state.api_key

        if not api_key_val or not user_question_val:
            st.warning("Please provide your OpenAI API key and a question.")
        else:
            with st.spinner("Forecasting in progress... please wait."):
                forecast_data = asyncio.run(get_forecast_results(
                    user_question_val, 
                    resolution_criteria_val, 
                    user_news_val, 
                    api_key_val
                ))
                
                if forecast_data.get("error"):
                    st.error(f"Forecast failed: {forecast_data['error']}")
                    st.session_state.final_result = None
                    st.session_state.summarization = forecast_data['error']
                    st.session_state.deliberation_results = None
                    st.session_state.group_results = None
                    st.session_state.revision_results = None
                    st.session_state.deliberation_mean_probability = None
                    st.session_state.revision_mean_probability = None
                else:
                    st.success("Forecast completed!")
                    # Using .get("statistics", {}) to safely access nested dictionary
                    final_prob_stats = forecast_data.get("statistics", {}).get("final_result")
                    # The sample JSON's final_result under statistics IS the final one.
                    # If a different logic is needed based on phase, it would be:
                    # final_prob = forecast_data.get("revision_probability_result", forecast_data.get("deliberation_probability_result"))
                    st.session_state.final_result = final_prob_stats 

                    st.session_state.summarization = forecast_data.get("summary")
                    
                    # Extracting from the main level of forecast_data as per sample JSON structure
                    st.session_state.deliberation_results = forecast_data.get("results") # 'results' in final_json contains expert forecasts
                    st.session_state.group_results = forecast_data.get("group_results") # Assuming this key might appear
                    st.session_state.revision_results = forecast_data.get("revision_results") # Assuming this key might appear
                    
                    # Mean probabilities from statistics block
                    stats = forecast_data.get("statistics", {})
                    st.session_state.deliberation_mean_probability = stats.get("mean_first_step") # mean_first_step is deliberation
                    st.session_state.revision_mean_probability = stats.get("mean_second_step") # mean_second_step is revision

    # --- Display Results ---
    if st.session_state.get('final_result') is not None:
        st.markdown("---") 
        st.header("📊 Forecast Summary & Aggregated Results")

        # Display Overall Final Probability
        overall_final_prob = st.session_state.get('final_result')
        # The final_result from statistics is already a number (int for binary, dict for MC)
        # For binary, it's a percentage.
        if isinstance(overall_final_prob, (float, int)):
             st.metric(label="Overall Final Forecast Probability", value=f"{overall_final_prob}%")
        else: # For multiple choice, it might be a dict.
             st.write("Overall Final Forecast:")
             st.json(overall_final_prob)


        # Display Mean Probabilities using columns
        col1, col2 = st.columns(2)
        
        deliberation_mean = st.session_state.get('deliberation_mean_probability')
        if deliberation_mean is not None:
            with col1:
                st.metric(label="Mean Deliberation Probability (Phase 1)", value=f"{deliberation_mean:.1f}%")
        
        revision_mean = st.session_state.get('revision_mean_probability')
        if revision_mean is not None:
            with col2:
                st.metric(label="Mean Revised Probability (Phase 3)", value=f"{revision_mean:.1f}%")
        
        # Display overall text summary
        if st.session_state.get('summarization'):
            st.subheader("📝 Overall Analysis Summary")
            st.info(st.session_state.summarization)

        st.markdown("---") # Separator before detailed phase breakdown
        
        # Now, call the detailed phase display functions
        if st.session_state.get('deliberation_results'):
            display_deliberation_phase(st.session_state.deliberation_results)

        if st.session_state.get('group_results'):
            display_group_results_phase(st.session_state.group_results)

        if st.session_state.get('revision_results'):
            display_revision_phase(st.session_state.revision_results)

    elif st.session_state.get('summarization') is not None and st.session_state.get('final_result') is None:
        # This implies an error occurred and was stored in summarization,
        # and the error message is already displayed via st.error in the button logic.
        # No need to display it again here, st.error above is sufficient.
        pass


if __name__ == "__main__":
    main()
