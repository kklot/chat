from func import *

st.set_page_config(
    page_title="Chat Home", 
    page_icon=":shamrock:", 
    layout="wide", 
    initial_sidebar_state="auto", 
    menu_items=None)

if not check_password():
    st.stop() 

memory_on = st.toggle("Ghi nhớ", help = "Chọn để ghi nhớ nội dung hỏi đáp và dùng nó để trả lời các câu hỏi tiếp theo. Nếu không, mỗi lần hỏi đáp sẽ không phụ thuộc vào nội dung trước đó.")
model_405b = st.toggle("3.1 405b model", help = "Chọn để chạy mô hình mới", value = True)

if model_405b:
    st.session_state.chat_model = "meta/meta-llama-3.1-405b-instruct"
else:
    st.session_state.chat_model = "meta/meta-llama-3-70b-instruct"

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

if "prompt_len" not in st.session_state:
    st.session_state["prompt_len"] = 0

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hallo"}]

with st.sidebar:
    st.image('logo.jpeg')
    temperature = st.number_input("Nhiệt độ", help = "Càng gần 1 càng sáng tạo, càng gần 0 càng bảo thủ.",  min_value = 0.0, max_value = 1.0, value = 0.75, step = 0.01)
    "---"
    "Số tokens hiện tại"
    "~" + str(st.session_state["prompt_len"]) + " tokens/8000"
    "## Tỉa bớt nội dung"
    auto_trim = st.toggle("Tự động tỉa", value = True, help = "Tự động xóa 1/10 nội dung cũ khi tokens vượt quá 8000. Tắt và tự tỉa nhiều hơn bằng tùy chọn bên dưới.")
    if not auto_trim:
        rm_frac = st.number_input("Bỏ bao nhiêu phần trăm?", min_value = 0.0, max_value = 1.0, value = 0.25, step = 0.01)
        st.button("Tỉa", type="secondary", on_click = clear_context, kwargs = {"fraction": rm_frac}, help = "Xóa bớt thông tin cũ nhất khi tokens gần tới 8000")
    "---"
    st.button("Xóa hết", type="primary", on_click = clear_msg, use_container_width = True)
    st.download_button(
        label = "Lưu nội dung",
        data = st.session_state.chat_history, 
        # on_click = prep_export,
        mime = 'text/plain',
        use_container_width = True
    )
    "@Kinh Nguyen"

if not memory_on:
    st.session_state["messages"] = [{"role": "assistant", "content": "Hallo"}]

if auto_trim and st.session_state.prompt_len >= 8000:
    clear_context(1/10)

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

event_list = []

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt}) # save it
    st.chat_message("user").write(prompt) # print it out
    full = gen_context() # update context
    new_response = ask(full, temperature, event_list)
    st.chat_message("assistant").write(new_response)
    # saving
    st.session_state.chat_history = full
    st.session_state.messages.append({"role": "assistant", "content": "".join(event_list)})
    st.session_state.prompt_len = len(full)*0.75
