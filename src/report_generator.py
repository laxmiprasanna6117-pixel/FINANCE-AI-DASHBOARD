import io
from datetime import datetime
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class FinancialReportGenerator:
    """
    Generates institutional-grade executive reports in PDF (ReportLab) and Excel (openpyxl).
    Styled with professional corporate light theme and navy blue accents.
    """

    def __init__(self, df, kpis, ai_insights, quality_report, time_series, category_data):
        self.df = df
        self.kpis = kpis
        self.ai = ai_insights
        self.quality = quality_report
        self.time_series = time_series
        self.category_data = category_data

    # =========================================================================
    # PDF REPORT GENERATOR (ReportLab)
    # =========================================================================
    def generate_pdf(self):
        """Builds a formatted multi-section PDF financial report in memory."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        NAVY = colors.HexColor('#0F2942')
        SLATE_BLUE = colors.HexColor('#1E3A8A')
        ACCENT_BLUE = colors.HexColor('#2563EB')
        DARK_TEXT = colors.HexColor('#1E293B')
        MUTED_TEXT = colors.HexColor('#64748B')
        LIGHT_BG = colors.HexColor('#F1F5F9')
        BORDER_COLOR = colors.HexColor('#CBD5E1')
        GREEN_ACCENT = colors.HexColor('#16A34A')
        RED_ACCENT = colors.HexColor('#DC2626')

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=NAVY
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=MUTED_TEXT
        )
        h1_style = ParagraphStyle(
            'SectionH1',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=13,
            leading=17,
            textColor=SLATE_BLUE,
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'DocBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=DARK_TEXT
        )
        body_bold = ParagraphStyle(
            'DocBodyBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=13,
            textColor=DARK_TEXT
        )
        callout_style = ParagraphStyle(
            'DocCallout',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14,
            textColor=NAVY
        )

        story = []

        # Header Title Banner
        story.append(Paragraph("FINANCIAL PERFORMANCE & INTELLIGENCE REPORT", title_style))
        report_date = datetime.now().strftime("%B %d, %Y - %H:%M UTC")
        story.append(Paragraph(f"Autonomous Financial Data Analysis & AI Insights Engine  |  Generated: {report_date}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=ACCENT_BLUE, spaceBefore=4, spaceAfter=14))

        # 1. Executive Summary Callout
        story.append(Paragraph("1. Executive Financial Narrative", h1_style))
        exec_text = self.ai.get('executive_summary', 'Financial analysis complete.')
        summary_table = Table([[Paragraph(exec_text, callout_style)]], colWidths=[530])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
            ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LEFTPADDING', (0,0), (-1,-1), 12),
            ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 12))

        # 2. Financial KPI Scorecard Table
        story.append(Paragraph("2. Financial KPI Scorecard", h1_style))
        k = self.kpis
        profit_color = GREEN_ACCENT if k['net_profit'] >= 0 else RED_ACCENT

        kpi_data = [
            [
                Paragraph("<b>Metric</b>", body_bold),
                Paragraph("<b>Calculated Value</b>", body_bold),
                Paragraph("<b>Operational Context</b>", body_bold)
            ],
            [
                Paragraph("Total Gross Revenue", body_style),
                Paragraph(f"${k['total_revenue']:,.2f}", body_bold),
                Paragraph("Total top-line inflows identified across records", body_style)
            ],
            [
                Paragraph("Total Expenditures", body_style),
                Paragraph(f"${k['total_expenses']:,.2f}", body_bold),
                Paragraph("Total operational and direct costs recognized", body_style)
            ],
            [
                Paragraph("Net Operating Profit", body_style),
                Paragraph(f"<font color='{profit_color.hexval()}'><b>${k['net_profit']:,.2f}</b></font>", body_bold),
                Paragraph("Net financial outcome (Revenue - Expenses)", body_style)
            ],
            [
                Paragraph("Net Profit Margin", body_style),
                Paragraph(f"{k['profit_margin_pct']:.1f}%", body_bold),
                Paragraph("Bottom-line profitability efficiency", body_style)
            ],
            [
                Paragraph("Transaction Volume", body_style),
                Paragraph(f"{k['total_transactions']:,}", body_bold),
                Paragraph("Valid transaction rows analyzed", body_style)
            ],
            [
                Paragraph("Average Transaction Value", body_style),
                Paragraph(f"${k['avg_transaction_value']:,.2f}", body_bold),
                Paragraph("Average volume per transaction line", body_style)
            ],
        ]

        if k.get('has_budget'):
            kpi_data.append([
                Paragraph("Budget Variance", body_style),
                Paragraph(f"${k['budget_variance']:,.2f} ({k['budget_variance_pct']:.1f}%)", body_bold),
                Paragraph("Difference between planned budget and actual expenses", body_style)
            ])

        kpi_table = Table(kpi_data, colWidths=[150, 130, 250])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 14))

        # 3. Category Breakdown Summary
        story.append(Paragraph("3. Category-Wise Financial Contribution", h1_style))
        rev_cats = self.category_data.get('revenue_categories', {})
        exp_cats = self.category_data.get('expense_categories', {})

        cat_rows = [[
            Paragraph("<b>Rank</b>", body_bold),
            Paragraph("<b>Top Revenue Categories</b>", body_bold),
            Paragraph("<b>Revenue Amount</b>", body_bold),
            Paragraph("<b>Top Expense Categories</b>", body_bold),
            Paragraph("<b>Expense Amount</b>", body_bold)
        ]]

        max_len = max(len(rev_cats.get('labels', [])), len(exp_cats.get('labels', [])))
        for i in range(min(6, max(1, max_len))):
            r_label = rev_cats.get('labels', [])[i] if i < len(rev_cats.get('labels', [])) else '-'
            r_val = f"${rev_cats.get('values', [])[i]:,.2f}" if i < len(rev_cats.get('values', [])) else '-'
            e_label = exp_cats.get('labels', [])[i] if i < len(exp_cats.get('labels', [])) else '-'
            e_val = f"${exp_cats.get('values', [])[i]:,.2f}" if i < len(exp_cats.get('values', [])) else '-'

            cat_rows.append([
                Paragraph(f"#{i+1}", body_style),
                Paragraph(str(r_label), body_style),
                Paragraph(r_val, body_bold),
                Paragraph(str(e_label), body_style),
                Paragraph(e_val, body_bold)
            ])

        cat_table = Table(cat_rows, colWidths=[35, 145, 110, 145, 95])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), SLATE_BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
        ]))
        story.append(cat_table)
        story.append(Spacer(1, 14))

        # 4. Strategic Risks & AI Observations
        story.append(Paragraph("4. AI Risk Radar & Anomaly Observations", h1_style))
        risks = self.ai.get('risks', [])

        risk_rows = [[
            Paragraph("<b>Severity</b>", body_bold),
            Paragraph("<b>Identified Risk Factor</b>", body_bold),
            Paragraph("<b>Data Evidence & Recommended Mitigation</b>", body_bold)
        ]]

        for r in risks[:4]:
            sev_color = RED_ACCENT if r['severity'] in ('Critical', 'High') else colors.HexColor('#D97706')
            risk_rows.append([
                Paragraph(f"<font color='{sev_color.hexval()}'><b>{r['severity']}</b></font>", body_bold),
                Paragraph(f"<b>{r['title']}</b>", body_bold),
                Paragraph(f"{r['description']}<br/><i>Mitigation:</i> {r['mitigation']}", body_style)
            ])

        risk_table = Table(risk_rows, colWidths=[65, 175, 290])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), NAVY),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 14))

        # 5. Data-Backed Actionable Recommendations
        story.append(Paragraph("5. Data-Backed Actionable Recommendations", h1_style))
        recs = self.ai.get('recommendations', [])
        
        rec_rows = [[
            Paragraph("<b>Pillar</b>", body_bold),
            Paragraph("<b>Strategic Initiative</b>", body_bold),
            Paragraph("<b>Target Impact</b>", body_bold),
            Paragraph("<b>Action Plan</b>", body_bold)
        ]]

        for rec in recs[:4]:
            rec_rows.append([
                Paragraph(rec['category'], body_bold),
                Paragraph(f"<b>{rec['title']}</b>", body_style),
                Paragraph(rec['impact'], body_style),
                Paragraph(rec['action'], body_style)
            ])

        rec_table = Table(rec_rows, colWidths=[90, 140, 130, 170])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), SLATE_BLUE),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
        ]))
        story.append(rec_table)

        doc.build(story)
        buffer.seek(0)
        return buffer

    # =========================================================================
    # EXCEL REPORT GENERATOR (OpenPyXL)
    # =========================================================================
    def generate_excel(self):
        """Builds a formatted multi-sheet Excel financial workbook in memory."""
        wb = Workbook()
        buffer = io.BytesIO()

        NAVY_FILL = PatternFill(start_color="0F2942", end_color="0F2942", fill_type="solid")
        SLATE_FILL = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        TITLE_FONT = Font(name="Calibri", size=16, bold=True, color="0F2942")
        SECTION_FONT = Font(name="Calibri", size=12, bold=True, color="1E3A8A")
        BOLD_FONT = Font(name="Calibri", size=11, bold=True, color="000000")
        REG_FONT = Font(name="Calibri", size=11, color="000000")
        MUTED_FONT = Font(name="Calibri", size=9, color="64748B", italic=True)

        THIN_BORDER = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # ---------------------------------------------------------------------
        # TAB 1: EXECUTIVE SUMMARY & KPIS
        # ---------------------------------------------------------------------
        ws_exec = wb.active
        ws_exec.title = "Executive Summary"
        ws_exec.views.sheetView[0].showGridLines = True

        ws_exec.cell(row=1, column=1, value="FINANCIAL ANALYSIS & INTELLIGENCE REPORT").font = TITLE_FONT
        ws_exec.cell(row=2, column=1, value=f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')} | Autonomous Analytics Engine").font = MUTED_FONT

        ws_exec.cell(row=4, column=1, value="Executive Narrative:").font = SECTION_FONT
        ws_exec.merge_cells("A5:H6")
        cell_nar = ws_exec.cell(row=5, column=1, value=self.ai.get('executive_summary', ''))
        cell_nar.font = REG_FONT
        cell_nar.alignment = Alignment(wrap_text=True, vertical="top")

        ws_exec.cell(row=8, column=1, value="Core Financial KPIs:").font = SECTION_FONT
        kpi_headers = ["Metric", "Amount / Value", "Operational Meaning"]
        for c_idx, h in enumerate(kpi_headers, 1):
            cell = ws_exec.cell(row=9, column=c_idx, value=h)
            cell.font = HEADER_FONT
            cell.fill = NAVY_FILL
            cell.alignment = Alignment(horizontal="left")

        k = self.kpis
        kpi_rows = [
            ("Total Gross Revenue", k['total_revenue'], "Top-line inflow across all recognized lines"),
            ("Total Expenditures", k['total_expenses'], "Total cost allocations and expenses"),
            ("Net Operating Profit", k['net_profit'], "Revenue minus expenses"),
            ("Profit Margin %", f"{k['profit_margin_pct']:.2f}%", "Profit efficiency ratio"),
            ("Transaction Count", k['total_transactions'], "Total rows parsed in dataset"),
            ("Average Transaction Value", k['avg_transaction_value'], "Average monetary value per entry")
        ]
        if k.get('has_budget'):
            kpi_rows.append(("Total Planned Budget", k['total_budget'], "Total allocated target budget"))
            kpi_rows.append(("Budget Variance", k['budget_variance'], "Budget minus actual expenses"))

        for r_idx, row in enumerate(kpi_rows, 10):
            ws_exec.cell(row=r_idx, column=1, value=row[0]).font = REG_FONT
            cell_val = ws_exec.cell(row=r_idx, column=2, value=row[1])
            cell_val.font = BOLD_FONT
            if isinstance(row[1], (int, float)):
                cell_val.number_format = '$#,##0.00'
            ws_exec.cell(row=r_idx, column=3, value=row[2]).font = MUTED_FONT

            for c in range(1, 4):
                ws_exec.cell(row=r_idx, column=c).border = THIN_BORDER

        ws_exec.cell(row=19, column=1, value="Data Quality & Integrity Scorecard:").font = SECTION_FONT
        q = self.quality
        q_rows = [
            ("Overall Data Quality Score", f"{q.get('quality_score', 0)} / 100"),
            ("Valid Rows Processed", q.get('cleaned_rows', 0)),
            ("Duplicates Removed", q.get('duplicates_removed', 0)),
            ("Missing Cell Rate", f"{q.get('missing_rate_pct', 0)}%"),
            ("Statistical Outliers Detected", q.get('outlier_count', 0))
        ]
        for r_idx, (m, v) in enumerate(q_rows, 20):
            ws_exec.cell(row=r_idx, column=1, value=m).font = REG_FONT
            ws_exec.cell(row=r_idx, column=2, value=v).font = BOLD_FONT
            for c in range(1, 3):
                ws_exec.cell(row=r_idx, column=c).border = THIN_BORDER

        for col in ws_exec.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_exec.column_dimensions[col_letter].width = max(14, min(50, max_len + 3))

        # ---------------------------------------------------------------------
        # TAB 2: CLEANED FINANCIAL DATA
        # ---------------------------------------------------------------------
        ws_data = wb.create_sheet(title="Cleaned Data")
        ws_data.views.sheetView[0].showGridLines = True

        export_df = self.df.copy()
        display_cols = [c for c in export_df.columns if not c.startswith('__')]
        standard_cols = ['__revenue', '__expense', '__profit', '__category']
        for sc in standard_cols:
            if sc in export_df.columns and sc not in display_cols:
                display_cols.append(sc)

        for c_idx, col_name in enumerate(display_cols, 1):
            clean_name = col_name.replace('__', '').title()
            cell = ws_data.cell(row=1, column=c_idx, value=clean_name)
            cell.font = HEADER_FONT
            cell.fill = SLATE_FILL
            cell.alignment = Alignment(horizontal="center")

        for r_idx, row in enumerate(export_df[display_cols].head(5000).itertuples(index=False), 2):
            for c_idx, val in enumerate(row, 1):
                cell = ws_data.cell(row=r_idx, column=c_idx)
                if pd.isna(val):
                    cell.value = ""
                elif isinstance(val, (int, float)):
                    cell.value = val
                    if 'rev' in display_cols[c_idx-1].lower() or 'exp' in display_cols[c_idx-1].lower() or 'prof' in display_cols[c_idx-1].lower():
                        cell.number_format = '$#,##0.00'
                else:
                    cell.value = str(val)
                cell.font = REG_FONT
                cell.border = THIN_BORDER

        for col in ws_data.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_data.column_dimensions[col_letter].width = max(12, min(35, max_len + 3))

        # ---------------------------------------------------------------------
        # TAB 3: CATEGORY ANALYSIS
        # ---------------------------------------------------------------------
        ws_cat = wb.create_sheet(title="Category Breakdown")
        ws_cat.views.sheetView[0].showGridLines = True

        ws_cat.cell(row=1, column=1, value="Revenue by Category").font = SECTION_FONT
        ws_cat.cell(row=2, column=1, value="Category").font = HEADER_FONT
        ws_cat.cell(row=2, column=1).fill = NAVY_FILL
        ws_cat.cell(row=2, column=2, value="Revenue Amount").font = HEADER_FONT
        ws_cat.cell(row=2, column=2).fill = NAVY_FILL

        rev_cats = self.category_data.get('revenue_categories', {})
        for r_idx, (cat, val) in enumerate(zip(rev_cats.get('labels', []), rev_cats.get('values', [])), 3):
            ws_cat.cell(row=r_idx, column=1, value=cat).font = REG_FONT
            cell_val = ws_cat.cell(row=r_idx, column=2, value=val)
            cell_val.font = BOLD_FONT
            cell_val.number_format = '$#,##0.00'
            ws_cat.cell(row=r_idx, column=1).border = THIN_BORDER
            ws_cat.cell(row=r_idx, column=2).border = THIN_BORDER

        ws_cat.cell(row=1, column=4, value="Expenses by Category").font = SECTION_FONT
        ws_cat.cell(row=2, column=4, value="Category").font = HEADER_FONT
        ws_cat.cell(row=2, column=4).fill = SLATE_FILL
        ws_cat.cell(row=2, column=5, value="Expense Amount").font = HEADER_FONT
        ws_cat.cell(row=2, column=5).fill = SLATE_FILL

        exp_cats = self.category_data.get('expense_categories', {})
        for r_idx, (cat, val) in enumerate(zip(exp_cats.get('labels', []), exp_cats.get('values', [])), 3):
            ws_cat.cell(row=r_idx, column=4, value=cat).font = REG_FONT
            cell_val = ws_cat.cell(row=r_idx, column=5, value=val)
            cell_val.font = BOLD_FONT
            cell_val.number_format = '$#,##0.00'
            ws_cat.cell(row=r_idx, column=4).border = THIN_BORDER
            ws_cat.cell(row=r_idx, column=5).border = THIN_BORDER

        for col in ws_cat.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_cat.column_dimensions[col_letter].width = max(14, min(35, max_len + 3))

        # ---------------------------------------------------------------------
        # TAB 4: TIME SERIES TRENDS
        # ---------------------------------------------------------------------
        ws_ts = wb.create_sheet(title="Time Trends")
        ws_ts.views.sheetView[0].showGridLines = True

        ts_headers = ["Period", "Revenue", "Expenses", "Net Profit", "Cumulative Revenue", "Cumulative Expenses"]
        for c_idx, h in enumerate(ts_headers, 1):
            cell = ws_ts.cell(row=1, column=c_idx, value=h)
            cell.font = HEADER_FONT
            cell.fill = NAVY_FILL
            cell.alignment = Alignment(horizontal="center")

        ts = self.time_series
        labels = ts.get('labels', [])
        revs = ts.get('revenue', [])
        exps = ts.get('expenses', [])
        profs = ts.get('profit', [])
        cum_revs = ts.get('cumulative_revenue', [])
        cum_exps = ts.get('cumulative_expenses', [])

        for r_idx in range(len(labels)):
            row_num = r_idx + 2
            ws_ts.cell(row=row_num, column=1, value=labels[r_idx]).font = REG_FONT
            for c_idx, val in enumerate([revs[r_idx], exps[r_idx], profs[r_idx], cum_revs[r_idx], cum_exps[r_idx]], 2):
                cell = ws_ts.cell(row=row_num, column=c_idx, value=val)
                cell.font = BOLD_FONT
                cell.number_format = '$#,##0.00'
                cell.border = THIN_BORDER
            ws_ts.cell(row=row_num, column=1).border = THIN_BORDER

        for col in ws_ts.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_ts.column_dimensions[col_letter].width = max(15, min(30, max_len + 3))

        # ---------------------------------------------------------------------
        # TAB 5: RISKS, ANOMALIES & RECOMMENDATIONS
        # ---------------------------------------------------------------------
        ws_ai = wb.create_sheet(title="AI Risk & Recommendations")
        ws_ai.views.sheetView[0].showGridLines = True

        ws_ai.cell(row=1, column=1, value="Strategic Recommendations").font = SECTION_FONT
        rec_headers = ["Pillar", "Initiative", "Target Impact", "Action Plan"]
        for c_idx, h in enumerate(rec_headers, 1):
            cell = ws_ai.cell(row=2, column=c_idx, value=h)
            cell.font = HEADER_FONT
            cell.fill = NAVY_FILL

        for r_idx, rec in enumerate(self.ai.get('recommendations', []), 3):
            ws_ai.cell(row=r_idx, column=1, value=rec['category']).font = BOLD_FONT
            ws_ai.cell(row=r_idx, column=2, value=rec['title']).font = REG_FONT
            ws_ai.cell(row=r_idx, column=3, value=rec['impact']).font = REG_FONT
            ws_ai.cell(row=r_idx, column=4, value=rec['action']).font = REG_FONT
            for c in range(1, 5):
                ws_ai.cell(row=r_idx, column=c).border = THIN_BORDER

        start_row = len(self.ai.get('recommendations', [])) + 5
        ws_ai.cell(row=start_row, column=1, value="Statistical Anomaly Audit Log").font = SECTION_FONT
        ano_headers = ["Date / ID", "Category", "Metric", "Amount", "Z-Score", "Severity", "Audit Reason"]
        for c_idx, h in enumerate(ano_headers, 1):
            cell = ws_ai.cell(row=start_row + 1, column=c_idx, value=h)
            cell.font = HEADER_FONT
            cell.fill = SLATE_FILL

        for r_idx, a in enumerate(self.ai.get('anomalies', []), start_row + 2):
            ws_ai.cell(row=r_idx, column=1, value=a['date']).font = REG_FONT
            ws_ai.cell(row=r_idx, column=2, value=a['category']).font = REG_FONT
            ws_ai.cell(row=r_idx, column=3, value=a['metric']).font = REG_FONT
            cell_amt = ws_ai.cell(row=r_idx, column=4, value=a['amount'])
            cell_amt.font = BOLD_FONT
            cell_amt.number_format = '$#,##0.00'
            ws_ai.cell(row=r_idx, column=5, value=a['z_score']).font = REG_FONT
            ws_ai.cell(row=r_idx, column=6, value=a['severity']).font = BOLD_FONT
            ws_ai.cell(row=r_idx, column=7, value=a['reason']).font = REG_FONT
            for c in range(1, 8):
                ws_ai.cell(row=r_idx, column=c).border = THIN_BORDER

        for col in ws_ai.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws_ai.column_dimensions[col_letter].width = max(14, min(45, max_len + 3))

        wb.save(buffer)
        buffer.seek(0)
        return buffer
