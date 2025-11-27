#!/usr/bin/env python3
"""
CSV to Bank Statement Converter
Converts the sample financial transactions CSV into a formatted text file
that resembles a bank statement for document parser testing.
"""

import pandas as pd
import os
from datetime import datetime

def create_bank_statement():
    """Convert CSV to formatted bank statement text"""

    # Read the CSV file
    csv_file = 'sample_financial_transactions.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return

    df = pd.read_csv(csv_file)

    # Create bank statement header
    statement = []
    statement.append("=" * 80)
    statement.append("                    HDFC BANK STATEMENT")
    statement.append("                    Account: XXXX-XXXX-1234")
    statement.append(f"                    Period: {df['Date'].min()} to {df['Date'].max()}")
    statement.append("=" * 80)
    statement.append("")

    # Group by date and format transactions
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date', ascending=False)

    current_date = None
    for _, row in df.iterrows():
        date_str = row['Date'].strftime('%d/%m/%Y')

        if current_date != date_str:
            if current_date is not None:
                statement.append("")
            statement.append(f"Date: {date_str}")
            statement.append("-" * 50)
            current_date = date_str

        # Format transaction line
        amount = f"₹{row['Amount']:,.2f}"
        desc = row['Description'][:50]  # Truncate long descriptions

        # Right-align amount for expenses, left-align for income
        if row['Type'] == 'expense':
            line = f"  {desc:<50} {amount:>12}"
        else:
            line = f"+ {desc:<50} {amount:>12}"

        statement.append(line)

    # Add summary
    statement.append("")
    statement.append("=" * 80)
    total_expenses = df[df['Type'] == 'expense']['Amount'].sum()
    total_income = df[df['Type'] == 'income']['Amount'].sum()
    net_balance = total_income - total_expenses

    statement.append("SUMMARY:")
    statement.append("-" * 80)
    statement.append(f"Total Income:     ₹{total_income:,.2f}")
    statement.append(f"Total Expenses:   ₹{total_expenses:,.2f}")
    statement.append(f"Net Balance:      ₹{net_balance:,.2f}")
    statement.append("=" * 80)

    # Save to text file
    output_file = 'sample_bank_statement.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(statement))

    print(f"✅ Bank statement created: {output_file}")
    print(f"📊 Contains {len(df)} transactions")
    print(".2f")
    print(".2f")
    print(".2f")

    return output_file

if __name__ == "__main__":
    create_bank_statement()