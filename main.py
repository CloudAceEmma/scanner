from scanner.scanner import scan_repository
import click
import json


@click.command()
@click.option("--repo", required=True, help="Path or URL to the Git repository.")
@click.option(
    "--n",
    "commits_count",
    default=10,
    type=int,
    help="Number of recent commits to scan.",
)
@click.option(
    "--out", "output_file", default="report.json", help="Output JSON report file."
)
def main(repo, commits_count, output_file):
    """
    Scans the last N commits of a Git repository for secrets.
    """
    click.echo(f"Scanning repository: {repo}")
    findings = scan_repository(repo, commits_count)

    with open(output_file, "w") as f:
        json.dump(findings, f, indent=2)

    click.echo(f"Scan complete. Report saved to {output_file}")


if __name__ == "__main__":
    main()
