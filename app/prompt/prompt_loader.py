from pathlib import Path


def load_prompt(name: str)->str:
    # 获取提示词文件的路径
    prompt_path = Path(__file__).parents[2] / 'prompts'/f'{name}.prompt'

    # 返回读取的文本内容
    return prompt_path.read_text(encoding='utf-8')

if __name__ == '__main__':
    print(load_prompt('correct_sql'))