from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

torch.num_threads = 1  # Limit to 1 thread for CPU inference
# Load model and tokenizer
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("⏳ Loading tokenizer and model (this may take a while on first run)...")
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()
model.to("cpu")  # Ensures it runs on CPU

# Simple chatbot loop
print("\n🤖 TinyLlama Chatbot (type 'exit' to quit)")
chat_history = ""

while True:
    user_input = input("👤 You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("👋 Exiting chatbot.")
        break

    # Add to chat history
    chat_history += f"<|user|>\n{user_input}\n<|assistant|>\n"

    # Tokenize input
    inputs = tokenizer(chat_history, return_tensors="pt", return_attention_mask=True).to("cpu")

    # Generate response
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.7,
            top_k=50,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    # Decode and extract new response
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    new_response = full_output[len(chat_history.strip()):].strip()

    # Update chat history with TinyLlama's response
    chat_history += new_response + "\n"
    print(f"🤖 TinyLlama: {new_response}")
