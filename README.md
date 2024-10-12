# kritanet-builder.py

A simple Python script, that builds a [Krita](https://krita.org/)-based [Antinet](https://www.scottscheper.com/antinet) by converting Krita files to JPEG and replicating the source directory structure.

Since the conversion from Krita source files to JPEG is time-consuming, the script checks which cards need to be created/updated, and also warns about unaccounted files and directories, that probably shouldn't be in the destination structure.

## Usage

Run the script by supplying the paths to the source Kritanet directory and the destination directory:
```bash
python kritanet-builder.py -s ~/Kritanet/ -d ~/Kritanet-JPG/
```