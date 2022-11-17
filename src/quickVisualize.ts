// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { DOMWidgetModel, DOMWidgetView } from '@jupyter-widgets/base';

import { models } from 'powerbi-client';

import { MODULE_NAME, MODULE_VERSION } from './version';
import { powerbi, setTokenExpirationListener } from './utils';
import '../css/report.css';

// Set threshold to refresh token in minutes
const TOKEN_REFRESH_THRESHOLD = 10;

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
      _embedded: false,
      _token_expired: false,
      _init_error: null,
      container_height: 0,
      container_width: 0,
    };
  };

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

    if (this.quickCreate) {
      // To avoid re-embedding Quick Create
      if (this.quickCreate.config.accessToken !== quickCreateConfig.accessToken) {
        // Set new access token
        this.quickCreate.setAccessToken(quickCreateConfig.accessToken);

        if (embedConfig.tokenExpiration) {
          // Set token expiration listener to update the token TOKEN_REFRESH_THRESHOLD minutes before expiration
          setTokenExpirationListener(embedConfig.tokenExpiration, TOKEN_REFRESH_THRESHOLD, this);
        }
      }

      this.model.set('_embedded', true);
      this.touch();
      return;
    }

    this.quickCreate = powerbi.quickCreate(this.quickCreateContainer, quickCreateConfig);

    if (embedConfig.tokenExpiration) {
      // Set token expiration listener to update the token TOKEN_REFRESH_THRESHOLD minutes before expiration
      setTokenExpirationListener(embedConfig.tokenExpiration, TOKEN_REFRESH_THRESHOLD, this);
    }

    // TODO: show iframe when report is loaded once "loaded" event is implemented
    try {
      // this.el is updated with correct width when report is loaded. Using timeout until "loaded" event is implemented
      setTimeout(() => {
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
      }, 500)
    } catch (error) {
      console.error(error);
    }

    this.quickCreate.on('error', (errorMessage: any) => {
      // Invoke error handling on kernel side
      const messageDetail = errorMessage?.detail;
      this.model.set('_init_error', `${messageDetail?.message} - ${messageDetail?.detailedMessage}`);
      this.touch();
    });

    // Notify that report embedding has started
    this.model.set('_embedded', true);

    // Commit model changes
    this.touch();
  }
}
