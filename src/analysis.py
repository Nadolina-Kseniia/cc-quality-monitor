import numpy as np
import pandas as pd


def enrich_calls(calls: pd.DataFrame) -> pd.DataFrame:
    calls = calls.copy()
    calls["start_time"] = pd.to_datetime(calls["start_time"])
    calls["call_date"]  = calls["start_time"].dt.date

    # np.where — векторизованный if/else
    calls["error_long_pause"] = np.where(calls["wait_time_sec"] > 120, 1, 0)
    calls["error_dropped"]    = np.where(calls["status"] == "dropped", 1, 0)
    calls["error_low_rating"] = np.where(
        calls["rating"].notna() & calls["rating"].lt(3), 1, 0
    )
    calls["is_error"] = calls[
        ["error_long_pause", "error_dropped", "error_low_rating"]
    ].max(axis=1)

    # str.join — собираем список типов ошибок в одну строку
    def _types(row) -> str:
        flags = []
        if row["error_long_pause"]: flags.append("long_pause")
        if row["error_dropped"]:    flags.append("dropped")
        if row["error_low_rating"]: flags.append("low_rating")
        return "|".join(flags) if flags else "none"

    calls["error_types"] = calls.apply(_types, axis=1)
    return calls


def analyze(calls: pd.DataFrame, operators: pd.DataFrame) -> dict:
    # merge — объединяем звонки с операторами
    merged = calls.merge(operators, on="operator_id", how="left")

    # slices — берём нужные строки/столбцы
    completed = merged.loc[merged["status"] == "completed",
                           ["call_id", "operator_id", "rating", "is_error"]]

    # groupby + transform — отклонение от среднего по команде
    op_stats = (
        merged.groupby(["team_id", "operator_id"])
              .agg(total_calls=("call_id", "count"), errors=("is_error", "sum"))
              .reset_index()
    )
    op_stats["team_mean_errors"] = op_stats.groupby("team_id")["errors"].transform("mean")
    op_stats["deviation"]        = op_stats["errors"] - op_stats["team_mean_errors"]

    # cumsum — накопительные ошибки по дням
    daily = (
        merged.groupby(["operator_id", "call_date"])["is_error"]
              .sum().reset_index()
              .sort_values(["operator_id", "call_date"])
    )
    daily["cum_errors"] = daily.groupby("operator_id")["is_error"].cumsum()

    # unstack — матрица operator_id × call_date
    daily_matrix = (
        merged.groupby(["operator_id", "call_date"])["is_error"]
              .sum().unstack(fill_value=0)
    )

    # str.split + explode — разворачиваем типы ошибок в строки
    exploded = merged.loc[merged["error_types"] != "none"].copy()
    exploded["error_type"] = exploded["error_types"].str.split("|")
    exploded = exploded.explode("error_type")
    error_pivot = (
        exploded.groupby(["operator_id", "error_type"]).size().unstack(fill_value=0)
    )

    # str.join снова — сводка по командам
    team_summary = (
        merged.groupby("team_id")
              .agg(
                  total_calls=("call_id", "count"),
                  total_errors=("is_error", "sum"),
                  operators=("name", lambda s: ", ".join(sorted(s.unique()))),
              )
              .reset_index()
    )
    team_summary["error_rate_pct"] = (
        100 * team_summary["total_errors"] / team_summary["total_calls"]
    ).round(2)

    # slices — топ-5
    top5 = op_stats.sort_values("errors", ascending=False).iloc[:5]

    return {
        "merged": merged,
        "completed": completed,
        "op_stats": op_stats,
        "daily_cum": daily,
        "daily_matrix": daily_matrix,
        "error_pivot": error_pivot,
        "team_summary": team_summary,
        "top5": top5,
    }