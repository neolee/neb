import logfire
from langdetect import detect
import spacy


def chunk_text(text, batch_size=1) -> list[str]:
    lang = detect(text)
    logfire.info("language detected: {lang}", lang=lang)

    if lang == 'en':
        model = "en_core_web_sm"
    elif lang == 'zh-cn' or lang == 'zh-tw':
        model = "zh_core_web_sm"
    else:
        raise ValueError("language not supported")

    with logfire.span("create chunks using model {model}", model=model):
        nlp = spacy.load(model)
        doc = nlp(text)
        if batch_size < 2:
            chunks = [sent.text for sent in doc.sents]
        else:
            sentences = [sent.text for sent in doc.sents]
            chunks = [' '.join(sentences[i:i+batch_size]) for i in range(0, len(sentences), batch_size)]
        return chunks
