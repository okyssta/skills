# HuggingFace Ingestion for ModelBench

## API Endpoint

`https://huggingface.co/api/models?author=ORG&sort=lastModified&direction=-1&limit=100&page=N`

Returns list of models from that org. Each model has: `id`, `pipeline_tag`, `downloads`, `likes`, `config.max_position_embeddings`, `cardData.license`, `tags`, `private`, `createdAt`.

## Filtering Pipeline

1. **Pipeline**: keep only `text-generation`, `image-text-to-text`, `text-to-image`, `any-to-any`
2. **Visibility**: skip `private: true`
3. **Quality**: skip if `downloads < 100 AND likes < 5`
4. **Variant skip** — exclude model IDs matching:
   ```
   GGUF|AWQ|GPTQ|q[48]_|fp[48]|mxfp[48]|quantiz|4bit|8bit|
   -GGUF|-AWQ|-GPTQ|Q4[_0-9]|Q8[_0-9]|
   Imatrix|imatrix|IQ[1-4]_|IQ[3-4]|
   fp16|bf16|half|merged|onnx|qat|mobile|
   DSpark|DFlash|Sico|
   AgentWorld|Lab-|experiment|
   forcedaligner
   ```

## Official Orgs Mapped

| HF Author | Developer Name |
|-----------|---------------|
| meta-llama | Meta |
| google | Google |
| microsoft | Microsoft |
| mistralai | Mistral AI |
| CohereForAI | Cohere |
| Qwen | Alibaba Qwen |
| deepseek-ai | DeepSeek |
| nvidia | NVIDIA |
| stabilityai | Stability AI |
| upstage | Upstage |
| ai21labs | AI21 Labs |
| bigcode | BigCode |
| ibm-granite | IBM |
| 01-ai | 01.AI |
| x-ai | xAI |

## Context Extraction

HF list API returns `config` field for some models. Try these keys in order:
```
max_position_embeddings → max_length → n_positions → max_sequence_length
```

Fall back to 0 if none found. Full config requires individual model API call — not worth it for bulk ingestion.

## License Extraction

Check `cardData.license` first, then scan `tags` for `license:*` prefix. Set `open_source = True` unless license is empty, "other", or "proprietary".

## Existing Model Handling

HF ingestion only fills gaps for existing models (doesn't overwrite):
- Updates `name`, `developer`, `description`, `context_length`, `open_source` only if the existing field is empty
- Sets `metadata_json.hf` with HF-specific fields (downloads, likes, pipeline, license, org, created_at)

## First Run

From 15 orgs × 100 models each (3 pages max), ~400 models pass the filter. **First run (Jul 14 2026): 403 new models** from all 15 orgs. Subsequent runs import ~0 since all slugs already in DB.
