# ============================================================
# Tech Consulting Interview Simulator – Streamlit (Stable Build)
# ============================================================

import random, textwrap
import streamlit as st

st.set_page_config(page_title="Consulting Interview Simulator", layout="wide")

# ------------------- QUIZ DATA -------------------

quiz_bank = {
    "Day 1 - Networking Basics": [
        {
            "q": "Which device primarily operates at OSI Layer 2?",
            "choices": [
                {"text": "Router", "ex": "Routers are Layer 3 and forward on IP."},
                {"text": "Switch", "ex": "Correct. Switches forward frames using MAC at Layer 2."},
                {"text": "Gateway", "ex": "Protocol translation at higher layers."},
                {"text": "Repeater", "ex": "Layer 1; regenerates signals only."}
            ],
            "answer": 1,
            "hint": "Think MAC vs IP."
        },
        {
            "q": "Best description of routing?",
            "choices": [
                {"text": "Broadcasting frames to all ports", "ex": "That is switching, not routing."},
                {"text": "Selecting paths between networks using IP", "ex": "Correct. Layer 3 path selection."},
                {"text": "Encrypting traffic between hosts", "ex": "Security, not routing."},
                {"text": "Assigning IPs automatically", "ex": "That is DHCP, not routing."}
            ],
            "answer": 1,
            "hint": "Layer 3 = IP and path selection."
        },
        {
            "q": "Primary purpose of VLANs?",
            "choices": [
                {"text": "Boost Wi-Fi signal", "ex": "Radio power unrelated."},
                {"text": "Logically segment broadcast domains", "ex": "Correct. Limits broadcasts and improves security."},
                {"text": "Encrypt internet traffic", "ex": "VPN does that."},
                {"text": "Replace routing entirely", "ex": "Inter-VLAN routing still required."}
            ],
            "answer": 1,
            "hint": "Broadcast domain control."
        }
    ],

    "Day 2 - IT Infra and Transformation": [
        {
            "q": "First step in a hybrid cloud migration advisory?",
            "choices": [
                {"text": "Pick a cloud provider", "ex": "Tool before need; premature."},
                {"text": "Assess current estate and workloads", "ex": "Correct. Baseline drives strategy."},
                {"text": "Lift-and-shift everything", "ex": "Usually inflates cost."},
                {"text": "Buy new licenses", "ex": "Procure after design."}
            ],
            "answer": 1,
            "hint": "Discovery before design."
        },
        {
            "q": "Most consulting KPI for infra cost optimization?",
            "choices": [
                {"text": "Number of servers", "ex": "Surface metric only."},
                {"text": "Cost per business transaction", "ex": "Correct. Business-aligned view."},
                {"text": "CPU clock speed", "ex": "Spec detail, not KPI."},
                {"text": "Rack space used", "ex": "Proxy metric."}
            ],
            "answer": 1,
            "hint": "Tie cost to business output."
        }
    ]
}

# ------------------- SESSION STATE -------------------

if "topic" not in st.session_state:
    st.session_state.topic = None
    st.session_state.questions = []
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.lives = 3
    st.session_state.streak = 0
    st.session_state.fifty_left = 1
    st.session_state.removed = set()
    st.session_state.selected = -1
    st.session_state.answered = False

# ------------------- UI -------------------

st.title("💼 Tech Consulting Interview Simulator")
st.caption("MCQs with hints, 50/50, streaks, and full explanations.")

with st.sidebar:
    st.header("Control Panel")
    topic_list = list(quiz_bank.keys())
    pick = st.selectbox("Select Topic", ["—"] + topic_list, index=0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Score", st.session_state.score)
        st.metric("Streak", st.session_state.streak)
    with col2:
        st.metric("Lives", st.session_state.lives)
        st.metric("50/50", st.session_state.fifty_left)

    if st.button("Start / Reset Topic", use_container_width=True):
        if pick != "—":
            st.session_state.topic = pick
            st.session_state.questions = quiz_bank[pick][:]
            random.shuffle(st.session_state.questions)
            st.session_state.q_index = 0
            st.session_state.score = 0
            st.session_state.lives = 3
            st.session_state.streak = 0
            st.session_state.fifty_left = 1
            st.session_state.removed = set()
            st.session_state.selected = -1
            st.session_state.answered = False

# ------------------- MAIN LOGIC -------------------

def explain(q, sel):
    st.subheader("Explanations")
    for i, opt in enumerate(q["choices"]):
        tag = "✅" if i == q["answer"] else "❌"
        chosen = " *(your choice)*" if i == sel else ""
        st.markdown(f"**{tag} {chr(65+i)}. {opt['text']}**{chosen}\n\n> {opt['ex']}")

if st.session_state.topic:
    total = len(st.session_state.questions)
    prog = st.session_state.q_index / max(total, 1)
    st.progress(prog, text=f"{st.session_state.topic} • Question {st.session_state.q_index+1} of {total}")

    if st.session_state.q_index >= total or st.session_state.lives <= 0:
        st.success(f"Topic complete: {st.session_state.topic}")
        st.write(f"Score: {st.session_state.score} | Lives left: {st.session_state.lives}")
    else:
        q = st.session_state.questions[st.session_state.q_index]
        st.subheader(f"Q{st.session_state.q_index+1}. {q['q']}")

        opts = [f"{chr(65+i)}. {o['text']}" for i, o in enumerate(q["choices"]) if i not in st.session_state.removed]
        ans = st.radio("Choose one:", opts, index=None)
        if ans:
            st.session_state.selected = ord(ans.split('.')[0]) - 65

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.button("Submit", type="primary", disabled=st.session_state.answered):
                sel = st.session_state.selected
                if sel == -1:
                    st.warning("Pick an option first.")
                else:
                    correct = sel == q["answer"]
                    if correct:
                        delta = 10
                        st.session_state.streak += 1
                        if st.session_state.streak % 3 == 0:
                            delta += 3
                        st.session_state.score += delta
                        st.success(f"✅ Correct (+{delta})")
                    else:
                        st.session_state.streak = 0
                        st.session_state.lives -= 1
                        st.session_state.score -= 5
                        st.error(f"❌ Wrong (-5). Lives left: {st.session_state.lives}")
                    explain(q, sel)
                    st.session_state.answered = True
        with c2:
            if st.button("Hint"):
                st.info(q.get("hint", "No hint available."))
        with c3:
            if st.button(f"50/50 ({st.session_state.fifty_left})", disabled=st.session_state.fifty_left==0 or st.session_state.answered):
                correct = q["answer"]
                wrong = [i for i in range(len(q["choices"])) if i != correct]
                hide = set(random.sample(wrong, k=min(2, len(wrong))))
                st.session_state.removed |= hide
                st.session_state.fifty_left -= 1
                st.rerun()
        with c4:
            if st.button("Skip", disabled=st.session_state.answered):
                st.session_state.q_index += 1
                st.session_state.streak = 0
                st.session_state.removed = set()
                st.session_state.selected = -1
                st.session_state.answered = False
                st.rerun()

        if st.session_state.answered:
            if st.button("Next →", type="primary"):
                st.session_state.q_index += 1
                st.session_state.removed = set()
                st.session_state.selected = -1
                st.session_state.answered = False
                st.rerun()
else:
    st.info("Select a topic in the sidebar and click Start / Reset Topic.")
