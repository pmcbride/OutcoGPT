import gradio as gr

gr.Interface(fn=lambda x: x, inputs="text", outputs="text").launch(share=True, server_name="0.0.0.0")