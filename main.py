from io import BytesIO
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
import plotly.graph_objects as go

app = FastAPI(title="Gauge Image API")


def get_status_config(value: float) -> dict:
    if value < 0 or value > 100:
        raise ValueError("El valor debe estar entre 0 y 100")

    if value < 60:
        status = "rojo"
        bar_color = "#dc2626"
    elif value < 85:
        status = "amarillo"
        bar_color = "#d97706"
    else:
        status = "verde"
        bar_color = "#16a34a"

    return {
        "status": status,
        "bar_color": bar_color,
    }


def build_gauge_figure(
    value: float,
    title: str = "Indicador",
    min_value: float = 0,
    max_value: float = 100,
):
    cfg = get_status_config(value)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%"},
            title={"text": title},
            gauge={
                "axis": {"range": [min_value, max_value]},
                "bar": {"color": cfg["bar_color"], "thickness": 0.35},
                "steps": [
                    {"range": [0, 60], "color": "#fecaca"},   # rojo claro
                    {"range": [60, 85], "color": "#fde68a"},  # amarillo claro
                    {"range": [85, 100], "color": "#bbf7d0"}, # verde claro
                ],
                "threshold": {
                    "line": {"color": "#111827", "width": 3},
                    "thickness": 0.8,
                    "value": value,
                },
            },
        )
    )

    fig.update_layout(
        width=105,
        height=70,
        margin=dict(t=12, r=10, l=10, b=6),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#111827", size=4),
    )

    return fig


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/gauge.png")
def gauge_png(
    value: float,
    title: str = "Recaudación mensual",
):
    try:
        fig = build_gauge_figure(value=value, title=title)

        # Genera bytes PNG en memoria, sin guardar archivo temporal
        image_bytes = fig.to_image(format="png", width=105, height=70, scale=2)

        return Response(
            content=image_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": 'inline; filename="gauge.png"',
                "Cache-Control": "no-store",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando imagen: {e}")
