# Chess Puzzles to PDF booklet[^1]
## What this site provides 
- a collection of PDF files (A4), evtl. for your personal printout as a booklet[^1], 
- some scripts that has been used for its generation, and 
- this readme with a description about the PDF compilation.

## My intention
... was to support myself learning chess. 

Starting chess learning at [lichess.org](https://lichess.org/) which has a good entry point for online-[training](https://lichess.org/training/themes), I like to have a couple (e.g. ten) of these puzzles as a printout, to take them with me for later offline-walkthrough. 

After some googling I found the [lichess puzzle database](https://database.lichess.org/#puzzles) giving us access to lots of the puzzle as a free download of the CSV-formated data.

## Steps
... to prepare the PDF-collection
1. Install a [MySQL](https://www.mysql.com/) or [MariaDB](https://mariadb.org/) database, for later accessing the puzzles' data, etvl. plus an [apache](https://httpd.apache.org/) Webserver, a [PHP](https://www.php.net/) and the [phpMyAdmin](https://www.phpmyadmin.net/downloads/) - alternatively you may use [XAMPP](https://www.apachefriends.org/download.html), which has that environment in one package.
3. Download the puzzle's CSV-file from [lichess puzzle database](https://database.lichess.org/#puzzles)
4. (optionally) split the large file into multiple smaller files with [split command](https://man7.org/linux/man-pages/man1/split.1.html), e.g. `split -l 1000 <input-filename>`
5. Import the CSV-file into your database
6. add some columns e.g. for tuning the access to a group of puzzles by its theme. The CSV-file has a column that lists for each puzzle the themes belonging to that puzzle. There are less than 64 themes, so I used the `set` type and made a `view` for each theme with the same columns
7. use the Python script from this repository `generate_theme_puzzles.py` to generate for each theme (that are the `views` in your database) a dedicated subdirectory with ten puzzles' HTML-files
   - The Python script uses the [`python-chess`](https://python-chess.readthedocs.io/en/latest/) to parse the FEN[^3] and UCI moves[^4] to generate the SVG[^5] chess board diagrams.
9. use [`google-chrome --headless`](https://developers.google.com/web/updates/2017/04/headless-chrome) to generate for each HTML-file a PDF-file
   - e.g. 
     - for one file: `google-chrome --headless --disable-gpu --print-to-pdf-no-header --print-to-pdf=underPromotion_00001.pdf underPromotion_00001.html`
     - for multiple files: `ls *.html | awk '{html = $1; gsub(/html/, "pdf", $1); pdf = $0; print "google-chrome --headless --disable-gpu --print-to-pdf-no-header --print-to-pdf=",pdf, html}' | sed -e 's/= /=/g' | while read -r line; do $line; done`  
     - [`wkhtmltopdf`](https://wkhtmltopdf.org/) and [`python-pdfkit`](https://github.com/JazzCore/python-pdfkit) corrupts my A4 layout; although HTML-files has the CSS `@page { size: A4 }`
10. use `gs` [ghostscript for merging](https://stackoverflow.com/questions/8158584/ghostscript-to-merge-pdfs-compresses-the-result) / concatination ten puzzle's PDF-files to one puzzle's PDF-file
    - e.g.
      - for all PDF-files of one puzzle: `gs -dNOPAUSE -sDEVICE=pdfwrite -sOUTPUTFILE=../zugzwang.pdf -dBATCH $(ls -a *.pdf)`

## Open item
- [ ] alternatively to [`python-chess`](https://python-chess.readthedocs.io/en/latest/) SVG drawing the chessboards, use free chess fonts ([chess TTF examples here](http://www.enpassant.dk/chess/fonteng.htm)). Just B/W diagrams may give more contrast; anyway seems that Latex will be best choise for this ([see that paper](https://ftp.tu-chemnitz.de/pub/tex/macros/latex/contrib/chessfss/chessfss.pdf)).
- [ ] documentation of the used database structure and used `import` and `alter` scripts
- [ ] add some manual comments or automatically generated comments to each puzzle's move; e.g. by means of `python-chess` accessing the [Stockfish](https://stockfishchess.org/) engine
- [ ] scripts for tasks' automation (with 1.) HTML-->PDF, 2.) merging PDFs, etc.)
- [ ] \(evtl. for another project) similar script(s) for PGN[^2] files or a script that takes the FEN[^3] plus the PGN[^2] of a match generating such a booklet[^1].

## Contact
[@hlotze](https://github.com/hlotze)

[^1]: [booklet](https://helpx.adobe.com/acrobat/kb/print-booklets-acrobat-reader.html) - one A4 sheet folded takes four pages
[^2]: PGN - see [Wikipedia Portable Game Notation](https://en.wikipedia.org/wiki/Portable_Game_Notation)
[^3]: FEN - see [Wikipedia Forsyth–Edwards Notation](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation)
[^4]: UCI - see [Wikipedia Universal Chess Interface](https://en.wikipedia.org/wiki/Universal_Chess_Interface)
[^5]: SVG - see [Wikipedia Scalable Vector Graphics](https://en.wikipedia.org/wiki/Scalable_Vector_Graphics)
