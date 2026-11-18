# AI context: decisions

## Current decisions

- Keep the product local-first and retain Ollama for local answer generation.
- Reuse the existing RAG service for MCP instead of creating a second retrieval implementation.
- Use a local stdio MCP server and expose read-only knowledge tools in the first iteration.
- Keep developer memory (this directory) separate from end-user chat memory. Chat history currently stores individual question/answer records and is not included in later prompts.
- Authentication and document-level access control are not implemented.
