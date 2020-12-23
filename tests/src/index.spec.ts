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


describe('Example', () => {

  describe('ReportModel', () => {

    it('should be createable', () => {
      const model = createTestModel(ReportModel);
      expect(model).to.be.an(ReportModel);
    });

    it('should be createable using embed_config', () => {
      const state = { embed_config: {'accessToken': null, 'embedUrl': null} }
      const model = createTestModel(ReportModel, state);
      expect(model).to.be.an(ReportModel);
      expect(model.get('embed_config')).to.be.equal(state.embed_config);
    });

  });

});
