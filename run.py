from pathlib import Path
from src.db import get_engine, load_data
from src.analysis import enrich_calls, analyze
from src.report import save_report

def main():
    engine = get_engine()
    operators, calls = load_data(engine)
    print(f"✔ Loaded {len(operators)} operators, {len(calls)} calls")

    enriched = enrich_calls(calls)
    result = analyze(enriched, operators)

    save_report(result, Path("outputs"))
    print("✔ Report saved to outputs/")
    print("\nТоп-5 операторов по ошибкам:")
    print(result["top5"].to_string(index=False))

if __name__ == "__main__":
    main()