from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


plt.style.use("dark_background")

DATA_PATH = "sales_data.csv"
OUTPUT_DIR = Path("output")

OUTPUT_DIR.mkdir(exist_ok=True)

BACKGROUND = "#070B1A"
CARD_BG = "#0B1020"
GRID = "#2A334A"


def load_sales_data(path: str):
    df = pd.read_csv(path)

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    return df



def calculate_kpis(df):

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    total_orders = df["order_id"].nunique()
    total_units = df["units_sold"].sum()

    average_order_value = total_revenue / total_orders
    profit_margin = (total_profit / total_revenue) * 100

    best_category = (
        df.groupby("category")["revenue"]
        .sum()
        .idxmax()
    )

    best_product = (
        df.groupby("product")["revenue"]
        .sum()
        .idxmax()
    )

    best_channel = (
        df.groupby("sales_channel")["revenue"]
        .sum()
        .idxmax()
    )

    best_region = (
        df.groupby("region")["profit"]
        .sum()
        .idxmax()
    )

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
        "best_region": best_region
    }



def style_axis(ax):

    ax.set_facecolor(BACKGROUND)

    ax.grid(
        alpha=0.10,
        color="white",
        linestyle="--",
        linewidth=0.7
    )

    for spine in ax.spines.values():
        spine.set_color("#2E3445")

    ax.tick_params(colors="white", labelsize=11)

    ax.title.set_color("white")

    ax.set_axisbelow(True)



def create_bar_chart(
    labels,
    values,
    title,
    xlabel,
    ylabel,
    color,
    filename
):

    fig, ax = plt.subplots(figsize=(9, 4))

    fig.patch.set_facecolor(BACKGROUND)

    bars = ax.bar(
        labels,
        values,
        width=0.38,        
        color=color,
        edgecolor="white",
        linewidth=1.2,
        alpha=0.88
    )

    style_axis(ax)

    ax.set_title(
        title,
        fontsize=22,
        weight="bold",
        pad=18
    )

    ax.set_xlabel(
        xlabel,
        fontsize=12
    )

    ax.set_ylabel(
        ylabel,
        fontsize=12
    )

    ax.margins(x=0.15)

    plt.xticks(rotation=15)

    plt.tight_layout()

    path = OUTPUT_DIR / filename

    plt.savefig(
        path,
        dpi=300,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight"
    )

    plt.close()

    return path



def create_line_chart(df):

    monthly = (
        df.groupby("month")[["revenue", "profit"]]
        .sum()
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(9, 4))

    fig.patch.set_facecolor(BACKGROUND)

    ax.plot(
        monthly["month"],
        monthly["revenue"],
        color="#00E5FF",
        linewidth=2.2,
        marker="o",
        markersize=4,
        label="Revenue"
    )

    ax.plot(
        monthly["month"],
        monthly["profit"],
        color="#39FF14",
        linewidth=2.5,
        marker="o",
        markersize=5,
        label="Profit"
    )

    style_axis(ax)

    ax.legend()

    ax.set_title(
        "Monthly Revenue & Profit",
        fontsize=22,
        weight="bold",
        pad=18
    )

    plt.xticks(rotation=20)

    plt.tight_layout()

    path = OUTPUT_DIR / "monthly_analysis.png"

    plt.savefig(
        path,
        dpi=300,
        facecolor=fig.get_facecolor(),
        bbox_inches="tight"
    )

    plt.close()

    return path



def generate_charts(df):

    chart_paths = []

    category = (
        df.groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    chart_paths.append(
        create_bar_chart(
            category.index,
            category.values,
            "Revenue by Category",
            "Category",
            "Revenue",
            "#00E5FF",
            "category_chart.png"
        )
    )

    region = (
        df.groupby("region")["profit"]
        .sum()
        .sort_values(ascending=False)
    )

    chart_paths.append(
        create_bar_chart(
            region.index,
            region.values,
            "Profit by Region",
            "Region",
            "Profit",
            "#39FF14",
            "region_chart.png"
        )
    )

    channel = (
        df.groupby("sales_channel")["revenue"]
        .sum()
        .sort_values(ascending=False)
    )

    chart_paths.append(
        create_bar_chart(
            channel.index,
            channel.values,
            "Revenue by Sales Channel",
            "Channel",
            "Revenue",
            "#FF7A00",
            "channel_chart.png"
        )
    )

    chart_paths.append(
        create_line_chart(df)
    )

    return chart_paths



def generate_pdf(kpis, chart_paths):

    pdf_path = OUTPUT_DIR / "automated_sales_report.pdf"

    with PdfPages(str(pdf_path)) as pdf:

        
        fig = plt.figure(figsize=(11.69, 8.27))

        fig.patch.set_facecolor(BACKGROUND)

        plt.axis("off")

        plt.text(
            0.5,
            0.90,
            "AUTOMATED E-COMMERCE SALES REPORT",
            ha="center",
            fontsize=26,
            color="#00E5FF",
            weight="bold"
        )

        plt.text(
            0.5,
            0.84,
            "Executive Business Dashboard",
            ha="center",
            fontsize=16,
            color="white"
        )

        stats = [
            f"Total Revenue: ${kpis['total_revenue']:,.2f}",
            f"Total Profit: ${kpis['total_profit']:,.2f}",
            f"Orders: {kpis['total_orders']}",
            f"Profit Margin: {kpis['profit_margin']:.2f}%",
            f"Best Category: {kpis['best_category']}",
            f"Best Product: {kpis['best_product']}",
            f"Best Region: {kpis['best_region']}"
        ]

        y = 0.68

        for item in stats:
            plt.text(
                0.12,
                y,
                item,
                fontsize=17,
                color="white"
            )

            y -= 0.07

        plt.text(
            0.5,
            0.08,
            "Automate. Analyze. Report. Grow.",
            ha="center",
            fontsize=18,
            color="#39FF14",
            weight="bold"
        )

        pdf.savefig(fig, facecolor=fig.get_facecolor())

        plt.close()

        
        for chart in chart_paths:

            img = plt.imread(chart)

            fig = plt.figure(figsize=(11.69, 8.27))

            fig.patch.set_facecolor(BACKGROUND)

            plt.imshow(img)

            plt.axis("off")

            pdf.savefig(fig, facecolor=fig.get_facecolor())

            plt.close()

    return pdf_path



def main():

    print("Loading sales data...")

    df = load_sales_data(DATA_PATH)

    print("Calculating KPIs...")

    kpis = calculate_kpis(df)

    print("Generating charts...")

    chart_paths = generate_charts(df)

    print("Generating PDF report...")

    pdf_path = generate_pdf(kpis, chart_paths)

    print("\\nSUCCESS!")
    print(f"PDF REPORT: {pdf_path}")
    print(f"CHARTS SAVED IN: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()