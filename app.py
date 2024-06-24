import streamlit as st
from difflib import ndiff
from annotated_text import annotated_text
from optimum.intel import OVModelForSeq2SeqLM
from Levenshtein import editops
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
@st.cache_resource
def get_sage():
    tokenizer = AutoTokenizer.from_pretrained("ai-forever/sage-fredt5-distilled-95m")
    #model = AutoModelForSeq2SeqLM.from_pretrained("ai-forever/sage-fredt5-distilled-95m")
    model = OVModelForSeq2SeqLM.from_pretrained('app/', local_files_only=True, compile=True)
    #model.to("cuda")
    return tokenizer, model


# Function to highlight differences
def highlight_differences(original, corrected):

    # diff = ndiff(original.split(), corrected.split())
    highlighted_text = []
    # print(list(diff))
    original = original.split()
    corrected = corrected.split()

    for word in range(len(corrected)):
        error = []
        dif = editops(original[word], corrected[word])
        for type in dif:
            ind1 = type[1]
            ind2 = type[2]
            if corrected[word][ind2] in ",.:;'[]|\()!@#$%^&*-=+?" and 'пропущен знак препинания' not in error:
                error.append('пропущен знак препинания')
            else:
                if type[0] == 'replace' and corrected[word][ind2].islower() != original[word][ind1].islower() and 'регистр буквы' not in error:
                    error.append('регистр буквы')
                elif type[0] == 'replace' and 'ошибка в написании' not in error:
                    error.append('ошибка в написании')
                if type[0] == 'insert' and corrected[word][ind2] in ",.:;'[]|\()!@#$%^&*-=+?" and 'пропущен знак препинания' not in error:
                    error.append('пропущен знак препинания')
                elif type[0] == 'insert' and 'пропущена буква' not in error:
                    error.append('пропущена буква')
                if type[0] == 'delete' and 'лишняя буква' not in error:
                    error.append('лишняя буква')



        # if len(corrected[word]) > len(original[word]):
        #   if corrected[word][-1] in ",.:;'[]|\()!@#$%^&*-=+?" and corrected[word][-1] != original[word][-1]:
        #     error.append('пропущен знак препинания')
        #     if len(corrected[word][:-1]) > len(original[word]):
        #       error.append('пропущена буква')
        #   else:
        #       error.append('пропущена буква')
        # if len(corrected[word]) < len(original[word]):
        #   error.append('лишняя буква')
        # n = min(len(corrected[word]), len(original[word]))
        # for i in range(n):
        #     print(corrected[word][i], original[word][i])
        #     if corrected[word][i].islower() != original[word][i].islower() and 'регистр буквы' not in error:
        #         error.append('регистр буквы')
        #
        #     if corrected[word][i].lower() != original[word][i].lower() and 'ошибка в написании' not in error:
        #         error.append('ошибка в написании')

        if error:
            if on:
                highlighted_text.append((corrected[word] + ' ', ', '.join(error).capitalize(), "#afa"))
                highlighted_text.append('  ')
            else:
                highlighted_text.append(f'<span>{corrected[word]}</span>')
        else:
            if on:
                highlighted_text.append(' ' + corrected[word] + ' ')
            else:
                highlighted_text.append(corrected[word])

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
