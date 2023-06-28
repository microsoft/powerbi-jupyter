// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { DOMWidgetModel, DOMWidgetView } from '@jupyter-widgets/base';

import { models } from 'powerbi-client';

import { MODULE_NAME, MODULE_VERSION } from './version';
import { powerbi, setTokenExpirationListener, getTokenExpirationTimeout } from './utils';
import '../css/report.css';

const quickCreateEmbedUrl = 'https://app.powerbi.com/quickCreate';
const reportCreationMode = models.ReportCreationMode.QuickExplore;
const quickCreateTokenType = models.TokenType.Aad;

export class QuickVisualizeModel extends DOMWidgetModel {
  defaults(): any {
    return {
      ...super.defaults(),
      _model_name: QuickVisualizeModel.model_name,
      _model_module: QuickVisualizeModel.model_module,
      _model_module_version: QuickVisualizeModel.model_module_version,
      _view_name: QuickVisualizeModel.view_name,
      _view_module: QuickVisualizeModel.view_module,
      _view_module_version: QuickVisualizeModel.view_module_version,
      _embed_config: {},
      _event_data: {
        event_name: null,
        event_details: null,
      },
      _saved_report_id: null,
      _embedded: false,
      _token_expired: false,
      _init_error: null,
      container_height: 0,
      container_width: 0,
    };
  }

  static model_name = 'QuickVisualizeModel';
  static model_module = MODULE_NAME;
  static model_module_version = MODULE_VERSION;
  static view_name = 'QuickVisualizeView';
  static view_module = MODULE_NAME;
  static view_module_version = MODULE_VERSION;
}

export class QuickVisualizeView extends DOMWidgetView {
  quickCreate: any; //TODO: update type once QuickCreate will be exported
  quickCreateContainer: HTMLDivElement;

  render(): void {
    const newDivElement = document.createElement('div');
    newDivElement.style.visibility = 'hidden';
    this.el.appendChild(newDivElement);

    this.quickCreateContainer = newDivElement;

    this.embedConfigChanged();

    // Observe changes in the traitlets in Python, and define custom callback.
    this.model.on('change:_embed_config', this.embedConfigChanged, this);
    this.model.on('change:container_height', this.containerSizeChanged, this);
    this.model.on('change:container_width', this.containerSizeChanged, this);
  }

  containerSizeChanged(): void {
    if (this.quickCreateContainer) {
      this.quickCreateContainer.style.height = `${this.model.get('container_height')}px`;
      this.quickCreateContainer.style.width = `${this.model.get('container_width')}px`;
    }
  }

  setTokenExpiredFlag(): void {
    this.model.set('_token_expired', true);
    this.touch();
  }

  embedConfigChanged(): void {
    const embedConfig = this.model.get('_embed_config');
    const quickCreateConfig = embedConfig as models.IQuickCreateConfiguration;

    if (!quickCreateConfig) {
      this.model.set('_init_error', 'Embed configuration is missing');
      this.touch();
      return;
    }

    // Populate fixed configuration
    quickCreateConfig.type = 'quickCreate';
    quickCreateConfig.tokenType = quickCreateTokenType;
    quickCreateConfig.embedUrl = quickCreateEmbedUrl;
    quickCreateConfig.reportCreationMode = reportCreationMode;

    if (this.quickCreate) {
      // To avoid re-embedding Quick Create
      if (this.quickCreate.config.accessToken !== quickCreateConfig.accessToken) {
        // Set new access token
        this.quickCreate.setAccessToken(quickCreateConfig.accessToken);

        if (quickCreateConfig.accessToken) {
          // Set token expiration listener to update the token TOKEN_REFRESH_THRESHOLD minutes before expiration
          setTokenExpirationListener(quickCreateConfig.accessToken, this);
        }
      }

      this.model.set('_embedded', true);
      this.touch();
      return;
    } else {
      // Refresh access token before embedding if token is expired
      if (
        !quickCreateConfig.accessToken ||
        getTokenExpirationTimeout(quickCreateConfig.accessToken) <= 0
      ) {
        this.setTokenExpiredFlag();
        return;
      }
    }

    this.quickCreate = powerbi.quickCreate(this.quickCreateContainer, quickCreateConfig);

    try {
      // this.el is updated with correct width when report is loaded. Using timeout until "loaded" event is implemented
      setTimeout(() => {
        if (quickCreateConfig.accessToken) {
          // Set token expiration listener to update the token TOKEN_REFRESH_THRESHOLD minutes before expiration
          setTokenExpirationListener(embedConfig.accessToken, this);
        }

        // Set default aspect ratio
        const aspectRatio = 9 / 16;

        let width = this.model.get('container_width') as number;
        let height = this.model.get('container_height') as number;

        if (!width || !height) {
          // Get dimensions of output cell
          const DOMRect = this.el.getBoundingClientRect();

          width = DOMRect.width || 980;
          height = width * aspectRatio;
        }

        // Set dimensions of quick create container
        this.quickCreateContainer.style.width = `${width}px`;
        this.quickCreateContainer.style.height = `${height}px`;

        this.quickCreateContainer.style.visibility = 'visible';
      }, 500);
    } catch (error) {
      console.error(error);
    }

    this.quickCreate.on('loaded', () => {
      console.log('Loaded');

      // Invoke loaded event handler on kernel side
      this.model.set('_event_data', {
        event_name: 'loaded',
        event_details: null,
      });

      this.touch();
    });

    this.quickCreate.on('rendered', () => {
      console.log('Rendered');

      // Invoke rendered event handler on kernel side
      this.model.set('_event_data', {
        event_name: 'rendered',
        event_details: null,
      });

      this.touch();
    });

    this.quickCreate.on('saved', (saved_event_details: any) => {
      console.log('Report saved to workspace');

      // Create a reportDetails object so that we can only pass report id and report name
      const reportDetails = {
        reportObjectId: saved_event_details?.detail?.reportObjectId,
        reportName: saved_event_details?.detail?.reportName,
      };

      // Invoke rendered event handler on kernel side
      this.model.set('_event_data', {
        event_name: 'saved',
        event_details: reportDetails,
      });

      this.touch();

      // Save report details
      this.model.set('_saved_report_id', saved_event_details?.detail?.reportObjectId);

      this.touch();
    });

    this.quickCreate.on('error', (errorMessage: any) => {
      // Invoke error handling on kernel side if container isn't visible yet
      if (this.quickCreateContainer.style.visibility === 'visible') {
        return;
      }

      const messageDetail = (errorMessage as any)?.detail;
      this.model.set(
        '_init_error',
        `${messageDetail?.message} - ${messageDetail?.detailedMessage}`
      );
      this.touch();
    });

    // Notify that report embedding has started
    this.model.set('_embedded', true);

    // Commit model changes
    this.touch();
  }
}
