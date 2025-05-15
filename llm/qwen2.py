import os
from openai import OpenAI

user_prompt = """图片的描述如下:"""


def generate_story(input_text: str, system_prompt: str, story_user_prompt: str = user_prompt, stream=False):
    """
    根据多张图片的描述生成一个连贯的儿童故事
    
    Args:
        input_text: 包含多张图片描述的文本，每张图片描述由换行符分隔
        stream: 是否使用流式输出
        
    Returns:
        str 或 generator: 生成的完整故事或故事流
        :param stream:
        :param input_text:
        :param system_prompt:
    """

    # 打印输入文本的长度，用于调试
    print(f"输入文本长度: {len(input_text)} 字符")

    # 创建OpenAI客户端
    client = OpenAI(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    user_prompt2 = story_user_prompt + "\n\n" + input_text

    # 调用模型生成故事
    completion = client.chat.completions.create(
        model="qwen-max",
        extra_body={
            "enable_search": True
        },
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt2},
        ],
        stream=stream
    )

    if stream:
        # 流式输出
        return completion
    else:
        # 非流式输出
        result = completion.choices[0].message.content
        print(f"输出文本长度: {len(result)} 字符")
        return result
