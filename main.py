from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

DATA_PATH = Path("sales_data.csv")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def load_sales_data(file_path: Path) -> pd.DataFrame:
    """Load sales data and prepare date/month columns."""
    df = pd.read_csv(file_path)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate business KPIs for the executive summary."""
    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    total_units = df["units_sold"].sum()
    average_order_value = total_revenue / total_orders
    profit_margin = (total_profit / total_revenue) * 100
    best_category = df.groupby("category")["revenue"].sum().idxmax()
    best_product = df.groupby("product")["revenue"].sum().idxmax()
    best_channel = df.groupby("sales_channel")["revenue"].sum().idxmax()

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "total_orders": total_orders,
        "total_units": total_units,
        "average_order_value": average_order_value,
        "profit_margin": profit_margin,
        "best_category": best_category,
        "best_product": best_product,
        "best_channel": best_channel,
    }


def create_charts(df: pd.DataFrame) -> list[Path]:
    """Create business charts and return saved image paths."""
    chart_paths = []

    monthly = df.groupby("month")[["revenue", "profit"]].sum().reset_index()
    plt.figure(figsize=(10, 5))
    plt.plot(monthly["month"], monthly["revenue"], marker="o", label="Revenue")
    plt.plot(monthly["month"], monthly["profit"], marker="o", label="Profit")
    plt.title("Monthly Revenue and Profit")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.legend()
    plt.tight_layout()
    path = OUTPUT_DIR / "monthly_revenue_profit.png"
    plt.savefig(path, dpi=160)
    plt.close()
    chart_paths.append(path)

    category = df.groupby("category")[["revenue", "profit"]].sum().sort_values("revenue", ascending=False)
    plt.figure(figsize=(10, 5))
    category["revenue"].plot(kind="bar")
    plt.title("Revenue by Product Category")
    plt.xlabel("Category")
    plt.ylabel("Revenue")
    plt.tight_layout()
    path = OUTPUT_DIR / "revenue_by_category.png"
    plt.savefig(path, dpi=160)
    plt.close()
    chart_paths.append(path)

    region = df.groupby("region")["profit"].sum().sort_values(ascending=False)
    plt.figure(figsize=(8, 5))
    region.plot(kind="bar")
    plt.title("Profit by Region")
    plt.xlabel("Region")
    plt.ylabel("Profit")
    plt.tight_layout()
    path = OUTPUT_DIR / "profit_by_region.png"
    plt.savefig(path, dpi=160)
    plt.close()
    chart_paths.append(path)

    channel = df.groupby("sales_channel")["revenue"].sum().sort_values(ascending=False)
    plt.figure(figsize=(9, 5))
    channel.plot(kind="bar")
    plt.title("Revenue by Sales Channel")
    plt.xlabel("Sales Channel")
    plt.ylabel("Revenue")
    plt.tight_layout()
    path = OUTPUT_DIR / "revenue_by_channel.png"
    plt.savefig(path, dpi=160)
    plt.close()
    chart_paths.append(path)

    return chart_paths


def export_excel_dashboard(df: pd.DataFrame, kpis: dict) -> Path:
    """Export a multi-sheet Excel dashboard report."""
    excel_path = OUTPUT_DIR / "automated_sales_dashboard.xlsx"

    summary = pd.DataFrame([
        ["Total Revenue", round(kpis["total_revenue"], 2)],
        ["Total Profit", round(kpis["total_profit"], 2)],
        ["Total Orders", kpis["total_orders"]],
        ["Total Units Sold", kpis["total_units"]],
        ["Average Order Value", round(kpis["average_order_value"], 2)],
        ["Profit Margin %", round(kpis["profit_margin"], 2)],
        ["Best Category", kpis["best_category"]],
        ["Best Product", kpis["best_product"]],
        ["Best Sales Channel", kpis["best_channel"]],
    ], columns=["Metric", "Value"])

    monthly = df.groupby("month")[["revenue", "profit", "units_sold"]].sum().reset_index()
    category = df.groupby("category")[["revenue", "profit", "units_sold"]].sum().reset_index()
    region = df.groupby("region")[["revenue", "profit", "units_sold"]].sum().reset_index()
    top_products = df.groupby("product")[["revenue", "profit", "units_sold"]].sum().sort_values("revenue", ascending=False).head(10).reset_index()

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Executive Summary", index=False)
        monthly.to_excel(writer, sheet_name="Monthly Analysis", index=False)
        category.to_excel(writer, sheet_name="Category Analysis", index=False)
        region.to_excel(writer, sheet_name="Region Analysis", index=False)
        top_products.to_excel(writer, sheet_name="Top Products", index=False)
        df.to_excel(writer, sheet_name="Raw Data", index=False)

    return excel_path


def generate_pdf_report(kpis: dict, chart_paths: list[Path]) -> Path:
    """Generate a business-style PDF report with KPI summary and charts."""
    pdf_path = OUTPUT_DIR / "automated_sales_report.pdf"

    with PdfPages(pdf_path) as pdf:
        fig = plt.figure(figsize=(8.27, 11.69))
        fig.text(0.08, 0.93, "Automated E-Commerce Sales Report", fontsize=22, weight="bold")
        fig.text(0.08, 0.88, "Executive Summary", fontsize=16, weight="bold")

        lines = [
            f"Total Revenue: ${kpis['total_revenue']:,.2f}",
            f"Total Profit: ${kpis['total_profit']:,.2f}",
            f"Total Orders: {kpis['total_orders']}",
            f"Total Units Sold: {kpis['total_units']}",
            f"Average Order Value: ${kpis['average_order_value']:,.2f}",
            f"Profit Margin: {kpis['profit_margin']:.2f}%",
            f"Best Category: {kpis['best_category']}",
            f"Best Product: {kpis['best_product']}",
            f"Best Sales Channel: {kpis['best_channel']}",
            "",
            "Business Insight:",
            "This report helps track revenue, profit, product performance,",
            "sales channels, and regional performance automatically.",
        ]

        y = 0.82
        for line in lines:
            fig.text(0.08, y, line, fontsize=12)
            y -= 0.038

        plt.axis("off")
        pdf.savefig(fig)
        plt.close(fig)

        for chart_path in chart_paths:
            img = plt.imread(chart_path)
            fig = plt.figure(figsize=(11.69, 8.27))
            plt.imshow(img)
            plt.axis("off")
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    return pdf_path


def main() -> None:
    df = load_sales_data(DATA_PATH)
    kpis = calculate_kpis(df)
    chart_paths = create_charts(df)
    excel_path = export_excel_dashboard(df, kpis)
    pdf_path = generate_pdf_report(kpis, chart_paths)

    print("Automation completed successfully.")
    print(f"Excel dashboard created: {excel_path}")
    print(f"PDF report created: {pdf_path}")
    print("Charts saved in the output folder.")


if __name__ == "__main__":
    main()
