import streamlit as st
from difflib import ndiff
from annotated_text import annotated_text


# Function to highlight differences
def highlight_differences(original, corrected):

    # diff = ndiff(original.split(), corrected.split())
    highlighted_text = []
    # print(list(diff))
    original = original.split()
    corrected = corrected.split()
    for word in range(len(corrected)):
        error = []
        for i in range(len(corrected[word])):
            # print(corrected[word][i], original[word][i])
            if corrected[word][i].islower() != original[word][i].islower() and 'Регистр буквы' not in error:
                error.append('Регистр буквы')

            if corrected[word][i] != original[word][i] and len(corrected[word][i]) > len(original[word][i]) and 'Пропущена буква' not in error:
                error.append('Пропущена буква')

        if error:
            if on:
                highlighted_text.append((corrected[word] + ' ', ', '.join(error), "#afa"))
                highlighted_text.append('  ')
            else:
                highlighted_text.append(f'<span>{corrected[word]}</span>')
        else:
            if on:
                highlighted_text.append(' ' + corrected[word] + ' ')
            else:
                highlighted_text.append(corrected[word])
        # if word.startswith('+'):
        #     # highlighted_text.append(f'<span style="color:green;">{word[2:]}</span>')
        #     if on:
        #         highlighted_text.append((word[2:] + ' ', 'Заглавная буква', "#afa"))
        #         highlighted_text.append('  ')
        #     else:
        #         highlighted_text.append(f'<span>{word[2:]}</span>')
        # elif word.startswith('?'):
        #     pass
        # else:
        #     if on:
        #         highlighted_text.append(' ' + word[2:] + ' ')
        #     else:
        #         highlighted_text.append(word[2:])
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
            # Correct the text
            corrected_text = user_input.title()

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
