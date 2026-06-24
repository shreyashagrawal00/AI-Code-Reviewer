import streamlit as st
from dotenv import load_dotenv

from utils.constants import (
    APP_TITLE,
    APP_ICON,
    MODEL_OPTIONS,
    SUPPORTED_EXTENSIONS,
    STREAMLIT_LANG_MAP,
    REVIEW_FOCUS_MAP,
    LANGUAGE_OPTIONS,
)
from services.file_service import (
    safe_decode_uploaded_file,
    detect_language_from_filename,
    validate_code_size,
    default_task_description_if_empty,
)
from services.review_service import run_code_review
from services.repo_ingestion_service import ingest_github_repo
from services.file_analysis_service import analyze_repo_files
from services.repo_analysis_service import analyze_repository
from services.chunking_service import chunk_repo_files
from services.vector_store_service import (
    build_vector_store,
    retrieve_relevant_chunks,
    format_retrieved_chunks,
)
from services.repo_qa_service import answer_repo_question

load_dotenv()

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }

    .hero-card {
        background: linear-gradient(135deg, #111827, #1f2937);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 22px;
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #c9d1d9;
        font-size: 15px;
        margin-bottom: 14px;
    }

    .badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .badge {
        background: rgba(68, 136, 255, 0.16);
        color: #9cc0ff;
        border: 1px solid rgba(68, 136, 255, 0.25);
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }

    .review-card {
        background-color: #161b22;
        border-radius: 14px;
        padding: 18px;
        margin: 10px 0;
        border: 1px solid rgba(255,255,255,0.06);
        border-left: 4px solid;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }

    .repo-card { border-left-color: #4488ff; }
    .issue-card { border-left-color: #ff4d4f; }
    .strength-card { border-left-color: #00cc88; }
    .file-card { border-left-color: #ffaa00; }
    .answer-card { border-left-color: #7c4dff; }
    .code-card { border-left-color: #00bcd4; }
    .explanation-card { border-left-color: #f59e0b; }

    .metric-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin: 8px 0 18px 0;
    }

    .metric-chip {
        background: #111827;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        padding: 12px 14px;
        min-width: 150px;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 12px;
        margin-bottom: 4px;
    }

    .metric-value {
        color: #ffffff;
        font-size: 18px;
        font-weight: 800;
    }

    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        font-size: 15px;
        font-weight: 700;
        border-radius: 12px;
        padding: 10px 14px;
        border: none;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        color: white;
    }

    .severity-pill {
        display: inline-block;
        padding: 4px 11px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        margin-bottom: 10px;
        margin-right: 8px;
    }

    .sev-high {
        background: rgba(255, 77, 79, 0.18);
        color: #ff6b6b;
    }

    .sev-medium {
        background: rgba(255, 170, 0, 0.18);
        color: #ffb84d;
    }

    .sev-low {
        background: rgba(0, 204, 136, 0.18);
        color: #4dffb8;
    }

    .muted-note {
        color: #9ca3af;
        font-size: 13px;
    }

    .section-title {
        font-size: 22px;
        font-weight: 800;
        margin: 6px 0 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================
def severity_class(severity: str) -> str:
    sev = (severity or "").strip().lower()
    if sev == "high":
        return "sev-high"
    if sev == "medium":
        return "sev-medium"
    return "sev-low"


def get_streamlit_lang(language_name: str) -> str:
    return STREAMLIT_LANG_MAP.get(language_name, "text")


def init_session_state():
    defaults = {
        "repo_name": None,
        "file_records": None,
        "repo_metadata": None,
        "file_summaries": None,
        "repo_summary": None,
        "vector_store": None,
        "chunk_records": None,
        "debug_records": None,
        "repo_model_name": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_hero():
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">🔍 AI Code Reviewer</div>
        <div class="hero-subtitle">
            Review pasted code, uploaded files, or entire GitHub repositories with structured AI analysis, repo summaries, and Ask Repo Q&A.
        </div>
        <div class="badge-row">
            <span class="badge">LangChain</span>
            <span class="badge">Groq</span>
            <span class="badge">GitHub Repo Review</span>
            <span class="badge">RAG / FAISS</span>
            <span class="badge">Single File + Full Repo</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_repo_metrics(repo_metadata, chunk_records):
    total_chunks = len(chunk_records) if chunk_records else 0

    st.markdown(f"""
    <div class="metric-strip">
        <div class="metric-chip">
            <div class="metric-label">Repository</div>
            <div class="metric-value">{repo_metadata.get("repo", "Unknown")}</div>
        </div>
        <div class="metric-chip">
            <div class="metric-label">Files Analyzed</div>
            <div class="metric-value">{repo_metadata.get("total_files_selected", 0)}</div>
        </div>
        <div class="metric-chip">
            <div class="metric-label">Total Chars</div>
            <div class="metric-value">{repo_metadata.get("total_chars", 0)}</div>
        </div>
        <div class="metric-chip">
            <div class="metric-label">Chunks Created</div>
            <div class="metric-value">{total_chunks}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_code_review_result(review, final_language):
    st.markdown('<div class="section-title">🧠 Code Review Result</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="review-card code-card">
        <h4 style="margin-top:0;">Overall Understanding</h4>
        <p>{review.understanding}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🐛 Bugs / Problems Found")
    if review.bugs:
        for i, bug in enumerate(review.bugs, 1):
            sev_class = severity_class(bug.severity)
            st.markdown(f"""
            <div class="review-card issue-card">
                <div class="severity-pill {sev_class}">{bug.severity.title()}</div>
                <h4 style="margin-top:0;">{i}. {bug.title}</h4>
                <p><b>Why it’s a problem:</b> {bug.explanation}</p>
                <p><b>Fix:</b> {bug.fix}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No major bugs found.")

    st.markdown("### 🛠 Corrected Code")
    st.code(review.corrected_code, language=get_streamlit_lang(final_language))

    st.markdown(f"""
    <div class="review-card explanation-card">
        <h4 style="margin-top:0;">Human Explanation</h4>
        <p>{review.explanation}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🚀 Suggestions")
    if review.suggestions:
        for suggestion in review.suggestions:
            st.markdown(f"""
            <div class="review-card strength-card">
                {suggestion}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No extra suggestions returned.")


def render_repo_summary(repo_summary):
    st.markdown('<div class="section-title">📦 Repository Overview</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="review-card repo-card">
        <h4 style="margin-top:0;">Overview</h4>
        <p>{repo_summary.overview}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="review-card repo-card">
        <h4 style="margin-top:0;">Architecture</h4>
        <p>{repo_summary.architecture}</p>
    </div>
    """, unsafe_allow_html=True)

    if repo_summary.tech_stack:
        st.markdown("### 🛠 Tech Stack")
        st.write(", ".join(repo_summary.tech_stack))

    if repo_summary.important_files:
        st.markdown("### 📂 Important Files")
        for f in repo_summary.important_files:
            st.write(f"- {f}")

    if repo_summary.strengths:
        st.markdown("### ✅ Strengths")
        for strength in repo_summary.strengths:
            st.markdown(f"""
            <div class="review-card strength-card">
                {strength}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("### 🐛 Repository-Level Issues")
    if repo_summary.issues:
        for issue in repo_summary.issues:
            sev_class = severity_class(issue.severity)
            affected = ", ".join(issue.affected_files) if issue.affected_files else "Not specified"

            st.markdown(f"""
            <div class="review-card issue-card">
                <div class="severity-pill {sev_class}">{issue.severity.title()}</div>
                <h4 style="margin-top:0;">{issue.title}</h4>
                <p><b>Why it matters:</b> {issue.explanation}</p>
                <p><b>Affected files:</b> {affected}</p>
                <p><b>Fix:</b> {issue.fix}</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("No major repository-level issues found.")

    if repo_summary.suggestions:
        st.markdown("### 🚀 Suggestions")
        for suggestion in repo_summary.suggestions:
            st.markdown(f"- {suggestion}")

    st.markdown("### 🧾 Final Verdict")
    st.info(repo_summary.final_verdict)


def render_file_summaries(file_summaries):
    st.markdown('<div class="section-title">📄 File-by-File Review</div>', unsafe_allow_html=True)

    if not file_summaries:
        st.warning("No file summaries available.")
        return

    for file_summary in file_summaries:
        with st.expander(f"📁 {file_summary.file_path}", expanded=False):
            st.markdown(f"""
            <div class="review-card file-card">
                <p><b>Language:</b> {file_summary.language}</p>
                <p><b>Purpose:</b> {file_summary.purpose}</p>
                <p><b>Summary:</b> {file_summary.summary}</p>
            </div>
            """, unsafe_allow_html=True)

            if file_summary.key_components:
                st.markdown("**Key Components**")
                for item in file_summary.key_components:
                    st.write(f"- {item}")

            st.markdown("**Issues**")
            if file_summary.issues:
                for issue in file_summary.issues:
                    sev_class = severity_class(issue.severity)
                    st.markdown(f"""
                    <div class="review-card issue-card">
                        <div class="severity-pill {sev_class}">{issue.severity.title()}</div>
                        <h4 style="margin-top:0;">{issue.title}</h4>
                        <p><b>Why it matters:</b> {issue.explanation}</p>
                        <p><b>Fix:</b> {issue.fix}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("No major issues found in this file.")

            if file_summary.suggestions:
                st.markdown("**Suggestions**")
                for suggestion in file_summary.suggestions:
                    st.write(f"- {suggestion}")


def render_debug_section(debug_records):
    if not debug_records:
        return

    with st.expander("🧪 Debug / File Processing Details"):
        for record in debug_records:
            st.write(record)


# =========================================================
# APP START
# =========================================================
init_session_state()
render_hero()

st.markdown(
    '<div class="muted-note">Analyze single files, uploaded code, or full GitHub repositories with live status updates.</div>',
    unsafe_allow_html=True
)
st.divider()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.header("⚙️ Global Settings")
    global_model_name = st.selectbox("Groq Model", MODEL_OPTIONS, index=0)
    debug_mode = st.checkbox("Debug mode", value=False)

    st.divider()
    st.markdown("### 📋 App Modes")
    st.markdown("""
- **Code Review** → Paste code or upload a single file  
- **Repo Review** → Analyze a GitHub repository  
- **Ask Repo** → Ask questions about the analyzed repo  
""")

# =========================================================
# MAIN TABS
# =========================================================
tab_code, tab_repo, tab_ask = st.tabs(["💻 Code Review", "📦 Repo Review", "💬 Ask Repo"])

# =========================================================
# TAB 1 — CODE REVIEW
# =========================================================
with tab_code:
    st.markdown('<div class="section-title">💻 Single Code Review</div>', unsafe_allow_html=True)
    st.markdown("Paste code or upload a code file and get a structured review.")

    col1, col2 = st.columns([1, 1], gap="large")

    file_code = ""
    detected_lang = None
    uploaded_file = None

    with col1:
        st.markdown("### Input")
        selected_language = st.selectbox("Programming Language", LANGUAGE_OPTIONS, key="code_lang")
        task_description = st.text_input(
            "What is this code supposed to do?",
            placeholder="e.g. Sort a list of numbers using bubble sort",
            key="code_task"
        )
        review_focus_ui = st.selectbox(
            "Review Focus",
            [
                "All (Bug fix + Explain + Optimize)",
                "Bug Fix Only",
                "Explain Only",
                "Optimize Only"
            ],
            key="code_focus"
        )

        input_tab1, input_tab2 = st.tabs(["✏️ Paste Code", "📁 Upload File"])

        with input_tab1:
            pasted_code = st.text_area(
                "Paste your code here",
                height=420,
                placeholder="# Paste your code here...\ndef example():\n    pass",
                label_visibility="collapsed"
            )

        with input_tab2:
            uploaded_file = st.file_uploader(
                "Upload a code file",
                type=SUPPORTED_EXTENSIONS,
                help="Supported code extensions configured in utils/constants.py",
                key="code_upload"
            )

            if uploaded_file:
                file_code = safe_decode_uploaded_file(uploaded_file)
                detected_lang = detect_language_from_filename(uploaded_file.name)
                preview_lang = get_streamlit_lang(detected_lang or "text")
                preview_text = file_code[:1200] + ("..." if len(file_code) > 1200 else "")

                st.code(preview_text, language=preview_lang)
                st.success(f"Loaded file: {uploaded_file.name} ({len(file_code)} chars)")
                if detected_lang:
                    st.info(f"Detected language: {detected_lang}")

        review_clicked = st.button("🚀 Review My Code", use_container_width=True, key="code_review_btn")

    with col2:
        st.markdown("### Results")

        if review_clicked:
            code = ""
            final_language = selected_language
            normalized_focus = REVIEW_FOCUS_MAP.get(review_focus_ui, "all")

            if uploaded_file and file_code:
                code = file_code
                if selected_language == "Auto Detect" and detected_lang:
                    final_language = detected_lang
            elif pasted_code.strip():
                code = pasted_code
            else:
                st.error("Please paste code or upload a file first.")
                st.stop()

            final_task_description = default_task_description_if_empty(task_description)

            if final_language == "Auto Detect":
                final_language = detected_lang or "Unknown"

            validate_code_size(code)

            progress = st.progress(0)
            with st.status("Running code review...", expanded=True) as status:
                try:
                    st.write("**[1/3]** Reading and validating code input...")
                    progress.progress(20)

                    st.write("**[2/3]** Sending code to Groq reviewer...")
                    review, raw_output = run_code_review(
                        selected_model=global_model_name,
                        language=final_language,
                        task_description=final_task_description,
                        review_focus=normalized_focus,
                        code=code
                    )
                    progress.progress(75)

                    st.write("**[3/3]** Parsing structured review output...")
                    progress.progress(100)
                    status.update(label="Code review completed successfully.", state="complete")

                    render_code_review_result(review, final_language)

                    if debug_mode:
                        with st.expander("🧪 Raw AI Output"):
                            st.text(raw_output)

                except Exception as e:
                    status.update(label="Code review failed.", state="error")
                    st.error(f"Something went wrong during code review: {str(e)}")

# =========================================================
# TAB 2 — REPO REVIEW
# =========================================================
with tab_repo:
    st.markdown('<div class="section-title">📦 GitHub Repository Review</div>', unsafe_allow_html=True)
    st.markdown("Analyze an entire GitHub repository with file-level review, repo summary, chunking, and vector search setup.")

    repo_col1, repo_col2 = st.columns([1, 1.15], gap="large")

    with repo_col1:
        st.markdown("### Repository Input")
        repo_url = st.text_input(
            "GitHub Repository URL",
            placeholder="https://github.com/username/repo",
            key="repo_url"
        )

        analyze_repo_clicked = st.button("🚀 Analyze Repository", use_container_width=True, key="repo_review_btn")

    with repo_col2:
        st.markdown("### Repository Review Output")

        if analyze_repo_clicked:
            if not repo_url.strip():
                st.error("Please enter a GitHub repository URL.")
                st.stop()

            progress = st.progress(0)
            with st.status("Analyzing repository...", expanded=True) as status:
                try:
                    st.write("**[1/7]** Validating and fetching repository...")
                    repo_name, file_records, repo_metadata = ingest_github_repo(repo_url)
                    progress.progress(15)

                    st.write("**[2/7]** Running file-by-file AI analysis...")
                    file_summaries, debug_records = analyze_repo_files(
                        selected_model=global_model_name,
                        repo_name=repo_name,
                        file_records=file_records
                    )
                    progress.progress(45)

                    st.write("**[3/7]** Generating repository-level summary...")
                    repo_summary, repo_raw_output = analyze_repository(
                        selected_model=global_model_name,
                        repo_name=repo_name,
                        file_records=file_records,
                        repo_metadata=repo_metadata,
                        file_summaries=file_summaries
                    )
                    progress.progress(65)

                    st.write("**[4/7]** Chunking repository files for retrieval...")
                    chunk_records = chunk_repo_files(file_records)
                    progress.progress(80)

                    st.write("**[5/7]** Building FAISS vector store with embeddings...")
                    vector_store = build_vector_store(chunk_records)
                    progress.progress(100)

                    st.session_state.repo_name = repo_name
                    st.session_state.file_records = file_records
                    st.session_state.repo_metadata = repo_metadata
                    st.session_state.file_summaries = file_summaries
                    st.session_state.repo_summary = repo_summary
                    st.session_state.vector_store = vector_store
                    st.session_state.chunk_records = chunk_records
                    st.session_state.debug_records = debug_records
                    st.session_state.repo_model_name = global_model_name

                    status.update(label="Repository analysis completed successfully.", state="complete")
                    st.success("Repository analysis finished.")

                    render_repo_metrics(repo_metadata, chunk_records)
                    render_repo_summary(repo_summary)
                    render_file_summaries(file_summaries)

                    if debug_mode:
                        render_debug_section(debug_records)
                        with st.expander("🧪 Raw Repo Summary Output"):
                            st.text(str(repo_raw_output))

                except Exception as e:
                    status.update(label="Repository analysis failed.", state="error")
                    st.error(f"Something went wrong while analyzing the repository: {str(e)}")

    # Show previous repo analysis if available
    if st.session_state.repo_summary:
        st.divider()
        st.markdown("### Latest Analyzed Repository")
        render_repo_metrics(st.session_state.repo_metadata or {}, st.session_state.chunk_records or [])
        render_repo_summary(st.session_state.repo_summary)
        render_file_summaries(st.session_state.file_summaries or [])
        if debug_mode:
            render_debug_section(st.session_state.debug_records)

# =========================================================
# TAB 3 — ASK REPO
# =========================================================
with tab_ask:
    st.markdown('<div class="section-title">💬 Ask Repo</div>', unsafe_allow_html=True)

    if not st.session_state.repo_summary or not st.session_state.vector_store:
        st.info("Analyze a repository first in the **Repo Review** tab to enable Ask Repo.")
    else:
        repo_metadata = st.session_state.repo_metadata or {}
        repo_name = st.session_state.repo_name
        vector_store = st.session_state.vector_store

        st.markdown(f"""
        <div class="muted-note">
            Active repository: <b>{repo_metadata.get("owner", "Unknown")}/{repo_metadata.get("repo", "Unknown")}</b>
        </div>
        """, unsafe_allow_html=True)

        repo_query = st.text_input(
            "Ask something about this repository",
            placeholder="e.g. Where is authentication handled? Which file manages API routes?",
            key="ask_repo_query"
        )

        col_a, col_b = st.columns(2)
        with col_a:
            retrieve_only = st.button("🔎 Show Retrieved Chunks", use_container_width=True, key="ask_repo_retrieve")
        with col_b:
            answer_question = st.button("🤖 Answer with AI", use_container_width=True, key="ask_repo_answer")

        if retrieve_only:
            if not repo_query.strip():
                st.warning("Please enter a question.")
            else:
                progress = st.progress(0)
                with st.status("Retrieving repository context...", expanded=True) as status:
                    try:
                        st.write("**[1/2]** Searching vector store for relevant chunks...")
                        docs = retrieve_relevant_chunks(vector_store, repo_query)
                        progress.progress(70)

                        st.write("**[2/2]** Formatting retrieved repository context...")
                        retrieved_text = format_retrieved_chunks(docs)
                        progress.progress(100)

                        status.update(label="Retrieved repository chunks successfully.", state="complete")
                        st.markdown("### Retrieved Repository Chunks")
                        st.code(retrieved_text, language="text")

                    except Exception as e:
                        status.update(label="Chunk retrieval failed.", state="error")
                        st.error(f"Failed to retrieve repository chunks: {str(e)}")

        if answer_question:
            if not repo_query.strip():
                st.warning("Please enter a question.")
            else:
                progress = st.progress(0)
                with st.status("Answering repository question...", expanded=True) as status:
                    try:
                        st.write("**[1/3]** Retrieving relevant repository chunks...")
                        progress.progress(35)

                        st.write("**[2/3]** Sending retrieved context to the LLM...")
                        answer_text, retrieved_context = answer_repo_question(
                            selected_model=st.session_state.repo_model_name or global_model_name,
                            repo_name=repo_name,
                            vector_store=vector_store,
                            question=repo_query
                        )
                        progress.progress(85)

                        st.write("**[3/3]** Finalizing repository answer...")
                        progress.progress(100)
                        status.update(label="Repository question answered successfully.", state="complete")

                        st.markdown("### 🤖 AI Answer")
                        st.markdown(f"""
                        <div class="review-card answer-card">
                            {answer_text}
                        </div>
                        """, unsafe_allow_html=True)

                        with st.expander("📎 Retrieved Context Used"):
                            st.code(retrieved_context, language="text")

                    except Exception as e:
                        status.update(label="Ask Repo failed.", state="error")
                        st.error(f"Failed to answer repository question: {str(e)}")