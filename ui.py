from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich import box
from rich.columns import Columns
from typing import List, Dict, Any
import time

console = Console()


def display_header():
    """Display the application header."""
    header_text = """
    ╭─────────────────────────────────────────────╮
    │         AI Resume Shortlister               │
    │     Powered by Groq ⚡ Qwen 3.8            │
    ╰─────────────────────────────────────────────╯
    """
    console.print(header_text, style="bold blue")


def show_processing_progress(num_resumes: int):
    """Show processing progress animation."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Processing {task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"{num_resumes} resumes with AI...", total=None)

        # Simulate some processing time for visual effect
        for i in range(10):
            time.sleep(0.3)
            progress.update(
                task, description=f"{num_resumes} resumes with AI... {i * 10}% complete"
            )

        return progress


def get_score_color(score: int, max_score: int = 10) -> str:
    """Get color based on score value."""
    percentage = score / max_score
    if percentage >= 0.8:
        return "green"
    elif percentage >= 0.6:
        return "yellow"
    elif percentage >= 0.4:
        return "orange3"
    else:
        return "red"


def get_total_score_color(score: int, max_score: int = 50) -> str:
    """Get color for total score."""
    percentage = score / max_score
    if percentage >= 0.8:
        return "bright_green"
    elif percentage >= 0.7:
        return "green"
    elif percentage >= 0.6:
        return "yellow"
    elif percentage >= 0.5:
        return "orange3"
    else:
        return "red"




def display_results_table(candidates: List[Dict[str, Any]]):
    """Display results in a beautiful table."""
    if not candidates:
        console.print("[red]No candidates found in evaluation results.[/red]")
        return

    # Sort by total score (descending)
    sorted_candidates = sorted(
        candidates, key=lambda x: x.get("total_score", 0), reverse=True
    )

    # Create main results table
    table = Table(
        title="🏆 Resume Evaluation Results",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )

    table.add_column("Rank", style="bold", width=6)
    table.add_column("Candidate", style="bold cyan", width=20)
    table.add_column("Technical\nSkills", justify="center", width=10)
    table.add_column("Experience", justify="center", width=10)
    table.add_column("Industry\nRelevance", justify="center", width=10)
    table.add_column("Education", justify="center", width=10)
    table.add_column("Overall\nFit", justify="center", width=10)
    table.add_column("Total Score", justify="center", width=12, style="bold")

    for i, candidate in enumerate(sorted_candidates, 1):
        # Get colors for scores
        tech_color = get_score_color(candidate.get("technical_skills", 0))
        exp_color = get_score_color(candidate.get("experience", 0))
        industry_color = get_score_color(candidate.get("industry_relevance", 0))
        edu_color = get_score_color(candidate.get("education", 0))
        fit_color = get_score_color(candidate.get("overall_fit", 0))
        total_color = get_total_score_color(candidate.get("total_score", 0))

        # Rank styling
        rank_style = "gold1" if i == 1 else "bright_white" if i <= 3 else "white"
        rank_icon = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."

        table.add_row(
            f"[{rank_style}]{rank_icon}[/{rank_style}]",
            f"[bold]{candidate.get('name', 'Unknown')}[/bold]",
            f"[{tech_color}]{candidate.get('technical_skills', 0)}/10[/{tech_color}]",
            f"[{exp_color}]{candidate.get('experience', 0)}/10[/{exp_color}]",
            f"[{industry_color}]{candidate.get('industry_relevance', 0)}/10[/{industry_color}]",
            f"[{edu_color}]{candidate.get('education', 0)}/10[/{edu_color}]",
            f"[{fit_color}]{candidate.get('overall_fit', 0)}/10[/{fit_color}]",
            f"[{total_color}]{candidate.get('total_score', 0)}/50[/{total_color}]",
        )

    console.print(table)


def display_summary_stats(candidates: List[Dict[str, Any]]):
    """Display summary statistics."""
    if not candidates:
        return

    total_candidates = len(candidates)
    sorted_candidates = sorted(
        candidates, key=lambda x: x.get("total_score", 0), reverse=True
    )

    # Calculate stats
    avg_score = sum(c.get("total_score", 0) for c in candidates) / total_candidates
    top_candidate = sorted_candidates[0] if sorted_candidates else None
    strong_candidates = [
        c for c in candidates if c.get("total_score", 0) >= 35
    ]  # 70% threshold

    # Create summary panels
    summary_panels = []

    # Total candidates panel
    summary_panels.append(
        Panel(
            f"[bold blue]{total_candidates}[/bold blue]",
            title="Total Candidates",
            border_style="blue",
        )
    )

    # Average score panel
    avg_color = get_total_score_color(int(avg_score))
    summary_panels.append(
        Panel(
            f"[{avg_color}]{avg_score:.1f}/50[/{avg_color}]",
            title="Average Score",
            border_style=avg_color,
        )
    )

    # Top candidate panel
    if top_candidate:
        top_color = get_total_score_color(top_candidate.get("total_score", 0))
        summary_panels.append(
            Panel(
                f"[bold]{top_candidate.get('name', 'Unknown')}[/bold]\n[{top_color}]{top_candidate.get('total_score', 0)}/50[/{top_color}]",
                title="🏆 Top Candidate",
                border_style="gold1",
            )
        )

    # Strong candidates panel
    summary_panels.append(
        Panel(
            f"[bold green]{len(strong_candidates)}[/bold green]",
            title="Strong Candidates\n(35+ score)",
            border_style="green",
        )
    )

    console.print(Columns(summary_panels))


def display_reasoning_summary(raw_response):
    """Display usage stats from Groq response."""
    try:
        usage = raw_response.usage
        if usage:
            stats = f"Model: {raw_response.model}\n"
            stats += f"Prompt tokens: {usage.prompt_tokens}\n"
            stats += f"Completion tokens: {usage.completion_tokens}\n"
            stats += f"Total tokens: {usage.total_tokens}"

            panel = Panel(
                stats,
                title="⚡ Groq Inference Stats",
                border_style="blue",
                expand=False,
            )
            console.print(panel)
        else:
            console.print("[dim]No usage stats available.[/dim]")
    except Exception as e:
        console.print(f"[dim]Could not extract stats: {e}[/dim]")


def display_raw_evaluation(evaluation_data: dict):
    """Display the raw structured evaluation data in a panel."""
    import json
    formatted_json = json.dumps(evaluation_data, indent=2, ensure_ascii=False)
    panel = Panel(
        formatted_json,
        title="🤖 AI Structured Evaluation Data",
        border_style="dim",
        expand=False,
    )
    console.print(panel)


