// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { DOMWidgetModel, DOMWidgetView, ISerializers } from '@jupyter-widgets/base';

import {
  Report,
  models,
  VisualDescriptor,
  Page,
  IReportEmbedConfiguration,
} from 'powerbi-client';

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/report.css';
import { getActivePageSize, getRequestedPage, powerbi, setTokenExpirationListener, getTokenExpirationTimeout } from './utils';

const EXPORT_DATA_DEFAULT_STATE: ExportVisualDataRequest = {
  pageName: undefined,
  visualName: undefined,
  rows: undefined,
  exportDataType: undefined,
};

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
      _embed_config: {},
      _embedded: false,
      container_height: 0,
      container_width: 0,
      _export_visual_data_request: EXPORT_DATA_DEFAULT_STATE,
      _visual_data: null,
      _event_data: {
        event_name: null,
        event_details: null,
      },
      _get_filters_request: false,
      _report_filters: [],
      _report_filters_request: REPORT_FILTER_REQUEST_DEFAULT_STATE,
      _get_pages_request: false,
      _report_pages: [],
      _get_visuals_page_name: null,
      _page_visuals: [],
      _report_bookmark_name: null,
      _get_bookmarks_request: false,
      _report_bookmarks: [],
      _report_active_page: null,
      _token_expired: false,
      _client_error: null,
      _init_error: null
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
  exportDataType?: number;
}

interface ReportFilterRequest {
  filters: models.ReportLevelFilters[];
  request_completed: boolean;
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

    this.embedConfigChanged();

    // Observe changes in the traitlets in Python, and define custom callback.
    this.model.on('change:_embed_config', this.embedConfigChanged, this);
    this.model.on('change:container_height', this.containerSizeChanged, this);
    this.model.on('change:container_width', this.containerSizeChanged, this);
    this.model.on('change:_export_visual_data_request', this.exportVisualDataRequestChanged, this);
    this.model.on('change:_get_filters_request', this.getFiltersRequestChanged, this);
    this.model.on('change:_report_filters_request', this.reportFiltersChanged, this);
    this.model.on('change:_get_pages_request', this.getPagesRequestChanged, this);
    this.model.on('change:_get_visuals_page_name', this.getVisualsPageNameChanged, this);
    this.model.on('change:_report_bookmark_name', this.reportBookmarkNameChanged, this);
    this.model.on('change:_get_bookmarks_request', this.getBookmarksRequestChanged, this);
    this.model.on('change:_report_active_page', this.reportActivePageChanged, this);
  }

  containerSizeChanged(): void {
    if (this.reportContainer) {
      this.reportContainer.style.height = `${this.model.get('container_height')}px`;
      this.reportContainer.style.width = `${this.model.get('container_width')}px`;
    }
  }

  setTokenExpiredFlag(): void {
    this.model.set('_token_expired', true);
    this.touch();
  }

  embedConfigChanged(): void {
    const embedConfig = this.model.get('_embed_config');
    const reportConfig = embedConfig as IReportEmbedConfiguration;

    if (this.report) {
      const accessToken = reportConfig.accessToken as string;

      // To avoid re-embedding the report
      if (
        this.report.config.embedUrl === reportConfig.embedUrl &&
        this.report.config.accessToken !== reportConfig.accessToken
      ) {
        // Set new access token
        this.report.setAccessToken(accessToken);

        if (reportConfig.accessToken) {
          // Set token expiration listener to update the token TOKEN_REFRESH_THRESHOLD minutes before expiration
          setTokenExpirationListener(reportConfig.accessToken, this);
        }
      }
      this.model.set('_embedded', true);
      this.touch();
      return;
    } else {
      // Refresh access token before embedding if token is expired
      if (!reportConfig.accessToken || getTokenExpirationTimeout(reportConfig.accessToken) <= 0) {
        this.setTokenExpiredFlag();
        return;
      }
    }

    // Flag for checking create mode
    const createReportMode =
      embedConfig.viewMode !== models.ViewMode.View &&
      embedConfig.viewMode !== models.ViewMode.Edit;

    // Check if the embedding mode is create mode
    if (createReportMode) {
      // Create blank Power BI report
      this.report = powerbi.createReport(this.reportContainer, reportConfig as models.IReportCreateConfiguration) as Report;
    } else {
      // Phased loading
      this.report = powerbi.load(this.reportContainer, reportConfig) as Report;
    }

    // Set default aspect ratio
    let aspectRatio = 9 / 16;

    this.report.on('loaded', async () => {
      console.log('Loaded');

      if (reportConfig.accessToken) {
        // Set token expiration listener to update the token TOKEN_REFRESH_THRESHOLD minutes before expiration
        setTokenExpirationListener(embedConfig.accessToken, this);
      }

      try {
        // Check if embed mode is view/edit to get active page size
        if (!createReportMode) {
          // Get page size for the Power BI report
          const { width, height } = await getActivePageSize(this.report);
          if (width && height) {
            // Update aspect ratio according to the page size
            aspectRatio = height / width;
          } else {
            console.error('Invalid report size');
          }
        }

        let width = this.model.get('container_width') as number;
        let height = this.model.get('container_height') as number;

        if (!width || !height) {
          // Get dimensions of output cell
          const DOMRect: DOMRectSize = this.el.getBoundingClientRect();

          width = DOMRect.width || 980;
          height = width * aspectRatio;
        }

        // Set dimensions of report container
        this.reportContainer.style.width = `${width}px`;
        this.reportContainer.style.height = `${height}px`;

        
        // Show the report container
        this.reportContainer.style.visibility = 'visible';

        if (!createReportMode) {
          // Complete the phased embedding
          this.report.render();
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
      // Invoke error handling on kernel side if container isn't visible yet
      if (this.reportContainer.style.visibility === "visible") {
        return;
      }

      const messageDetail = (errorMessage as any)?.detail;
      this.model.set('_init_error', `${messageDetail?.message} - ${messageDetail?.detailedMessage}`);
      this.touch();
    });

    // Notify that report embedding has started
    this.model.set('_embedded', true);

    // Commit model changes
    this.touch();
  }

  async exportVisualDataRequestChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const exportVisualDataRequest = this.model.get(
      '_export_visual_data_request'
    ) as ExportVisualDataRequest;

    // Check export visual data request object is null or empty
    if (
      !exportVisualDataRequest.pageName &&
      !exportVisualDataRequest.visualName &&
      !exportVisualDataRequest.rows &&
      !exportVisualDataRequest.exportDataType
    ) {
      // This is the case of model reset
      return;
    }

    if (!exportVisualDataRequest.pageName || !exportVisualDataRequest.visualName) {
      const errorMessage = 'Page and visual names are required';
      this.logError(errorMessage);

      return;
    }

    const pageName = exportVisualDataRequest.pageName;
    const visualName = exportVisualDataRequest.visualName;
    const dataRows = exportVisualDataRequest.rows;
    const exportDataType = exportVisualDataRequest.exportDataType;

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
      this.model.set('_visual_data', data.data);
      this.touch();
    } catch (error) {
      this.logError(error);
    }
  }

  async getFiltersRequestChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const get_filters_request = this.model.get('_get_filters_request') as boolean;
    if (!get_filters_request) {
      // Reset of get filters request
      return;
    }

    try {
      // Get list of filters applied on the report
      const filters: models.IFilter[] = await this.report.getFilters();

      if (!filters) {
        throw 'No filters available';
      }

      this.model.set('_report_filters', filters);
      this.model.set('_get_filters_request', false);
      this.touch();
    } catch (error) {
      this.logError(error);
    }
  }

  async reportFiltersChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
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
        await this.report.updateFilters(models.FiltersOperations.Replace, filterRequest.filters);
      } else {
        await this.report.updateFilters(models.FiltersOperations.RemoveAll);
      }

      // Reset filter request
      this.model.set('_report_filters_request', REPORT_FILTER_REQUEST_DEFAULT_STATE);
      this.touch();
    } catch (error) {
      this.logError(error);
    }
  }

  async getPagesRequestChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
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
      const pagesWithoutReport = pages.map((page) => {
        const { report, ...newPage } = page;
        return newPage;
      });

      this.model.set('_report_pages', pagesWithoutReport);
      this.touch();
    } catch (error) {
      this.logError(error);
    }
  }

  async getVisualsPageNameChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
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
      const visualsWithoutPage = visuals.map((visual) => {
        const { page, ...newVisual } = visual;
        return newVisual;
      });

      this.model.set('_page_visuals', visualsWithoutPage);
      this.touch();
    } catch (error) {
      this.logError(error);
    }
  }

  async reportBookmarkNameChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const bookmarkName = this.model.get('_report_bookmark_name') as string;

    try {
      // Apply corresponding bookmark to the embedded report
      await this.report.bookmarksManager.apply(bookmarkName);
    } catch (error) {
      this.logError(error);
    }
  }

  async getBookmarksRequestChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
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
      this.logError(error);
    }
  }

  async reportActivePageChanged(): Promise<void> {
    if (!this.report) {
      this.logError(REPORT_NOT_EMBEDDED_MESSAGE);
      return;
    }

    const pageName = this.model.get('_report_active_page') as string;

    try {
      // Set the provided page as active
      await this.report.setPage(pageName);
    } catch (error) {
      this.logError(error);
    }
  }

  private logError(errorMessage: any): void {
    let stringifiedError = JSON.stringify(errorMessage);
    if (stringifiedError === '{}') {
      stringifiedError = errorMessage.toString();
    }

    console.error(errorMessage);
    this.model.set('_client_error', stringifiedError);
    this.touch();
  }
}
