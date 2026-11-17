from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

# ==================== 日志配置模型 ====================
@dataclass
class File:
    enable: bool
    level: str
    path: str
    rotation: str
    retention: str


@dataclass
class Console:
    enable: bool
    level: str


@dataclass
class LoggingConfig:
    file: File
    console: Console


# ==================== database配置模型 ====================

@dataclass
class DBConfig:
    host: str
    port: int
    user: str
    password: str
    database: str

# ==================== Qdrant 配置模型 ====================

@dataclass
class QdrantConfig:
    host: str
    port: int
    embedding_size: int


# ==================== Embedding 配置模型 ====================

@dataclass
class EmbeddingConfig:
    host: str
    port: int
    model: str


# ==================== ES 配置模型 ====================

@dataclass
class ESConfig:
    host: str
    port: int
    index_name: str


# ==================== LLM 配置模型 ====================

@dataclass
class LLMConfig:
    model_name: str
    api_key: str


# ==================== app总配置模型 ====================

@dataclass
class AppConfig:
    logging: LoggingConfig
    db_meta: DBConfig
    db_dw: DBConfig
    qdrant: QdrantConfig
    embedding: EmbeddingConfig
    es: ESConfig
    llm: LLMConfig


# 1.获取yaml文件的路径
yaml_path = Path(__file__).parents[2] / 'conf/app_config.yaml'

# 2.读取yaml文件内容
yaml_data = OmegaConf.load(yaml_path)

# 3.合并创建对象
app_config: AppConfig = OmegaConf.to_object(OmegaConf.merge(AppConfig,yaml_data))

if __name__ == '__main__':
    print(app_config)
    print(app_config.logging.console.level) # INFO