// Copyright (c) Microsoft
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers,
} from '@jupyter-widgets/base';

import {
  Report,
  service,
  factories,
  models,
  VisualDescriptor,
  Page,
  IEmbedConfiguration,
} from 'powerbi-client';

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/report.css';

// Initialize powerbi service
const powerbi = new service.Service(
  factories.hpmFactory,
  factories.wpmpFactory,
  factories.routerFactory
);

export class ReportModel extends DOMWidgetModel {
  defaults() {
    return {
      ...super.defaults(),
      _model_name: ReportModel.model_name,
      _model_module: ReportModel.model_module,
      _model_module_version: ReportModel.model_module_version,
      _view_name: ReportModel.view_name,
      _view_module: ReportModel.view_module,
      _view_module_version: ReportModel.view_module_version,
      embed_config: {},
      _embedded: false,
      container_height: 0,
      container_width: 0,
      extract_data_request: {},
      visual_data: null,
      _event_data: {
        event_name: null,
        event_details: null,
      },
    };
  }

  static serializers: ISerializers = {
    ...DOMWidgetModel.serializers,
  };

  static model_name = 'ReportModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'ReportView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

interface ExtractDataRequest {
  pageName?: string;
  visualName?: string;
  rows?: number;
}

export class ReportView extends DOMWidgetView {
  report: Report;
  render(): void {
    this.el.classList.add('report-container');

    this.embed_configChanged();

    // Observe changes in the traitlets in Python, and define custom callback.
    this.model.on('change:embed_config', this.embed_configChanged, this);
    this.model.on('change:container_height', this.dimensionsChanged, this);
    this.model.on('change:container_width', this.dimensionsChanged, this);
    this.model.on(
      'change:extract_data_request',
      this.extract_data_requestChanged,
      this
    );
  }

  dimensionsChanged(): void {
    this.el.style.height = `${this.model.get('container_height')}px`;
    this.el.style.width = `${this.model.get('container_width')}px`;
  }

  embed_configChanged(): void {
    const reportConfig = this.model.get('embed_config') as IEmbedConfiguration;
    this.report = powerbi.embed(this.el, reportConfig) as Report;

    this.report.on('loaded', () => {
      console.log('Loaded');
      // Invoke loaded event handler on kernel side
      this.model.set('_event_data', {
        event_name: 'loaded',
        event_details: null,
      });

      this.touch();
    });

    this.report.on('rendered', () => {
      console.log('Rendered');
      // Invoke rendered event handler on kernel side
      this.model.set('_event_data', {
        event_name: 'rendered',
        event_details: null,
      });

      this.touch();
    });

    this.report.on('error', (errorMessage) => {
      // Invoke error event handler on kernel side
      this.model.set('_event_data', {
        event_name: 'error',
        event_details: errorMessage.detail,
      });

      this.touch();
    });

    // Notify that report embedding has started
    this.model.set('_embedded', true);

    // Commit model changes
    this.touch();
  }

  async extract_data_requestChanged(): Promise<void> {
    if (!this.report) {
      console.error('Power BI report not found');
      return;
    }
    
    const extract_data_request = this.model.get('extract_data_request') as ExtractDataRequest;

    // Check extract data request object is null or empty
    if (!extract_data_request || Object.keys(extract_data_request).length === 0) {
      // This is the case of model reset
      return;
    }

    if (!extract_data_request.pageName || !extract_data_request.visualName) {
      console.error('Page and visual names are required');
      return;
    }

    const pageName = extract_data_request.pageName;
    const visualName = extract_data_request.visualName;
    const dataRows = extract_data_request.rows;

    try {
      const pages: Page[] = await this.report.getPages();
      const selectedPage: Page = pages.filter((page: Page) => {
        return page.name === pageName;
      })[0];

      if (!selectedPage) {
        throw 'Page not found';
      }

      const visuals: VisualDescriptor[] = await selectedPage.getVisuals();
      const selectedVisual: VisualDescriptor = visuals.filter(
        (visual: VisualDescriptor) => {
          return visual.name === visualName;
        }
      )[0];

      if (!selectedVisual) {
        throw 'Visual not found';
      }

      // TODO: Allow both exportData types
      // TODO: Remove "as unknown" when return type of exportData is fixed
      const data = await selectedVisual.exportData(
        models.ExportDataType.Summarized,
        dataRows
      ) as unknown as models.IExportDataResult; 

      // Update data
      this.model.set('visual_data', data.data);
      this.touch();
    } catch (error) {
      console.error('Extract data error:', error);
    }
  }
}
