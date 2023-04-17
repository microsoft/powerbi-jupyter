// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import expect = require('expect.js');
import { createTestModel } from './utils.spec';
import { ReportModel, QuickVisualizeModel } from '../../src/'


describe('Widget model tests', () => {
  [ReportModel, QuickVisualizeModel].forEach(widgetModel => {
    it(`${widgetModel.model_name}: should be creatable`, () => {
      const state = { _embed_config: {'accessToken': null, 'embedUrl': null} }
      const model = createTestModel(widgetModel, state);
      expect(model).to.be.an(widgetModel);
      expect(model.get('_embed_config')).to.be.equal(state._embed_config);
    });
  });
});
