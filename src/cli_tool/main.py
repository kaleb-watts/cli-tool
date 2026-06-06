import typer

from cli_tool.commands.analyze import analyze
from cli_tool.commands.ask_file import ask_file
from cli_tool.commands.chat import chat
from cli_tool.commands.email import email
from cli_tool.commands.meeting import meeting
from cli_tool.commands.repo_review import repo_review
from cli_tool.commands.research import research
from cli_tool.commands.review import review

app = typer.Typer(help="CLI Tool: simple AI CLI for emails, code reviews, and meeting summaries.")

app.command()(email)
app.command()(review)
app.command()(meeting)
app.command("research")(research)
app.command("ask-file")(ask_file)
app.command("analyze")(analyze)
app.command("repo-review")(repo_review)
app.command("chat")(chat)


if __name__ == "__main__":
    app()
