import csv
import datetime
import os
from collections import defaultdict

# --- Configuration ---
HOME_DIR = os.path.expanduser('~')
CSV_SUB_PATH = os.path.join('Solis', 'config', 'SolisManagerExecutionHistory.csv')
CSV_FILE_PATH = os.path.join(HOME_DIR, CSV_SUB_PATH)

DATE_FORMAT = '%d-%b-%Y %H:%M'
# Price threshold in POUNDS (e.g., 10.0 pence = 0.10 pounds)
PRICE_THRESHOLD_POUNDS = 0.10
EXPORT_CREDIT_RATE = 0.15  # £0.15 per kWh exported

# Column indices (0-based)
DATE_COL_IDX = 0
UNIT_PRICE_COL_IDX = 2 # This column contains PENCE
IMPORTED_KWH_COL_IDX = 8 # Import kWh
EXPORTED_KWH_COL_IDX = 9 # Export kWh
# --- End Configuration ---

def get_date_input(prompt):
    """Gets and validates date input from the user."""
    while True:
        date_str = input(prompt)
        try:
            dt_obj_date_only = datetime.datetime.strptime(date_str, '%d-%b-%Y')
            if "Start" in prompt:
                 return dt_obj_date_only.replace(hour=0, minute=0, second=0, microsecond=0)
            elif "End" in prompt:
                 return dt_obj_date_only.replace(hour=23, minute=59, second=59, microsecond=999999)
            else: # Should not happen
                 return dt_obj_date_only
        except ValueError:
            try:
                dt_obj = datetime.datetime.strptime(date_str, DATE_FORMAT)
                if "Start" in prompt:
                     return dt_obj.replace(hour=0, minute=0, second=0, microsecond=0)
                elif "End" in prompt:
                     return dt_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
                else: # Should not happen
                    return dt_obj
            except ValueError:
                print(f"Invalid date format. Please use 'dd-Mon-yyyy' or '{DATE_FORMAT}' (e.g., 25-Dec-2023 or 01-Jan-2024 08:00)")

def create_daily_summary_template():
    """Returns a dictionary template for storing daily results."""
    return {
        'total_imported_kwh': 0.0,
        'low_price_imported_kwh': 0.0,
        'high_price_imported_kwh': 0.0,
        'total_import_cost': 0.0,
        'low_price_import_cost': 0.0,
        'high_price_import_cost': 0.0,
        'total_exported_kwh': 0.0,
        'total_export_credit': 0.0,
        'final_billed_cost': 0.0,
        'rows_in_range': 0,
        'rows_in_range_low_price': 0,
        'rows_in_range_high_price': 0,
    }

def analyze_data_daily(file_path, start_date, end_date):
    """
    Reads the CSV, analyzes data, and returns daily summaries and overall stats.
    """
    daily_summaries = defaultdict(create_daily_summary_template)
    overall_stats = {
        'rows_processed': 0,
        'rows_skipped_errors': 0,
        'total_rows_in_range': 0,
        'rows_skipped_by_date': 0,
    }

    required_cols = [DATE_COL_IDX, UNIT_PRICE_COL_IDX, IMPORTED_KWH_COL_IDX, EXPORTED_KWH_COL_IDX]
    max_col_index = max(required_cols)

    print(f"Attempting to read file: {file_path}")

    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            print("File opened successfully.")

            header = None
            try:
                header = next(reader)
                print(f"Skipped header: {header}")
            except StopIteration:
                print("Warning: CSV file is empty.")
                return None, overall_stats
            except Exception as e:
                 print(f"Warning: Could not read header row. Assuming no header. Error: {e}")

            row_num = 1
            for row in reader:
                row_num += 1
                overall_stats['rows_processed'] += 1

                if len(row) <= max_col_index:
                    # Check if the row is just empty or whitespace before printing warning
                    if not any(field.strip() for field in row):
                         # print(f"Info: Row {row_num}: Skipping blank row.") # Optional: Info about blank rows
                         overall_stats['rows_skipped_errors'] += 1 # Count blank rows as errors for now
                         continue
                    print(f"Warning: Row {row_num}: Too short (needs {max_col_index+1} cols, has {len(row)}). Skipping: {row}")
                    overall_stats['rows_skipped_errors'] += 1
                    continue

                try:
                    date_str = row[DATE_COL_IDX].strip() # Add strip() for robustness
                    # Skip if date string is empty after stripping
                    if not date_str:
                         print(f"Warning: Row {row_num}: Empty date field. Skipping: {row}")
                         overall_stats['rows_skipped_errors'] += 1
                         continue

                    row_datetime = datetime.datetime.strptime(date_str, DATE_FORMAT)
                    row_date = row_datetime.date()

                    if not (start_date <= row_datetime <= end_date):
                        overall_stats['rows_skipped_by_date'] += 1
                        continue

                    day_summary = daily_summaries[row_date]
                    day_summary['rows_in_range'] += 1
                    overall_stats['total_rows_in_range'] += 1

                    # Add strip() and handle potential empty strings before float conversion
                    unit_price_str = row[UNIT_PRICE_COL_IDX].strip()
                    imported_kwh_str = row[IMPORTED_KWH_COL_IDX].strip()
                    exported_kwh_str = row[EXPORTED_KWH_COL_IDX].strip()

                    if not unit_price_str or not imported_kwh_str or not exported_kwh_str:
                         print(f"Warning: Row {row_num}: Empty numeric field. Skipping: {row}")
                         overall_stats['rows_skipped_errors'] += 1
                         # Decrement counters added optimistically before conversion
                         day_summary['rows_in_range'] -= 1
                         overall_stats['total_rows_in_range'] -= 1
                         continue


                    unit_price_pence = float(unit_price_str)
                    unit_price_pounds = unit_price_pence / 100.0
                    imported_kwh = float(imported_kwh_str)
                    exported_kwh = float(exported_kwh_str)

                    # Accumulate totals
                    day_summary['total_imported_kwh'] += imported_kwh
                    day_summary['total_exported_kwh'] += exported_kwh

                    row_import_cost = imported_kwh * unit_price_pounds
                    day_summary['total_import_cost'] += row_import_cost

                    # Categorize Import based on Price
                    if unit_price_pounds < PRICE_THRESHOLD_POUNDS:
                        day_summary['low_price_imported_kwh'] += imported_kwh
                        day_summary['low_price_import_cost'] += row_import_cost
                        day_summary['rows_in_range_low_price'] += 1
                    else: # Price is >= threshold
                        day_summary['high_price_imported_kwh'] += imported_kwh
                        day_summary['high_price_import_cost'] += row_import_cost
                        day_summary['rows_in_range_high_price'] += 1

                except ValueError as ve:
                    print(f"Warning: Row {row_num}: Parse error (ValueError: {ve}). Skipping: {row}")
                    overall_stats['rows_skipped_errors'] += 1
                    # Need to potentially undo increments if error happens after some increments
                    # Check if day_summary was already modified for this row before error
                    if row_date in daily_summaries and daily_summaries[row_date]['rows_in_range'] > 0:
                       # Safer to just skip, but could try rollback if needed
                       pass # For now, just count the error and continue
                    continue
                except IndexError:
                     print(f"Warning: Row {row_num}: Missing columns (IndexError). Check columns {DATE_COL_IDX}, {UNIT_PRICE_COL_IDX}, {IMPORTED_KWH_COL_IDX}, {EXPORTED_KWH_COL_IDX}. Skipping: {row}")
                     overall_stats['rows_skipped_errors'] += 1
                     continue

        # Calculate final derived values after processing all rows
        if not daily_summaries:
             print("No valid data found within the specified date range.")

        for day_date, day_summary in daily_summaries.items():
            day_summary['total_export_credit'] = day_summary['total_exported_kwh'] * EXPORT_CREDIT_RATE
            day_summary['final_billed_cost'] = day_summary['total_import_cost'] - day_summary['total_export_credit']

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print(f"Please ensure '~/{CSV_SUB_PATH}' exists.")
        return None, overall_stats
    except PermissionError:
        print(f"Error: Permission denied reading '{file_path}'.")
        return None, overall_stats
    except Exception as e:
        print(f"An unexpected error occurred during processing: {e}")
        import traceback
        traceback.print_exc()
        return None, overall_stats

    return daily_summaries, overall_stats

# --- Main Execution ---
if __name__ == "__main__":
    print("--- Solis Data Analysis (Daily Summary) ---")
    print(f"Expecting data file at: {CSV_FILE_PATH}")
    print(f"Using column indices: Date={DATE_COL_IDX}, Price={UNIT_PRICE_COL_IDX}, Import_kWh={IMPORTED_KWH_COL_IDX}, Export_kWh={EXPORTED_KWH_COL_IDX}")
    print(f"Low price threshold: < £{PRICE_THRESHOLD_POUNDS:.2f}/kWh")


    if not os.path.exists(CSV_FILE_PATH):
         print("\nError: Data file not found.")
         exit()
    else:
         print("Data file found.")

    start_date = get_date_input("Enter Start Date (dd-Mon-yyyy or dd-Mon-yyyy HH:MM): ")
    end_date = get_date_input("Enter End Date (dd-Mon-yyyy or dd-Mon-yyyy HH:MM):   ")

    if start_date > end_date:
        print("Error: Start date cannot be after end date. Exiting.")
        exit()

    print(f"\nAnalyzing data from {start_date.strftime('%d-%b-%Y %H:%M')} to {end_date.strftime('%d-%b-%Y %H:%M')}...")

    daily_results, overall_stats = analyze_data_daily(CSV_FILE_PATH, start_date, end_date)

    # --- Print Overall Processing Summary ---
    print("\n--- Processing Summary ---")
    print(f"Period Analyzed: {start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')}")
    print(f"Total Rows Processed:      {overall_stats['rows_processed']}")
    print(f"Total Rows In Date Range:  {overall_stats['total_rows_in_range']}")
    print(f"Rows Skipped (Errors):   {overall_stats['rows_skipped_errors']}")
    print(f"Rows Skipped (Date):     {overall_stats['rows_skipped_by_date']}")
    print("-" * 30)


    # --- Print Daily Summaries (Single Line Format with Low/High) ---
    if daily_results is not None:
        if not daily_results:
             print("No data rows found within the specified date range to summarize.")
        else:
            print("\n--- Daily Summaries ---")
            # Define Header Row - Expanded
            header_parts = [
                f"{'Date':<11}", f"{'Rows':>5}",
                f"{'ImpTot':>8}", f"{'ImpLo':>8}", f"{'ImpHi':>8}", # kWh
                f"{'CostTot':>8}", f"{'CostLo':>8}", f"{'CostHi':>8}", # Costs £
                f"{'ExpTot':>8}", f"{'ExpCred':>8}", # Export
                f"{'NetCost':>8}"  # Net
            ]
            header = " | ".join(header_parts)
            print(header)
            print("-" * len(header)) # Separator line

            # Sort the results by date before printing
            sorted_dates = sorted(daily_results.keys())

            # Initialize totals for summary row - Expanded
            grand_total = create_daily_summary_template() # Use template for totals too
            grand_total_rows = 0

            for day_date in sorted_dates:
                day_summary = daily_results[day_date]

                # Accumulate totals
                grand_total_rows += day_summary['rows_in_range']
                grand_total['total_imported_kwh'] += day_summary['total_imported_kwh']
                grand_total['low_price_imported_kwh'] += day_summary['low_price_imported_kwh']
                grand_total['high_price_imported_kwh'] += day_summary['high_price_imported_kwh']
                grand_total['total_import_cost'] += day_summary['total_import_cost']
                grand_total['low_price_import_cost'] += day_summary['low_price_import_cost']
                grand_total['high_price_import_cost'] += day_summary['high_price_import_cost']
                grand_total['total_exported_kwh'] += day_summary['total_exported_kwh']
                grand_total['total_export_credit'] += day_summary['total_export_credit']
                grand_total['final_billed_cost'] += day_summary['final_billed_cost']
                # Note: row counts for low/high price periods are not directly summed in the totals row display


                # Print daily data row using f-string formatting - Expanded
                data_parts = [
                    f"{day_date.strftime('%d-%b-%Y'):<11}", f"{day_summary['rows_in_range']:>5}",
                    f"{day_summary['total_imported_kwh']:>8.2f}", f"{day_summary['low_price_imported_kwh']:>8.2f}", f"{day_summary['high_price_imported_kwh']:>8.2f}",
                    f"{day_summary['total_import_cost']:>8.2f}", f"{day_summary['low_price_import_cost']:>8.2f}", f"{day_summary['high_price_import_cost']:>8.2f}",
                    f"{day_summary['total_exported_kwh']:>8.2f}", f"{day_summary['total_export_credit']:>8.2f}",
                    f"{day_summary['final_billed_cost']:>8.2f}"
                ]
                print(" | ".join(data_parts))


            # Print Totals Row - Expanded
            print("-" * len(header)) # Separator line
            total_parts = [
                 f"{'TOTALS':<11}", f"{grand_total_rows:>5}",
                 f"{grand_total['total_imported_kwh']:>8.2f}", f"{grand_total['low_price_imported_kwh']:>8.2f}", f"{grand_total['high_price_imported_kwh']:>8.2f}",
                 f"{grand_total['total_import_cost']:>8.2f}", f"{grand_total['low_price_import_cost']:>8.2f}", f"{grand_total['high_price_import_cost']:>8.2f}",
                 f"{grand_total['total_exported_kwh']:>8.2f}", f"{grand_total['total_export_credit']:>8.2f}",
                 f"{grand_total['final_billed_cost']:>8.2f}"
            ]
            print(" | ".join(total_parts))


    else:
        print("\nDaily analysis could not be completed due to errors.")


    print("\n--- End of Report ---")