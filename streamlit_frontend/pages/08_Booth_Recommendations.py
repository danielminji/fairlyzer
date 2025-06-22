import streamlit as st
from lib import api
from lib.auth_client import require_auth
from lib.navigation import display_sidebar_navigation
from datetime import datetime # Import datetime
from lib.ocr_utils import get_image_from_url, highlight_booths_on_map # Import OCR utils
from PIL import Image # For checking if an image is returned
import requests # For Geoapify directions API call
import folium # For interactive route map
from streamlit_folium import st_folium # For interactive route map
from streamlit_geolocation import streamlit_geolocation # UPDATED IMPORT

st.set_page_config(
    page_title="Job Fair Details & Recommendations - Resume Analyzer", # Updated Title
    page_icon="🎯",
    layout="wide"
)

# Define the missing helper function here
def format_job_fair_display(job_fair_dict):
    if not isinstance(job_fair_dict, dict):
        return "Invalid Job Fair Data"
    title = job_fair_dict.get('title', 'N/A')
    start_datetime_str = job_fair_dict.get('start_datetime')
    start_date_str = "Unknown Start"
    if start_datetime_str:
        try:
            start_date_str = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00')).strftime('%d %b %Y')
        except ValueError:
            start_date_str = start_datetime_str.split('T')[0] # Fallback to just date part
    return f"{title} (Starts: {start_date_str})"

def render_match_details_for_booth_rec(match_details):
    # Similar to the one in resume_analysis.py but adapted for booth recs if needed
    if not match_details:
        st.caption("No detailed match information available.")
        return

    cols = st.columns(3)
    with cols[0]:
        st.markdown("**General Skills**")
        if match_details.get('matched_general_skills'):
            st.markdown("Matched: " + ", ".join(match_details['matched_general_skills']))
        if match_details.get('missing_general_skills'):
            st.markdown("<span style='color: orange'>Missing: " + ", ".join(match_details['missing_general_skills']) + "</span>", unsafe_allow_html=True)
        if not match_details.get('matched_general_skills') and not match_details.get('missing_general_skills'):
            st.caption("N/A")
    
    with cols[1]:
        st.markdown("**Soft Skills**")
        if match_details.get('matched_soft_skills'):
            st.markdown("Matched: " + ", ".join(match_details['matched_soft_skills']))
        if match_details.get('missing_soft_skills'):
            st.markdown("<span style='color: orange'>Missing: " + ", ".join(match_details['missing_soft_skills']) + "</span>", unsafe_allow_html=True)
        if not match_details.get('matched_soft_skills') and not match_details.get('missing_soft_skills'):
            st.caption("N/A")

    with cols[2]:
        st.markdown("**Experience**")
        exp_met_color = "green" if match_details.get('experience_met') else "orange"
        st.markdown(f"Required: {match_details.get('required_experience_years', 'N/A')} years")
        st.markdown(f"<span style='color: {exp_met_color}'>Your Experience: {match_details.get('resume_formatted_total_experience', 'N/A')}</span>", unsafe_allow_html=True)
        
        st.markdown("**Education (CGPA)**")
        edu_met_color = "green" if match_details.get('education_met') else "orange"
        st.markdown(f"Required: {match_details.get('required_cgpa', 'N/A')}")
        st.markdown(f"<span style='color: {edu_met_color}'>Your CGPA: {match_details.get('resume_cgpa', 'N/A')}</span>", unsafe_allow_html=True)

@require_auth() # Basic authentication
def display_job_fair_page(): # Renamed function for clarity
    display_sidebar_navigation()
    st.title("🌟 Job Fair Details & Personalized Booth Recommendations") # Updated Title

    # Retrieve resume_id from session state (set by 02_resume_analysis.py)
    resume_id_from_session = st.session_state.get('current_resume_id_for_booth_recommendation')

    if not resume_id_from_session:
        st.error("No resume selected. Please go back to Resume Analysis and click the button to find recommendations.")
        if st.button("Go to Resume Analysis"):
            st.switch_page("pages/02_resume_analysis.py")
        st.stop()

    st.query_params.resume_id = str(resume_id_from_session)
    current_resume_id = resume_id_from_session
    st.info(f"Finding recommendations for Resume ID: **{current_resume_id}**") # Changed to st.info for less emphasis than title

    # --- Fetch Job Fairs for Selection ---
    job_fairs_data, success = api.get_all_job_fairs() 
    job_fairs_list = []
    if success and job_fairs_data and isinstance(job_fairs_data.get('data'), list):
        job_fairs_list = job_fairs_data['data']
    elif not success:
        st.error(f"Failed to load job fairs: {job_fairs_data.get('error', 'Please try again.') if isinstance(job_fairs_data, dict) else 'Error'}")
        return
    
    if not job_fairs_list:
        st.warning("No active job fairs found or failed to parse them.")
        return

    # --- Job Fair Selection --- 
    # Use a session state variable to store selected job fair ID to persist selection across reruns for tabs
    if 'selected_job_fair_id_for_details' not in st.session_state:
        st.session_state.selected_job_fair_id_for_details = None

    job_fair_options = {jf['id']: format_job_fair_display(jf) for jf in job_fairs_list}
    # Add a "Select a Job Fair" option to allow deselection or initial state
    options_with_prompt = {None: "-- Select a Job Fair --"} # type: ignore
    options_with_prompt.update(job_fair_options)
    
    def on_job_fair_change():
        # Clear dependent states when job fair changes
        st.session_state.pop('personalized_booth_recommendations', None)
        st.session_state.pop('directions_map_html', None) # Clear map
        st.session_state.pop('directions_info', None) # Clear directions info
        # Any other states that depend on the specific job fair details can be cleared here too

    selected_job_fair_id = st.selectbox(
        "Select a Job Fair to View Details and Get Recommendations:",
        options=list(options_with_prompt.keys()),
        format_func=lambda x: options_with_prompt[x],
        key="selected_job_fair_id_for_details", # Using the session state key directly
        on_change=on_job_fair_change
    )

    st.markdown("---")

    # --- Display Details if a Job Fair is Selected ---
    if selected_job_fair_id:
        selected_fair_details = next((jf for jf in job_fairs_list if jf['id'] == selected_job_fair_id), None)
        
        if not selected_fair_details:
            st.error("Could not load details for the selected job fair. It might have been removed.")
            return

        st.header(f"{selected_fair_details.get('title', 'Job Fair Details')}")

        # --- Tabs for Job Fair Information ---
        tab_details_location, tab_floor_plan, tab_all_openings, tab_recommendations = st.tabs([
            "📍 Details & Location", 
            "🗺️ Floor Plan", 
            "📋 All Openings", 
            "🎯 Recommendations"
        ])

        with tab_details_location:
            st.subheader("Event Information")
            # ... (Logic from 07_Explore_Job_Fairs for description, dates, organizer, status) ...
            st.markdown(f"**Description:** {selected_fair_details.get('description', 'N/A')}")
            start_date = selected_fair_details.get('start_datetime', '')
            end_date = selected_fair_details.get('end_datetime', '')
            if start_date and end_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    st.markdown(f"**Dates:** {start_dt.strftime('%B %d, %Y, %I:%M %p')} to {end_dt.strftime('%B %d, %Y, %I:%M %p')}")
                except ValueError:
                    st.markdown(f"**Dates:** {start_date} - {end_date}")
            st.markdown(f"**Organizer:** {selected_fair_details.get('organizer', {}).get('name', 'N/A')}") # Assuming organizer is nested like in 07
            st.markdown(f"**Status:** {selected_fair_details.get('status', 'N/A').capitalize()}")

            st.subheader("Location")
            # ... (Logic from 07_Explore_Job_Fairs for formatted_address, static map, Get Directions) ...
            loc_query = selected_fair_details.get('location_query')
            formatted_addr = selected_fair_details.get('formatted_address')
            lat = selected_fair_details.get('latitude')
            lon = selected_fair_details.get('longitude')

            if formatted_addr:
                st.markdown(f"**Address:** {formatted_addr}")
            elif loc_query:
                st.markdown(f"**Location Queried:** {loc_query}")
            else:
                st.info("Location information not available.")
            
            if lat and lon:
                if 'GEOAPIFY_API_KEY' not in st.secrets:
                    st.warning("Geoapify API key not found. Map and directions unavailable.")
                else:
                    GEOAPIFY_API_KEY = st.secrets['GEOAPIFY_API_KEY']
                    static_map_url = f"https://maps.geoapify.com/v1/staticmap?style=osm-carto&width=600&height=400&center=lonlat:{lon},{lat}&zoom=14&marker=lonlat:{lon},{lat};color:%23ff0000;size:medium&apiKey={GEOAPIFY_API_KEY}"
                    st.image(static_map_url, caption=f"Map of {formatted_addr or loc_query or 'Job Fair'}")
                    
                    st.markdown("---")
                    st.subheader("Get Directions")

                    # Initialize session state for directions and user location
                    session_key_base = f"directions_jf_{selected_job_fair_id}"
                    if f"{session_key_base}_user_lat" not in st.session_state:
                        st.session_state[f"{session_key_base}_user_lat"] = None
                    if f"{session_key_base}_user_lon" not in st.session_state:
                        st.session_state[f"{session_key_base}_user_lon"] = None
                    if f"{session_key_base}_location_status" not in st.session_state:
                        st.session_state[f"{session_key_base}_location_status"] = "Attempting to retrieve location..."
                    if f"{session_key_base}_route_data_for_map" not in st.session_state:
                        st.session_state[f"{session_key_base}_route_data_for_map"] = None
                    if f"{session_key_base}_info" not in st.session_state:
                        st.session_state[f"{session_key_base}_info"] = None
                    if f"{session_key_base}_fetch_location_requested" not in st.session_state: # New flag
                        st.session_state[f"{session_key_base}_fetch_location_requested"] = False
                    if f"{session_key_base}_display_directions_active" not in st.session_state: # New flag for controlling display
                        st.session_state[f"{session_key_base}_display_directions_active"] = False

                    location_status_placeholder = st.empty()
                    # location_status_placeholder.info(st.session_state[f"{session_key_base}_location_status"]) # Initial message set below or by component outcome

                    # --- Only show location fetching UI if we don't have coordinates yet, or user explicitly requests ---
                    if st.session_state.get(f"{session_key_base}_user_lat") is None:
                        location_status_placeholder.info("Click the button to use your current location for directions.")
                        if st.button("📍 Use My Current Location", key=f"{session_key_base}_get_loc_btn"):
                            st.session_state[f"{session_key_base}_fetch_location_requested"] = True
                            st.session_state[f"{session_key_base}_location_status"] = "Attempting to retrieve location..." # Set status before rerun
                            location_status_placeholder.info(st.session_state[f"{session_key_base}_location_status"])
                            st.rerun() # Rerun to make the flag take effect and render the geolocation component

                        if st.session_state.get(f"{session_key_base}_fetch_location_requested"):
                            # This block runs after the first rerun when fetch_location_requested is True
                            location_status_placeholder.info(st.session_state[f"{session_key_base}_location_status"]) # Show "Attempting..."
                            location_data = streamlit_geolocation() 

                            if location_data: # Component has returned something
                                new_lat = location_data.get('latitude')
                                new_lon = location_data.get('longitude')
                                error_info = location_data.get('error')
                                
                                processed_location = False # Flag to indicate if we got a definitive outcome

                                if new_lat is not None and new_lon is not None:
                                    st.session_state[f"{session_key_base}_user_lat"] = new_lat
                                    st.session_state[f"{session_key_base}_user_lon"] = new_lon
                                    st.session_state[f"{session_key_base}_location_status"] = f"Location found: Lat {new_lat:.4f}, Lon {new_lon:.4f}"
                                    # Placeholder will be updated outside this if/else after flag reset by success or error
                                    processed_location = True
                                elif error_info:
                                    error_message = error_info.get('message', 'Unknown error')
                                    error_code = error_info.get('code', 'N/A')
                                    st.session_state[f"{session_key_base}_user_lat"] = None # Clear any stale lat/lon
                                    st.session_state[f"{session_key_base}_user_lon"] = None
                                    st.session_state[f"{session_key_base}_location_status"] = f"Error getting location (Code: {error_code}): {error_message}"
                                    processed_location = True
                                
                                if processed_location:
                                    st.session_state[f"{session_key_base}_fetch_location_requested"] = False # Reset flag
                                    # Clear map/info as location context has changed (either new or errored)
                                    st.session_state[f"{session_key_base}_route_data_for_map"] = None
                                    st.session_state[f"{session_key_base}_info"] = None
                                    st.rerun() # Rerun to reflect new state (either display location or error, and remove geolocation widget)
                                # If location_data is not None but not processed (no coords, no error), component is still trying.
                                # "Attempting..." message remains via the placeholder.info above.
                    else:
                        # We have lat/lon, so display the success/error message directly from session state
                        current_status = st.session_state[f"{session_key_base}_location_status"]
                        if "Error" in current_status:
                            location_status_placeholder.error(current_status)
                        else:
                            location_status_placeholder.success(current_status)

                    # The rest of the logic that uses user_lat and user_lon remains the same
                    user_lat = st.session_state.get(f"{session_key_base}_user_lat")
                    user_lon = st.session_state.get(f"{session_key_base}_user_lon")

                    if user_lat and user_lon:
                        travel_modes = {"Driving": "drive", "Walking": "walk", "Bicycling": "bicycle", "Transit": "transit"}
                        selected_travel_mode_display = st.selectbox("Travel mode:", options=list(travel_modes.keys()), key=f"{session_key_base}_travel_mode")
                        travel_mode_api_value = travel_modes[selected_travel_mode_display]

                        # REMOVED External Map Links from here

                        if st.button("Show Directions", key=f"{session_key_base}_show_dir_btn"):
                            # Clear previous data
                            st.session_state[f"{session_key_base}_route_data_for_map"] = None 
                            st.session_state[f"{session_key_base}_info"] = None   
                            st.session_state[f"{session_key_base}_display_directions_active"] = False 
                            with st.spinner("Fetching directions..."):
                                route_data_from_api, success_dir = api.get_directions_to_job_fair(
                                    job_fair_id=selected_job_fair_id,
                                    user_lat=user_lat,
                                    user_lon=user_lon,
                                    mode=travel_mode_api_value
                                )
                                if success_dir and route_data_from_api and route_data_from_api.get('data'):
                                    route_data = route_data_from_api['data']
                                    if route_data and 'features' in route_data and route_data['features']:
                                        # st.success("Directions found!") # Success message will be part of the display block
                                        properties = route_data['features'][0]['properties']
                                        distance_km = properties.get('distance', 0) / 1000
                                        time_seconds = properties.get('time', 0)
                                        
                                        directions_info_list = []
                                        if time_seconds > 0:
                                            hours, rem = divmod(time_seconds, 3600)
                                            minutes, _ = divmod(rem, 60)
                                            directions_info_list.append({"label": f"Travel Time ({selected_travel_mode_display})", "value": f"{int(hours)}h {int(minutes)}m"})
                                        if distance_km > 0:
                                            directions_info_list.append({"label": f"Distance ({selected_travel_mode_display})", "value": f"{distance_km:.2f} km"})
                                        st.session_state[f"{session_key_base}_info"] = directions_info_list
                                        
                                        route_geometry_raw = route_data['features'][0].get('geometry', {})
                                        route_geometry_coords = route_geometry_raw.get('coordinates')
                                        geometry_type = route_geometry_raw.get('type')

                                        if route_geometry_coords:
                                            folium_route_coords = []
                                            if geometry_type == 'LineString':
                                                folium_route_coords = [[coord[1], coord[0]] for coord in route_geometry_coords]
                                            elif geometry_type == 'MultiLineString':
                                                for line_segment in route_geometry_coords:
                                                    folium_route_coords.extend([[coord[1], coord[0]] for coord in line_segment])
                                            
                                            if folium_route_coords and selected_fair_details: # Ensure selected_fair_details is available for marker
                                                jf_lat_for_map = selected_fair_details.get('latitude')
                                                jf_lon_for_map = selected_fair_details.get('longitude')
                                                if jf_lat_for_map and jf_lon_for_map:
                                                    # Store data needed to reconstruct the map, not the map object itself
                                                    st.session_state[f"{session_key_base}_route_data_for_map"] = {
                                                        "user_lat": user_lat,
                                                        "user_lon": user_lon,
                                                        "jf_lat": jf_lat_for_map,
                                                        "jf_lon": jf_lon_for_map,
                                                        "route_coords": folium_route_coords,
                                                        "jf_title": selected_fair_details.get('title', 'Job Fair')
                                                    }
                                                    # st.session_state[f"{session_key_base}_map_object"] = m # REMOVED storing map object
                                                    st.session_state[f"{session_key_base}_display_directions_active"] = True 
                                                else:
                                                    st.error("Job fair location coordinates are missing for map display.")
                                                    st.session_state[f"{session_key_base}_display_directions_active"] = False
                                            else: # No folium_route_coords or selected_fair_details missing
                                                st.error("Could not generate route path for the map.")
                                                st.session_state[f"{session_key_base}_display_directions_active"] = False
                                    else:
                                        st.error("Could not retrieve valid route data from API.")
                                        if route_data_from_api: st.json(route_data_from_api)
                                        st.session_state[f"{session_key_base}_display_directions_active"] = False
                                else:
                                    err_msg = route_data_from_api.get('error', 'Unknown API error') if isinstance(route_data_from_api, dict) else 'Unknown API error'
                                    st.error(f"Failed to get directions: {err_msg}")
                                    st.session_state[f"{session_key_base}_display_directions_active"] = False

                    # Display stored directions info, map, and links IF the flag is set
                    if st.session_state.get(f"{session_key_base}_display_directions_active"):
                        st.success("Directions found!") 
                        if st.session_state.get(f"{session_key_base}_info"):
                            for info_item in st.session_state[f"{session_key_base}_info"]:
                                st.metric(label=info_item["label"], value=info_item["value"])
                        
                        # --- Add External Map Links HERE, BEFORE the map is displayed ---
                        retrieved_travel_mode_display = st.session_state.get(f"{session_key_base}_travel_mode", "Driving") 
                        retrieved_travel_mode_api_value = travel_modes.get(retrieved_travel_mode_display, "drive")

                        if selected_fair_details and selected_fair_details.get('latitude') and selected_fair_details.get('longitude') and user_lat and user_lon:
                            jf_lat = selected_fair_details['latitude']
                            jf_lon = selected_fair_details['longitude']

                            google_maps_url = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={jf_lat},{jf_lon}&travelmode={retrieved_travel_mode_api_value}"
                            
                            apple_travel_flag = 'd' # default to driving
                            if retrieved_travel_mode_api_value == 'walk':
                                apple_travel_flag = 'w'
                            elif retrieved_travel_mode_api_value == 'transit':
                                apple_travel_flag = 'r'
                            
                            apple_maps_url = f"http://maps.apple.com/?saddr={user_lat},{user_lon}&daddr={jf_lat},{jf_lon}&dirflg={apple_travel_flag}"

                            col_gmap, col_amap = st.columns(2)
                            with col_gmap:
                                st.link_button("Open in Google Maps", google_maps_url, use_container_width=True)
                            with col_amap:
                                st.link_button("Open in Apple Maps", apple_maps_url, use_container_width=True)
                        # --- End External Map Links ---
                        
                        # Reconstruct map here if data is available
                        route_map_data = st.session_state.get(f"{session_key_base}_route_data_for_map")
                        if route_map_data:
                            try:
                                r_user_lat = route_map_data["user_lat"]
                                r_user_lon = route_map_data["user_lon"]
                                r_jf_lat = route_map_data["jf_lat"]
                                r_jf_lon = route_map_data["jf_lon"]
                                r_route_coords = route_map_data["route_coords"]
                                r_jf_title = route_map_data["jf_title"]

                                m = folium.Map(location=[(r_user_lat + r_jf_lat)/2, (r_user_lon + r_jf_lon)/2], zoom_start=7)
                                folium.Marker([r_user_lat, r_user_lon], popup="Your Location", icon=folium.Icon(color='blue', icon='user', prefix='fa')).add_to(m)
                                folium.Marker([r_jf_lat, r_jf_lon], popup=r_jf_title, icon=folium.Icon(color='red', icon='map-marker', prefix='fa')).add_to(m)
                                folium.PolyLine(r_route_coords, color="blue", weight=5, opacity=0.7).add_to(m)
                                m.fit_bounds([[min(r_user_lat, r_jf_lat), min(r_user_lon, r_jf_lon)], [max(r_user_lat, r_jf_lat), max(r_user_lon, r_jf_lon)]])
                                
                                map_render_output = st_folium(m, width=700, height=500, key=f"{session_key_base}_folium_map_RECONSTRUCTED")
                            except KeyError as e:
                                st.error(f"Error reconstructing map: Missing key {e}. Please try fetching directions again.")
                            except Exception as e:
                                st.error(f"An unexpected error occurred while reconstructing the map: {e}")

        with tab_floor_plan:
            st.subheader("Venue Floor Plan / Map")
            map_image_db_path = selected_fair_details.get('map_image_path') # Corrected to map_image_path
            
            if map_image_db_path:
                base_display_url = api.API_BASE_URL.replace("/api", "") # Use api.API_BASE_URL
                full_map_url = ""

                # Ensure map_image_db_path is a string before path operations
                if isinstance(map_image_db_path, str):
                    # Construct full_map_url robustly
                    if not map_image_db_path.startswith('/'):
                        map_image_db_path = '/' + map_image_db_path # path is now /job_fair_maps/....png

                    if not map_image_db_path.startswith('/storage/'):
                        # map_image_db_path is /job_fair_maps/....png
                        # map_image_db_path.lstrip('/') is job_fair_maps/....png
                        # Corrected line below:
                        full_map_url = f"{base_display_url}/storage/{map_image_db_path.lstrip('/')}"
                    else:
                        # Path already includes /storage/ (e.g. /storage/job_fair_maps/....png)
                        full_map_url = f"{base_display_url}{map_image_db_path}"
                else:
                    st.error("Map image path is not valid.")

                if full_map_url:
                    try:
                        # Fetch and display the image
                        response_test = requests.get(full_map_url, stream=True, timeout=10)
                        response_test.raise_for_status()
                        
                        content_type = response_test.headers.get('content-type')
                        if content_type and 'image' in content_type:
                            st.image(full_map_url, caption="Job Fair Layout", use_container_width=True)
                            # OCR Highlighting section (can be uncommented and refined later)
                            # if st.button("Highlight My Recommended Booths"):
                            #     recommended_booths_for_ocr = [] # Populate with actual recs
                            #     if recommended_booths_for_ocr:
                            #         with st.spinner("Analyzing map..."):
                            #             highlighted_image = highlight_booths_on_map(full_map_url, recommended_booths_for_ocr)
                            #             if isinstance(highlighted_image, Image.Image):
                            #                 st.image(highlighted_image, caption="Highlighted Booths")
                            #             else:
                            #                 st.error(highlighted_image) # Show error from OCR util
                            #     else:
                            #         st.info("No specific booths recommended to highlight on this map yet.")
                        else:
                            st.warning(f"The resource at the map URL does not appear to be a valid image. URL: {full_map_url}, Content-Type: {content_type}")
                            st.markdown(f"Problematic Map URL: `{full_map_url}`")
                    except requests.exceptions.RequestException as e_req:
                        st.error(f"Could not load map image from URL: {full_map_url}. Error: {e_req}")
                    except Exception as e_img:
                        st.error(f"An error occurred while trying to display the map image: {e_img}. URL: {full_map_url}")
            else:
                st.info("No floor plan uploaded for this job fair.")

        with tab_all_openings:
            # ... (Existing logic for listing all openings from 08_Booth_Recommendations) ...
            st.subheader("All Listed Openings at this Fair")
            all_openings_data, openings_success = api.get_job_fair_openings(selected_job_fair_id)
            if openings_success and all_openings_data and all_openings_data.get('data', {}).get('booths_with_openings'):
                booths_with_openings = all_openings_data['data']['booths_with_openings']
                if not booths_with_openings: 
                    st.info("No booths or job openings currently listed for this job fair.")
                else:
                    for booth in booths_with_openings:
                        with st.expander(f"**{booth.get('company_name', 'N/A')}** (Booth {booth.get('booth_number_on_map', 'N/A')})"):
                            if booth.get('job_openings'):
                                for opening in booth['job_openings']:
                                    st.markdown(f"##### {opening.get('job_title', 'N/A')} (ID: {opening.get('id', 'N/A')})")
                                    st.markdown(f"**Primary Field:** {opening.get('primary_field', 'N/A')}")
                                    
                                    description = opening.get('description', 'N/A')
                                    if description and description.lower() != 'none' and description.lower() != 'n/a':
                                        st.markdown("**Description:**")
                                        st.markdown(description) 
                                    else:
                                        st.markdown(f"**Description:** {description}")

                                    general_skills = opening.get('required_skills_general', [])
                                    soft_skills = opening.get('required_skills_soft', [])
                                    experience_years = opening.get('required_experience_years', 'N/A')
                                    experience_entries = opening.get('required_experience_entries', 'N/A') 
                                    cgpa = opening.get('required_cgpa', 'N/A')

                                    if general_skills:
                                        st.markdown(f"**General Skills:** {', '.join(general_skills)}")
                                    if soft_skills:
                                        st.markdown(f"**Soft Skills:** {', '.join(soft_skills)}")
                                    st.markdown(f"**Experience Required:** {experience_years} years, {experience_entries} entries")
                                    st.markdown(f"**Min CGPA:** {cgpa}")
                                    st.markdown("---")
                            else:
                                st.write("No specific job openings listed for this booth yet.")
            elif not openings_success: 
                st.warning(f"Could not retrieve all openings for this job fair: {all_openings_data.get('error', 'API error') if isinstance(all_openings_data, dict) else 'Error'}")
            else: 
                st.info("No opening data available for this job fair.")

        with tab_recommendations:
            st.subheader("Your Personalized Recommendations")
            # Logic for "Get Personalized Booth Recommendations" button
            if st.button("🔍 Get Personalized Booth Recommendations", key="get_personalized_recs_button_tab", type="primary"):
                if current_resume_id and selected_job_fair_id:
                    recommendations_response, rec_success = api.get_personalized_booth_recommendations(current_resume_id, selected_job_fair_id)
                    recommendations_data = None
                    if rec_success and recommendations_response:
                        recommendations_data = recommendations_response.get('data')
                    
                    st.session_state.personalized_booth_recommendations = recommendations_data 

                    if recommendations_data and recommendations_data.get('recommended_booths'):
                        st.success("Found Personalized Recommendations!")
                    elif recommendations_data is not None: 
                        st.info("No specific booth recommendations found based on your resume and the selected job fair criteria.")
                    else: 
                        error_message = "Could not retrieve personalized booth recommendations. Please try again."
                        if not rec_success and isinstance(recommendations_response, dict):
                            error_message = recommendations_response.get('error', error_message)
                            if recommendations_response.get('message'): 
                                 error_message = recommendations_response.get('message')
                        st.error(error_message)
                else:
                    st.warning("Missing Resume ID or Job Fair ID for recommendations.")

            # Display recommendations if they are in session state
            if st.session_state.get('personalized_booth_recommendations'):
                recommendations_data = st.session_state.personalized_booth_recommendations
                if recommendations_data and recommendations_data.get('recommended_booths'):
                    # This success message might be redundant if the button click already showed it.
                    # st.success("Displaying Personalized Recommendations!") 
                    
                    # OCR Map Highlighting Section (copied from original 08_Booth_Recommendations.py logic)
                    map_image_to_display = None
                    original_map_url_for_rec_tab = None # Use a distinct variable name to avoid conflicts

                    if recommendations_data.get('job_fair_map_url'):
                        original_map_url_for_rec_tab = recommendations_data['job_fair_map_url']
                    elif selected_fair_details and selected_fair_details.get('map_image_url'): # Fallback to selected fair's map
                         original_map_url_for_rec_tab = selected_fair_details['map_image_url']

                    if original_map_url_for_rec_tab:
                        # Ensure original_map_url is absolute before fetching for OCR
                        if not original_map_url_for_rec_tab.startswith('http'):
                            base_url_for_storage = api.API_BASE_URL.replace('/api', '') 
                            if original_map_url_for_rec_tab.startswith('/'):
                                absolute_ocr_map_url = base_url_for_storage + original_map_url_for_rec_tab
                            else:
                                absolute_ocr_map_url = base_url_for_storage + "/" + original_map_url_for_rec_tab
                            
                            # Clean up potential double slashes after host
                            scheme_ocr, rest_ocr = absolute_ocr_map_url.split("://", 1)
                            host_ocr, path_ocr = rest_ocr.split("/",1)
                            absolute_ocr_map_url = f"{scheme_ocr}://{host_ocr}/{path_ocr.lstrip('/')}"
                        else:
                            absolute_ocr_map_url = original_map_url_for_rec_tab
                        
                        recommended_booth_numbers_for_ocr = [
                            str(booth_rec.get('booth_number_on_map')) 
                            for booth_rec in recommendations_data.get('recommended_booths', [])
                            if booth_rec.get('booth_number_on_map')
                        ]
                        
                        if recommended_booth_numbers_for_ocr:
                            # st.write(f"DEBUG OCR: Booth numbers for OCR: {recommended_booth_numbers_for_ocr}") # Optional DEBUG
                            st.caption("Attempting to highlight recommended booths on the map...")
                            image_bytes = get_image_from_url(absolute_ocr_map_url) 
                            if image_bytes:
                                highlighted_image = highlight_booths_on_map(image_bytes, recommended_booth_numbers_for_ocr)
                                if highlighted_image and isinstance(highlighted_image, Image.Image):
                                    map_image_to_display = highlighted_image
                                else: 
                                    st.warning("Could not highlight booths. Displaying original map.")
                                    map_image_to_display = absolute_ocr_map_url # Display original URL if highlight fails
                            else:
                                st.warning("Could not fetch map image for highlighting.")
                                map_image_to_display = absolute_ocr_map_url # Display original URL if fetch fails
                        else: # No booth numbers to highlight, use original map
                            map_image_to_display = absolute_ocr_map_url 
                    
                    if map_image_to_display:
                        if isinstance(map_image_to_display, str): # It's a URL
                             st.image(map_image_to_display, caption=f"Map for {recommendations_data.get('job_fair_title', selected_fair_details.get('title', 'Job Fair'))}", use_container_width=True)
                        elif isinstance(map_image_to_display, Image.Image): # It's a PIL Image
                             st.image(map_image_to_display, caption=f"Highlighted Map for {recommendations_data.get('job_fair_title', selected_fair_details.get('title', 'Job Fair'))}", use_container_width=True, channels="BGR")
                    else:
                        st.info("No map image available for this job fair to display with recommendations.")
                    st.markdown("---") # Separator after map

                    # Displaying each recommended booth (copied from original 08_Booth_Recommendations.py logic)
                    filtered_recommended_booths = [
                        booth for booth in recommendations_data['recommended_booths']
                        if booth.get('highest_score_in_booth', 0) >= 50 # Example threshold
                    ]

                    if not filtered_recommended_booths:
                        st.info("No booths met the 50% or higher score threshold for recommendation in this fair.")
                    else:
                        for booth_rec in filtered_recommended_booths:
                            expander_title = f"📍 **{booth_rec.get('company_name', 'N/A')}** (Booth {booth_rec.get('booth_number_on_map', 'N/A')}) - Highest Score: {booth_rec.get('highest_score_in_booth', 0):.2f}%"
                            with st.expander(expander_title):
                                st.markdown(f"_Booth Number on Map: {booth_rec.get('booth_number_on_map', 'N/A')}_")
                                
                                if booth_rec.get('recommended_openings'):
                                    for opening in booth_rec['recommended_openings']:
                                        st.markdown(f"#### {opening.get('job_title', 'N/A')}")
                                        st.markdown(f"**Overall Score:** {opening.get('score', 0):.2f}%")
                                        st.markdown(f"**Primary Field:** {opening.get('primary_field', 'N/A')}")
                                        opening_desc = opening.get('description', 'N/A')
                                        if opening_desc and opening_desc.lower() != 'none' and opening_desc.lower() != 'n/a':
                                            st.markdown(f"**Description:** {opening_desc}")
                                        
                                        score_details = opening.get('score_details', {})
                                        st.markdown(f"""**Score Breakdown:** 
                                        *   Skills: {score_details.get('skills', 0):.2f}% 
                                        *   Experience: {score_details.get('experience', 0):.2f}% 
                                        *   Education: {score_details.get('education', 0):.2f}%""")
                                        
                                        match_details = opening.get('match_details', {})
                                        render_match_details_for_booth_rec(match_details) 
                                        st.markdown("---")
                                else:
                                    st.write("No specific recommended openings in this booth based on the criteria.")
                elif recommendations_data is not None: 
                    if not st.session_state.get('personalized_booth_recommendations', {}).get('recommended_booths'): # Check if key exists but list is empty
                         st.info("No specific booth recommendations found based on your resume and the selected job fair criteria. Try selecting a different job fair or resume.")
                # else: No recommendations in session state yet (button not pressed or API failed) - implicitly handled by lack of data

    else: # No job fair selected
        st.info("Please select a job fair from the dropdown above to see details and get recommendations.")

if __name__ == "__main__":
    # display_booth_recommendations() # Old function name
    display_job_fair_page() # New function name 