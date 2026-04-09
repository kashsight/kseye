"""
ks-eye Data Processing Engine — FULLY OFFLINE
CSV/Excel import, data validation, cross-tabulation, auto-coding, ASCII charts
No AI required. Optional AI enhancement when tgpt is available.
"""

import csv
import io
import os
import json
import math
from collections import defaultdict, Counter
from datetime import datetime


# ════════════════════════════════════════════════════════════
#  CSV / EXCEL IMPORT
# ════════════════════════════════════════════════════════════

class DataImport:
    """Import data from CSV, TSV, or raw text — fully offline"""

    @staticmethod
    def from_csv_string(csv_text, delimiter=None):
        """Parse CSV text into structured data"""
        if not csv_text.strip():
            return {"status": "error", "message": "Empty CSV data"}

        # Auto-detect delimiter
        if not delimiter:
            sample = csv_text[:1000]
            if "\t" in sample:
                delimiter = "\t"
            elif ";" in sample and "," not in sample:
                delimiter = ";"
            else:
                delimiter = ","

        try:
            reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
            rows = []
            for row in reader:
                # Clean keys and values
                clean_row = {}
                for k, v in row.items():
                    key = k.strip() if k else ""
                    if key:
                        clean_row[key] = v.strip() if v else ""
                if clean_row:
                    rows.append(clean_row)

            if not rows:
                return {"status": "error", "message": "No data rows found"}

            return {
                "status": "ok",
                "row_count": len(rows),
                "columns": list(rows[0].keys()),
                "data": rows,
                "sample": rows[:3],
            }
        except Exception as e:
            return {"status": "error", "message": f"CSV parse error: {e}"}

    @staticmethod
    def from_csv_file(filepath, delimiter=None):
        """Import from CSV file"""
        if not os.path.exists(filepath):
            return {"status": "error", "message": f"File not found: {filepath}"}
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                csv_text = f.read()
            return DataImport.from_csv_string(csv_text, delimiter)
        except Exception as e:
            return {"status": "error", "message": f"File read error: {e}"}

    @staticmethod
    def from_json_string(json_text):
        """Parse JSON data into standardized format"""
        if not json_text.strip():
            return {"status": "error", "message": "Empty JSON data"}
        try:
            data = json.loads(json_text)
            return DataImport._normalize_json(data)
        except json.JSONDecodeError as e:
            return {"status": "error", "message": f"JSON parse error: {e}"}

    @staticmethod
    def _normalize_json(data):
        """Convert various JSON formats to standard rows"""
        rows = []

        if isinstance(data, list):
            # List of dicts
            rows = data
        elif isinstance(data, dict):
            if "responses" in data:
                rows = data["responses"]
            elif "data" in data:
                rows = data["data"]
            elif "rows" in data:
                rows = data["rows"]
            else:
                # Single object — wrap in list
                rows = [data]

        if not rows:
            return {"status": "error", "message": "No data found in JSON"}

        # Flatten nested dicts for column access
        flat_rows = []
        for row in rows:
            flat = DataImport._flatten(row)
            flat_rows.append(flat)

        columns = list(flat_rows[0].keys()) if flat_rows else []
        return {
            "status": "ok",
            "row_count": len(flat_rows),
            "columns": columns,
            "data": flat_rows,
            "sample": flat_rows[:3],
        }

    @staticmethod
    def _flatten(obj, prefix=""):
        """Flatten nested dict to dot-notation keys"""
        items = {}
        if isinstance(obj, dict):
            for k, v in obj.items():
                new_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    items.update(DataImport._flatten(v, new_key))
                else:
                    items[new_key] = v
        else:
            items[prefix] = obj
        return items


# ════════════════════════════════════════════════════════════
#  DATA VALIDATION ENGINE — FULLY OFFLINE
# ════════════════════════════════════════════════════════════

class DataValidator:
    """Validates data quality before analysis — no AI needed"""

    def __init__(self, data, columns=None):
        self.data = data
        self.columns = columns or (data[0].keys() if data else [])
        self.issues = []
        self.warnings = []
        self.info = []

    def run_all_checks(self):
        """Run all validation checks"""
        self.check_empty_dataset()
        self.check_missing_columns()
        self.check_empty_cells()
        self.check_duplicate_rows()
        self.check_column_completeness()
        self.check_constant_columns()
        self.check_numeric_columns()
        self.check_response_distribution()
        return self.get_report()

    def check_empty_dataset(self):
        if not self.data:
            self.issues.append("CRITICAL: Dataset is empty")

    def check_missing_columns(self):
        if not self.data:
            return
        expected = set(self.columns)
        for i, row in enumerate(self.data):
            missing = expected - set(row.keys())
            if missing:
                self.warnings.append(f"Row {i+1}: missing columns: {', '.join(missing)}")

    def check_empty_cells(self):
        empty_counts = {}
        for col in self.columns:
            count = sum(1 for row in self.data if str(row.get(col, "")).strip() == "")
            if count > 0:
                empty_counts[col] = count
                pct = count / len(self.data) * 100
                if pct > 50:
                    self.issues.append(f"Column '{col}': {count}/{len(self.data)} empty cells ({pct:.1f}%)")
                elif pct > 20:
                    self.warnings.append(f"Column '{col}': {count}/{len(self.data)} empty cells ({pct:.1f}%)")
                else:
                    self.info.append(f"Column '{col}': {count} empty cells ({pct:.1f}%)")

    def check_duplicate_rows(self):
        if not self.data:
            return
        seen = {}
        for i, row in enumerate(self.data):
            key = json.dumps(row, sort_keys=True)
            if key in seen:
                self.warnings.append(f"Duplicate rows: row {i+1} matches row {seen[key]+1}")
            else:
                seen[key] = i

    def check_column_completeness(self):
        if not self.data:
            return
        for col in self.columns:
            filled = sum(1 for row in self.data if str(row.get(col, "")).strip() != "")
            pct = filled / len(self.data) * 100
            if pct < 10:
                self.issues.append(f"Column '{col}': only {pct:.0f}% populated — consider removing")

    def check_constant_columns(self):
        if not self.data:
            return
        for col in self.columns:
            values = set(str(row.get(col, "")).strip() for row in self.data)
            if len(values) == 1:
                self.info.append(f"Column '{col}': constant value '{values.pop()}' — no variation")

    def check_numeric_columns(self):
        if not self.data:
            return
        for col in self.columns:
            values = [row.get(col, "") for row in self.data if str(row.get(col, "")).strip()]
            numeric_count = 0
            for v in values:
                try:
                    float(v)
                    numeric_count += 1
                except (ValueError, TypeError):
                    pass
            if numeric_count > len(values) * 0.8 and len(values) > 2:
                self.info.append(f"Column '{col}': appears numeric ({numeric_count}/{len(values)} values)")

    def check_response_distribution(self):
        """Check if response IDs are unique"""
        id_cols = [c for c in self.columns if "id" in c.lower() or "respondent" in c.lower()]
        for col in id_cols:
            values = [str(row.get(col, "")).strip() for row in self.data]
            unique = len(set(values))
            if unique < len(values):
                self.warnings.append(f"ID column '{col}': {len(values)-unique} duplicate IDs")

    def get_report(self):
        quality_score = 100
        quality_score -= len(self.issues) * 15
        quality_score -= len(self.warnings) * 5
        quality_score = max(0, min(100, quality_score))

        return {
            "quality_score": quality_score,
            "row_count": len(self.data),
            "column_count": len(self.columns),
            "issues": self.issues,
            "warnings": self.warnings,
            "info": self.info,
            "rating": "Excellent" if quality_score >= 90 else
                      "Good" if quality_score >= 70 else
                      "Fair" if quality_score >= 50 else
                      "Poor",
        }


# ════════════════════════════════════════════════════════════
#  CROSS-TABULATION ENGINE — FULLY OFFLINE
# ════════════════════════════════════════════════════════════

class CrossTabulator:
    """Cross-tabulation analysis — no AI needed"""

    def __init__(self, data):
        self.data = data

    def cross_tab(self, row_col, col_col, value_col=None):
        """
        Create cross-tabulation of two columns

        Args:
            row_col: Column name for rows
            col_col: Column name for columns
            value_col: If given, count/aggregate this; otherwise count occurrences

        Returns:
            Cross-tabulation result dict
        """
        table = defaultdict(lambda: defaultdict(int))
        row_totals = defaultdict(int)
        col_totals = defaultdict(int)
        total = 0

        for row in self.data:
            r_val = str(row.get(row_col, "Unknown")).strip()
            c_val = str(row.get(col_col, "Unknown")).strip()
            if not r_val:
                r_val = "(empty)"
            if not c_val:
                c_val = "(empty)"

            if value_col:
                try:
                    val = float(row.get(value_col, 0))
                except (ValueError, TypeError):
                    val = 1
            else:
                val = 1

            table[r_val][c_val] += val
            row_totals[r_val] += val
            col_totals[c_val] += val
            total += val

        # Build percentage table
        pct_table = defaultdict(lambda: defaultdict(float))
        for r in table:
            for c in table[r]:
                pct_table[r][c] = (table[r][c] / row_totals[r] * 100) if row_totals[r] > 0 else 0

        # Chi-square approximation (simplified)
        chi_sq = 0
        for r in table:
            for c in table[r]:
                expected = (row_totals[r] * col_totals[c]) / total if total > 0 else 0
                if expected > 0:
                    chi_sq += (table[r][c] - expected) ** 2 / expected

        return {
            "row_column": row_col,
            "col_column": col_col,
            "counts": dict(table),
            "percentages": dict(pct_table),
            "row_totals": dict(row_totals),
            "col_totals": dict(col_totals),
            "grand_total": total,
            "chi_square": round(chi_sq, 2),
            "row_categories": len(table),
            "col_categories": len(col_totals),
        }

    def auto_cross_tabs(self, demographic_cols, question_cols, top_n=5):
        """Generate cross-tabs for all demographic × question combinations"""
        results = []
        for demo in demographic_cols[:5]:
            for q in question_cols[:top_n]:
                ct = self.cross_tab(demo, q)
                if ct["row_categories"] > 1 and ct["col_categories"] > 1:
                    results.append(ct)
        return results


# ════════════════════════════════════════════════════════════
#  AUTO-CODING OF OPEN-ENDED RESPONSES — OFFLINE + OPTIONAL AI
# ════════════════════════════════════════════════════════════

class AutoCoder:
    """
    Automatically code open-ended responses into themes.
    Works fully offline with pattern matching.
    Enhanced with AI when tgpt is available.
    """

    def __init__(self):
        # Common theme keywords (offline pattern matching)
        self.theme_keywords = {
            "access_issues": ["access", "internet", "connection", "wifi", "data", "network", "device", "phone", "computer", "laptop"],
            "satisfaction": ["satisfied", "happy", "good", "excellent", "great", "love", "enjoy", "like", "useful", "helpful"],
            "dissatisfaction": ["dissatisfied", "bad", "poor", "terrible", "hate", "dislike", "frustrating", "difficult", "confusing"],
            "cost_concerns": ["cost", "expensive", "price", "money", "affordable", "cheap", "free", "budget", "pay", "fee"],
            "time_management": ["time", "schedule", "busy", "deadline", "late", "hours", "when", "morning", "evening", "weekend"],
            "learning_quality": ["learn", "understand", "comprehend", "knowledge", "skill", "improve", "better", "effective", "quality"],
            "teacher_support": ["teacher", "instructor", "professor", "support", "help", "guidance", "feedback", "tutor"],
            "technical_issues": ["error", "crash", "bug", "slow", "freeze", "problem", "issue", "broken", "not working", "fail"],
            "motivation": ["motivated", "motivation", "interest", "engaged", "boring", "exciting", "inspire", "encourage"],
            "social_interaction": ["group", "team", "collaborate", "peer", "discuss", "together", "social", "communication", "interaction"],
        }

    def code_responses(self, responses, column_name, use_ai=False):
        """
        Code open-ended responses into themes

        Args:
            responses: List of response texts
            column_name: Name of the response column
            use_ai: If True and tgpt available, use AI for better coding

        Returns:
            Coding results dict
        """
        # Filter out empty responses
        valid = [(i, r) for i, r in enumerate(responses) if str(r).strip()]
        if not valid:
            return {"status": "error", "message": "No valid responses to code"}

        # Offline pattern-based coding
        code_counts = defaultdict(int)
        coded_responses = []

        for idx, text in valid:
            text_lower = str(text).lower()
            assigned_codes = []

            for theme, keywords in self.theme_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    assigned_codes.append(theme)
                    code_counts[theme] += 1

            if not assigned_codes:
                assigned_codes.append("other")
                code_counts["other"] += 1

            coded_responses.append({
                "index": idx,
                "text": str(text)[:200],
                "codes": assigned_codes,
            })

        # AI enhancement (optional)
        ai_themes = {}
        if use_ai:
            ai_themes = self._ai_enhance_coding(responses, code_counts)

        # Build codebook
        codebook = {}
        for theme, count in sorted(code_counts.items(), key=lambda x: -x[1]):
            # Find example responses
            examples = [
                cr["text"] for cr in coded_responses
                if theme in cr["codes"]
            ][:3]

            codebook[theme] = {
                "count": count,
                "percentage": count / len(valid) * 100,
                "examples": examples,
                "ai_description": ai_themes.get(theme, ""),
            }

        return {
            "status": "ok",
            "total_responses": len(valid),
            "empty_responses": len(responses) - len(valid),
            "code_count": len(code_counts),
            "codebook": codebook,
            "coded_responses": coded_responses,
            "method": "ai_enhanced" if use_ai else "pattern_matching",
        }

    def _ai_enhance_coding(self, responses, existing_codes):
        """Use AI to generate theme descriptions and discover missed themes"""
        try:
            from ks_eye.engines.tgpt_engine import run_tgpt
            sample = "\n".join([f"- {r}" for r in list(responses)[:15]])

            prompt = (
                "I have these open-ended survey responses:\n{}\n\n"
                "The following themes were detected by pattern matching: {}\n\n"
                "For each theme, provide a 1-sentence description of what it means in this context. "
                "Also suggest any additional themes you notice that might have been missed.\n"
                "Format: theme_name: description"
            ).format(sample, ", ".join(existing_codes.keys()))

            result = run_tgpt(message=prompt, provider="sky", timeout=30)
            if result:
                themes = {}
                for line in result.split("\n"):
                    if ":" in line:
                        parts = line.split(":", 1)
                        themes[parts[0].strip().lower().replace(" ", "_")] = parts[1].strip()
                return themes
        except Exception:
            pass
        return {}


# ════════════════════════════════════════════════════════════
#  ASCII CHART VISUALIZATIONS — FULLY OFFLINE
# ════════════════════════════════════════════════════════════

class ASCIICharts:
    """Generate text-based charts — no AI needed"""

    @staticmethod
    def bar_chart(data, title="", width=60, sort=True):
        """
        Create ASCII horizontal bar chart

        Args:
            data: Dict of {label: value} or list of (label, value) tuples
            title: Chart title
            width: Maximum width
            sort: Sort by value descending
        """
        if isinstance(data, dict):
            items = list(data.items())
        else:
            items = list(data)

        if sort:
            items.sort(key=lambda x: x[1], reverse=True)

        if not items:
            return ""

        max_val = max(v for _, v in items) if items else 1
        if max_val == 0:
            max_val = 1

        max_label = max(len(str(k)) for k, _ in items)

        lines = []
        if title:
            lines.append(f"  {title}")
            lines.append(f"  {'─' * (max_label + width + 15)}")

        for label, value in items:
            bar_len = int(value / max_val * (width - max_label - 10))
            bar_len = max(1, bar_len)
            bar = "█" * bar_len
            pct = f"{value:.0f}" if isinstance(value, (int, float)) else str(value)
            label_str = str(label).ljust(max_label)
            lines.append(f"  {label_str} │{bar} {pct}")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def likert_chart(data, title="", width=50):
        """
        Create diverging Likert scale bar chart

        Args:
            data: Dict with negative values on left, positive on right
                  e.g., {"Strongly Disagree": -12, "Disagree": -8, "Neutral": 0, "Agree": 25, "Strongly Agree": 15}
        """
        lines = []
        if title:
            lines.append(f"  {title}")
            lines.append(f"  {'─' * (width * 2 + 20)}")

        max_val = max(abs(v) for v in data.values()) if data.values() else 1
        if max_val == 0:
            max_val = 1

        # Sort: negative first, then zero, then positive
        neg = [(k, v) for k, v in data.items() if v < 0]
        pos = [(k, v) for k, v in data.items() if v > 0]
        neutral = [(k, v) for k, v in data.items() if v == 0]

        for label, value in neg + neutral + pos:
            bar_len = int(abs(value) / max_val * width)
            bar_len = max(1, bar_len)
            if value < 0:
                bar = "░" * bar_len
                display = f"{bar} {abs(value)}"
            elif value > 0:
                bar = "█" * bar_len
                display = f"{' ' * (width - bar_len)}{bar} {value}"
            else:
                display = f"{' ' * (width // 2 - 2)}┃{' ' * (width // 2 - 2)} {value}"

            label_str = str(label)[:20].ljust(20)
            lines.append(f"  {label_str} │{display}")

        # Center line
        center = width + 21
        lines.append(f"  {' ' * 20} ┃")
        lines.append(f"  {' ' * 20} │{' ' * (width // 2 - 3)} Negative    Positive {' ' * (width // 2 - 3)}")
        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def pie_chart(data, title="", size=20):
        """
        Create ASCII pie chart approximation

        Args:
            data: Dict of {label: value}
            title: Chart title
            size: Radius (character count)
        """
        total = sum(data.values())
        if total == 0:
            return ""

        lines = []
        if title:
            lines.append(f"  {title}")
            lines.append("")

        # Sort by value
        items = sorted(data.items(), key=lambda x: x[1], reverse=True)

        # Legend
        chars = "█▓▒░╬╫╪┼"
        for i, (label, value) in enumerate(items):
            pct = value / total * 100
            char = chars[i % len(chars)]
            lines.append(f"  {char} {label:<25s} {pct:5.1f}%  ({value})")

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def trend_line(data_points, title="", width=50, height=10):
        """
        Create ASCII trend/sparkline

        Args:
            data_points: List of numeric values over time
            title: Chart title
            width: Chart width
            height: Chart height in characters
        """
        if not data_points or len(data_points) < 2:
            return ""

        lines = []
        if title:
            lines.append(f"  {title}")
            lines.append(f"  {'─' * (width + 10)}")

        min_val = min(data_points)
        max_val = max(data_points)
        range_val = max_val - min_val if max_val != min_val else 1

        # Create grid
        grid = [[" " for _ in range(width)] for _ in range(height)]

        # Plot points
        step = max(1, len(data_points) // width)
        for i, val in enumerate(data_points[::step]):
            if i >= width:
                break
            y = height - 1 - int((val - min_val) / range_val * (height - 1))
            y = max(0, min(height - 1, y))
            grid[y][i] = "●"

        # Draw connecting lines
        prev_y = None
        for i in range(width):
            # Find the point in this column
            for row in range(height):
                if grid[row][i] == "●":
                    if prev_y is not None and prev_y != row:
                        # Draw vertical line
                        start = min(prev_y, row)
                        end = max(prev_y, row)
                        for r in range(start + 1, end):
                            if grid[r][i] == " ":
                                grid[r][i] = "│"
                    prev_y = row
                    break

        # Render
        max_val_label = f"{max_val:.0f}"
        min_val_label = f"{min_val:.0f}"
        for row in range(height):
            if row == 0:
                label = max_val_label.rjust(6)
            elif row == height - 1:
                label = min_val_label.rjust(6)
            else:
                label = " " * 6
            line = "".join(grid[row])
            lines.append(f"  {label} │{line}")

        # X axis
        lines.append(f"  {' ' * 6} └{'─' * width}")

        # X labels
        if len(data_points) >= 2:
            x_label = f"  {' ' * 6}  {data_points[0]:.0f}{' ' * (width - len(str(data_points[0])) - len(str(data_points[-1])))}{data_points[-1]:.0f}"
            lines.append(x_label)

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def frequency_table(data, title="", show_pct=True):
        """Create formatted frequency table"""
        if isinstance(data, dict):
            items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        else:
            items = data

        total = sum(v for _, v in items)
        if total == 0:
            return ""

        lines = []
        if title:
            lines.append(f"  {title}")

        max_label = max(len(str(k)) for k, _ in items)
        header = f"  {'Category':<{max_label}}  {'Count':>6}  {'%':>6}  {'Bar':<30}"
        lines.append(f"  {'─' * (max_label + 50)}")
        lines.append(header)
        lines.append(f"  {'─' * (max_label + 50)}")

        for label, count in items:
            pct = count / total * 100
            bar_len = int(pct / 2)
            bar = "█" * bar_len + "░" * (50 - bar_len)
            lines.append(f"  {str(label):<{max_label}}  {count:>6}  {pct:>5.1f}%  {bar}")

        lines.append(f"  {'─' * (max_label + 50)}")
        lines.append(f"  {'Total':<{max_label}}  {total:>6}  100.0%")
        lines.append("")
        return "\n".join(lines)


# ════════════════════════════════════════════════════════════
#  STATISTICAL SUMMARY — FULLY OFFLINE
# ════════════════════════════════════════════════════════════

class Statistics:
    """Basic statistical functions — no AI needed"""

    @staticmethod
    def describe(values):
        """Descriptive statistics for numeric data"""
        nums = []
        for v in values:
            try:
                nums.append(float(v))
            except (ValueError, TypeError):
                pass

        if not nums:
            return {"count": 0}

        nums.sort()
        n = len(nums)
        mean = sum(nums) / n
        variance = sum((x - mean) ** 2 for x in nums) / n if n > 0 else 0
        std = math.sqrt(variance)

        return {
            "count": n,
            "mean": round(mean, 2),
            "median": round(nums[n // 2], 2) if n % 2 == 1 else round((nums[n // 2 - 1] + nums[n // 2]) / 2, 2),
            "std_dev": round(std, 2),
            "min": round(nums[0], 2),
            "max": round(nums[-1], 2),
            "range": round(nums[-1] - nums[0], 2),
            "q1": round(nums[n // 4], 2),
            "q3": round(nums[3 * n // 4], 2),
        }

    @staticmethod
    def frequency_distribution(values, bins=10):
        """Create frequency distribution"""
        nums = []
        for v in values:
            try:
                nums.append(float(v))
            except (ValueError, TypeError):
                pass

        if not nums:
            return {}

        min_val = min(nums)
        max_val = max(nums)
        if min_val == max_val:
            return {str(min_val): len(nums)}

        bin_width = (max_val - min_val) / bins
        dist = defaultdict(int)

        for v in nums:
            bin_idx = min(int((v - min_val) / bin_width), bins - 1)
            bin_label = f"{min_val + bin_idx * bin_width:.1f}-{min_val + (bin_idx + 1) * bin_width:.1f}"
            dist[bin_label] += 1

        return dict(dist)
