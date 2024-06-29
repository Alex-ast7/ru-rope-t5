import streamlit as st
from difflib import ndiff
from annotated_text import annotated_text
from optimum.intel import OVModelForSeq2SeqLM
from Levenshtein import editops
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
@st.cache_resource
def get_sage():
    tokenizer = AutoTokenizer.from_pretrained("ru-rope-t5/", local_files_only=True, compile=True)
    model = OVModelForSeq2SeqLM.from_pretrained('sage/', local_files_only=True, compile=True)
    return tokenizer, model



def class_error(errors):
    ans = []
    for error in errors:
        type, id1, id2, sign = error
        if sign in ",.:;'[]|\()!@#$%^&*-—=+?" and 'пропущен знак препинания' not in ans:
            ans.append('пропущен знак препинания')
            if type == 'replace' and 'лишний символ' not in ans:
                ans.append('лишний символ')
        elif type == 'insert' and sign == ' ' and 'слитное написание' not in ans:
            ans.append('слитное написание')
        elif type == 'insert' and 'лишний символ' not in ans:
            ans.append('лишний символ')
        elif type == 'delete' and sign == ' ' and 'раздельное написание' not in ans:
            ans.append('раздельное написание')
        elif type == 'delete' and 'пропущен символ' not in ans:
            ans.append('пропущен символ')

        elif type == 'replace' and 'ошибка в написании' not in ans:
            ans.append('ошибка в написании')

    return ans
def get_levenshtein_mask(source, correct):
    mask = [[0] for _ in range(len(correct))]
    changes = editops(correct, source)
    changes_letters = []
    for change in changes:
        if change[0] == 'delete' or change[0] == 'replace':
            changes_letters.append((change[0], change[1], change[2], correct[change[1]]))
        else:
            changes_letters.append((change[0], change[1], change[2], source[change[2]]))
    swap_changes = []
    i = 0
    while i < len(changes_letters) - 1:
        change_1 = changes_letters[i]
        change_2 = changes_letters[i + 1]
        swap_changes.append(change_1)
        i += 1
    if i == len(changes_letters) - 1:
        swap_changes.append(changes_letters[i])
    return swap_changes
def highlight_differences(original, corrected):
    highlighted_text = []

    words = []
    start = 0
    for word in corrected.split():
        words.append(start)
        start += len(word) + 1
    words.append(words[-1] + 100)
    diff = get_levenshtein_mask(original, corrected)
    for start in range(1, len(words)):
        errors = []
        for type in diff[:]:
            if type[1] < words[start]:
                errors.append(type)

                diff.remove(type)
        w = corrected.split()[start - 1]
        error = class_error(errors)
        if errors:
            if on:
                highlighted_text.append((w + ' ', ', '.join(error).capitalize(), "#afa"))
                highlighted_text.append('  ')
            else:
                highlighted_text.append(f'<span>{w}</span>')
        else:
            if on:
                highlighted_text.append(' ' + w + ' ')
            else:
                highlighted_text.append(w)

    if on:
        return highlighted_text
    return ' '.join(highlighted_text)


st.title("Корректор текста")

# Initialize session state for user input
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# User input
user_input = st.text_area("Введите текст для исправления:", height=200, value=st.session_state.user_input)

on = st.toggle("Указать на исправления", value=True)

# Buttons
col1, col2 = st.columns([4, 1])  # Ширина первой колонки больше для полного поля ввода
with col1:
    if st.button("Исправить текст"):
        if user_input:
            tokenizer, model = get_sage()
            sentence = user_input
            inputs = tokenizer(sentence, max_length=None, padding="longest", truncation=False, return_tensors="pt")
            outputs = model.generate(**inputs.to(model.device), max_length = inputs["input_ids"].size(1) * 1.5)
            corrected_text = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]

            # Highlight corrections
            highlighted_text = highlight_differences(user_input, corrected_text)
            st.markdown("### Исправленный текст:")
            if on:
                annotated_text(highlighted_text)
            else:
                st.markdown(f'<div class="highlighted-text">{highlighted_text}</div>', unsafe_allow_html=True)
        else:
            st.warning("Пожалуйста, введите текст для исправления.")

with col2:
    if st.button("Очистить всё", key='clear_button'):
        st.session_state.user_input = ""
        st.experimental_rerun()

# CSS для выравнивания кнопки "Очистить всё" к правому краю
st.markdown("""
    <style>
    .css-1v2yshv {
        display: flex;
        justify-content: flex-end;
    }
    </style>
""", unsafe_allow_html=True)
