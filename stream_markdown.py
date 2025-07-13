import asyncio

from rich.console import Console, ConsoleOptions, RenderResult
from rich.live import Live
from rich.markdown import CodeBlock, Markdown
from rich.syntax import Syntax
from rich.text import Text

from pydantic_ai import Agent
import models as m

import instrument
instrument.init()


coding_agent = Agent()

models = [m.deepseek, m.qwen_coder]

async def main():
    prettier_code_blocks()
    console = Console()
    prompt = 'Show me a short example of using Pydantic.'
    console.log(f'Asking: {prompt}...', style='cyan')
    for model in models:
        console.rule(f"[bold red]Using model {model.model_name}")
        with Live('', console=console, vertical_overflow='visible') as live:
            async with coding_agent.run_stream(prompt, model=model) as result:
                async for message in result.stream_text():
                    live.update(Markdown(message))
        console.log(result.usage())


def prettier_code_blocks():
    """Make rich code blocks prettier and easier to copy.

    ref: https://github.com/samuelcolvin/aicli/blob/v0.8.0/samuelcolvin_aicli.py#L22
    """

    class SimpleCodeBlock(CodeBlock):
        def __rich_console__(
            self, console: Console, options: ConsoleOptions
        ) -> RenderResult:
            code = str(self.text).rstrip()
            yield Text(self.lexer_name, style='dim')
            yield Syntax(
                code,
                self.lexer_name,
                theme=self.theme,
                background_color='default',
                word_wrap=True,
            )
            yield Text(f'/{self.lexer_name}', style='dim')

    Markdown.elements['fence'] = SimpleCodeBlock


if __name__ == '__main__':
    asyncio.run(main())
