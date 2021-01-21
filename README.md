
# powerbi-jupyter

A Custom Jupyter Widget Library

## Installation

You can install using `pip`:

```bash
pip install powerbi_client
```

Or if you use jupyterlab:

```bash
pip install powerbi_client
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] powerbi_client
```

## Development Installation

### Setup
```bash
# First install the python package. This will also build the JS packages.
pip install -e ".[test, examples]"
```

When developing your extensions, you need to manually enable your extensions with the
notebook / lab frontend. For lab, this is done by the command:

```
jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build
jupyter labextension install .
```

For classic notebook, you can run:

```
jupyter nbextension install --sys-prefix --symlink --overwrite --py powerbi_client
jupyter nbextension enable --sys-prefix --py powerbi_client
```

__Note__ that the `--symlink` flag doesn't work on Windows, so you will here have to run
the `install` command every time that you rebuild your extension. For certain installations
you might also need another flag instead of `--sys-prefix`, but we won't cover the meaning
of those flags here.

### How to see your changes
#### Typescript (Frontend):
To continuously monitor the project for changes and automatically trigger a rebuild, 

For Jupyter Lab:
1. Start Jupyter Lab in watch mode:
    ```bash
    jupyter lab --watch
    ```

For classic jupyter notebook:
1. Build frontend code with either watch or single build mode:
    ```bash
    npm run build 
    ```
    or,
    ```bash
    npm run watch
    ```

1. Copy output to jupyter directory
    ```bash
    jupyter nbextension install --sys-prefix --overwrite --py powerbi_client
    ```

1. Reload webpage in browser

In a separate shell session, keep the Jupyter notebook running:
```bash
jupyter notebook
```

#### Python (Backend kernel):
If you make changes to the python code then you will need to restart the notebook kernel to have it take effect.

## Run Tests
#### Frontend:
`npm run test`<br/>
`npm run test:chrome`<br/>
`npm run firefox`<br/>
`npm run ie`<br/>
`npm run debug`<br/>

#### Python:
1. `pytest powerbi_client --cov -v`
