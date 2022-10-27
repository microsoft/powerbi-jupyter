// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

import { models, Page, Report, service, factories } from 'powerbi-client';
import { QuickVisualizeView } from './quickVisualize';
import { ReportView } from './report';
import { MODULE_VERSION } from './version';

// Jupyter SDK type to be passed with service instance creation
const JUPYTER_SDK_TYPE = 'powerbi-jupyter';

// Initialize powerbi service
export const powerbi = new service.Service(
  factories.hpmFactory,
  factories.wpmpFactory,
  factories.routerFactory,
  { type: JUPYTER_SDK_TYPE, sdkWrapperVersion: MODULE_VERSION }
);

/**
 * Returns width and height of the active page as an object
 * @param report PowerBI Report
 */
export async function getActivePageSize(report: Report): Promise<models.ICustomPageSize> {
  const pages = await report.getPages();

  // Get the active page
  const activePage = pages.find((page) => {
    return page.isActive;
  });

  if (!activePage) {
    throw 'No active report page';
  }

  return activePage.defaultSize;
}

export async function getRequestedPage(report: Report, pageName: string): Promise<Page> {
  const pages: Page[] = await report.getPages();
  const requestedPage: Page = pages.filter((page: Page) => {
    return page.name === pageName;
  })[0];

  if (!requestedPage) {
    throw 'Page not found';
  }

  return requestedPage;
}

/**
 * Set token expiration listener
 * @param tokenExpiration Access token expiration timestamp
 * @param minutesToRefresh Minutes before expiration
 * @param widgetView ReportView | QuickVisualizeView
 */
export async function setTokenExpirationListener(
  tokenExpiration: number,
  minutesToRefresh: number,
  widgetView: ReportView | QuickVisualizeView
): Promise<void> {
  // Get current time
  const currentTime = Date.now();
  const expiration = tokenExpiration * 1000;
  const safetyInterval = minutesToRefresh * 60 * 1000;

  // Time until token refresh in milliseconds
  const timeout = expiration - currentTime - safetyInterval;

  // If timeout reaches safetyInterval, invoke the setTokenExpiredFlag method
  if (timeout <= 0) {
    widgetView.setTokenExpiredFlag();
  } else {
    // Set timeout so minutesToRefresh minutes before token expires, setTokenExpiredFlag will be invoked
    console.log('Access Token will expire in ' + timeout + ' milliseconds.');
    setTimeout(() => {
      widgetView.setTokenExpiredFlag();
    }, timeout);
  }
}
