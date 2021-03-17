
# powerbi-jupyter

Powerbi-jupyter is a python IPyWidget that enables customers to use many embedding capabilities in a Jupyter notebook seamlessly

## Installation

You can install using `pip`:

```bash
pip install powerbiclient
```

Or if you use jupyterlab:

```bash
pip install powerbiclient
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] powerbiclient
```
For the list of features, refer [DOCUMENTATION](\DOCUMENTATION.md).

## [Demo Notebook](\demo\demo.ipynb)
A Jupyter notebook that embeds a sample report.
It demonstrates the complete flow of embedding and interacting with Power BI report i.e. embedding a Power BI report, setting report event handlers, get list of pages, get list of visuals, export and visualize visual data and apply filters.

### Required python packages:
- pandas
- matplotlib

To run the demo, run the following commands:
```bash
cd demo
jupyter notebook
```
Now, run demo.ipynb