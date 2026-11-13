# dashboard/app.py
import streamlit as st
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from ai_engine.post_generator import PostGenerator
from analytics.tracker import get_stats

st.set_page_config(page_title="LinkedIn AI Agent", layout="wide")
st.title("🤖 LinkedIn AI Agent - Ollama 20B")

# Sidebar
with st.sidebar:
    st.header("📊 Stats")
    stats = get_stats()
    st.metric("Total Posts", stats['total_posts'])
    
    st.header("⚙️ Settings")
    st.info("Model: llama3:70b")

# Main content
tab1, tab2 = st.tabs(["📝 Generate", "📊 Analytics"])

with tab1:
    project_details = st.text_area("Project Details", height=150)
    tone = st.selectbox("Tone", ["professional", "motivational", "educational"])
    
    if st.button("Generate Post", type="primary"):
        with st.spinner("Generating with Ollama 20B..."):
            generator = PostGenerator()
            post = generator.generate_post(project_details, tone)
            if post:
                st.success("✅ Post generated!")
                st.text_area("Generated Post", post.get("full_post", ""), height=300)
                
                if st.button("Save to Database"):
                    from analytics.tracker import save_post
                    save_post(post.get("full_post", ""), "generated", tone)
                    st.success("✅ Saved!")