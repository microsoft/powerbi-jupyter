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
For the list of features, refer [DOCUMENTATION](/DOCUMENTATION.md).

## [Demo Notebook](/demo/demo.ipynb)
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

## Contributing

This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit <https://cla.opensource.microsoft.com>.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.

Please read the [contributing guide](./CONTRIBUTING.md) before starting.

## We Value and Adhere to the Microsoft Open Source Code of Conduct

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
