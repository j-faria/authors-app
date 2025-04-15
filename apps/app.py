import marimo

__generated_with = "0.12.9"
app = marimo.App(width="full", app_title="Authors")


@app.cell
def _():
    import marimo as mo
    import micropip
    return micropip, mo


@app.cell
async def _(micropip):
    await micropip.install("authors", keep_going=True)
    import authors
    return (authors,)


@app.cell
def _(mo):
    get_input, set_input = mo.state('')
    get_output, set_output = mo.state('')
    return get_input, get_output, set_input, set_output


@app.cell
def _(authors, get_input, get_output, mo, pyperclip, set_input, set_output):
    author_text = mo.ui.text_area(value=get_input(), label='Author List:', rows=20)

    def get_aanda(s):
        if author_text.value:
            set_output(authors.Authors(author_text.value).AandA(show=False, add_orcids=orcid.value))
        else:
            set_output('No authors in list')

    def get_mnras(s):
        if author_text.value:
            set_output(authors.Authors(author_text.value).MNRAS(show=False, add_orcids=orcid.value))
        else:
            set_output('No authors in list')

    def clear(s):
        set_input('')
        set_output('')

    def copy_output(s):
        pyperclip.copy(get_output())

    aanda_button = mo.ui.button(label='A&A', tooltip='create LaTeX for A&A', on_click=get_aanda)
    mnras_button = mo.ui.button(label='MNRAS', tooltip='create LaTeX for MNRAS', on_click=get_mnras)
    orcid = mo.ui.checkbox(label='orcid?')
    return (
        aanda_button,
        author_text,
        clear,
        copy_output,
        get_aanda,
        get_mnras,
        mnras_button,
        orcid,
    )


@app.cell
def _(
    aanda_button,
    author_text,
    clear,
    copy_output,
    get_output,
    mnras_button,
    mo,
    orcid,
):
    output = mo.md(fr"""
    Output:
    <pre>{get_output()}</pre>
    """)
    clear_button = mo.ui.button(label='Clear', kind='warn', on_click=clear)
    copy_button = mo.ui.button(label='Copy output', kind='success', on_click=copy_output)

    layout = mo.hstack([
        mo.vstack([
            author_text, 
            mo.hstack([clear_button, aanda_button, mnras_button, orcid], justify='start'),
            #mo.hstack([copy_button], justify='start') if can_copy else '',
        ]),
        output
    ], justify='start', widths=[1, 4])
    layout
    return clear_button, copy_button, layout, output


@app.cell
def _(authors, get_table_selection, mo):
    all_known_authors = authors.authors.get_all_known_authors()
    table = mo.ui.table(
        [
            {
                'Name' : k, 
                'Affiliations': v['affiliations'],
                'ORCID': v.get('orcid', '-')
            } 
            for k, v in all_known_authors.items()
        ], 
        label="All Known Authors:", pagination=True, show_download=False, on_change=get_table_selection)
    table
    return all_known_authors, table


@app.cell
def _(set_input):
    def get_table_selection(selection):
        set_input('\n'.join([s['Name'] for s in selection]))
    return (get_table_selection,)


@app.cell
def _():
    def validate_new_author(v):
        if v['name'] == '':
            return 'Author name cannot be empty'
        if v['affil'] == '':
            return 'At least one affiliation must be defined'
    def on_new_author(v):
        print(v)
    return on_new_author, validate_new_author


@app.cell(hide_code=True)
def _():
    def validate_update_author_name(v):
        if v['old_name'] == '':
            return 'Old author name cannot be empty'
        if v['new_name'] == '':
            return 'New author name cannot be empty'
        if v['old_name'] == v['new_name']:
            return 'Old author name is equal to new author name'
    def on_update_author_name(v):
        print(v)
    return on_update_author_name, validate_update_author_name


@app.cell
def _(mo):
    mo.md("""---""")
    return


@app.cell
def _(
    mo,
    on_new_author,
    on_update_author_name,
    validate_new_author,
    validate_update_author_name,
):
    explanation = mo.md("""
    Use the forms in these tabs to interact with the author database, 
    adding new authors or updating author names, affiliations or ORCIDs.
    """)

    tab1 = (
        mo.vstack([mo.md("{name}"), mo.md("{affil}"), mo.md("{orcid}")])
        .batch(
            name = mo.ui.text(label="Author name: ", full_width=True),
            affil = mo.ui.text_area(label="Affiliations (one per line): ", full_width=True),
            orcid = mo.ui.text(label="ORCID: ", max_length=19),
        )
        .form(show_clear_button=True, clear_on_submit=False, bordered=True,
              validate=validate_new_author, on_change=on_new_author)
    )

    tab2 = (
        mo.vstack([mo.md("{old_name}"), mo.md("{new_name}")])
        .batch(
            old_name = mo.ui.text(label="**Old** author name: ", full_width=True),
            new_name = mo.ui.text(label="**New** author name: ", full_width=True),
        )
        .form(show_clear_button=True, clear_on_submit=False, bordered=True,
              validate=validate_update_author_name, on_change=on_update_author_name)
    )

    tab3 = (
        mo.vstack([mo.md("{name}"), mo.md("{affil}"), mo.md("{add_replace}")])
        .batch(
            name = mo.ui.text(label="Author name: ", full_width=True),
            affil = mo.ui.text_area(label="Affiliations (one per line): ", full_width=True),
            add_replace = mo.ui.radio(options=['Add', 'Replace'], inline=True, label='Strategy:&nbsp;')
        )
        .form(show_clear_button=True, clear_on_submit=True, bordered=True)
    )

    tab4 = (
        mo.vstack([mo.md("{name}"), mo.md("{orcid}")])
        .batch(
            name = mo.ui.text(label="Author name: ", full_width=True),
            orcid = mo.ui.text(label="ORCID: ", max_length=19),
        )
        .form(show_clear_button=True, clear_on_submit=True, bordered=True)
    )

    tabs = mo.ui.tabs({
        "Interact": explanation,
        "New Author": tab1,
        "Update Author Name": tab2,
        "Update Author Affiliations": tab3,
        "Update Author ORCID": tab4,
    })
    tabs
    return explanation, tab1, tab2, tab3, tab4, tabs


@app.cell
def _(authors, get_input, mo):
    from pathlib import Path

    try:
        a = authors.Authors(get_input())
        pdf_aanda = authors.latex_pdf_utils.preview_AandA(a.AandA(show=False), open_pdf=False)
        pdf_mnras = authors.latex_pdf_utils.preview_MNRAS(a.MNRAS(show=False), open_pdf=False)
        pdfs = mo.hstack([
            mo.pdf(Path(pdf_aanda), width="100%", height='40vh'),
            mo.pdf(Path(pdf_mnras), width="100%", height='40vh')
        ], widths=[1, 1])
    except ValueError:
        pdfs = ''

    pdfs
    return Path, a, pdf_aanda, pdf_mnras, pdfs


if __name__ == "__main__":
    app.run()
