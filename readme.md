# Mind Map Markdown

This is a tool to convert markdown files to a realtime mind map. Markdown has become the ubiquitous format for writing notes. This tool allows you to visualize your notes in a mind map format. It is a tool to help you organize your thoughts and ideas. Speaking for myself, whenever I write something down, I end up not using it again. I hope that with this tool I become a bit more disciplined and use my notes more often.

## Features (ToDo)

I want to version this project's planning along with its sources as an experiment. It seems like a good idea to be using it as a test bed.

- [x] Support clicking on markdown elements and opening file in that line
- [x] Support depth of markdown headers
- [x] Add button to pick layout (dropdown with options, including manual which serializes and saves coordinates)
- [ ] Improve crap rest API
- [ ] Support click expand/collapse of markdown headers
- [ ] Support auto resize of window (currently you have to click on "fit view" control, also for some layouts it doesn't work at all)
- [ ] Send back position to mind map when user clicks on a node and save that position
- [ ] Start feeding back project documentation into the mind map (dunno what content it would have, maybe a features showcase/story-book-esque)
- [ ] Support other editors besides pycharm (all jetbrains?)
- [ ] Use docker for testing (local CI)
- [ ] Acceptable theme for the mind map.
- [ ] Maybe make a plugin for VSCode to make it easier to use.
- [ ] Maybe use electron or native. I love KDE so maybe a KDE app.
- [ ] Maybe support serialization of the mind map to github compatible format.
- [ ] Maybe git history back'n'forth.
- [ ] Bug: what if you have equal headers in different lines, click to line will go to first encountered, you'll have to go up to parent or something. Maybe just ignore this

## Usage

### Backend

```bash
cd backend
python -m venv venv
. ./venv/bin/activate
pip install -r requirements.txt
python app.py --root-dir=$PWD/../docs/example
```

### Frontend

```bash
cd frontend
yarn
yarn start
```

Your default browser should show the mind map:
![img.png](docs/img.png)

## CI

I opted to use [pre-commit](https://pre-commit.com/) instead of a github pipeline for now because it seems my runner would be exposed for repo forks for instance. I haven't looked into it yet.

Anyway to use git hooks you need to install the pre-commit package:

```bash
pip install pre-commit
pre-commit install
# et voila
```
