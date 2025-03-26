# RAG 相关技术选型

## PDF 工具

根据[相关报告](pdf-tools.md)的分析，选定 `marker` 作为基本的PDF文本抽取工具，如果碰到需要OCR或者复杂格式解析的场合，准备尝试 `open-parse` 作为补充方案。

- [marker](https://github.com/VikParuchuri/marker?tab=readme-ov-file)
- [open-parser](https://github.com/Filimoa/open-parse?tab=readme-ov-file)

## 文本分块工具

根据[相关报告](text-chunk.md)的分析，选定 `spaCy` 作为中英文文本分块的主要工具。

在特定情况下可以考虑直接使用大语言模型（LLM）的方案，即利用 LLM 的语义理解能力，动态识别文本中的逻辑边界（如段落、主题变化），生成更符合人类理解的分块结果。相比固定规则（如按字符数或标点分割），LLM 分块能更好地保留上下文完整性。

## 代码示例

代码示例为 Grok、Qwen 等大模型生成，完全不保证可用，仅供参考。

### Marker + spaCy

```python
import os
from marker_pdf.marker import extract_text
import spacy
from langdetect import detect

nlp_en = spacy.load("en_core_web_sm")
nlp_zh = spacy.load("zh_core_web_sm")

pdf_path = "path/to/your/document.pdf"

def extract_pdf_text(pdf_path):
    try:
        markdown_text = extract_text(pdf_path)
        return markdown_text
    except Exception as e:
        print(f"提取 PDF 文本时出错: {e}")
        return None

def chunk_text(text):
    try:
        lang = detect(text)
        print(f"检测到的语言: {lang}")

        if lang == 'en':
            doc = nlp_en(text)
        elif lang == 'zh-cn' or lang == 'zh-tw':
            doc = nlp_zh(text)
        else:
            raise ValueError("不支持的语言")

        sentences = [sent.text for sent in doc.sents]
        return sentences
    except Exception as e:
        print(f"分块时出错: {e}")
        return []

def main():
    markdown_text = extract_pdf_text(pdf_path)
    if markdown_text:
        print("提取的 Markdown 文本（前 500 字符）：")
        print(markdown_text[:500])
        text_chunks = chunk_text(markdown_text)
        print("\n文本分块结果（前 5 个句子）：")
        for i, chunk in enumerate(text_chunks[:5]):
            print(f"分块 {i+1}: {chunk}")
    else:
        print("无法从 PDF 中提取文本。")

if __name__ == "__main__":
    main()
```

说明：
- 安装 `spaCy` 之后需要下载中英文语言模型：
  - 英文：`python -m spacy download en_core_web_sm`
  - 中文：`python -m spacy download zh_core_web_sm`
- 性能优化：对于大型 PDF 文件，建议分批处理或使用 GPU 加速。
- 混合语言：对于混合语言文本，语言检测可能不完美，建议测试多种工具（如 `fasttext`）以提高准确性。

### LLM Chunking

```python
import requests

def llm_split_text(text, model_name="qwen:latest"):
    # 构造提示词
    prompt = f"""
    请将以下文本按语义分块，用特殊标记 <<<SPLIT>>> 分隔：
    ---
    {text}
    ---
    """
    
    # 调用 Ollama API
    response = requests.post(
        "http://127.0.0.1:1234/v1/chat/completions",
        json={
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
    )
    result = response.json()["response"]
    
    # 按标记分割
    chunks = [c.strip() for c in result.split("<<<SPLIT>>>") if c.strip()]
    return chunks
```

### Marker + NLTK

```python
import os
from marker_pdf.marker import extract_text
import nltk
from nltk.tokenize import sent_tokenize

# 定义 PDF 文件路径
pdf_path = "path/to/your/document.pdf"  # 请替换为你的 PDF 文件路径

# 使用 Marker 提取 PDF 文本
def extract_pdf_text(pdf_path):
    try:
        # 提取文本并返回 Markdown 格式
        markdown_text = extract_text(pdf_path)
        return markdown_text
    except Exception as e:
        print(f"提取 PDF 文本时出错: {e}")
        return None

# 文本分块：按句子切分
def chunk_text(text):
    # 使用 NLTK 的 sent_tokenize 将文本按句子切分
    sentences = sent_tokenize(text)
    return sentences

# 主函数
def main():
    # 提取 PDF 文本
    markdown_text = extract_pdf_text(pdf_path)
    if markdown_text:
        print("提取的 Markdown 文本（前 500 字符）：")
        print(markdown_text[:500])  # 打印前 500 字符作为预览

        # 将 Markdown 文本分块
        text_chunks = chunk_text(markdown_text)
        print("\n文本分块结果（前 5 个句子）：")
        for i, chunk in enumerate(text_chunks[:5]):
            print(f"分块 {i+1}: {chunk}")
    else:
        print("无法从 PDF 中提取文本。")

if __name__ == "__main__":
    main()
```

说明：
1. PDF 文本提取
   - 使用 `marker_pdf.marker.extract_text` 函数从 PDF 文件中提取文本。
   - 提取的文本以 Markdown 格式返回，能够保留 PDF 中的结构化信息（如标题、表格等）。
   - 通过 `try-except `块处理可能出现的异常，确保程序健壮性。
2. 文本分块
   - 使用 `nltk.tokenize.sent_tokenize` 函数将提取的文本按句子切分。
   - 每个句子作为一个独立的文本块，适合 RAG 系统的检索需求。
   - 如果需要更细粒度的分块，可以使用 `word_tokenize` 按单词切分，或自定义分块逻辑。
3. 运行流程
   - 指定 PDF 文件路径（pdf_path）。
   - 调用 `extract_pdf_text` 函数提取文本，并打印前 500 字符作为预览。
   - 调用 `chunk_text` 函数将文本分块，并打印前 5 个句子作为示例。
4. 扩展思考
   - 对于复杂布局的 PDF，`marker-pdf` 会尽力保留结构，但结果可能因文件而异，必要时需要使用更专门的工具处理。
   - 对于大型 PDF 文件，可以考虑分批处理或使用多线程来提高效率。
   - 可以根据需求调整分块粒度，例如按段落或固定字数切分。
   - 确保 PDF 文件来源可靠，避免混入恶意文件，在生产环境中，建议对用户上传的 PDF 进行安全检查。
