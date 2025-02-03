# app/translator.py

from transformers import MarianMTModel, MarianTokenizer

def load_translation_model(src_lang: str = "en", tgt_lang: str = "fr"):
    """
    Load a MarianMT model and tokenizer for translating from src_lang to tgt_lang.
    For instance, for English to French translation, use:
        src_lang = "en", tgt_lang = "fr"
    """
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

def translate_text(text: str, tokenizer, model) -> str:
    """
    Translate the provided text using the specified tokenizer and model.
    """
    # Tokenize the text
    batch = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    # Generate the translated tokens
    generated_ids = model.generate(**batch)
    # Decode to string
    translated = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return translated
