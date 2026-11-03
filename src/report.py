from pathlib import Path
import matplotlib.pyplot as plt


def save_report(result: dict, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)

    result["op_stats"].to_csv(out_dir / "operator_stats.csv", index=False)
    result["daily_matrix"].to_csv(out_dir / "operator_daily_errors.csv")
    result["error_pivot"].to_csv(out_dir / "operator_error_types.csv")
    result["team_summary"].to_csv(out_dir / "team_summary.csv", index=False)

    # График 1: топ-5 по ошибкам
    top = result["top5"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(top["operator_id"].astype(str), top["errors"])
    ax.set_title("Топ-5 операторов по количеству ошибок")
    ax.set_xlabel("Ошибки")
    ax.set_ylabel("Operator ID")
    fig.savefig(out_dir / "top_operators.png", dpi=120, bbox_inches="tight")
    plt.close(fig)

    # График 2: cumsum для топ-3 операторов
    daily = result["daily_cum"]
    fig, ax = plt.subplots(figsize=(10, 4))
    for op_id in top.head(3)["operator_id"].tolist():
        sub = daily[daily["operator_id"] == op_id]
        ax.plot(sub["call_date"], sub["cum_errors"], label=f"Operator {op_id}")
    ax.set_title("Накопленные ошибки по дням (топ-3)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Накопленные ошибки")
    ax.legend()
    ax.tick_params(axis="x", rotation=45)
    fig.savefig(out_dir / "cum_errors_top3.png", dpi=120, bbox_inches="tight")
    plt.close(fig)