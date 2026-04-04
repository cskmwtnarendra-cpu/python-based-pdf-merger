# 📂 PDF Master Merger v1.0

A high-performance, cross-platform tool to merge multiple PDFs into one. Simple, fast, and secure.

---

## 💻 System Requirements
* **Python:** 3.7 or higher.
* **OS:** Windows, macOS, or Linux.
* **Libraries:** `pypdf` and `rich` (**Automated setup included**).

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

---

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
