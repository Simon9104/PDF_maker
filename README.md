# Customer Table Generator

A desktop app to create professional customer tables and export them as PDF documents — like a receipt but fully customizable.

## Features

- Set a **headline**, subtitle, and footer note
- Define any number of **custom columns**
- Add, edit, and delete rows via a clean GUI
- **Preview** the table before exporting
- Export a **professionally styled PDF** with alternating row colors

## Download

Go to the [Releases](../../releases) page and download the version for your OS:

| Platform | File |
|----------|------|
| macOS | `CustomerTableGenerator-macOS.dmg` |
| Windows | `CustomerTableGenerator-Windows.zip` |

## Run from source

```bash
pip install reportlab
python app.py
```

## Build locally

```bash
pip install pyinstaller reportlab
pyinstaller app.spec
```

The built app/exe will be in the `dist/` folder.
