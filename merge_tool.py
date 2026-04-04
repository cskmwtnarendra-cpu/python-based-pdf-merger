import os
import sys
import time
import argparse
import subprocess
import socket  # Added for cross-platform internet check
from pathlib import Path
from datetime import datetime

# --- DEPENDENCY CHECKER ---
def check_dependencies():
    required = {"pypdf", "rich"}
    missing = set()
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            missing.add(lib)
    
    if missing:
        timestamp = datetime.now().strftime("[%X]")
        try:
            line = "─" * 65
            print(f"\033[95m┌{line}┐\033[0m")
            print(f"\033[95m│\033[0m \033[96m{timestamp} [!] INITIAL SETUP\033[0m                                   \033[95m│\033[0m")
            print(f"\033[95m│\033[0m Some required components are missing. This is a one-time setup. \033[95m│\033[0m")
            print(f"\033[95m│\033[0m Missing: {', '.join(missing):<54} \033[95m│\033[0m")
            print(f"\033[95m└{line}┘\033[0m")
            
            choice = input(f"\n{timestamp} [?] Would you like to install them now? (y/n): ").lower()
            if choice == 'y':
                # 1. Internet Connection Check (Platform Independent)
                print(f"{timestamp} [*] Step 1/4: Checking Internet Connection...", end="\r")
                try:
                    # Using socket is more reliable across OS than calling nslookup
                    socket.create_connection(("1.1.1.1", 53), timeout=3)
                    print(f"\033[92m{timestamp} [+] Step 1/4: Internet Connection OK!                        \033[0m")
                except Exception:
                    print(f"\n\033[91m{timestamp} [FATAL ERROR] No Internet Connection detected.\033[0m")
                    sys.exit(1)

                # 2. Download & Installation
                print(f"{timestamp} [*] Step 2/4: Downloading & Installing components...", end="\r")
                install_cmd = [sys.executable, "-m", "pip", "install", *missing]
                process = subprocess.Popen(install_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                
                chars = "/—\\"
                i = 0
                while process.poll() is None:
                    print(f"{timestamp} [*] Step 2/4: Installing {', '.join(missing)} {chars[i % len(chars)]} ", end="\r")
                    time.sleep(0.2)
                    i += 1
                
                if process.returncode != 0:
                    print(f"\n\033[91m{timestamp} [FATAL ERROR] Installation failed.\033[0m")
                    sys.exit(1)
                print(f"\033[92m{timestamp} [+] Step 2/4: Installation complete!                          \033[0m")

                # 3. Verification
                print(f"{timestamp} [*] Step 3/4: Verifying libraries...", end="\r")
                time.sleep(0.5)
                if all(__import__(lib, fromlist=['']) for lib in required):
                    print(f"\033[92m{timestamp} [+] Step 3/4: Verification successful!                       \033[0m")
                    print(f"\n\033[92m{timestamp} [DONE] All components are ready.\033[0m")
                    print(f"\033[96m{timestamp} [ACTION] Please RESTART the program to begin merging.\033[0m\n")
                    sys.exit(0)
            else:
                sys.exit(1)

        except KeyboardInterrupt:
            sys.exit(1)
        except Exception as e:
            print(f"\n\n\033[91m[ERROR] {e}\033[0m")
            sys.exit(1)

check_dependencies()

# Import Rich components after dependency check
from pypdf import PdfWriter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn, TimeElapsedColumn
from rich.logging import RichHandler
from rich.prompt import Confirm
import logging

# --- CONFIGURATION ---
PDF_SETTINGS = {
    "default_input_name": "input_pdfs",
    "default_output_name": "merged_output",
    "base_filename": "Final_Merged_Document",
    "repo_url": "https://github.com/cskmwtnarendra-cpu/python-pdf-merger-windows",
    "ui_width": 85 
}

console = Console()

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, show_path=False, console=console)]
)
log = logging.getLogger("rich")

def get_unique_filename(directory, base_name):
    counter = 0
    while True:
        suffix = f" ({counter})" if counter > 0 else ""
        candidate = directory / f"{base_name}{suffix}.pdf"
        if not candidate.exists():
            return candidate
        counter += 1

def check_write_permission(directory):
    try:
        if not directory.exists():
            return True 
        test_file = directory / f".write_test_{int(time.time())}"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception:
        return False

def setup_terminal(show_help=False):
    # Cross-platform terminal titling
    title = "PDF Master Merger v1.0"
    if os.name == 'nt':
        os.system(f"title {title}")
    else:
        # Standard ANSI escape sequence for macOS/Linux terminal titles
        sys.stdout.write(f"\x1b]2;{title}\x07")
    
    console.print("\n")
    console.print(
        Panel(
            "[bold cyan] 📂 PDF MASTER MERGER [/bold cyan]\n"
            "[white]Maintainer:[/white] [bold magenta]Narendra Kumawat[/bold magenta]\n"
            f"[dim]{PDF_SETTINGS['repo_url']}[/dim]",
            border_style="magenta",
            padding=(1, 2),
            title="[bold white]v1.0[/bold white]",
            subtitle="[italic white]Secure & Fast[/italic white]",
            width=PDF_SETTINGS["ui_width"]
        ),
        justify="left"
    )

def merge_pdfs(source_path_str=None, output_path_str=None):
    is_default_run = not (source_path_str or output_path_str)
    setup_terminal(show_help=is_default_run)
    
    # Pathlib handles the forward/backward slash automatically
    base_path = Path(__file__).parent.resolve()
    source_dir = Path(source_path_str).resolve() if source_path_str else (base_path / PDF_SETTINGS["default_input_name"]).resolve()
    output_dir = Path(output_path_str).resolve() if output_path_str else (base_path / PDF_SETTINGS["default_output_name"]).resolve()
    
    current_action = "initializing"

    try:
        current_action = f"creating the output folder at [yellow]{output_dir}[/yellow]"
        if not output_dir.exists():
            output_dir.mkdir(parents=True)
        
        current_action = f"verifying write access to the directory [yellow]{output_dir}[/yellow]"
        if not check_write_permission(output_dir):
            raise PermissionError("Access is denied to this folder or drive.")
            
        final_file_path = get_unique_filename(output_dir, PDF_SETTINGS["base_filename"])

        summary_table = Table(box=None, padding=(0, 2))
        summary_table.add_column("Property", style="bold cyan", width=20)
        summary_table.add_column("Value", style="white")
        summary_table.add_row("Input Source", str(source_dir))
        summary_table.add_row("Output Target", str(output_dir))
        summary_table.add_row("Status", "[green]Ready (Write Access Verified)[/green]")
        
        console.print(Panel(summary_table, title="[bold white]Configuration Summary[/bold white]", border_style="cyan", width=PDF_SETTINGS["ui_width"]), justify="left")

        plan_text = (
            f"[bold white]1. SEARCH:[/bold white] Scanning PDFs from [magenta]{source_dir}[/magenta]\n"
            f"[bold white]2. COMBINE:[/bold white] Merging all discovered PDFs in memory.\n"
            f"[bold white]3. SAVE:[/bold white] Writing PDF file to [bold cyan]{final_file_path.name}[/bold cyan]"
        )
        console.print(Panel(plan_text, title="[bold yellow]The Plan[/bold yellow]", border_style="yellow", width=PDF_SETTINGS["ui_width"]), justify="left")

        if not Confirm.ask("\n[bold cyan]Proceed with merge?[/bold cyan]", default=True):
            log.info("Task aborted by user.")
            return

        pdf_files = sorted([f for f in source_dir.glob("*.pdf")])
        if not pdf_files:
            log.warning(f"No PDF files found.")
            return

        log.info(f"Found {len(pdf_files)} files. Initiating memory buffer...")
        merger = PdfWriter()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40, pulse_style="magenta"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=True
        ) as progress:
            merge_task = progress.add_task("[yellow]Queuing PDFs...", total=len(pdf_files))
            for pdf in pdf_files:
                progress.update(merge_task, description=f"[cyan]Adding:[/cyan] {pdf.name[:40]}")
                merger.append(pdf)
                progress.advance(merge_task)

        current_action = f"writing the final PDF file [bold cyan]{final_file_path.name}[/bold cyan]"
        with console.status(f"[bold green]Writing...[/bold green]", spinner="bouncingBall"):
            timestamp = datetime.now().strftime("[%X]")
            console.print(f"{timestamp} INFO      Preparing to write [bold cyan]{final_file_path.name}[/bold cyan]...")
            with open(final_file_path, "wb") as f:
                merger.write(f)
            merger.close()

        success_content = (
            f"[bold green]✔ MERGE SUCCESSFUL![/bold green]\n\n"
            f"Files Processed: [bold cyan]{len(pdf_files)}[/bold cyan]\n"
            f"Final Output:    [bold yellow]{final_file_path}[/bold yellow]\n\n"
            f"[bold magenta]Everything looks perfect.[/bold magenta]"
        )
        console.print("\n", Panel(success_content, border_style="green", title="[bold green]Complete[/bold green]", width=PDF_SETTINGS["ui_width"]), justify="left")
        console.print(f"[bold magenta]Happy merging. Cheers! [/bold magenta]\n", justify="left")

    except PermissionError as e:
        console.print("\n") 
        title_text = "ACCESS DENIED"
        error_panel = Panel(
            f"[bold red]{title_text}![/bold red]\n\n"
            f"I failed while: [white]{current_action}[/white]\n\n"
            f"Please check your folder permissions or if the file is open.",
            border_style="red",
            title="[bold red]Permission Error[/bold red]",
            width=PDF_SETTINGS["ui_width"],
            padding=(1, 2)
        )
        console.print(error_panel, justify="left")
    except Exception as e:
        console.print(f"\n[bold red]CRITICAL ERROR during {current_action}:[/bold red]\n{e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    args = parser.parse_args()
    try:
        merge_pdfs(args.input, args.output)
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user. Exiting...[/bold red]")