// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

import expect = require('expect.js');

import {
  // Add any needed widget imports here (or from controls)
} from '@jupyter-widgets/base';

import {
  createTestModel
} from './utils.spec';

import {
  ReportModel
} from '../../src/'


describe('Widget model tests', () => {

  describe('ReportModel', () => {

    it('should be creatable', () => {
      const model = createTestModel(ReportModel);
      expect(model).to.be.an(ReportModel);
    });

    it('should be creatable using embed_config', () => {
      const state = { _embed_config: {'accessToken': null, 'embedUrl': null} }
      const model = createTestModel(ReportModel, state);
      expect(model).to.be.an(ReportModel);
      expect(model.get('_embed_config')).to.be.equal(state._embed_config);
    });

  });

});
