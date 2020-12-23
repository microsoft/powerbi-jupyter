// Copyright (c) Microsoft
// Distributed under the terms of the Modified BSD License.

import {
  DOMWidgetModel,
  DOMWidgetView,
  ISerializers
} from '@jupyter-widgets/base';

import { Report, service, factories } from 'powerbi-client';

import { MODULE_NAME, MODULE_VERSION } from './version';

// Import the CSS
import '../css/report.css';

// Initialize powerbi service
const powerbi = new service.Service(factories.hpmFactory, factories.wpmpFactory, factories.routerFactory);

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
      container_width: 0
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

export class ReportView extends DOMWidgetView {
  report: Report;
  render() {
    this.el.classList.add('report-container');

    this.embed_configChanged();

    // Observe changes in the traitlets in Python, and define custom callback.
    this.model.on('change:embed_config', this.embed_configChanged, this);
    this.model.on('change:container_height', this.dimensionsChanged, this);
    this.model.on('change:container_width', this.dimensionsChanged, this);
  }

  dimensionsChanged() {
    this.el.style.height = `${this.model.get('container_height')}px`;
    this.el.style.width = `${this.model.get('container_width')}px`;
  }

  embed_configChanged() {
    const reportConfig = this.model.get('embed_config');
    this.report = powerbi.embed(this.el, reportConfig) as Report;
    this.model.set('_embedded', true);

    this.touch();
  }
}
