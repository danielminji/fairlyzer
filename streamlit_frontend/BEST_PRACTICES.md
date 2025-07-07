# Streamlit Best Practices

This document provides guidelines for writing maintainable, secure Streamlit applications.

## UI Components

### Text Elements

Use native Streamlit text functions instead of HTML in markdown:

```python
# GOOD ✅
st.title("My Application")
st.header("Section Title")
st.subheader("Subsection")
st.caption("A small caption")
st.write("Regular text content")
st.markdown("**Rich** _formatted_ text")
st.code("print('Hello world')")

# BAD ❌
st.markdown("<h1>My Application</h1>", unsafe_allow_html=True)
st.markdown("<h2>Section Title</h2>", unsafe_allow_html=True)
```

### HTML Content

When you need to include HTML content:

```python
# GOOD ✅
from streamlit.components.v1 import html
html("<div>Complex HTML content</div>")

# BAD ❌
st.markdown("<div>Complex HTML content</div>", unsafe_allow_html=True)
```

### Layout Components

Use Streamlit's built-in layout components:

```python
# Columns
col1, col2 = st.columns(2)
with col1:
    st.write("Column 1")
with col2:
    st.write("Column 2")

# Containers
with st.container():
    st.write("Contained content")

# Expanders
with st.expander("Click to expand"):
    st.write("Hidden content")

# Tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])
with tab1:
    st.write("Content for tab 1")
```

### Status Messages

Use proper status indicators:

```python
st.success("Operation completed successfully")
st.info("Informational message")
st.warning("Warning message")
st.error("Error message")
```

### Forms & Inputs

Use Streamlit forms for input:

```python
with st.form("my_form"):
    name = st.text_input("Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    submit = st.form_submit_button("Submit")

if submit:
    st.write(f"Hello {name}, you are {age} years old")
```

## JavaScript Integration

### Including JavaScript

When you need to include JavaScript, use the HTML component:

```python
from streamlit.components.v1 import html

js_code = """
<script>
    // Your JavaScript code here
    console.log('Hello from JavaScript!');
</script>
"""

html(js_code)
```

### Page Navigation

For page navigation:

```python
# Within the same app
if st.button("Go to Page 2"):
    st.switch_page("pages/page2.py")

# External links
from streamlit.components.v1 import html
if st.button("Visit External Site"):
    html("""
    <script>
        window.open('https://example.com', '_blank');
    </script>
    """)
```

## Styling

### CSS Styling

Use separate CSS files:

```python
def load_css():
    with open("style.css") as f:
        html(f"<style>{f.read()}</style>")

# Call load_css() at the start of your app
```

### Theme Configuration

Configure themes in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

## Golden Rules for Streamlit UI/UX Design

### 1. Consistency

- Use consistent layout, colors, and typography across all pages
- Maintain consistent navigation patterns
- Keep similar components in similar locations on different pages
- Follow a unified design system for all UI elements

```python
# Load CSS at the start of each page
from lib.ui_components import load_css
load_css()

# Use consistent header patterns
st.title("Page Title")  # Always use this pattern for main titles
```

### 2. Hierarchy and Navigation

- Place the most important information at the top
- Use clear visual hierarchy (headings, subheadings, body text)
- Implement intuitive navigation between pages
- Use breadcrumbs or navigation indicators for complex apps

```python
# Clear navigation
if st.button("Back to Dashboard"):
    st.switch_page("pages/dashboard.py")

# Visual hierarchy
st.title("Main Title")
st.header("Section Title")
st.subheader("Subsection")
```

### 3. Progressive Disclosure

- Reveal information progressively (don't overwhelm users)
- Use expandable sections for detailed information
- Implement tabs for related but separate content
- Show complex options only when needed

```python
# Progressive disclosure with expanders
with st.expander("Advanced Options", expanded=False):
    st.slider("Precision", 1, 10, 5)
    st.checkbox("Enable feature X")
```

### 4. Responsive Design

- Design for both wide and narrow screens
- Use relative widths rather than fixed pixels
- Test your app at different screen sizes
- Use appropriate column layouts based on content needs

```python
# Responsive column layouts
if st.session_state.get("screen_width", 1200) > 768:
    cols = st.columns(3)  # 3 columns on large screens
else:
    cols = st.columns(1)  # Stack on small screens
```

### 5. Clear Feedback

- Provide clear feedback for user actions
- Show loading states for time-consuming operations
- Use appropriate status messages (success, error, warning, info)
- Confirm successful operations clearly

```python
# Clear feedback
with st.spinner("Processing..."):
    result = process_data()

if result.success:
    st.success("Data processed successfully!")
else:
    st.error(f"Error: {result.error_message}")
```

### 6. Accessibility

- Ensure sufficient color contrast
- Add descriptive alt text for images
- Use semantic structures in your content
- Test with screen readers if possible

```python
# Good accessibility practices
st.image("chart.png", caption="Sales chart showing 20% growth in Q4")

# Use semantic headers for screen readers
st.header("Results Section")  # Rather than just making text bold
```

### 7. Simplicity

- Focus on core functionality without clutter
- Use whitespace effectively to separate content
- Limit the number of elements on a single screen
- Provide sensible defaults for all options

```python
# Use containers to group related content
with st.container():
    st.subheader("User Information")
    st.text_input("Name")
    st.text_input("Email")
    
# Add whitespace between sections
st.write("")  # Adds vertical space
```

### 8. Data Visualization Best Practices

- Choose the right chart type for your data
- Use clear labels and legends
- Keep visualizations simple and focused
- Ensure color choices work for color-blind users

```python
# Clear charts with proper labels
fig = px.bar(
    data, 
    x="Category", 
    y="Value",
    title="Sales by Category",
    labels={"Value": "Revenue ($)", "Category": "Product Category"}
)
st.plotly_chart(fig, use_container_width=True)
```

## Performance Tips

1. Cache expensive operations:
```python
@st.cache_data
def load_large_dataset():
    # Expensive operation
    return data
```

2. Use session state wisely:
```python
if "counter" not in st.session_state:
    st.session_state.counter = 0
```

3. Avoid rerunning the entire app unnecessarily:
```python
if st.button("Update"):
    # Only update what's needed
    st.session_state.value = new_value
```

## Security Best Practices

1. Never use `unsafe_allow_html=True` in `st.markdown()` with untrusted content
2. Sanitize user inputs before processing or displaying
3. Use `html()` component for trusted HTML/JS content
4. Do not expose sensitive information in the UI
5. Use proper authentication and authorization

## API Integrations

1. Use API keys in environment variables:
```python
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")
```

2. Handle errors gracefully:
```python
try:
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for HTTP errors
    data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"API request failed: {e}")
```

3. Use caching for API calls:
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_data(url):
    return requests.get(url).json()
```

## Testing

1. Use `streamlit test` for testing your app
2. Write unit tests for business logic
3. Test your app on different devices and browsers

## Deployment

1. Use `requirements.txt` to specify dependencies
2. Set environment variables in deployment settings
3. Monitor app performance after deployment

---

Following these best practices will help you build maintainable, secure, and performant Streamlit applications that provide an excellent user experience. 