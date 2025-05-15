import time

from openai import OpenAI
import os
import base64





#  base 64 编码格式
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_text_from_image(image_path: str, index: int, messages):
    max_retries = 2
    retries = 0
    
    # 保留系统提示和最近的对话历史，限制上下文长度
    if len(messages) > 10:
        # 保留系统提示
        system_messages = [msg for msg in messages if msg["role"] == "system"]
        # 获取最近的非系统消息
        recent_messages = [msg for msg in messages if msg["role"] != "system"][-8:]
        # 重建消息列表
        messages = system_messages + recent_messages
    
    print(f"Processing image {index} with {len(messages)} messages in context")
    
    while retries < max_retries:
        try:
            user_prompt = f"图片:{index}"
            base64_image = encode_image(image_path)
            client = OpenAI(
                api_key=os.getenv('DASHSCOPE_API_KEY'),
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )

            # 添加用户消息到上下文
            user_message = {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {"type": "text", "text": user_prompt},
                ],
            }
            messages.append(user_message)

            completion = client.chat.completions.create(
                # model="qwen-vl-max-2025-01-25",
                model="qwen2.5-vl-32b-instruct",
                messages=messages,
            )
            
            # 获取助手回复
            assistant_message = completion.choices[0].message
            content = assistant_message.content
            
            # 将助手回复添加到上下文
            messages.append({
                "role": "assistant",
                "content": content
            })
            
            return content, messages
        except Exception as e:
            retries += 1
            print(f"Attempt {retries} failed: {e}")
            if retries == max_retries:
                print(f"Failed to infer image [{index}] after {max_retries} attempts.")
                raise e
