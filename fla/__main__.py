import typer
from typing_extensions import Annotated
from core import classification, execution, reporting
from shared.utils import setup_gcs_client, get_gcs_bucket_name
import core.verify as verify_module

app = typer.Typer(
    name="flaccid-reorg",
    help="A serverless pipeline for reorganizing files in a GCS bucket based on a canonical blueprint.",
    add_completion=False,
)


@app.command()
def analyze(
    source_uri: Annotated[str, typer.Option()],
    project_id: Annotated[str, typer.Option()],
    manifest_path: Annotated[str, typer.Option()],
):
    typer.echo(f"Starting analysis of GCS path: {source_uri}")
    client = setup_gcs_client(project_id)
    bucket_name = get_gcs_bucket_name(source_uri)
    prefix = source_uri.replace(f"gs://{bucket_name}/", "")
    classification.generate_action_plan(client, bucket_name, prefix, manifest_path)
    typer.echo(f"Analysis complete. Action plan saved to: {manifest_path}")


@app.command()
def report(
    manifest_path: Annotated[str, typer.Option()],
    report_path: Annotated[str, typer.Option()],
):
    typer.echo(f"Generating reports from manifest: {manifest_path}")
    reporting.generate_reports(manifest_path, report_path)
    typer.echo(f"Reports saved to GCS path: {report_path}")


@app.command()
def execute(
    manifest_path: Annotated[str, typer.Option()],
    project_id: Annotated[str, typer.Option()],
    workers: Annotated[int, typer.Option()] = 16,
):
    typer.echo(f"Executing reorganization plan from: {manifest_path}")
    client = setup_gcs_client(project_id)
    execution.execute_plan(client, manifest_path, max_workers=workers)
    typer.echo("Execution complete.")


@app.command()
def verify(
    manifest_path: Annotated[str, typer.Option()],
    project_id: Annotated[str, typer.Option()],
):
    """CLI entrypoint for verification."""
    typer.echo(f"Verifying final state against manifest: {manifest_path}")
    client = setup_gcs_client(project_id)
    verify_module.verify_execution(client, manifest_path)
    typer.echo("Verification complete.")


if __name__ == "__main__":
    app()
