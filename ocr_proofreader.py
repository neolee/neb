from __future__ import annotations as _annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Iterable

import logfire
from pydantic import BaseModel, Field
from pydantic_ai import Agent

import instrument
instrument.init()

import models as m


PROOFREADER_SYSTEM_PROMPT = """
你是一名精通中文的专业文字编辑，专注于修正 OCR 扫描稿中常见的错误。

## 重点关注
- 形近字误识：判断因字形相似导致的错字。
- 同音字误用：识别因拼音输入造成的发音相同但字形错误的词。
- 明显不通顺的词句：若句子语义明显有误或不通顺，可做最小幅度的润色。

## 修改准则
1. 保持 Markdown 结构与语义，避免破坏标题、列表、代码块、链接等格式。
2. 仅在必要处进行最小修改，避免大段重写或风格化改写。
3. 保持原文的语体与术语，用词要与上下文一致。
4. 若没有发现需要修正的错误，请返回空的 `edits` 列表。

## 输出格式
- 严格返回 JSON 对象，键名为 `edits`，值为按行号升序排列的列表。
- 每个元素为：`{"line": <起始行号>, "original": "原文本", "replacement": "修正文"}`。
- `line` 为 1 起始的行号，指向 `original` 的首行；当需要在文末追加内容时可使用 `line = 总行数 + 1`。
- `original`、`replacement` 可跨多行。若仅插入内容，则 `original` 为空字符串，并在指定行号的行首插入 `replacement`；若删除内容，则 `replacement` 为空字符串。
- 为减少 token，请仅返回必要的修改内容，避免重复未变动的文本。

## 示例
```json
{"edits": [{"line": 12, "original": "第十二行错别字", "replacement": "第十二行正字"}]}
```
"""


class EditInstruction(BaseModel):
    line: int = Field(..., ge=1, description="1 起始的行号，指向 original 的首行。")
    original: str = Field("", description="需要替换的原始文本，可为空。")
    replacement: str = Field("", description="替换后的文本，可为空。")


class ProofreadResponse(BaseModel):
    edits: list[EditInstruction] = Field(
        default_factory=list,
        description="按行号排序的修改指令，若无需修改则为空列表。",
    )


proofreader_agent = Agent(
    model=m.deepseek,
    output_type=ProofreadResponse,
    system_prompt=PROOFREADER_SYSTEM_PROMPT,
    name="ocr_proofreader",
    retries=1,
)


class EditApplyError(RuntimeError):
    """Raised when edits cannot be applied cleanly."""


def list_markdown_files(directory: Path) -> list[Path]:
    """Return all direct `.md` files under the given directory."""
    return sorted(
        f for f in directory.iterdir() if f.is_file() and f.suffix.lower() == ".md"
    )


def build_user_prompt(file_path: Path, content: str) -> str:
    """Construct the user prompt for the proofreader agent."""
    return (
        "请校对以下 Markdown 文本，修正 OCR 形近字与同音字错误，并保持格式：\n"
        f"目标文件：{file_path.name}\n"
        "请输出 JSON，并仅包含 `edits` 列表。\n"
        "每个元素结构为 {\"line\": 行号, \"original\": 原文, \"replacement\": 修正文}。\n"
        "若无需调整请返回 {\"edits\": []}。\n\n"
        "<ORIGINAL_MARKDOWN>\n"
        "```markdown\n"
        f"{content}\n"
        "```\n"
        "</ORIGINAL_MARKDOWN>"
    )


def _line_start_index(text: str, line: int) -> int:
    if line < 1:
        raise EditApplyError(f"行号（line={line}）必须大于等于 1")
    if line == 1:
        return 0

    current_line = 1
    index = 0
    length = len(text)
    while current_line < line:
        newline = text.find("\n", index)
        if newline == -1:
            if current_line + 1 == line:
                return length
            raise EditApplyError(f"行号（line={line}）超出原文范围")
        index = newline + 1
        current_line += 1
    return index


def apply_edits(original_text: str, edits: list[EditInstruction]) -> str:
    if not edits:
        return original_text

    text = original_text
    for edit in sorted(edits, key=lambda item: item.line, reverse=True):
        start_index = _line_start_index(text, edit.line)
        if edit.original:
            match_index = text.find(edit.original, start_index)
            if match_index == -1:
                raise EditApplyError(
                    f"未在指定位置找到原文片段: {edit.original!r} (line={edit.line})"
                )
            start_index = match_index
            end_index = match_index + len(edit.original)
        else:
            end_index = start_index

        text = text[:start_index] + edit.replacement + text[end_index:]

    return text


def usage_as_dict(usage: object) -> dict[str, object]:
    if usage is None:
        return {}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()  # type: ignore[no-any-return]
    if hasattr(usage, "dict"):
        return usage.dict()  # type: ignore[no-any-return]
    if isinstance(usage, dict):
        return usage
    return {"raw": str(usage)}


async def proofread_file(path: Path, *, dry_run: bool = False) -> None:
    with logfire.span("proofread_markdown", file=str(path)):
        logfire.info("开始校对 {file}", file=str(path))
        content = path.read_text(encoding="utf-8")
        prompt = build_user_prompt(path, content)

        result = await proofreader_agent.run(user_prompt=prompt)
        usage = usage_as_dict(result.usage())
        if usage:
            logfire.info("LLM 令牌用量", usage=usage)

        response = result.output
        edits = response.edits or []
        if not edits:
            logfire.info("未发现需要修改的内容", file=str(path))
            print(f"[skip] {path.name} 未发现明显错误")
            return

        try:
            updated = apply_edits(content, edits)
        except EditApplyError as exc:
            logfire.error("无法自动应用修改: {error}", error=str(exc), file=str(path))
            payload = json.dumps(response.model_dump(), ensure_ascii=False, indent=2)
            print(f"[manual] {path.name} 请手工执行以下修改指令:\n{payload}")
            return

        if dry_run:
            payload = json.dumps(response.model_dump(), ensure_ascii=False, indent=2)
            print(f"[dry-run] {path.name}\n{payload}")
            return

        if updated == content:
            logfire.warning("应用修改后文件无变化", file=str(path))
            print(f"[noop] {path.name} 修改未改变文件内容")
            return

        path.write_text(updated, encoding="utf-8")
        logfire.info("文件已更新", file=str(path), edits=len(edits))
        print(f"[updated] {path.name}")


async def proofread_directory(directory: Path, *, dry_run: bool = False) -> None:
    files = list_markdown_files(directory)
    if not files:
        logfire.warning("目录中未找到 Markdown 文件", directory=str(directory))
        print(f"未在 {directory} 中找到 Markdown 文件。")
        return

    for file_path in files:
        await proofread_file(file_path, dry_run=dry_run)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="使用 LLM 校对 OCR 结果的 Markdown 文件并根据编辑指令更新内容。"
    )
    parser.add_argument("directory", type=Path, help="包含 Markdown 文件的目录")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅输出差异而不写回文件",
    )
    return parser.parse_args(list(argv) if argv is not None else None)


async def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    directory = args.directory.expanduser().resolve()
    if not directory.exists() or not directory.is_dir():
        raise SystemExit(f"目录不存在或不是有效的文件夹: {directory}")

    with logfire.span("ocr_proofreader_run", directory=str(directory), dry_run=args.dry_run):
        await proofread_directory(directory, dry_run=args.dry_run)


if __name__ == "__main__":
    asyncio.run(main())
