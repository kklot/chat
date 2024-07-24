import hmac
import streamlit as st
import replicate

def clear_msg():
    del st.session_state['messages']
    st.markdown('Old messages cleared')

def clear_context(fraction = 1/4):
    # TODO: add option first or last windows?
    n_msg = len(st.session_state.messages)
    n_rm = int(n_msg * fraction)
    st.session_state.messages = [st.session_state.messages[i] for i in range(n_rm, n_msg)]
    st.markdown('Remove '+str(fraction * 100) + "% of the messages")

def gen_context(quote = True):
    context = ""
    pre = ""
    post = ""
    if quote:
        pre = "[INST] "
        post = " [/INST]"
    for i in range(1, len(st.session_state.messages)):
        msg = st.session_state.messages[i]
        if msg['role'] == "user":
            ct = pre + msg['content'] + post
        else:
            ct = msg['content']
        context = context + str(ct) + '\n'
    return context

def prep_export():
    st.session_state.chat_history = gen_context(False)

def ask(what = "", temp = 0.75, event_list = []):
    input = {
        "prompt": what,
        "min_tokens": 0,
        "temperature": temp,
        "length_penalty": 1,
        "presence_penalty": 1.15, 
        "stop": ["[INST]", "User:"]
    }
    for event in replicate.stream(
        st.session_state.chat_model,
        input=input
    ):
        yield str(event) + ""
        event_list.append(str(event))

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False):
        return True
    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False
