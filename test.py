import torch
from transformers import T5Tokenizer, T5Config, T5ForConditionalGeneration

# load tokenizer and model
pretrained_model = "../../model/Randeng-T5-784M-MultiTask-Chinese"

special_tokens = ["<extra_id_{}>".format(i) for i in range(100)]
tokenizer = T5Tokenizer.from_pretrained(
    pretrained_model,
    do_lower_case=True,
    max_length=512,
    truncation=True,
    additional_special_tokens=special_tokens,
)
config = T5Config.from_pretrained(pretrained_model)
model = T5ForConditionalGeneration.from_pretrained(pretrained_model, config=config)
model.resize_token_embeddings(len(tokenizer))
model.eval()

def keyword_generation(model,text,):
    # tokenize
    text = f"'关键词抽取':【{text}】这篇文章的关键词是什么？"
    encode_dict = tokenizer(text, max_length=512, padding="max_length", truncation=True)

    inputs = {
        "input_ids": torch.tensor([encode_dict["input_ids"]]).long(),
        "attention_mask": torch.tensor([encode_dict["attention_mask"]]).long(),
    }

    # generate answer
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    inputs["input_ids"] = inputs["input_ids"].to(device)
    inputs["attention_mask"] = inputs["attention_mask"].to(device)

    logits = model.generate(
        input_ids=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        max_length=100,
        do_sample=True,
        # early_stopping=True,
    )

    logits = logits[:, 1:]
    predict_label = [tokenizer.decode(i, skip_special_tokens=True) for i in logits]
    return predict_label
