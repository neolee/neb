import logfire

from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

from rag.text.chunk import chunk_text


default_config = {
    "output_format": "markdown",
    "disable_image_extraction": "true"
}


class PDFLoader:
    def __init__(self, path: str, config: dict=default_config) -> None:
        self.path = path
        self.config = config

    def extract_text(self) -> str:
        config_parser = ConfigParser(self.config)
        converter = PdfConverter(
            config=config_parser.generate_config_dict(),
            artifact_dict=create_model_dict(),
            processor_list=config_parser.get_processors(),
            renderer=config_parser.get_renderer(),
            llm_service=config_parser.get_llm_service()
        )

        with logfire.span("extracting text from {path}", path=self.path):
            rendered = converter(self.path)
            text, _, _ = text_from_rendered(rendered)
            return text

    def chunks(self, batch_size=1) -> list[str]:
        text = self.extract_text()
        return chunk_text(text, batch_size)


if __name__ == "__main__":
    loader = PDFLoader("books/cap.pdf")
    chunks = loader.chunks(batch_size=10)
    print("\nthe first 10 trunks: ")
    for idx, chunk in enumerate(chunks[:10]):
        print(f"trunk {idx+1}: {chunk}")
