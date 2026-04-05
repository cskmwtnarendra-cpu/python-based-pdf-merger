import os
import sys
import time
import math
import argparse
import subprocess
import socket
from pathlib import Path
from datetime import datetime
from threading import Thread

# --- STAGE 1: DEPENDENCY CHECKER ---
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
                print(f"{timestamp} [*] Step 1/4: Checking Internet Connection...", end="\r")
                try:
                    socket.create_connection(("1.1.1.1", 53), timeout=3)
                    print(f"\033[92m{timestamp} [+] Step 1/4: Internet Connection OK!                        \033[0m")
                except Exception:
                    print(f"\n\033[91m{timestamp} [FATAL ERROR] No Internet Connection detected.\033[0m")
                    sys.exit(1)

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

                print(f"{timestamp} [*] Step 3/4: Verifying libraries...", end="\r")
                time.sleep(0.5)
                if all(__import__(lib, fromlist=['']) for lib in required):
                    print(f"\033[92m{timestamp} [+] Step 3/4: Verification successful!                       \033[0m")
                    print(f"\n\033[92m{timestamp} [DONE] All components are ready.\033[0m")
                    print(f"\033[96m{timestamp} [ACTION] Please RESTART the program to begin merging.\033[0m\n")
                    sys.exit(0)
            else:
                sys.exit(1)
        except (KeyboardInterrupt, Exception):
            sys.exit(1)

check_dependencies()

# --- STAGE 2: IMPORTS & CONFIG ---
from pypdf import PdfWriter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn, TimeElapsedColumn
from rich.logging import RichHandler
from rich.prompt import Confirm, Prompt
import logging

PDF_SETTINGS = {
    "default_input_name": "input_pdfs",
    "default_output_name": "merged_output",
    "base_filename": "Merged",
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

# --- UTILITIES ---
def human_mb(b): 
    return round(b / (1024 * 1024), 2)

def get_unique_filename(directory, base_name):
    counter = 0
    while True:
        suffix = f" ({counter})" if counter > 0 else ""
        candidate = directory / f"{base_name}{suffix}.pdf"
        if not candidate.exists(): return candidate
        counter += 1

def check_write_permission(directory):
    try:
        if not directory.exists(): return True 
        test_file = directory / f".write_test_{int(time.time())}"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception: return False

def setup_terminal():
    title = "PDF Master Merger v1.0"
    if os.name == 'nt': os.system(f"title {title}")
    else: sys.stdout.write(f"\x1b]2;{title}\x07")
    
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

    cli_guide = (
        f"[bold white]Available Arguments:[/bold white]\n"
        f"  [magenta]--input[/magenta]        Source folder path  [dim](Default: /input_pdfs)[/dim]\n"
        f"  [magenta]--output[/magenta]       Result folder path  [dim](Default: /merged_output)[/dim]\n"
        f"  [magenta]--max-size-mb[/magenta]  Force split limit   [dim](e.g., 150)[/dim]\n\n"
        f"[bold yellow]Quick Start:[/bold yellow] [cyan]python merge_tool.py --input \"./my_files\" --max-size-mb 100[/cyan]"
    )
    console.print(Panel(cli_guide, title="[bold white]CLI Reference[/bold white]", border_style="blue", width=PDF_SETTINGS["ui_width"]), justify="left")

# --- LIVE FEEDBACK WRITER ---
def write_with_feedback(merger, file_path, label):
    done = {"flag": False}
    def writer():
        with open(file_path, "wb") as f:
            merger.write(f)
        done["flag"] = True

    t = Thread(target=writer)
    t.start()

    with Progress(SpinnerColumn(), TextColumn(f"[green]{label} writing...[/green]"), TimeElapsedColumn(), console=console, transient=True) as progress:
        task = progress.add_task("writing", total=None)
        last_size = 0
        while not done["flag"]:
            if file_path.exists():
                size = file_path.stat().st_size
                if size != last_size:
                    progress.update(task, description=f"[green]{label} writing... {human_mb(size)} MB[/green]")
                    last_size = size
            time.sleep(0.2)
    t.join()

# --- CORE LOGIC ---
def merge_pdfs(source_path_str=None, output_path_str=None, max_size_mb_cli=None):
    setup_terminal()
    base_path = Path(__file__).parent.resolve()
    source_dir = Path(source_path_str).resolve() if source_path_str else (base_path / PDF_SETTINGS["default_input_name"]).resolve()
    output_dir = Path(output_path_str).resolve() if output_path_str else (base_path / PDF_SETTINGS["default_output_name"]).resolve()
    
    try:
        if not output_dir.exists(): output_dir.mkdir(parents=True)
        if not check_write_permission(output_dir): raise PermissionError("Access is denied to this folder.")

        pdf_files = sorted([f for f in source_dir.glob("*.pdf")])
        if not pdf_files:
            console.print(Panel(f"[bold red]MISSING ASSETS[/bold red]\n\nNo PDFs found in: [cyan]{source_dir}[/cyan]", title="[bold red]Error[/bold red]", border_style="red", width=PDF_SETTINGS["ui_width"]))
            return

        total_size = sum(f.stat().st_size for f in pdf_files)
        file_count = len(pdf_files)
        DEFAULT_LIMIT_MB = 200
        strategy_note = ""
        max_size_mb = max_size_mb_cli

        console.print(f"\n[bold white]Summary:[/bold white] [cyan]{file_count}[/cyan] files found, totaling [magenta]{human_mb(total_size)} MB[/magenta].")
        
        if max_size_mb is None:
            if total_size <= (DEFAULT_LIMIT_MB * 1024 * 1024):
                if Confirm.ask("\n[bold cyan]Proceed with merging into a single file?[/bold cyan]", default=True):
                    strategy_note = "Single File (Under Limit)"
                else: return
            else:
                potential_parts = math.ceil(total_size / (DEFAULT_LIMIT_MB * 1024 * 1024))
                prompt_msg = f"\n[bold yellow]Large Volume Detected![/bold yellow]\n [y] Single File (~{human_mb(total_size)} MB)\n [n] Split into ({potential_parts} parts)\n\nMerge into single?"
                if Confirm.ask(prompt_msg, default=True):
                    strategy_note = "Single File (User Choice)"
                else:
                    max_size_mb = DEFAULT_LIMIT_MB if Confirm.ask(f"Use default {DEFAULT_LIMIT_MB}MB limit?", default=True) else int(Prompt.ask("Enter custom limit (MB)", default="100"))
                    strategy_note = f"Split ({max_size_mb}MB)"
        else:
            strategy_note = f"CLI Override ({max_size_mb}MB)"

        # Final Split Determination
        will_split = False
        parts = 1
        if max_size_mb:
            max_size_bytes = max_size_mb * 1024 * 1024
            will_split = total_size > max_size_bytes
            parts = math.ceil(total_size / max_size_bytes) if will_split else 1

        # Summary Table
        summary_table = Table(box=None, padding=(0, 2))
        summary_table.add_column("Property", style="bold cyan")
        summary_table.add_column("Value", style="white")
        summary_table.add_row("Input", str(source_dir))
        summary_table.add_row("Files", f"{file_count} PDFs")
        summary_table.add_row("Strategy", strategy_note)
        console.print(Panel(summary_table, title="[bold white]Configuration[/bold white]", border_style="cyan", width=PDF_SETTINGS["ui_width"]))

        if not Confirm.ask("\n[bold cyan]Proceed with operation?[/bold cyan]", default=True): return

        final_file_path = None
        parts_dir_path = None

        if not will_split:
            merger = PdfWriter()
            with Progress(SpinnerColumn(), TextColumn("[cyan]{task.description}"), BarColumn(), TaskProgressColumn(), console=console, transient=True) as progress:
                task = progress.add_task("Queuing PDFs...", total=file_count)
                for pdf in pdf_files:
                    merger.append(pdf)
                    progress.advance(task)

            final_file_path = get_unique_filename(output_dir, PDF_SETTINGS["base_filename"])
            log.info(f"Initiating write for {final_file_path.name}...")
            write_with_feedback(merger, final_file_path, "Final")
            merger.close()
        else:
            parts_dir_path = output_dir / "parts"
            parts_dir_path.mkdir(exist_ok=True)
            start, base_count, remainder = 0, file_count // parts, file_count % parts
            for i in range(parts):
                count = base_count + (1 if i < remainder else 0)
                chunk = pdf_files[start:start+count]
                start += count
                merger = PdfWriter()
                for pdf in chunk: merger.append(pdf)
                part_file = parts_dir_path / f"{PDF_SETTINGS['base_filename']}_Part_{i+1}.pdf"
                log.info(f"Processing Part {i+1}/{parts} ({len(chunk)} files)")
                write_with_feedback(merger, part_file, f"Part {i+1}")
                merger.close()

        # Success Message
        loc = f"[bold yellow]{final_file_path}[/bold yellow]" if not will_split else f"[bold yellow]{parts_dir_path}[/bold yellow] ({parts} Parts)"
        success_content = f"[bold green]✔ OPERATION SUCCESSFUL![/bold green]\n\nProcessed: [bold cyan]{file_count}[/bold cyan] files\nLocation:  {loc}\n\n[bold magenta]Everything looks perfect. Cheers![/bold magenta]"
        console.print("\n", Panel(success_content, border_style="green", title="[bold green]Complete[/bold green]", width=PDF_SETTINGS["ui_width"]), justify="left")

    except Exception as e:
        console.print(f"\n[bold red]CRITICAL ERROR:[/bold red] {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str)
    parser.add_argument("--output", type=str)
    parser.add_argument("--max-size-mb", type=int, default=None)
    args = parser.parse_args()
    try:
        merge_pdfs(args.input, args.output, args.max_size_mb)
    except KeyboardInterrupt:
        console.print("\n[bold red]Interrupted by user. Exiting...[/bold red]")