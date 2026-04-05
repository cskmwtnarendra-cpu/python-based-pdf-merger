## 💻 System Requirements
* **OS:** Windows 10/11 (or macOS/Linux).
* **Python:** 3.7 or higher.
* **Libraries:** `pypdf` and `rich` (**Automated setup included**).

---

## 🛠 Step 0: Install Python (Windows)

If you don't have Python installed, follow these steps:

1. **Download:** Go to the official [Python.org Downloads](https://www.python.org/downloads/windows/) page.
2. **Run Installer:** Download the "Windows installer (64-bit)" and run it.
3. **CRITICAL STEP:** On the first screen of the installer, check the box that says **"Add Python to PATH"**. 
   > *If you miss this, the `python` command will not work in your terminal.*
4. **Install Now:** Click "Install Now" and wait for it to finish.
5. **Verify:** Open **PowerShell** or **Command Prompt** and type:
   ```powershell
   python --version
   ```
   If it returns `Python 3.x.x`, you are ready to go.

---

## 🚀 How to Use

### 1. Setup
Clone the repo and enter the folder:
```bash
git clone https://github.com/cskmwtnarendra-cpu/python-pdf-merger.git
cd python-pdf-merger
```

### 2. Prepare Files
* Create a folder named `input_pdfs` in the script directory.
* Drop all the PDFs you want to merge into that folder.

### 3. Run
Execute the script. It will automatically detect and install missing libraries for you:
```bash
python pdf_merger.py
```

### 4. Custom Paths (Optional)
Specify custom locations via terminal arguments:
```bash
python pdf_merger.py --input "C:/MyPDFs" --output "D:/MergedResults"
```

## Sample Output
#### 📂 Place files and tool like this
```text
E:\PdfMerge\
│
├── tool\
│   ├── merge_tool.py
│   ├── README.md
│   └── merged_output\   (auto-created)
│
└── pdfs\              ← 👈 Place your PDF files here
    ├── file1.pdf
    ├── file2.pdf
    ├── file3.pdf
    └── ...
```
```bash
E:\PdfMerge\tool>dir
Volume in drive E is New Volume
Volume Serial Number is 50F3-FBA9

Directory of E:\PdfMerge\tool
05-04-2026  10:44    <DIR>          .
05-04-2026  10:47    <DIR>          ..
05-04-2026  10:44            11,401 merge_tool.py
05-04-2026  10:44             2,303 README.md
               2 File(s)         13,704 bytes
               2 Dir(s)  21,420,523,520 bytes free

E:\PdfMerge\tool>python merge_tool.py --input="E:\PdfMerge\pdfs"
╭────────────────────────────────────── v1.0 ───────────────────────────────────────╮
│                                                                                   │
│   📂 PDF MASTER MERGER                                                            │
│   Maintainer: Narendra Kumawat                                                    │
│   https://github.com/cskmwtnarendra-cpu/python-pdf-merger-windows                 │
│                                                                                   │
╰────────────────────────────────── Secure & Fast ──────────────────────────────────╯
╭────────────────────────────── Configuration Summary ──────────────────────────────╮
│   Property                Value                                                   │
│   Input Source            E:\PdfMerge\pdfs                                      │
│   Output Target           E:\PdfMerge\tool\merged_output                          │
│   Status                  Ready (Write Access Verified)                           │
╰───────────────────────────────────────────────────────────────────────────────────╯
╭──────────────────────────────────── The Plan ─────────────────────────────────────╮
│ 1. SEARCH: Scanning PDFs from E:\PdfMerge\pdfs                                  │
│ 2. COMBINE: Merging all discovered PDFs in memory.                                │
│ 3. SAVE: Writing PDF file to Final_Merged_Document.pdf                            │
╰───────────────────────────────────────────────────────────────────────────────────╯

Proceed with merge? [y/n] (y): y
[11:06:48] INFO     Found 20 files. Initiating memory buffer...
[11:06:50] INFO     Preparing to write Final_Merged_Document.pdf...
╭──────────────────────────────────── Complete ─────────────────────────────────────╮
│ ✔ MERGE SUCCESSFUL!                                                               │
│                                                                                   │
│ Files Processed: 20                                                               │
│ Final Output:    E:\PdfMerge\tool\merged_output\Final_Merged_Document.pdf         │
│                                                                                   │
│ Everything looks perfect.                                                         │
╰───────────────────────────────────────────────────────────────────────────────────╯
Happy merging. Cheers!
```

## 🛠 Features
* **Auto-Setup:** No manual `pip install` required; the script handles dependencies.
* **Permission Check:** Validates write access **before** merging to prevent crashes.
* **Smart Versioning:** Automatically renames output (e.g., `Document (1).pdf`) to avoid overwriting.
* **Progress UI:** Real-time progress bars for large batches of files.

---

## ⚙️ How it Works
1. **Scan:** Finds and sorts all `.pdf` files in the input folder.
2. **Verify:** Runs a "write-test" to ensure the destination isn't locked or read-only.
3. **Merge:** Buffers PDF structures into memory for high-speed combining.
4. **Export:** Safely writes the final file and closes all background handles.

---

**Maintainer:** Narendra Kumawat
