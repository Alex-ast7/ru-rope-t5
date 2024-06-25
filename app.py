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
        if change_1[0] == 'insert' and change_2[0] == 'delete' and change_1[3] == change_2[3] and change_2[1] - \
                change_1[1] == 1:
            swap_changes.append(('swap', change_1[1], change_1[2], change_1[3]))
            swap_changes.append(('swap', change_2[1], change_1[2] + 1, change_2[3]))
            i += 2
        else:
            swap_changes.append(change_1)
            i += 1
    if i == len(changes_letters) - 1:
        swap_changes.append(changes_letters[i])
    print(swap_changes)

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
            print(corrected, word, ind2)
            # if corrected[word][ind2] in ",.:;'[]|\()!@#$%^&*-=+?" and 'пропущен знак препинания' not in error:
            #     error.append('пропущен знак препинания')
            # elif (len(original[word]) == len(corrected[word]) or len(original[word]) == len(
            #         corrected[word][:-1])) and 'ошибка в написании' not in error:
            #     error.append('ошибка в написании')
            # else:
            #     if type[0] == 'replace' and corrected[word][ind2].islower() != original[word][ind1].islower() and original[word][ind1] not in ",.:;'[]|\()!@#$%^&*-=+?" and 'регистр буквы' not in error:
            #         error.append('регистр буквы')
            #     elif type[0] == 'replace' and 'ошибка в написании' not in error:
            #         error.append('ошибка в написании')
            #     if type[0] == 'insert' and corrected[word][ind2] in ",.:;'[]|\()!@#$%^&*-=+?" and 'пропущен знак препинания' not in error:
            #         error.append('пропущен знак препинания')
            #     elif type[0] == 'insert' and 'пропущена буква' not in error:
            #         error.append('пропущена буква')
            #     if type[0] == 'delete' and 'лишняя буква' not in error:
            #         error.append('лишняя буква')
            error.append('test')



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
            highlighted_text = get_levenshtein_mask(user_input, corrected_text)

            # highlighted_text = highlight_differences(user_input, corrected_text)
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
