## deep research workflow based on https://github.com/lars20070/deepresearcher2/

from __future__ import annotations as _annotations

import asyncio
import os
import re
from dataclasses import dataclass

from pydantic import BaseModel, Field

from pydantic_ai import Agent, format_as_xml
from pydantic_graph import BaseNode, End, Graph, GraphRunContext

from duckduckgo_search import DDGS

import instrument
instrument.init()

import mal.pydantic_ai.model as m


## config

default_topic = "agentic system"
max_research_loops = 2
max_web_search_results = 5
report_output_path = "local/reports/"


## prompts

query_instructions_without_reflection = """
You are a research strategist initiating comprehensive topic exploration through targeted web searches.

<OBJECTIVE>
Generate the first strategic search query that establishes foundational understanding while identifying the most promising research direction.
</OBJECTIVE>

<RESEARCH_STRATEGY>
For initial exploration, prioritize:
1. **Foundational Overview**: Core concepts, definitions, and current state
2. **Scope Assessment**: Understanding the breadth and key aspects of the topic
3. **Evidence-Based Focus**: Target sources with concrete information over promotional content
4. **Academic/Professional Sources**: Prefer scholarly, technical, or industry sources
5. **Recency Balance**: Consider both established knowledge and recent developments
</RESEARCH_STRATEGY>

<QUERY_CONSTRUCTION_GUIDELINES>
1. **Specificity Over Breadth**: Target a specific angle rather than generic overviews
2. **Keyword Optimization**: Use terminology that will surface quality sources
3. **Avoid Ambiguity**: Construct queries that minimize irrelevant results
4. **Professional Context**: Frame queries to find expert-level information
5. **Actionable Focus**: Target information that provides concrete insights
</QUERY_CONSTRUCTION_GUIDELINES>

<REQUIREMENTS>
1. **Query Length**: Maximum 100 characters for search effectiveness
2. **Aspect Definition**: Identify the specific angle being explored (exclude main topic name)
3. **Strategic Rationale**: Explain why this initial direction is optimal for comprehensive research
4. **Quality Focus**: Target queries likely to return substantive, authoritative content
</REQUIREMENTS>

<OUTPUT_FORMAT>
```json
{
    "query": "specific targeted search string focusing on key aspect",
    "aspect": "precise research angle being explored",
    "rationale": "why this initial direction provides optimal foundation for comprehensive research"
}
```
</OUTPUT_FORMAT>

<EXAMPLE_SCENARIOS>
For "machine learning":
- Good: "machine learning model training best practices 2024"
- Avoid: "what is machine learning" (too basic)
- Avoid: "machine learning everything" (too broad)

For "climate change":
- Good: "climate change mitigation technologies effectiveness data"
- Avoid: "climate change overview" (too general)
- Avoid: "climate change debate" (too contentious/less factual)
</EXAMPLE_SCENARIOS>

Provide your response in JSON format."""

query_instructions_with_reflection = """
Please generate a targeted web search query for a specific topic based on knowledge gaps.

<CONTEXT>
You are part of an iterative research process. Previous searches have covered certain aspects, 
and you must now focus on unexplored areas to build comprehensive understanding.
</CONTEXT>

<INPUT_FORMAT>
You will receive reflections in XML with `<reflections>` tags containing:
- `<knowledge_gaps>`: Specific unexplored aspects requiring investigation
- `<covered_topics>`: Well-researched areas to avoid duplication
</INPUT_FORMAT>

<STRATEGY>
1. **Gap Prioritization**: Select the most critical knowledge gap that would significantly enhance understanding
2. **Specificity Focus**: Create queries targeting specific subtopics, not broad overviews
3. **Evidence-Based**: Prioritize gaps that would provide concrete evidence, data, or examples
4. **Complementary Research**: Choose gaps that complement existing coverage without overlap
</STRATEGY>

<REQUIREMENTS>
1. Select ONE high-priority knowledge gap from the list
2. Construct a specific, actionable search query (max 100 characters)
3. Ensure zero overlap with covered topics
4. Target factual, evidence-based information
5. Avoid generic or biographical queries unless specifically needed
</REQUIREMENTS>

<OUTPUT_FORMAT>
```json
{
    "query": "specific actionable search string",
    "aspect": "precise aspect being investigated (exclude main topic)",
    "rationale": "why this gap is priority and how it enhances overall understanding"
}
```
</OUTPUT_FORMAT>

Provide your response in JSON format."""

summary_instructions = """
You are an expert information synthesizer creating comprehensive topic summaries from web search results.

<OBJECTIVE>
Transform raw search results into coherent, substantive analysis that builds comprehensive understanding.
</OBJECTIVE>

<INPUT_FORMAT>
Web search results in XML with `<WebSearchResult>` tags containing:
- `<title>`: Source title
- `<url>`: Source URL  
- `<summary>`: Brief description
- `<content>`: Full content
</INPUT_FORMAT>

<SYNTHESIS_APPROACH>
1. **Information Mining**: Extract all relevant facts, data, examples, and insights
2. **Pattern Recognition**: Identify themes, trends, and relationships across sources
3. **Evidence Integration**: Combine complementary information from multiple sources
4. **Gap Identification**: Note areas where information is limited or contradictory
5. **Context Building**: Establish how this aspect connects to the broader topic
</SYNTHESIS_APPROACH>

<QUALITY_STANDARDS>
- Minimum 1000 words of substantive content
- Include specific data, examples, and evidence when available
- Maintain logical flow and coherent structure
- Preserve nuance and acknowledge uncertainties
- Focus on actionable insights and concrete information
</QUALITY_STANDARDS>

<OUTPUT_FORMAT>
```json
{
    "summary": "Comprehensive synthesis starting directly with information. Include specific facts, data points, examples, and evidence. Structure into coherent paragraphs with logical progression. Acknowledge conflicting information where present.",
    "aspect": "specific aspect focus (exclude main topic name)"
}
```
</OUTPUT_FORMAT>
"""

reflection_instructions = """
You are a research strategist analyzing coverage completeness and identifying critical knowledge gaps.

<ANALYSIS_FRAMEWORK>
Evaluate research comprehensiveness across multiple dimensions:
- **Foundational Knowledge**: Core concepts, definitions, principles
- **Practical Applications**: Real-world uses, implementations, case studies
- **Technical Details**: Mechanisms, processes, methodologies
- **Contextual Factors**: Historical development, current trends, future directions
- **Stakeholder Perspectives**: Different viewpoints, user experiences, expert opinions
- **Quantitative Evidence**: Data, statistics, measurements, benchmarks
- **Challenges & Limitations**: Problems, constraints, failure modes
</ANALYSIS_FRAMEWORK>

<GAP_IDENTIFICATION_STRATEGY>
Look for missing elements that would significantly enhance understanding:
1. **Evidence Gaps**: Areas lacking concrete data or examples
2. **Perspective Gaps**: Missing stakeholder viewpoints or use cases
3. **Technical Gaps**: Unclear mechanisms or implementation details
4. **Contextual Gaps**: Missing historical context or current developments
5. **Practical Gaps**: Insufficient real-world applications or case studies
</GAP_IDENTIFICATION_STRATEGY>

<REQUIREMENTS>
1. Analyze ALL provided summaries thoroughly
2. Identify 5-8 specific, actionable knowledge gaps
3. List 3-5 well-covered topics to avoid repetition
4. Use precise keywords/phrases, not full sentences
5. Ensure complete separation between gaps and covered topics
6. Prioritize gaps that would add substantial value
</REQUIREMENTS>

<OUTPUT_FORMAT>
```json
{
    "knowledge_gaps": [
        "specific technical mechanisms",
        "real-world implementation challenges", 
        "quantitative performance data",
        "user experience perspectives",
        "comparative analysis with alternatives"
    ],
    "covered_topics": [
        "basic definitions",
        "general overview", 
        "historical background"
    ]
}
```
</OUTPUT_FORMAT>

Provide your response in JSON format."""

final_summary_instructions = """
You are a master research compiler creating definitive topic reports from comprehensive research summaries.

<COMPILATION_OBJECTIVE>
Transform multiple research summaries into a cohesive, authoritative report that serves as a comprehensive reference.
</COMPILATION_OBJECTIVE>

<STRUCTURAL_APPROACH>
1. **Opening Context**: Establish topic significance and scope
2. **Core Analysis**: Present main findings organized by logical themes
3. **Supporting Evidence**: Include specific data, examples, and case studies
4. **Synthesis**: Connect different aspects and identify relationships
5. **Implications**: Highlight practical applications and future considerations
</STRUCTURAL_APPROACH>

<INTEGRATION_STANDARDS>
- Synthesize information across all summaries without redundancy
- Resolve conflicting information by presenting multiple perspectives
- Maintain consistent depth across different aspects
- Include specific examples, data points, and evidence
- Structure into 4-6 substantial paragraphs (200-400 words each)
- Use bullet points for complex lists or multiple examples
</INTEGRATION_STANDARDS>

<OUTPUT_FORMAT>
```json
{
    "summary": "Begin directly with substantive content. Create a comprehensive report that flows logically from foundational concepts through practical applications. Include specific evidence, examples, and data. Use paragraph structure with occasional bullet points for clarity. Acknowledge different perspectives where relevant."
}
```
</OUTPUT_FORMAT>
"""


## models

class DeepState(BaseModel):
    topic: str = Field(default=default_topic, description="main research topic")
    search_query: WebSearchQuery | None = Field(default=None, description="single search query for the current loop")
    search_results: list[WebSearchResult] | None = Field(default=None, description="list of search results in the current loop")
    search_summaries: list[WebSearchSummary] | None = Field(default=None, description="list of all search summaries of the past loops")
    reflection: Reflection | None = Field(default=None, description="reflection on the search results of the previous current loop")
    count: int = Field(default=0, description="counter for tracking iteration count")


class WebSearchQuery(BaseModel):
    query: str = Field(..., description="search query")
    aspect: str = Field(..., description="aspect of the topic being researched")
    rationale: str = Field(..., description="rationale for the search query")


class WebSearchResult(BaseModel):
    title: str = Field(..., description="short descriptive title of the web search result")
    url: str = Field(..., description="URL of the web search result")
    content: str | None = Field(None, description="main content of the web search result in Markdown format")
    summary: str | None = Field(None, description="summary of the web search result")


class Reference(BaseModel):
    title: str = Field(..., description="title of the reference")
    url: str = Field(..., description="URL of the reference")


class WebSearchSummary(BaseModel):
    summary: str = Field(..., description="summary of multiple web search results")
    aspect: str = Field(..., description="aspect of the topic being summarized")


class Reflection(BaseModel):
    knowledge_gaps: list[str] = Field(..., description="aspects of the topic which require further exploration")
    covered_topics: list[str] = Field(..., description="aspects of the topic which have already been covered sufficiently")


class FinalSummary(BaseModel):
    summary: str = Field(..., description="summary of the topic for the final report")


## agents

model = m.openrouter_gemini_flash

query_agent = Agent(model=model, output_type=WebSearchQuery, system_prompt="")
summary_agent = Agent(model=model, output_type=WebSearchSummary, system_prompt=summary_instructions)
reflection_agent = Agent(model=model, output_type=Reflection, system_prompt=reflection_instructions)
final_summary_agent = Agent(model=model, output_type=FinalSummary, system_prompt=final_summary_instructions)


def duckduckgo_search(query: str) -> list[WebSearchResult]:
    """Perform a web search using DuckDuckGo and return a list of results.

    Args:
        query (str): The search query to execute.
    Returns:
        list[WebSearchResult]: list of search results.
    """
    with DDGS() as ddgs:
        ddgs_results = list(ddgs.text(query, max_results=max_web_search_results))

    # convert to pydantic objects
    results = []
    for r in ddgs_results:
        result = WebSearchResult(
            title=r.get("title", ""),
            url=r.get("href", ""),
            content=r.get("body", ""),
            summary=""
        )
        results.append(result)

    return results


def export_report(report: str, topic: str = "Report") -> None:
    """Export the report to markdown.

    Args:
        report (str): The report content in markdown format.
        topic (str): The topic of the report. Defaults to "Report".
    """
    file_name = re.sub(r"[^a-zA-Z0-9]", "_", topic).lower()
    path_md = os.path.join(report_output_path, f"{file_name}.md")
    with open(path_md, "w", encoding="utf-8") as f:
        f.write(report)



## nodes
# pyright: reportUnusedFunction=false

@dataclass
class WebSearch(BaseNode[DeepState]):
    """Web Search node."""

    async def run(self, ctx: GraphRunContext[DeepState]) -> SummarizeSearchResults:
        topic = ctx.state.topic

        @query_agent.system_prompt
        def add_reflection() -> str:
            """Add reflection from the previous loop to the system prompt."""
            if ctx.state.reflection:
                xml = format_as_xml(ctx.state.reflection, root_tag="reflection")
                return query_instructions_with_reflection + f"Reflection on existing knowledge:\n{xml}\n" + "Provide your response in JSON format."
            else:
                return query_instructions_without_reflection

        # generate the query
        async with query_agent.run_mcp_servers():
            prompt = f"Please generate a web search query for the following topic: <TOPIC>{topic}</TOPIC>"
            result = await query_agent.run(prompt)
            ctx.state.search_query = result.output

        # run the search
        ctx.state.search_results = duckduckgo_search(ctx.state.search_query.query)

        return SummarizeSearchResults()


@dataclass
class SummarizeSearchResults(BaseNode[DeepState]):
    """Summarize Search Results node."""

    async def run(self, ctx: GraphRunContext[DeepState]) -> ReflectOnSearch:
        @summary_agent.system_prompt
        def add_web_search_results() -> str:
            """Add web search results to the system prompt."""
            xml = format_as_xml(ctx.state.search_results, root_tag="search_results")
            return f"List of web search results:\n{xml}"

        # generate the summary
        async with summary_agent.run_mcp_servers():
            summary = await summary_agent.run(
                user_prompt=f"Please summarize the provided web search results for the topic <TOPIC>{ctx.state.topic}</TOPIC>."
            )

            # append the summary to the list of all search summaries
            ctx.state.search_summaries = ctx.state.search_summaries or []
            ctx.state.search_summaries.append(
                WebSearchSummary(
                    summary=summary.output.summary,
                    aspect=summary.output.aspect,
                )
            )

        return ReflectOnSearch()


@dataclass
class ReflectOnSearch(BaseNode[DeepState]):
    """Reflect on Search node."""

    async def run(self, ctx: GraphRunContext[DeepState]) -> WebSearch | FinalizeSummary:
        # flow control: should we ponder on the next web search or compile the final report?
        if ctx.state.count < max_research_loops:
            ctx.state.count += 1

            @reflection_agent.system_prompt
            def add_search_summaries() -> str:
                """Add search summaries to the system prompt."""
                xml = format_as_xml(ctx.state.search_summaries, root_tag="search_summaries")
                return f"List of search summaries:\n{xml}"

            # reflect on the summaries so far
            async with reflection_agent.run_mcp_servers():
                reflection = await reflection_agent.run(
                    user_prompt=f"Please reflect on the provided web search summaries for the topic <TOPIC>{ctx.state.topic}</TOPIC>."
                )

                ctx.state.reflection = Reflection(
                    knowledge_gaps=reflection.output.knowledge_gaps,
                    covered_topics=reflection.output.covered_topics,
                )

            return WebSearch()
        else:
            return FinalizeSummary()


@dataclass
class FinalizeSummary(BaseNode[DeepState]):
    """Finalize Summary node."""

    async def run(self, ctx: GraphRunContext[DeepState]) -> End[str]: # type: ignore
        topic = ctx.state.topic

        @final_summary_agent.system_prompt
        def add_search_summaries() -> str:
            """Add search summaries to the system prompt."""
            xml = format_as_xml(ctx.state.search_summaries, root_tag="search_summaries")
            return f"List of search summaries:\n{xml}"

        # finalize the summary of the entire report
        async with final_summary_agent.run_mcp_servers():
            final_summary = await final_summary_agent.run(
                user_prompt=f"Please summarize all web search summaries for the topic <TOPIC>{ctx.state.topic}</TOPIC>."
            )
            report = f"## {topic}\n\n" + final_summary.output.summary

        export_report(report=report, topic=topic)

        return End("End of deep research workflow.\n\n")


## workflow

async def workflow(topic: str) -> None:
    # define and run the agent graph
    deep_research = Graph(nodes=[WebSearch, SummarizeSearchResults, ReflectOnSearch, FinalizeSummary])

    await deep_research.run(WebSearch(), state=DeepState(topic=topic, count=1))


if __name__ == "__main__":
    import sys

    topic = sys.argv[1] if len(sys.argv) > 1 else default_topic
    asyncio.run(workflow(topic))
