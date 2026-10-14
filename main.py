#!/usr/bin/env python3

import sys
import io

# Ensure UTF-8 output encoding on Windows consoles
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from utils import (
    setup_environment,
    load_text_file,
    get_resume_files,
    prepare_resume_inputs,
    call_groq_api,
)
from ui import (
    console,
    display_header,
    display_results_table,
    display_summary_stats,
    display_reasoning_summary,
    display_raw_evaluation,
)


def main():
    """Main application function."""

    try:
        # Display header
        display_header()

        # Setup and validate environment
        console.print("[bold blue]Setting up environment...[/bold blue]")
        setup_environment()
        console.print("[green]Environment setup complete![/green]\n")

        # Load guidance prompt and job description
        console.print(
            "[bold blue]Loading guidance prompt and job description...[/bold blue]"
        )

        try:
            guidance_prompt = load_text_file("guidance_prompt.md")
            job_description = load_text_file("job_description.md")
        except FileNotFoundError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(
                "[yellow]Make sure guidance_prompt.md and job_description.md exist and contain content.[/yellow]"
            )
            return

        console.print("[green]Templates loaded successfully![/green]\n")

        # Get resume files
        console.print("[bold blue]Scanning for resume PDFs...[/bold blue]")

        try:
            pdf_files = get_resume_files("resumes")
        except FileNotFoundError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print(
                "[yellow]Please add PDF resume files to the 'resumes' directory.[/yellow]"
            )
            return

        console.print(f"[green]Found {len(pdf_files)} resume files:[/green]")
        for pdf_file in pdf_files:
            console.print(f"\t{pdf_file.name}")

        console.print()

        # Prepare resume inputs
        console.print("[bold blue]Converting PDFs to base64 format...[/bold blue]")
        try:
            resume_inputs = prepare_resume_inputs(pdf_files)
        except Exception as e:
            console.print(f"[red]Error preparing resume files: {e}[/red]")
            return

        console.print(
            f"[green]Prepared {len(resume_inputs)} resumes for AI evaluation[/green]\n"
        )

        # Show processing animation
        console.print(
            "[bold blue]Sending all resumes to Groq for evaluation...[/bold blue]"
        )
        console.print(
            "[dim]This may take a few moments as the AI analyzes each resume...[/dim]\n"
        )

        # Add a progress indicator
        with console.status("[bold green]AI is thinking and evaluating resumes..."):
            try:
                # Make the API call with all resumes
                evaluation_result, raw_response = call_groq_api(
                    guidance_prompt=guidance_prompt,
                    job_description=job_description,
                    resume_inputs=resume_inputs,
                )
            except Exception as e:
                console.print(f"[red]Groq API Error: {e}[/red]")
                console.print(
                    "[yellow]Please check your API key and try again.[/yellow]"
                )
                return

        console.print("[green]AI evaluation completed![/green]\n")

        # Display structured results
        console.print("[bold blue]Processing results...[/bold blue]")

        try:
            # evaluation_result is now a structured ResumeEvaluationResults object
            candidates_data = []
            for candidate in evaluation_result.candidates:
                candidates_data.append({
                    "name": candidate.name,
                    "filename": candidate.filename,
                    "technical_skills": candidate.technical_skills.score,
                    "experience": candidate.experience.score,
                    "industry_relevance": candidate.industry_relevance.score,
                    "education": candidate.education.score,
                    "overall_fit": candidate.overall_fit.score,
                    "total_score": candidate.total_score,
                    "strengths": candidate.key_strengths,
                    "concerns": candidate.concerns,
                })

            if not candidates_data:
                console.print(
                    "[yellow]No candidates were evaluated by the AI.[/yellow]"
                )
                return

            console.print(
                f"[green]Successfully processed data for {len(candidates_data)} candidates[/green]\n"
            )

            # Display AI reasoning process
            console.print("[dim]AI reasoning process:[/dim]")
            display_reasoning_summary(raw_response)

            # Display full structured evaluation data
            console.print("\n[dim]Full structured evaluation data:[/dim]")
            display_raw_evaluation(evaluation_result.model_dump())

            # Display summary statistics
            console.print("\n")
            display_summary_stats(candidates_data)
            console.print()

            # Display detailed results table
            display_results_table(candidates_data)
            console.print()

            # Display structured summary
            console.print(f"[dim]Total Candidates Evaluated: {evaluation_result.total_candidates_evaluated}[/dim]")
            console.print(f"[dim]Top Recommendation: {evaluation_result.top_recommendation}[/dim]")
            console.print(f"[dim]Ready for Interview: {', '.join(evaluation_result.ready_for_interview)}[/dim]")

        except Exception as e:
            console.print(f"[red]Error processing structured results: {e}[/red]")
            return

        console.print(
            "\n[bold green]Resume evaluation completed successfully![/bold green]"
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
