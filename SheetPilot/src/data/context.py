from typing import Dict, Any

def generate_dataset_context(metadata: Dict[str, Any], filename: str) -> str:
    """
    Produce a compact, structured Markdown summary of the dataset for LLM ingestion context.
    Includes dimensions, columns, data types, semantic categories, null stats, unique counts,
    and a small, representative preview snippet.
    """
    if not metadata or "shape" not in metadata:
        return "No active dataset context."

    rows = metadata["shape"]["rows"]
    cols = metadata["shape"]["cols"]
    quality_score = metadata.get("data_quality_score", 100.0)
    dup_rows = metadata.get("duplicate_rows", 0)
    
    context_lines = [
        f"Dataset: {filename}",
        f"Dimensions: {rows:,} rows x {cols} columns",
        f"Data Quality Score: {quality_score}%",
        f"Duplicate Rows: {dup_rows:,}",
        "",
        "Columns:"
    ]
    
    for col in metadata.get("columns", []):
        col_name = col["name"]
        dtype = col["dtype"]
        sem_type = col.get("semantic_type", "unknown")
        null_count = col["null_count"]
        null_pct = col["null_pct"]
        uniq_count = col["unique_count"]
        samples = ", ".join(col.get("samples", []))
        
        col_desc = (
            f"- **{col_name}** ({dtype} / {sem_type}): "
            f"Nulls: {null_count:,} ({null_pct}%), "
            f"Unique: {uniq_count:,}"
        )
        if samples:
            col_desc += f", Samples: [{samples}]"
        context_lines.append(col_desc)
        
    context_lines.append("")
    context_lines.append("Key Statistics:")
    stats = metadata.get("stats", {})
    for col_name, col_stats in stats.items():
        if "mean" in col_stats:
            # Numeric column stats summary
            context_lines.append(
                f"- **{col_name}**: "
                f"Min={col_stats.get('min')}, "
                f"Max={col_stats.get('max')}, "
                f"Mean={col_stats.get('mean')}, "
                f"Median={col_stats.get('median')}"
            )
        else:
            # Categorical column stats summary
            context_lines.append(
                f"- **{col_name}**: "
                f"Top='{col_stats.get('top')}', "
                f"Freq={col_stats.get('freq')} ({col_stats.get('freq_pct')}%)"
            )
            
    # Add a compact sample payload block (first 3 rows)
    samples = metadata.get("sample", [])
    if samples:
        context_lines.append("")
        context_lines.append("Sample Data (First 3 Rows):")
        context_lines.append("```json")
        import json
        context_lines.append(json.dumps(samples[:3], indent=2))
        context_lines.append("```")
        
    return "\n".join(context_lines)
