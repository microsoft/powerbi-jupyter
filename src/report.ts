// Copyright (c) Microsoft
// Distributed under the terms of the Modified BSD License.

import { DOMWidgetModel, DOMWidgetView, ISerializers } from '@jupyter-widgets/base';

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
import { getActivePageSize, getRequestedPage } from './utils';
import { IPageNode } from 'page';
import { IReportNode } from 'report';

// Initialize powerbi service
const powerbi = new service.Service(
  factories.hpmFactory,
  factories.wpmpFactory,
  factories.routerFactory
);

const REPORT_FILTER_REQUEST_DEFAULT_STATE = {
  filters: [],
  request_completed: true,
};

const REPORT_NOT_EMBEDDED_MESSAGE = 'Power BI report is not embedded';

export class ReportModel extends DOMWidgetModel {
  defaults(): any {
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
      export_visual_data_request: {},
      visual_data: null,
      _event_data: {
        event_name: null,
        event_details: null,
      },
      _report_filters_request: REPORT_FILTER_REQUEST_DEFAULT_STATE,
      _get_pages_request: false,
      _report_pages: [],
      _get_visuals_page_name: null,
      _page_visuals: [],
      _report_bookmark_name: null,
      _get_bookmarks_request: false,
      _report_bookmarks: [],
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

interface ExportVisualDataRequest {
  pageName?: string;
  visualName?: string;
  rows?: number;
  underlyingData?: boolean;
}

interface ReportFilterRequest {
  filters: models.ReportLevelFilters[];
  request_completed: boolean;
}

interface PageWithOptionalReport {
  report?: IReportNode;
}

interface VisualWithOptionalPage {
  page?: IPageNode;
}

interface DOMRectSize {
  bottom: number;
  height: number;
  left: number;
  right: number;
  top: number;
  width: number;
  x: number;
  y: number;
}

export class ReportView extends DOMWidgetView {
  report: Report;
  reportContainer: HTMLDivElement;

  render(): void {
    const newDivElement = document.createElement('div');
    newDivElement.style.visibility = 'hidden';
    this.el.appendChild(newDivElement);

    this.reportContainer = newDivElement;

    this.embed_configChanged();

    // Observe changes in the traitlets in Python, and define custom callback.
    this.model.on('change:embed_config', this.embed_configChanged, this);
    this.model.on('change:container_height', this.dimensionsChanged, this);
    this.model.on('change:container_width', this.dimensionsChanged, this);
    this.model.on(
      'change:export_visual_data_request',
      this.export_visual_data_requestChanged,
      this
    );
    this.model.on('change:_report_filters_request', this.reportFiltersChanged, this);
    this.model.on('change:_get_pages_request', this.getPagesRequestChanged, this);
    this.model.on('change:_get_visuals_page_name', this.getVisualsPageNameChanged, this);
    this.model.on('change:_report_bookmark_name', this.reportBookmarkNameChanged, this);
    this.model.on('change:_get_bookmarks_request', this.getBookmarksRequestChanged, this);
  }

  dimensionsChanged(): void {
    this.reportContainer.style.height = `${this.model.get('container_height')}px`;
    this.reportContainer.style.width = `${this.model.get('container_width')}px`;
  }

  embed_configChanged(): void {
    const reportConfig = this.model.get('embed_config') as IEmbedConfiguration;

    // Phased loading
    this.report = powerbi.load(this.reportContainer, reportConfig) as Report;

    this.report.on('loaded', async () => {
      console.log('Loaded');

      try {
        // Get dimensions of output cell
        const DOMRect: DOMRectSize = this.el.getBoundingClientRect();

        const { width, height } = await getActivePageSize(this.report);

        if (width && height) {
          const outputCellWidth = DOMRect.width || 980;
          const newHeight = outputCellWidth * (height / width);

          this.reportContainer.style.width = `${outputCellWidth}px`;
          this.reportContainer.style.height = `${newHeight}px`;

          // Show the report container
          this.reportContainer.style.visibility = 'visible';

          // Complete the phased embedding
          this.report.render();
        } else {
          console.error('Invalid report size');
        }
      } catch (error) {
        console.error(error);
      }

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

  async export_visual_data_requestChanged(): Promise<void> {
    if (!this.report) {
      console.error(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const export_visual_data_request = this.model.get(
      'export_visual_data_request'
    ) as ExportVisualDataRequest;

    // Check export visual data request object is null or empty
    if (!export_visual_data_request || Object.keys(export_visual_data_request).length === 0) {
      // This is the case of model reset
      return;
    }

    if (!export_visual_data_request.pageName || !export_visual_data_request.visualName) {
      console.error('Page and visual names are required');
      return;
    }

    const pageName = export_visual_data_request.pageName;
    const visualName = export_visual_data_request.visualName;
    const dataRows = export_visual_data_request.rows;
    const exportDataType = export_visual_data_request.underlyingData
      ? models.ExportDataType.Underlying
      : models.ExportDataType.Summarized;

    try {
      const selectedPage: Page = await getRequestedPage(this.report, pageName);
      const visuals: VisualDescriptor[] = await selectedPage.getVisuals();
      const selectedVisual: VisualDescriptor = visuals.filter((visual: VisualDescriptor) => {
        return visual.name === visualName;
      })[0];

      if (!selectedVisual) {
        throw 'Visual not found';
      }

      const data = await selectedVisual.exportData(exportDataType, dataRows);

      // Update data
      this.model.set('visual_data', data.data);
      this.touch();
    } catch (error) {
      console.error('Export visual data error:', error);
    }
  }

  async reportFiltersChanged(): Promise<void> {
    if (!this.report) {
      console.error(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const filterRequest = this.model.get('_report_filters_request') as ReportFilterRequest;

    if (filterRequest.request_completed) {
      // Reset of filter request
      return;
    }

    try {
      // Add new filters or remove filters when filters array is empty
      if (filterRequest.filters.length > 0) {
        await this.report.updateFilters(models.FiltersOperations.Add, filterRequest.filters);
      } else {
        await this.report.updateFilters(models.FiltersOperations.RemoveAll);
      }
    } catch (error) {
      console.error(error);
    }

    // Reset filter request
    this.model.set('_report_filters_request', REPORT_FILTER_REQUEST_DEFAULT_STATE);
    this.touch();
  }

  async getPagesRequestChanged(): Promise<void> {
    if (!this.report) {
      console.error(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const get_pages_request = this.model.get('_get_pages_request') as boolean;
    if (!get_pages_request) {
      return;
    }

    try {
      const pages: Page[] = await this.report.getPages();

      if (!pages) {
        throw 'Pages not found';
      }

      // Remove 'report' property from Page object to handle nested property loop
      const pagesWithoutReport = pages.map((page: PageWithOptionalReport) => {
        delete page.report;
        return page;
      });

      this.model.set('_report_pages', pagesWithoutReport);
      this.touch();
    } catch (error) {
      console.error('Get pages error:', error);
    }
  }

  async getVisualsPageNameChanged(): Promise<void> {
    if (!this.report) {
      console.error(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const get_visuals_page_name = this.model.get('_get_visuals_page_name') as string;
    if (!get_visuals_page_name) {
      return;
    }

    try {
      const selectedPage: Page = await getRequestedPage(this.report, get_visuals_page_name);
      const visuals: VisualDescriptor[] = await selectedPage.getVisuals();

      if (!visuals) {
        throw 'Visuals not found';
      }

      // Remove 'page' property from Visual object to handle nested property loop
      const visualsWithoutPage = visuals.map((visual: VisualWithOptionalPage) => {
        delete visual.page;
        return visual;
      });

      this.model.set('_page_visuals', visualsWithoutPage);
      this.touch();
    } catch (error) {
      console.error('Get visuals error:', error);
    }
  }

  async reportBookmarkNameChanged(): Promise<void> {
    if (!this.report) {
      console.error(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const bookmarkName = this.model.get('_report_bookmark_name') as string;

    try {
      // Apply corresponding bookmark to the embedded report
      await this.report.bookmarksManager.apply(bookmarkName);
    } catch (error) {
      console.error('Set bookmark error:', error);
    }
  }

  async getBookmarksRequestChanged(): Promise<void> {
    if (!this.report) {
      console.error(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const get_bookmarks_request = this.model.get('_get_bookmarks_request') as boolean;
    if (!get_bookmarks_request) {
      return;
    }

    try {
      // Get list of bookmarks present in the report
      const bookmarks: models.IReportBookmark[] = await this.report.bookmarksManager.getBookmarks();

      // Check if there is any bookmark saved on the embedded report
      if (bookmarks.length === 0) {
        this.model.set('_report_bookmarks', ['']);
        this.touch();
      } else {
        this.model.set('_report_bookmarks', bookmarks);
        this.touch();
      }
    } catch (error) {
      console.error('Get bookmarks error:', error);
    }
  }
}
