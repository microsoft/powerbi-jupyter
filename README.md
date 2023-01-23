# powerbi-jupyter

Powerbi-jupyter is a python IPyWidget that enables customers to use Power BI embedding and reporting capabilities in a Jupyter notebook seamlessly.

## Installation

You can install using `pip`:

```bash
pip install powerbiclient
```

If you are using jupyterlab:

```bash
pip install powerbiclient
jupyter labextension install @jupyter-widgets/jupyterlab-manager
```

If you are using Jupyter Notebook 5.2 or earlier, you may also need to enable
the nbextension:
```bash
jupyter nbextension enable --py [--sys-prefix|--user|--system] powerbiclient
```
For the full list of features, refer to the [DOCUMENTATION](/DOCUMENTATION.md).

## [Demo Notebooks](/demo/)
- `Power BI report demo.ipynb`: a Jupyter notebook that embeds a user's report.
It demonstrates the complete flow of embedding and interacting with Power BI report i.e. embedding a Power BI report, setting report event handlers, getting a list of pages and visual, exporting and visualizing visual data and applying filters.
- `Visualize with Power BI demo.ipynb`: a Jupyter notebook that creates a quick auto-generated Power BI report over pandas DataFrames. The created reports can be customized and saved to a Power BI workspace.

### Required python packages:
- pandas
- matplotlib - only for `report_demo.ipynb`

To run the demo, first run the following commands:
```bash
cd demo
jupyter notebook
```
Then, open and run `report_demo.ipynb` or `quick_visualize_demo.ipynb`.

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.opensource.microsoft.com>.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

Please read the [contributing guide](./CONTRIBUTING.md) before starting.

## We Value and Adhere to the Microsoft Open Source Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.