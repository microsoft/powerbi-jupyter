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
  ReportModel, ReportView
} from '../../src/'


describe('Example', () => {

  describe('ReportModel', () => {

    it('should be createable', () => {
      let model = createTestModel(ReportModel);
      expect(model).to.be.an(ReportModel);
      expect(model.get('value')).to.be('Hello World');
    });

    it('should be createable with a value', () => {
      let state = { value: 'Foo Bar!' }
      let model = createTestModel(ReportModel, state);
      expect(model).to.be.an(ReportModel);
      expect(model.get('value')).to.be('Foo Bar!');
    });

  });

});
