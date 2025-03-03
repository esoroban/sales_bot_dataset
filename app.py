import gradio as gr

def chatbot(question, context):
    # Здесь вызываешь свою модель
    response = my_model.generate_response(question, context)
    return response

iface = gr.Interface(
    fn=chatbot,
    inputs=["text", "text"],
    outputs="text",
    title="ШІ для школи усного рахунку «Соробан»",
    description="Введіть питання та контекст, і бот надасть відповідь."
)

if __name__ == "__main__":
    iface.launch()