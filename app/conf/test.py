from dataclasses import dataclass
from pathlib import Path

import yaml
from omegaconf import OmegaConf

# yaml_path = Path(__file__)
# print(yaml_path) # E:\workspace\data-agent\app\conf\context.py

# 获取yaml文件的路径
# yaml_path = Path(__file__).parents[2] / 'conf/test.yaml'
# print(yaml_path) # E:\workspace\data-agent\conf\test.yaml

# 读取yaml文件内容
# with open(yaml_path, 'r', encoding='utf-8') as f:
#     yaml_data = yaml.safe_load(f)
#     print(yaml_data) # {'name': '老王', 'age': 35, 'sex': '男'}
#     print(yaml_data['name']) # 老王
#     print(yaml_data.get('name')) # 老王



# 1.获取yaml文件的路径
yaml_path = Path(__file__).parents[2] / 'conf/test.yaml'
# 2.读取yaml文件内容
yaml_data = OmegaConf.load(yaml_path)
# print(yaml_data) # {'name': '老王', 'age': 35, 'sex': '男'}

# 3定义数据类
@dataclass
class Person:
    name: str
    age: int
    sex: str

# 4.合并创建对象
person: Person = OmegaConf.to_object(OmegaConf.merge(Person,yaml_data))
print(person) # Person(name='老王', age=35, sex='男')
print(person.name) # 老王