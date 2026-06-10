from typing import List
from rich.table import Table
from rich.console import Console
from schemas.job_listing import ExportedJobListing

console = Console()

class ConsoleReporter:
    @staticmethod
    def report(jobs: List[ExportedJobListing]):
        if not jobs:
            console.print("[bold yellow]No jobs passed the pipeline.[/bold yellow]")
            return
            
        table = Table(title="Top Senior Angular Opportunities", show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("Category", width=12)
        table.add_column("Company", style="bold cyan")
        table.add_column("Title", width=30)
        table.add_column("Location", width=20)
        
        # Only show top 20 on console to prevent spam
        for job in jobs[:20]:
            table.add_row(
                str(job.rank),
                job.category.value,
                job.company_name,
                job.job_title[:30] + ("..." if len(job.job_title)>30 else ""),
                job.location[:20] + ("..." if len(job.location)>20 else "")
            )
            
        console.print(table)
        console.print(f"\n[bold green]Successfully exported {len(jobs)} matches to CSV/JSON![/bold green]")
